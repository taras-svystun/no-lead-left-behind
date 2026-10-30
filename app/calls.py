"""The after-call webhook: a processed call's summary and fields land on the buyer's lead.

Simulated: the payload follows Ringostat's "call processed by AI" event (D9), with the keys
the spec's "Call webhook fields" table marks simulated.

Run it, then post the fixture:
    python -m app.calls
    curl -d @tests/fixtures/call-processed.json http://127.0.0.1:8080/calls
"""

import json
import logging
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

import anthropic

from app import crm
from app.agent import MODEL
from app.bot import CRM_FILE, ROOT, load_env
from app.redact import redact

PORT = 8080
# Without these we cannot find the lead or read the call.
REQUIRED = ("call_id", "caller", "transcript_url")

# Simulated: Ringostat serves the .vtt at `transcript_url`; here it is the file of that name in
# tests/fixtures. Only the name is used, so a payload cannot point us at any other file.
SIMULATED_TRANSCRIPTS = ROOT / "tests" / "fixtures"

SYSTEM = """You read the transcript of a phone call between a manager of Client A, a residential developer in Kyiv, and a buyer.
Personal data is already replaced with [NAME], [PHONE] and [EMAIL].

Return:
- call_summary: one or two sentences for the manager: what the buyer wants and the agreed next step. Write in the language of the call.
- complex, rooms, budget_usd, timing, payment: only what the buyer said in this call; null for anything not said.
  rooms is 0 for a studio. budget_usd is a whole number of US dollars. payment is full, instalments or mortgage."""

# Structured output: the API constrains the reply to JSON in this shape.
FIELDS_SCHEMA = {
    "type": "object",
    "properties": {
        "call_summary": {"type": "string"},
        # The API rejects "enum" next to a type list, so a choice or null is an anyOf.
        "complex": {"anyOf": [{"type": "string", "enum": ["North", "River"]}, {"type": "null"}]},
        "rooms": {"type": ["integer", "null"]},
        "budget_usd": {"type": ["integer", "null"]},
        "timing": {"type": ["string", "null"]},
        "payment": {"anyOf": [{"type": "string", "enum": ["full", "instalments", "mortgage"]}, {"type": "null"}]},
    },
    "required": ["call_summary", "complex", "rooms", "budget_usd", "timing", "payment"],
    "additionalProperties": False,
}


def process_call(db, client, payload):
    """Put one processed call's summary and fields on the caller's lead.

    Return the lead id, or None for a call ID already processed.
    """
    call_id = str(payload["call_id"])
    if crm.call_processed(db, call_id):
        return None
    phone = payload["caller"]
    lead = crm.find_by_phone(db, phone)
    if lead is None:
        # Ringostat sends no CRM lead id, so a phone we do not know is a new buyer (D5).
        lead_id = crm.create_lead(db, "call")
        crm.update_lead(db, lead_id, phone=phone)
        lead = crm.find_by_phone(db, phone)

    transcript = read_vtt(fetch_transcript(payload["transcript_url"]))
    # The names we know: the buyer's from the lead, the manager's from the payload (D6).
    names = [name for name in (lead["name"], payload.get("employee_fio")) if name]
    fields = _summarise(client, redact(transcript, names))

    # Newest wins, but a field the call did not mention never erases what the chat saved.
    update = {name: value for name, value in fields.items() if value is not None and name != "call_summary"}
    # Each call adds a line, so an earlier call's note is kept.
    update["call_summary"] = "\n".join(filter(None, [lead["call_summary"], fields["call_summary"]]))
    crm.update_lead(db, lead["id"], **update)
    # Marked only after the lead is updated: if the AI call fails, Ringostat's resend is processed.
    crm.mark_call_processed(db, call_id, lead["id"])
    return lead["id"]


def _summarise(client, transcript):
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": FIELDS_SCHEMA}},
        system=SYSTEM,
        messages=[{"role": "user", "content": transcript}],
    )
    return json.loads(next(block.text for block in response.content if block.type == "text"))


def fetch_transcript(url):
    return (SIMULATED_TRANSCRIPTS / Path(urlparse(url).path).name).read_text()


# "<v Клієнт>" marks the speaker of a cue; other tags (<b>, </v>) carry nothing for us.
VOICE = re.compile(r"<v(?:\.[^ >]*)? ([^>]+)>")
TAG = re.compile(r"<[^>]+>")


def read_vtt(vtt):
    """Return a .vtt transcript as plain lines, "Speaker: words", without time codes.

    A .vtt file is blocks split by blank lines. A cue block has an optional id, a timing line
    ("00:00:01.000 --> 00:00:04.200") and its text; the header and NOTE blocks have no timing.
    """
    lines = []
    for block in re.split(r"\n\s*\n", vtt.strip()):
        rows = block.splitlines()
        timing = next((i for i, row in enumerate(rows) if "-->" in row), None)
        if timing is None:
            continue
        text = " ".join(rows[timing + 1 :])
        text = TAG.sub("", VOICE.sub(r"\1: ", text)).strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def make_server(crm_file, client, port=PORT):
    """The webhook endpoint: POST /calls with the event's JSON.

    One request at a time (HTTPServer, not ThreadingHTTPServer), so a resend arriving
    mid-processing waits and is then skipped. Local only: a real one needs HTTPS and a secret.
    """
    server = HTTPServer(("127.0.0.1", port), CallWebhook)
    server.crm_file = crm_file
    server.client = client
    return server


class CallWebhook(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/calls":
            return self._answer(404, {"error": "not found"})
        try:
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            missing = [key for key in REQUIRED if not payload.get(key)]
            if missing:
                raise ValueError(f"missing {missing}")
            crm.normalise_phone(payload["caller"])  # a hidden number has no lead to land on
        except (ValueError, TypeError, AttributeError) as error:
            # A payload we cannot use: Ringostat's resend would not help.
            return self._answer(400, {"error": str(error)})
        # Its own connection per request: SQLite connections stay in the thread that made them.
        db = crm.connect(self.server.crm_file)
        try:
            lead_id = process_call(db, self.server.client, payload)
        except FileNotFoundError:
            # No such transcript: a resend would fail the same way.
            return self._answer(400, {"error": "transcript not found"})
        except Exception:
            # Our failure (the AI or the transcript): a 500 makes Ringostat send the call again.
            logging.exception("Call %s failed", payload["call_id"])
            return self._answer(500, {"error": "processing failed"})
        finally:
            db.close()
        if lead_id is None:
            return self._answer(200, {"skipped": "call already processed"})
        logging.info("Call %s summarised on lead %s", payload["call_id"], lead_id)
        return self._answer(200, {"lead_id": lead_id})

    def _answer(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_env(ROOT / ".env")
    server = make_server(CRM_FILE, anthropic.Anthropic())
    logging.info("Call webhook on http://127.0.0.1:%s/calls; CRM in %s", PORT, CRM_FILE)
    server.serve_forever()


if __name__ == "__main__":
    main()
