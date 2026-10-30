"""The agent: answers a buyer in Telegram with Claude. No Telegram code here (that is app/bot.py)."""

import logging
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

from app import crm

MODEL = "claude-haiku-5-5"
KNOWLEDGE = Path(__file__).parent.parent / "knowledge"
KYIV = ZoneInfo("Europe/Kyiv")
# A model that keeps calling tools gets a manager instead of an endless bill.
MAX_AI_CALLS = 5

# Flat and step by step, for Haiku (D2). The knowledge files go in whole (D16).
SYSTEM = """You are the sales assistant of Client A, a residential developer in Kyiv. You chat with buyers in Telegram.

Rules:
1. You are an AI assistant. If asked whether you are a person or a bot, say you are an AI assistant. Never say you are a person. This question alone is not a request for a manager.
2. The system has already greeted the buyer and said you are an AI. Never greet (no "Hi", "Hello", "Вітаю") and never introduce yourself: start with the answer or your question.
3. Answer in the language the buyer writes in.
4. Answer only from the price list and the policies below. Quote prices exactly as written there.
5. Keep replies short: 1-3 sentences.
6. Learn these about the buyer, one question at a time: budget, rooms, complex, timing, payment method (full, instalments or mortgage). Do not ask about what the buyer already told you.
7. Each time the buyer tells you any of these, or their name or phone, call save_lead with what you learned, and in the same reply ask your next question.
8. After the other questions, ask once for the phone: the buyer can tap the "Share phone" button or type it. Never ask twice, never insist.
9. Call hand_off, and write nothing else, when:
   - the buyer asks for a person or a manager: reason "person";
   - the buyer wants a viewing or to book a flat: reason "viewing";
   - the question is not answered by the price list or the policies, for example completion or move-in dates: reason "unknown";
   - the buyer complains: reason "complaint".
10. Never promise a discount, a special price, a completion date, a free flat or a mortgage approval. If asked for a discount, say only a manager can discuss it and offer to pass the buyer to a manager.

{price_list}

{policies}"""

# Haiku once sent hand_off without a reason; strict makes the API return only schema-valid input.
# Every save_lead field is required but may be null: with optional fields, strict Haiku invented
# a payment or timing the buyer never said in 9 of 10 runs; with null it did in 0 of 10.
# The API rejects "enum" next to a type list, so a choice or null is an anyOf.
TOOLS = [
    {
        "name": "save_lead",
        "strict": True,
        "description": "Save what the buyer told you on their lead in the CRM. Use null for every field the buyer did not tell you.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": ["string", "null"]},
                "phone": {"type": ["string", "null"]},
                "complex": {"anyOf": [{"type": "string", "enum": ["North", "River"]}, {"type": "null"}]},
                "rooms": {"type": ["integer", "null"], "description": "0 for a studio"},
                "budget_usd": {"type": ["integer", "null"]},
                "timing": {"type": ["string", "null"], "description": "When the buyer plans to buy, e.g. 'within 3 months'"},
                "payment": {"anyOf": [{"type": "string", "enum": ["full", "instalments", "mortgage"]}, {"type": "null"}]},
            },
            "required": ["name", "phone", "complex", "rooms", "budget_usd", "timing", "payment"],
            "additionalProperties": False,
        },
    },
    {
        "name": "hand_off",
        "strict": True,
        "description": "Pass the buyer to a human manager. The buyer is told when the manager will write.",
        "input_schema": {
            "type": "object",
            "properties": {"reason": {"type": "string", "enum": ["person", "viewing", "unknown", "complaint"]}},
            "required": ["reason"],
            "additionalProperties": False,
        },
    },
]

# Code, not the model, says first that this is an AI (D7).
DISCLOSURE = {
    "uk": "Вітаю! Я AI-асистент Client A, не людина. Відповідаю за прайсом і правилами компанії.",
    "en": "Hello! I am Client A's AI assistant, not a person. I answer from the company's price list and rules.",
}

# Code picks the promise by the Kyiv hour, so the model never needs the time (D8).
# "By 12:00", never "tomorrow": after midnight "tomorrow" would be wrong.
HANDOFF = {
    "uk": {
        "day": "Передаю вас менеджеру: він напише вам тут протягом 15 хвилин.",
        "night": "Передаю вас менеджеру: він напише вам тут до 12:00.",
    },
    "en": {
        "day": "I am passing you to a manager, who will write to you here within 15 minutes.",
        "night": "I am passing you to a manager, who will write to you here by 12:00.",
    },
}

# Telegram sends /start before the buyer's first words; it needs no AI call.
START = {"uk": "Підкажіть, яку квартиру шукаєте?", "en": "What kind of flat are you looking for?"}

# What the AI hears when the buyer taps "Share phone": the number itself stays in code.
PHONE_NOTE = "[Note from the system, not the buyer: the buyer shared their phone with the button. Do not ask for it again.]"

# The model never sees the disclosure that code sends, so without this note it sometimes greets a second time.
DISCLOSURE_NOTE = (
    '[Note from the system, not the buyer: the system already sent the buyer this message: "{disclosure}" '
    "Do not greet or introduce yourself again.]"
)


@dataclass
class Reply:
    text: str
    ask_phone: bool = False  # show the "Share phone" button with this reply (D10)
    phone_saved: bool = False  # a phone reached the lead this turn: remove the button


