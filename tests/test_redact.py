import pytest

from app.redact import redact


@pytest.mark.parametrize(
    "phone",
    ["+380000000001", "380000000001", "0000000001", "000 000 00 01", "+38 (000) 000-00-01", "000-000-00-01"],
)
def test_redact_replaces_a_ukrainian_phone_in_any_format(phone):
    assert redact(f"Мій номер {phone}, дзвоніть.", names=[]) == "Мій номер [PHONE], дзвоніть."


def test_redact_keeps_prices_and_budgets():
    text = "Бюджет 100 000 доларів, двокімнатна за 89 900 USD, 1 450 USD за м2."

    assert redact(text, names=[]) == text


def test_redact_replaces_an_email():
    assert redact("Пишіть на olena.k+flat@example.com.ua, будь ласка.", names=[]) == "Пишіть на [EMAIL], будь ласка."


@pytest.mark.parametrize(
    "said, cleaned",
    [
        ("Олена, добрий день.", "[NAME], добрий день."),
        ("Олено, вам зручно?", "[NAME], вам зручно?"),
        ("Для Олени є варіант.", "Для [NAME] є варіант."),
        ("Це Андрій Коваль, відділ продажу.", "Це [NAME] [NAME], відділ продажу."),
        ("Дякую, Андрію!", "Дякую, [NAME]!"),
        ("ОЛЕНА", "[NAME]"),
    ],
)
def test_redact_replaces_known_names_in_any_form(said, cleaned):
    assert redact(said, names=["Олена", "Андрій Коваль"]) == cleaned


def test_redact_leaves_words_that_only_contain_a_name():
    # "Ян" is a known name; "Янтарна" street is not the name, it only starts the same.
    assert redact("Вулиця Янтарна, 5.", names=["Ян"]) == "Вулиця Янтарна, 5."


def test_redact_allows_at_most_three_letters_after_the_stem():
    # "Олен" + "ячий" is four letters: another word, not a form of "Олена".
    assert redact("Оленячий ріг.", names=["Олена"]) == "Оленячий ріг."
