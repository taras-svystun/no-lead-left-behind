"""Personal data removal: code, not Claude, cleans a call transcript before Claude sees it (D6)."""

import re

# A run of digits with the separators people and transcribers use: "+38 (000) 000-00-01".
# Spaces only, not newlines, so two numbers on two lines never merge.
PHONE_CANDIDATE = re.compile(r"\+?\(?\d[\d ()\-]{7,}\d")
# A Ukrainian number has 10 digits (0XX...) or 12 (380XX...); a price like "89 900" has fewer.
PHONE_MIN_DIGITS = 10
# Each dot-part needs letters after it, so a full stop after the address stays outside.
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


# Ukrainian names change their ending by case: Олена, Олено, Олени, Оленою; Андрій, Андрію.
# So we match the stem (the name without its last vowel or й/ь) plus up to 3 more letters.
ENDINGS = set("аеєиіїоуюяйьaeiouy")
MAX_ENDING = 3
# A shorter stem would hit ordinary words ("Ія" -> "І..."), so short names match only as written.
MIN_STEM = 3


def redact(text, names):
    """Replace emails with [EMAIL], phones with [PHONE] and the given names with [NAME].

    `names` are the names we already know: the buyer's from the lead, the manager's from the call.
    Emails go first: digits inside an address must not become a phone.
    """
    text = EMAIL.sub("[EMAIL]", text)
    text = PHONE_CANDIDATE.sub(_phone_or_unchanged, text)
    for name in names:
        # "Андрій Коваль" is two words, and a transcript may use either one alone.
        for word in name.split():
            text = _name_pattern(word).sub("[NAME]", text)
    return text


def _name_pattern(word):
    stem = word[:-1] if word[-1].lower() in ENDINGS else word
    if len(stem) < MIN_STEM:
        body = re.escape(word)
    else:
        body = re.escape(stem) + rf"\w{{0,{MAX_ENDING}}}"
    # Whole words only: "Ян" must not match inside "Янтарна".
    return re.compile(rf"(?<!\w){body}(?!\w)", re.IGNORECASE)


def _phone_or_unchanged(match):
    digits = re.sub(r"\D", "", match.group())
    return "[PHONE]" if len(digits) >= PHONE_MIN_DIGITS else match.group()
