import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from app import calls, crm
from tests.test_agent import BUYER, FakeClient, text

FIXTURES = Path(__file__).parent / "fixtures"


def test_read_vtt_keeps_who_said_what_and_drops_time_codes():
    vtt = (FIXTURES / "call-1001.vtt").read_text()

    lines = calls.read_vtt(vtt).splitlines()

    assert lines[0] == "Співробітник: Добрий день, Client A, мене звати Андрій. Чим можу допомогти?"
    assert len(lines) == 6
    assert not any("-->" in line or line == "WEBVTT" or line.startswith("NOTE") for line in lines)


def payload(**changes):
    return {**json.loads((FIXTURES / "call-processed.json").read_text()), **changes}


def summary(content="Wants a 2-room flat in North, budget up to 100k USD, instalments.", **fields):
    """What the AI returns: the summary and every field, null where the call said nothing."""
    result = {"call_summary": content, "complex": None, "rooms": None, "budget_usd": None,
              "timing": None, "payment": None}
    return text(json.dumps({**result, **fields}))


def test_a_call_from_a_known_phone_lands_on_that_lead():
    """Case 9."""
    db = crm.connect(":memory:")
    lead_id = crm.create_lead(db, source="telegram", telegram_id=BUYER)
    crm.update_lead(db, lead_id, phone="+380000000001", rooms=2)
    client = FakeClient(summary(budget_usd=100000, payment="instalments"))

    calls.process_call(db, client, payload())

    lead = crm.find_by_phone(db, "+380000000001")
    assert lead["id"] == lead_id
    assert db.execute("SELECT COUNT(*) FROM leads WHERE phone = '+380000000001'").fetchone()[0] == 1
    assert lead["call_summary"]
    assert (lead["budget_usd"], lead["payment"]) == (100000, "instalments")
    assert lead["rooms"] == 2  # the call said nothing about rooms, so the chat's value stays


def test_personal_data_is_removed_before_the_ai_sees_the_call():
    """Case 10."""
    db = crm.connect(":memory:")
    lead_id = crm.create_lead(db, source="telegram", telegram_id=BUYER)
    crm.update_lead(db, lead_id, name="Олена", phone="+380000000001")
    client = FakeClient(summary())

    calls.process_call(db, client, payload())

    sent = json.dumps(client.requests[0], ensure_ascii=False)
    for personal in ["Андрій", "Олена", "000 000 00 01", "+380000000001", "olena@example.com"]:
        assert personal not in sent
    for placeholder in ["[NAME]", "[PHONE]", "[EMAIL]"]:
        assert placeholder in sent


def test_a_call_from_an_unknown_phone_creates_a_call_lead():
    db = crm.connect(":memory:")
    client = FakeClient(summary(budget_usd=100000))

    lead_id = calls.process_call(db, client, payload(caller="380000000002"))

    lead = crm.find_by_phone(db, "+380000000002")
    assert (lead["id"], lead["source"], lead["budget_usd"]) == (lead_id, "call", 100000)
    assert lead["call_summary"]


def test_a_repeated_call_id_is_skipped_without_a_second_ai_call():
    # Ringostat resends a webhook it thinks was lost.
    db = crm.connect(":memory:")
    client = FakeClient(summary("Wants a viewing."))

    first = calls.process_call(db, client, payload())
    second = calls.process_call(db, client, payload())

    assert len(client.requests) == 1
    assert second is None
    assert crm.find_by_phone(db, "+380000000001")["call_summary"] == "Wants a viewing."
    assert first is not None


def test_a_second_call_adds_its_summary_under_the_first():
    db = crm.connect(":memory:")
    client = FakeClient(summary("Asked about prices."), summary("Wants a viewing."))

    calls.process_call(db, client, payload(call_id="1001"))
    calls.process_call(db, client, payload(call_id="1002"))

    assert crm.find_by_phone(db, "+380000000001")["call_summary"] == "Asked about prices.\nWants a viewing."


@pytest.fixture
def webhook(tmp_path):
    """The real HTTP server on a spare port, with a fake AI; yields (post, crm_file, client)."""
    crm_file = tmp_path / "crm.sqlite"
    client = FakeClient(summary(budget_usd=100000, payment="instalments"))
    server = calls.make_server(crm_file, client, port=0)  # port 0: the OS picks a free one
    threading.Thread(target=server.serve_forever, daemon=True).start()

    def post(body):
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/calls", data=body, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(request) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)

    yield post, crm_file, client
    server.shutdown()


def test_posting_the_fixture_updates_the_lead_and_a_repeat_is_skipped(webhook):
    post, crm_file, client = webhook
    body = (FIXTURES / "call-processed.json").read_bytes()

    status, answer = post(body)
    repeat_status, repeat = post(body)

    lead = crm.find_by_phone(crm.connect(crm_file), "+380000000001")
    assert (status, answer) == (200, {"lead_id": lead["id"]})
    assert (lead["budget_usd"], lead["payment"]) == (100000, "instalments")
    assert (repeat_status, repeat) == (200, {"skipped": "call already processed"})
    assert len(client.requests) == 1


@pytest.mark.parametrize("body", [b"not json", b'{"call_id": "1001"}', b'{"call_id": "1", "caller": "anonymous", "transcript_url": "x.vtt"}'])
def test_a_payload_we_cannot_use_gets_400_and_no_ai_call(webhook, body):
    post, _, client = webhook

    status, _ = post(body)

    assert status == 400
    assert client.requests == []


def test_a_value_the_call_states_replaces_the_chats():
    db = crm.connect(":memory:")
    lead_id = crm.create_lead(db, source="telegram", telegram_id=BUYER)
    crm.update_lead(db, lead_id, phone="+380000000001", budget_usd=90000)

    calls.process_call(db, FakeClient(summary(budget_usd=100000)), payload())

    assert crm.find_by_phone(db, "+380000000001")["budget_usd"] == 100000


def test_a_transcript_we_cannot_find_gets_400_so_it_is_not_resent_forever(webhook):
    post, _, _ = webhook

    status, _ = post(json.dumps(payload(transcript_url="https://ringostat.example/ai/missing.vtt")).encode())

    assert status == 400
