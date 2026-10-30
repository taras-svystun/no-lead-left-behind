from datetime import datetime

import pytest
from anthropic.types import Message, TextBlock, ToolUseBlock, Usage

from app import agent, crm

DAY = datetime(2026, 10, 30, 14, 0, tzinfo=agent.KYIV)
NIGHT = datetime(2026, 10, 30, 23, 30, tzinfo=agent.KYIV)
BUYER = 512339871


class FakeClient:
    """Stands in for anthropic.Anthropic: returns scripted responses, records every request."""

    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []
        self.messages = self  # the agent calls client.messages.create(...), so .messages is this object

    def create(self, **request):
        # Copy the list: the agent keeps appending to its chat after the call.
        self.requests.append({**request, "messages": list(request["messages"])})
        return self.responses.pop(0)


def text(content):
    return _message([TextBlock(type="text", text=content)], "end_turn")


def tool_call(name, said=None, **tool_input):
    """A response that calls a tool; `said` is text the model writes in the same response."""
    block = ToolUseBlock(type="tool_use", id=f"toolu_{name}", name=name, input=tool_input)
    content = [TextBlock(type="text", text=said), block] if said else [block]
    return _message(content, "tool_use")


def _message(content, stop_reason):
    return Message(
        id="msg_fake", type="message", role="assistant", model="claude-haiku-5-5",
        content=content, stop_reason=stop_reason,
        usage=Usage(input_tokens=10, output_tokens=5),
    )


def make_agent(*responses, now=DAY):
    db = crm.connect(":memory:")
    client = FakeClient(*responses)
    return agent.Agent(db, client, now=lambda: now), db, client


def test_first_message_creates_a_lead_and_opens_with_the_ukrainian_ai_disclosure():
    bot, db, _ = make_agent(text("Двокімнатна в North коштує 89 900 USD."))

    reply = bot.reply(BUYER, "Скільки коштує двокімнатна в North?")

    assert crm.find_by_telegram_id(db, BUYER) is not None
    assert reply.text.startswith(agent.DISCLOSURE["uk"])
    assert "89 900" in reply.text


def test_a_buyer_writing_in_english_gets_the_english_disclosure():
    bot, _, _ = make_agent(text("A 2-room flat in North costs 89,900 USD."))

    reply = bot.reply(BUYER, "Hi, how much is a two-room flat in North?")

    assert reply.text.startswith(agent.DISCLOSURE["en"])


def test_the_second_message_has_no_disclosure_and_the_ai_sees_the_whole_chat():
    bot, _, client = make_agent(text("89 900 USD."), text("Так, є іпотека."))
    bot.reply(BUYER, "Скільки коштує двокімнатна в North?")

    reply = bot.reply(BUYER, "А іпотека є?")

    assert reply.text == "Так, є іпотека."
    sent = [m["content"] for m in client.requests[1]["messages"] if m["role"] == "user"]
    assert sent[0].endswith("Скільки коштує двокімнатна в North?")
    assert sent[1] == "А іпотека є?"


def test_the_ai_hears_once_that_the_system_already_sent_the_disclosure():
    bot, _, client = make_agent(text("89 900 USD."), text("Так, є іпотека."))
    bot.reply(BUYER, "Скільки коштує двокімнатна в North?")
    bot.reply(BUYER, "А іпотека є?")

    note = agent.DISCLOSURE_NOTE.format(disclosure=agent.DISCLOSURE["uk"])
    assert client.requests[0]["messages"][0]["content"].startswith(note)
    assert agent.DISCLOSURE["uk"] not in client.requests[1]["messages"][-1]["content"]


def test_after_start_the_note_quotes_the_disclosure_the_buyer_saw_not_the_buyers_language():
    bot, _, client = make_agent(text("A studio in River is 33,800 USD."))
    bot.reply(BUYER, "/start")

    bot.reply(BUYER, "How much is a studio?")

    note = agent.DISCLOSURE_NOTE.format(disclosure=agent.DISCLOSURE["uk"])
    assert client.requests[0]["messages"][0]["content"].startswith(note)


