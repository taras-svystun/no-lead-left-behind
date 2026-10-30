"""End to end without the network: a Telegram update -> the real agent -> a lead in the CRM -> a sent message.

Claude and Telegram are fakes; the agent and the SQLite CRM are real.
"""

import os

from app import agent as agent_module
from app import bot, crm
from tests.test_agent import BUYER, make_agent, text, tool_call

STRANGER = 700000001


class FakeTelegram:
    """Stands in for bot.Telegram: records every method call instead of sending it."""

    def __init__(self):
        self.calls = []

    def call(self, method, **params):
        self.calls.append((method, params))

    def sent(self):
        return [params for method, params in self.calls if method == "sendMessage"]


def message(sender, **fields):
    """A Telegram update holding one message from `sender` in a private chat."""
    return {"update_id": 1, "message": {"from": {"id": sender}, "chat": {"id": sender, "type": "private"}, **fields}}


def test_a_text_from_an_allowed_buyer_creates_a_lead_and_replies_with_the_share_phone_button():
    agent, db, _ = make_agent(text("Двокімнатна в North коштує 89 900 USD."))
    telegram = FakeTelegram()

    bot.handle_update(message(BUYER, text="Скільки коштує двокімнатна в North?"), agent, telegram, {BUYER})

    assert crm.find_by_telegram_id(db, BUYER) is not None
    [sent] = telegram.sent()
    assert sent["chat_id"] == BUYER
    assert "89 900" in sent["text"]
    assert sent["reply_markup"]["keyboard"] == [[{"text": "Поділитися номером", "request_contact": True}]]


def test_an_id_not_on_the_allowed_list_gets_no_reply_no_ai_call_and_no_lead():
    agent, db, claude = make_agent()
    telegram = FakeTelegram()

    bot.handle_update(message(STRANGER, text="Привіт"), agent, telegram, {BUYER})

    assert telegram.calls == []
    assert claude.requests == []
    assert crm.find_by_telegram_id(db, STRANGER) is None


def test_a_shared_contact_puts_the_phone_on_the_lead_removes_the_button_and_never_reaches_claude():
    agent, db, claude = make_agent(text("Який у вас бюджет?"), text("Дякую! Коли плануєте купівлю?"))
    telegram = FakeTelegram()
    bot.handle_update(message(BUYER, text="Шукаю двокімнатну"), agent, telegram, {BUYER})

    contact = {"phone_number": "380000000001", "first_name": "Test", "user_id": BUYER}
    bot.handle_update(message(BUYER, contact=contact), agent, telegram, {BUYER})

    assert crm.find_by_telegram_id(db, BUYER)["phone"] == "+380000000001"
    assert telegram.sent()[-1]["reply_markup"] == {"remove_keyboard": True}
    assert "380000000001" not in str(claude.requests)


def test_a_message_without_text_such_as_a_sticker_gets_no_reply_and_no_ai_call():
    agent, _, claude = make_agent()
    telegram = FakeTelegram()

    bot.handle_update(message(BUYER, sticker={"file_id": "sticker"}), agent, telegram, {BUYER})

    assert telegram.calls == []
    assert claude.requests == []


def test_someone_elses_contact_sent_from_the_attachment_menu_is_not_saved_as_the_buyers_phone():
    agent, db, _ = make_agent(text("Який у вас бюджет?"))
    telegram = FakeTelegram()
    bot.handle_update(message(BUYER, text="Шукаю двокімнатну"), agent, telegram, {BUYER})

    friend = {"phone_number": "380000000002", "first_name": "Friend", "user_id": STRANGER}
    bot.handle_update(message(BUYER, contact=friend), agent, telegram, {BUYER})

    assert crm.find_by_telegram_id(db, BUYER)["phone"] is None
    assert len(telegram.sent()) == 1


def test_a_phone_the_buyer_types_also_removes_the_share_phone_button():
    agent, db, _ = make_agent(
        text("Який у вас бюджет?"),
        tool_call("save_lead", phone="+380000000001"),
        text("Дякую! Коли плануєте купівлю?"),
    )
    telegram = FakeTelegram()
    bot.handle_update(message(BUYER, text="Шукаю двокімнатну"), agent, telegram, {BUYER})

    bot.handle_update(message(BUYER, text="Мій номер +380000000001"), agent, telegram, {BUYER})

    assert crm.find_by_telegram_id(db, BUYER)["phone"] == "+380000000001"
    assert telegram.sent()[-1]["reply_markup"] == {"remove_keyboard": True}


def test_a_contact_sent_before_any_text_still_creates_the_lead_and_gets_the_ai_disclosure():
    agent, db, _ = make_agent(text("Дякую! Яку квартиру шукаєте?"))
    telegram = FakeTelegram()

    contact = {"phone_number": "380000000001", "first_name": "Test", "user_id": BUYER}
    bot.handle_update(message(BUYER, contact=contact), agent, telegram, {BUYER})

    assert crm.find_by_telegram_id(db, BUYER)["phone"] == "+380000000001"
    assert telegram.sent()[0]["text"].startswith(agent_module.DISCLOSURE["uk"])


def test_a_message_in_a_group_gets_no_reply_even_from_an_allowed_id():
    agent, db, claude = make_agent()
    telegram = FakeTelegram()
    update = message(BUYER, text="Привіт")
    update["message"]["chat"] = {"id": -100123, "type": "group"}

    bot.handle_update(update, agent, telegram, {BUYER})

    assert telegram.calls == []
    assert claude.requests == []


def test_load_env_skips_comments_and_keeps_a_variable_already_set(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('# a comment\nNLLB_TOKEN=123:abc\nNLLB_IDS=1,2\n')
    monkeypatch.delenv("NLLB_TOKEN", raising=False)
    monkeypatch.setenv("NLLB_IDS", "9")

    bot.load_env(env)

    assert os.environ["NLLB_TOKEN"] == "123:abc"
    assert os.environ["NLLB_IDS"] == "9"
