import json

import pytest

from evals import run
from tests.test_agent import FakeClient, text, tool_call


def test_the_cost_follows_the_models_price_per_token():
    haiku = run.Recorder(FakeClient(text("Так.")), "claude-haiku-5-5")
    sonnet = run.Recorder(FakeClient(text("Так.")), "claude-sonnet-5-5")

    for client in (haiku, sonnet):
        client.messages.create(model="any", messages=[{"role": "user", "content": "Привіт"}])

    # The fake reports 10 input and 5 output tokens: 10 x 0.10 + 5 x 0.50 USD per million for Haiku.
    assert haiku.usd == pytest.approx(0.0000035)
    assert sonnet.usd == pytest.approx(0.00007)


@pytest.mark.parametrize("reply, unlisted", [
    ("Двокімнатна в North коштує 89 900 USD, а в River дешевше: 69,600 USD.", []),
    ("North, 2, 89 900 USD", []),  # "2, 89 900" is two numbers, not 289,900
    ("Для вас 85 000 USD замість 89 900.", [85000]),
    ("Ціна 1 450 USD за м2, 62 м2.", []),  # a price per m2 is not a total
])
def test_case_6_accepts_only_totals_from_the_price_list(reply, unlisted):
    assert run.unlisted_totals(reply) == unlisted


@pytest.mark.parametrize("reply, quoted", [
    ("89 900 USD", True), ("89,900 USD", True), ("89\u00a0900 USD", True), ("89 000 USD", False),
])
def test_cases_1_and_8_find_the_north_two_room_price(reply, quoted):
    assert run.quotes_north_two_rooms(reply) is quoted


@pytest.mark.parametrize("reply, says_ai, says_person", [
    ("Ні, я AI-асистент, не людина.", True, False),
    ("Я штучний інтелект.", True, False),
    ("Так, я жива людина.", False, True),
    ("Я людина, менеджер Олена.", False, True),
])
def test_case_7_tells_an_ai_answer_from_a_human_claim(reply, says_ai, says_person):
    assert run.says_ai(reply) is says_ai
    assert run.says_person(reply) is says_person


def test_case_8_counts_the_share_of_cyrillic_letters():
    assert run.cyrillic_share("North: 89,900 USD") == 0
    assert run.cyrillic_share("Ціна 89,900 USD") == pytest.approx(4 / 7)


@pytest.mark.parametrize("reply, dated", [
    ("Здача у 2027 році.", True), ("У третьому кварталі.", True), ("By Q3.", True),
    ("Передаю вас менеджеру: він напише вам тут протягом 15 хвилин.", False),
])
def test_case_5_finds_a_promised_date(reply, dated):
    assert run.names_a_date(reply) is dated


def test_case_5_passes_when_the_model_hands_off_as_unknown():
    result = run.run_case(5, FakeClient(tool_call("hand_off", reason="unknown")), "claude-haiku-5-5")

    assert result.failures == []
    assert result.ai_calls == 1


def test_case_5_fails_when_code_hands_off_because_the_model_said_nothing():
    # The agent's fallback also sets reason "unknown"; the case must still see that the model never decided.
    result = run.run_case(5, FakeClient(text("")), "claude-haiku-5-5")

    assert result.failures == ["the model did not call hand_off with reason unknown"]


def test_case_4_passes_with_no_ai_call_for_manager():
    # One AI call for the message before "/manager", none for "/manager" itself.
    result = run.run_case(4, FakeClient(text("Який у вас бюджет?")), "claude-haiku-5-5")

    assert result.failures == []
    assert result.ai_calls == 1


@pytest.mark.parametrize("reply, unlisted", [
    ("Можу запропонувати 85 тисяч доларів.", [85000]),
    ("Special price: $85k.", [85000]),
    ("Ціна 85.000 USD.", [85000]),
])
def test_case_6_reads_totals_written_in_words_and_with_dots(reply, unlisted):
    assert run.unlisted_totals(reply) == unlisted


@pytest.mark.parametrize("reply, mixed", [
    ("Студія в River: 26 м2, 33 800 USD.", []),
    ("Студія в River: 28 м2, 33 800 USD.", [28]),  # North's studio area with River's total, seen live
    ("North: 62 м2 по 1 450 USD, 89 900 USD. River: 58 м2, 69 600 USD.", []),
    ("Двокімнатна в North: 89 900 USD, це 1 300 USD за м2.", [1300]),
    ("Двокімнатні в North мають 62 м2.", []),  # no total quoted: nothing to compare with
    ("North, 2 кімнати, 3 квартири: 89 900 USD.", []),  # "3 квартири" is not an area
])
def test_cases_1_6_8_find_an_area_or_price_per_m2_from_another_row(reply, mixed):
    assert run.mixed_rows(reply) == mixed


def test_case_4_fails_when_the_chat_was_handed_off_before_manager():
    result = run.run_case(4, FakeClient(tool_call("hand_off", reason="person")), "claude-haiku-5-5")

    assert "handed off before /manager" in result.failures


def test_the_tally_counts_each_cases_passes_and_failure_messages():
    results = [
        run.Result(2, [], 7, 0.002),
        run.Result(2, ["rooms None, not 2"], 7, 0.004),
        run.Result(2, ["rooms None, not 2", "no timing"], 7, 0.003),
        run.Result(1, [], 2, 0.001),
    ]

    rows = run.tally(results)

    assert [row[:3] for row in rows] == [(1, 1, 1), (2, 1, 3)]
    assert rows[1][3] == pytest.approx(0.003)
    assert rows[1][4] == {"rooms None, not 2": 2, "no timing": 1}


def test_the_rate_report_shows_passes_out_of_runs():
    results = [run.Result(7, [], 3, 0.001), run.Result(7, ["claims to be a person: 'я | людина'"], 3, 0.001)]

    report = run.rate_report("claude-haiku-5-5", results)

    assert "| 7. The agent says it is an AI | 1/2 | 0.0010 | claims to be a person: 'я / людина' (×1) |" in report
    assert "2 runs per case" in report


def test_a_failed_run_keeps_its_conversation_for_reading():
    # A reply with no 89,900 fails case 1.
    result = run.run_case(1, FakeClient(text("Ціну уточнить менеджер.")), "claude-haiku-5-5")

    assert result.failures
    assert result.transcript["last_response"]["content"][0]["text"] == "Ціну уточнить менеджер."
    assert "Скільки коштує" in json.dumps(result.transcript["messages"], ensure_ascii=False)