@pytest.mark.parametrize(
    ("hour", "promise"),
    [(8, "до 12:00"), (9, "15 хвилин"), (18, "15 хвилин"), (19, "до 12:00"), (23, "до 12:00")],
)
def test_manager_command_hands_off_without_calling_the_ai(hour, promise):
    bot, db, client = make_agent(text("Який у вас бюджет?"), now=DAY.replace(hour=hour))
    bot.reply(BUYER, "Шукаю двокімнатну")

    reply = bot.reply(BUYER, "/manager")

    assert len(client.requests) == 1
    assert promise in reply.text
    lead = crm.find_by_telegram_id(db, BUYER)
    assert (lead["status"], lead["handoff_reason"]) == ("handoff", "person")


def test_after_handoff_the_agent_only_repeats_that_a_manager_is_on_it():
    bot, _, client = make_agent(text("Який у вас бюджет?"))
    bot.reply(BUYER, "Шукаю двокімнатну")
    handoff = bot.reply(BUYER, "/manager")

    reply = bot.reply(BUYER, "А знижку дасте?")

    assert reply.text == handoff.text
    assert len(client.requests) == 1


def test_manager_as_the_very_first_message_still_opens_with_the_disclosure():
    bot, _, client = make_agent()

    reply = bot.reply(BUYER, "/manager")

    assert reply.text.startswith(agent.DISCLOSURE["uk"])
    assert "15 хвилин" in reply.text
    assert client.requests == []


def test_the_ai_gets_the_price_list_the_policies_and_both_tools_in_strict_mode():
    bot, _, client = make_agent(text("89 900 USD."))

    bot.reply(BUYER, "Скільки коштує двокімнатна в North?")

    request = client.requests[0]
    assert "| North | 2 | 62 | 1,450 | 89,900 |" in request["system"]
    assert "Discounts or special prices" in request["system"]
    assert [tool["name"] for tool in request["tools"]] == ["save_lead", "hand_off"]
    assert all(tool["strict"] is True for tool in request["tools"])


def test_save_lead_fills_the_lead_and_the_ai_goes_on_to_answer():
    bot, db, client = make_agent(
        tool_call("save_lead", rooms=2, budget_usd=95000, payment="mortgage", timing="3 months"),
        text("Дякую! Коли плануєте купівлю?"),
    )

    reply = bot.reply(BUYER, "Шукаю двокімнатну, бюджет до 95 тисяч доларів, іпотека")

    lead = crm.find_by_telegram_id(db, BUYER)
    assert (lead["rooms"], lead["budget_usd"], lead["payment"]) == (2, 95000, "mortgage")
    assert reply.text.endswith("Дякую! Коли плануєте купівлю?")
    tool_result = client.requests[1]["messages"][-1]["content"][0]
    assert (tool_result["type"], tool_result.get("is_error", False)) == ("tool_result", False)


def test_save_lead_with_a_value_the_crm_rejects_reports_an_error_to_the_ai():
    bot, db, client = make_agent(tool_call("save_lead", payment="cash"), text("Як плануєте платити?"))

    bot.reply(BUYER, "Заплачу готівкою")

    assert crm.find_by_telegram_id(db, BUYER)["payment"] is None
    assert client.requests[1]["messages"][-1]["content"][0]["is_error"] is True


def test_hand_off_sets_the_reason_and_the_buyer_gets_only_the_fixed_text():
    bot, db, client = make_agent(text("Який у вас бюджет?"), tool_call("hand_off", reason="viewing"))
    bot.reply(BUYER, "Шукаю двокімнатну")

    reply = bot.reply(BUYER, "Хочу подивитися квартиру в суботу")

    assert reply.text == agent.HANDOFF["uk"]["day"]
    assert len(client.requests) == 2
    lead = crm.find_by_telegram_id(db, BUYER)
    assert (lead["status"], lead["handoff_reason"]) == ("handoff", "viewing")