class Agent:
    def __init__(self, db, client, now):
        self.db = db
        self.client = client
        self.now = now
        self.system = SYSTEM.format(
            price_list=(KNOWLEDGE / "price_list.md").read_text(),
            policies=(KNOWLEDGE / "policies.md").read_text(),
        )
        # Chats live in memory: a restart forgets the chat, the lead stays in the CRM.
        self.chats = {}
        self.languages = {}
        self.disclosures = {}  # the disclosure each buyer saw, quoted to the AI later

    def reply(self, telegram_id, text):
        if not text.startswith("/"):
            self.languages.setdefault(telegram_id, language_of(text))
        return self._turn(telegram_id, text)

    def share_phone(self, telegram_id, phone):
        """Save a phone sent with the button; the AI only hears that it was shared."""
        return self._turn(telegram_id, PHONE_NOTE, phone)

    def _turn(self, telegram_id, text, phone=None):
        # Every chat becomes a lead on its first message, before any AI call.
        # A contact from the attachment menu can be the first message too.
        lead = crm.find_by_telegram_id(self.db, telegram_id)
        first_message = lead is None
        if first_message:
            crm.create_lead(self.db, "telegram", telegram_id)
            lead = crm.find_by_telegram_id(self.db, telegram_id)
            self.disclosures[telegram_id] = DISCLOSURE[self.language(telegram_id)]
        if phone:
            crm.update_lead(self.db, lead["id"], phone=phone)

        answer = self._answer(telegram_id, lead, text)

        # The button shows twice at most: with the first reply and with the handoff message.
        # It goes once a phone is on the lead, shared with the button or typed.
        after = crm.find_by_telegram_id(self.db, telegram_id)
        handed_off_now = lead["status"] == "new" and after["status"] == "handoff"
        ask_phone = after["phone"] is None and (first_message or handed_off_now)
        phone_saved = lead["phone"] is None and after["phone"] is not None
        if first_message:
            answer = self.disclosures[telegram_id] + "\n\n" + answer
        return Reply(answer, ask_phone, phone_saved)

    def _answer(self, telegram_id, lead, text):
        if lead["status"] == "handoff":
            return self._handoff_text(telegram_id)
        # "/manager@ClientABot" is how Telegram sends a command picked from the menu in a group.
        command = text.strip().split("@")[0]
        if command == "/manager":
            return self._hand_off(telegram_id, lead["id"], "person")
        if command == "/start":
            return START[self.language(telegram_id)]
        return self._ask_ai(telegram_id, lead["id"], text)

    def _ask_ai(self, telegram_id, lead_id, text):
        """Run the tool loop; return the text for the buyer."""
        chat = self.chats.setdefault(telegram_id, [])
        if not chat:
            # After "/start" the buyer's language can change, but the disclosure they saw does not.
            # A restart forgets it, so the buyer's language is the best guess.
            disclosure = self.disclosures.get(telegram_id, DISCLOSURE[self.language(telegram_id)])
            text = DISCLOSURE_NOTE.format(disclosure=disclosure) + "\n\n" + text
        chat.append({"role": "user", "content": text})
        # The model often asks its next question in the same response as a save_lead call.
        said = []
        for _ in range(MAX_AI_CALLS):
            response = self.client.messages.create(
                model=MODEL,
                # A ceiling, not a cost: thinking counts against it, and a cut reply could end inside a tool call.
                # If evals ever show stop_reason "max_tokens", hand off instead of guessing.
                max_tokens=8000,
                output_config={"effort": "low"},
                system=self.system,
                tools=TOOLS,
                messages=chat,
            )
            chat.append({"role": "assistant", "content": response.content})
            said += [block.text for block in response.content if block.type == "text" and block.text]
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            if not tool_calls:
                if said:
                    return "\n\n".join(said)
                break  # a refusal or an empty reply: a manager answers instead
            handoff = next((call for call in tool_calls if call.name == "hand_off"), None)
            results = [self._save_lead(lead_id, call) for call in tool_calls if call.name == "save_lead"]
            if handoff:
                # The fixed text replaces the model's words, and no AI call follows:
                # after a handoff the chat never goes back to the model.
                return self._hand_off(telegram_id, lead_id, handoff.input["reason"])
            chat.append({"role": "user", "content": results})
        # Logged apart from the model's own hand_off, so the evals show which one fired.
        logging.warning("No answer from the AI for lead %s: handing off as unknown", lead_id)
        return self._hand_off(telegram_id, lead_id, "unknown")

    def _hand_off(self, telegram_id, lead_id, reason):
        crm.set_handoff(self.db, lead_id, reason)
        logging.info("Simulated: manager notified about lead %s, reason %s", lead_id, reason)
        return self._handoff_text(telegram_id)

    def _save_lead(self, lead_id, call):
        # Null is "not said": it must not erase what the lead already has.
        stated = {name: value for name, value in call.input.items() if value is not None}
        if not stated:
            # Not an error: the model would retry it until MAX_AI_CALLS hands off.
            return {"type": "tool_result", "tool_use_id": call.id, "content": "nothing to save"}
        try:
            crm.update_lead(self.db, lead_id, **stated)
        except (ValueError, sqlite3.IntegrityError) as error:
            return {"type": "tool_result", "tool_use_id": call.id, "content": str(error), "is_error": True}
        return {"type": "tool_result", "tool_use_id": call.id, "content": "saved"}

    def _handoff_text(self, telegram_id):
        hour = self.now().astimezone(KYIV).hour
        time_of_day = "day" if 9 <= hour < 19 else "night"
        return HANDOFF[self.language(telegram_id)][time_of_day]

    def language(self, telegram_id):
        # Ukrainian until the buyer writes words: "/manager" alone says nothing.
        return self.languages.get(telegram_id, "uk")


def language_of(text):
    """Ukrainian if the text has any Cyrillic letter, else English: enough for the fixed texts."""
    return "uk" if re.search("[а-яіїєґ]", text, re.IGNORECASE) else "en"
