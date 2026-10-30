"""Simulated CRM: one SQLite table of leads. Bitrix24 replaces it in polish (P10)."""

import re
import sqlite3

# The spec's lead fields. CHECK keeps the CRM to the values the spec allows.
SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id             INTEGER PRIMARY KEY,
    source         TEXT NOT NULL CHECK (source IN ('telegram', 'call')),
    telegram_id    INTEGER UNIQUE,
    name           TEXT,
    phone          TEXT,
    complex        TEXT,
    rooms          INTEGER,
    budget_usd     INTEGER,
    timing         TEXT,
    payment        TEXT CHECK (payment IN ('full', 'instalments', 'mortgage')),
    status         TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'handoff')),
    handoff_reason TEXT CHECK (handoff_reason IN ('person', 'viewing', 'unknown', 'complaint')),
    call_summary   TEXT
)
"""

# Fields the agent and the after-call webhook may fill; status and reason go
# through set_handoff. Python checks the field names (they go into the SQL),
# the table's CHECK checks the values.
UPDATABLE_FIELDS = {"name", "phone", "complex", "rooms", "budget_usd", "timing", "payment", "call_summary"}


def connect(path):
    """Open the CRM file (":memory:" in tests) and create the table if missing."""
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute(SCHEMA)
    return db


def create_lead(db, source, telegram_id=None):
    """Create a lead and return its id."""
    cursor = db.execute(
        "INSERT INTO leads (source, telegram_id) VALUES (?, ?)", (source, telegram_id)
    )
    db.commit()
    return cursor.lastrowid


def find_by_telegram_id(db, telegram_id):
    """Return the lead for this Telegram ID as a dict, or None."""
    row = db.execute("SELECT * FROM leads WHERE telegram_id = ?", (telegram_id,)).fetchone()
    return dict(row) if row else None


def find_by_phone(db, phone):
    """Return the oldest lead with this phone as a dict, or None."""
    row = db.execute(
        "SELECT * FROM leads WHERE phone = ? ORDER BY id LIMIT 1", (normalise_phone(phone),)
    ).fetchone()
    return dict(row) if row else None


def update_lead(db, lead_id, **fields):
    """Set the given fields on a lead; the phone is stored as E.164."""
    if not fields:
        raise ValueError("no fields to update")
    unknown = set(fields) - UPDATABLE_FIELDS
    if unknown:
        raise ValueError(f"not a lead field: {sorted(unknown)}")
    if "phone" in fields:
        fields["phone"] = normalise_phone(fields["phone"])
    assignments = ", ".join(f"{name} = ?" for name in fields)
    db.execute(f"UPDATE leads SET {assignments} WHERE id = ?", (*fields.values(), lead_id))
    db.commit()


def set_handoff(db, lead_id, reason):
    """Mark the lead for a manager; the table's CHECK rejects a reason the spec lacks."""
    db.execute(
        "UPDATE leads SET status = 'handoff', handoff_reason = ? WHERE id = ?", (reason, lead_id)
    )
    db.commit()


def normalise_phone(raw):
    """Return a phone as E.164 (+380XXXXXXXXX for Ukraine), whatever the format.

    Telegram sends 380..., Ringostat +380..., a buyer may type 0XX XXX XX XX.
    A foreign number keeps its own country code, so a foreign caller still gets a lead.
    """
    digits = re.sub(r"\D", "", raw)
    if not digits:
        raise ValueError(f"not a phone: {raw!r}")
    if len(digits) == 10 and digits.startswith("0"):
        digits = "38" + digits
    return "+" + digits
