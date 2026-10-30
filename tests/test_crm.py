import sqlite3

import pytest

from app import crm


@pytest.mark.parametrize(
    "raw",
    ["380000000001", "+380000000001", "000 000 00 01", "+38 (000) 000-00-01"],
)
def test_normalise_phone_gives_e164_for_ukrainian_formats(raw):
    assert crm.normalise_phone(raw) == "+380000000001"


def test_normalise_phone_keeps_a_foreign_number_in_e164():
    assert crm.normalise_phone("+33 6 12 34 56 78") == "+33612345678"


def test_normalise_phone_rejects_text_without_digits():
    with pytest.raises(ValueError):
        crm.normalise_phone("anonymous")


@pytest.fixture
def db():
    return crm.connect(":memory:")


def test_new_lead_by_telegram_id_is_found_with_status_new(db):
    lead_id = crm.create_lead(db, source="telegram", telegram_id=512339871)

    lead = crm.find_by_telegram_id(db, 512339871)

    assert lead["id"] == lead_id
    assert lead["source"] == "telegram"
    assert lead["status"] == "new"


def test_unknown_telegram_id_finds_nothing(db):
    assert crm.find_by_telegram_id(db, 1) is None


def test_update_lead_saves_fields_and_stores_phone_as_e164(db):
    lead_id = crm.create_lead(db, source="telegram", telegram_id=512339871)

    crm.update_lead(db, lead_id, rooms=2, budget_usd=95000, payment="mortgage", phone="380000000001")

    lead = crm.find_by_telegram_id(db, 512339871)
    assert (lead["rooms"], lead["budget_usd"], lead["payment"]) == (2, 95000, "mortgage")
    assert lead["phone"] == "+380000000001"


def test_update_lead_rejects_a_field_the_spec_does_not_have(db):
    lead_id = crm.create_lead(db, source="telegram", telegram_id=512339871)

    with pytest.raises(ValueError):
        crm.update_lead(db, lead_id, discount=10)


def test_update_lead_rejects_no_fields(db):
    lead_id = crm.create_lead(db, source="telegram", telegram_id=512339871)

    with pytest.raises(ValueError):
        crm.update_lead(db, lead_id)


@pytest.mark.parametrize("lookup", ["+380000000001", "380000000001", "000 000 00 01"])
def test_find_by_phone_matches_whatever_the_format(db, lookup):
    lead_id = crm.create_lead(db, source="telegram", telegram_id=512339871)
    crm.update_lead(db, lead_id, phone="380000000001")

    assert crm.find_by_phone(db, lookup)["id"] == lead_id


def test_a_call_lead_without_telegram_id_is_found_by_phone(db):
    lead_id = crm.create_lead(db, source="call")
    crm.update_lead(db, lead_id, phone="+380000000001")

    assert crm.find_by_phone(db, "+380000000001")["source"] == "call"


def test_unknown_phone_finds_nothing(db):
    assert crm.find_by_phone(db, "+380000000002") is None


def test_set_handoff_sets_status_and_reason(db):
    lead_id = crm.create_lead(db, source="telegram", telegram_id=512339871)

    crm.set_handoff(db, lead_id, "viewing")

    lead = crm.find_by_telegram_id(db, 512339871)
    assert (lead["status"], lead["handoff_reason"]) == ("handoff", "viewing")


def test_set_handoff_rejects_a_reason_the_spec_does_not_have(db):
    lead_id = crm.create_lead(db, source="telegram", telegram_id=512339871)

    with pytest.raises(sqlite3.IntegrityError):
        crm.set_handoff(db, lead_id, "bored")


def test_a_lead_survives_reopening_the_crm_file(tmp_path):
    path = tmp_path / "crm.sqlite"
    crm.create_lead(crm.connect(path), source="telegram", telegram_id=512339871)

    assert crm.find_by_telegram_id(crm.connect(path), 512339871) is not None