def test_an_empty_ai_reply_goes_to_a_manager_as_unknown():
    bot, db, _ = make_agent(text(""))

    reply = bot.reply(BUYER, "Коли здача будинку в North?")

    assert reply.text.endswith(agent.HANDOFF["uk"]["day"])
    assert crm.find_by_telegram_id(db, BUYER)["handoff_reason"] == "unknown"


def test_the_phone_button_shows_with_the_first_reply_and_the_handoff_only():
    bot, _, _ = make_agent(text("Який бюджет?"), text("Скільки кімнат?"))

    first = bot.reply(BUYER, "Шукаю квартиру")
    second = bot.reply(BUYER, "До 95 тисяч")
    handoff = bot.reply(BUYER, "/manager")
    reminder = bot.reply(BUYER, "Ну що там?")

    assert [r.ask_phone for r in (first, second, handoff, reminder)] == [True, False, True, False]


def test_a_shared_phone_is_saved_by_code_and_never_reaches_the_ai():
    bot, db, client = make_agent(text("Який бюджет?"), text("Дякую! Скільки кімнат?"))
    bot.reply(BUYER, "Шукаю квартиру")

    reply = bot.share_phone(BUYER, "380000000001")

    assert crm.find_by_telegram_id(db, BUYER)["phone"] == "+380000000001"
    assert reply.text == "Дякую! Скільки кімнат?"
    assert "000000001" not in str(client.requests)


def test_after_the_phone_is_shared_the_handoff_has_no_button():
    bot, _, _ = make_agent(text("Який бюджет?"), text("Дякую!"))
    bot.reply(BUYER, "Шукаю квартиру")
    bot.share_phone(BUYER, "380000000001")

    assert bot.reply(BUYER, "/manager").ask_phone is False


def test_a_phone_shared_after_handoff_gets_the_reminder_without_an_ai_call():
    bot, db, client = make_agent()
    bot.reply(BUYER, "/manager")

    reply = bot.share_phone(BUYER, "380000000001")

    assert reply.text == agent.HANDOFF["uk"]["day"]
    assert crm.find_by_telegram_id(db, BUYER)["phone"] == "+380000000001"
    assert client.requests == []


def test_a_handoff_notifies_a_manager_with_a_simulated_log_line(caplog):
    bot, db, _ = make_agent()

    with caplog.at_level("INFO"):
        bot.reply(BUYER, "/manager")

    lead_id = crm.find_by_telegram_id(db, BUYER)["id"]
    assert f"Simulated: manager notified about lead {lead_id}, reason person" in caplog.text


def test_text_written_next_to_a_save_lead_call_reaches_the_buyer():
    bot, db, _ = make_agent(tool_call("save_lead", said="Записала! Скільки кімнат?", budget_usd=95000), text(""))

    reply = bot.reply(BUYER, "Бюджет до 95 тисяч доларів")

    assert reply.text.endswith("Записала! Скільки кімнат?")
    assert crm.find_by_telegram_id(db, BUYER)["status"] == "new"


def test_manager_command_with_the_bot_name_still_hands_off():
    bot, db, client = make_agent()

    bot.reply(BUYER, "/manager@ClientABot ")

    assert crm.find_by_telegram_id(db, BUYER)["handoff_reason"] == "person"
    assert client.requests == []


def test_start_command_gets_the_disclosure_without_calling_the_ai():
    bot, db, client = make_agent()

    reply = bot.reply(BUYER, "/start")

    assert reply.text.startswith(agent.DISCLOSURE["uk"])
    assert reply.ask_phone is True
    assert crm.find_by_telegram_id(db, BUYER) is not None
    assert client.requests == []


def test_a_handoff_forced_by_code_is_logged_apart_from_the_models_own(caplog):
    bot, _, _ = make_agent(text(""))

    bot.reply(BUYER, "Коли здача будинку в North?")

    assert "No answer from the AI" in caplog.text
