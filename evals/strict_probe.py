"""Probe: which save_lead schema makes Haiku save lead fields the buyer never said (T7).

Case 2's first message names only rooms and budget. Each schema answers it RUNS times;
the probe prints every run that saved a field wrong, and the count per schema.
Measured in T7: wrong in 9 of 10 (strict, optional), 0 of 10 (not strict), 0 of 10 (strict, nullable).

    python -m evals.strict_probe

Costs about 0.02 USD on Haiku 5.5: 30 first turns at about 0.0005 USD each.
"""

import copy

import anthropic

from app import agent, crm
from app.config import load_env
from evals.run import BUYER, Recorder, new_chat

RUNS = 10
MESSAGE = "Шукаю двокімнатну, бюджет до 95 тисяч доларів"
# What the message says; every other lead field must stay empty.
SAID = {"rooms": 2, "budget_usd": 95000}
NOT_SAID = ["name", "phone", "complex", "timing", "payment"]

# save_lead before T7, as in commit d021581: optional fields, strict.
STRICT_OPTIONAL = {
    "name": "save_lead",
    "strict": True,
    "description": "Save what the buyer told you on their lead in the CRM. Pass only the fields you learned.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "phone": {"type": "string"},
            "complex": {"type": "string", "enum": ["North", "River"]},
            "rooms": {"type": "integer", "description": "0 for a studio"},
            "budget_usd": {"type": "integer"},
            "timing": {"type": "string", "description": "When the buyer plans to buy, e.g. 'within 3 months'"},
            "payment": {"type": "string", "enum": ["full", "instalments", "mortgage"]},
        },
        "additionalProperties": False,
    },
}


def without_strict(tool):
    tool = copy.deepcopy(tool)
    tool.pop("strict")
    return tool


def required_nullable(tool):
    """Every field required, each one a value or null; the description stays as it was."""
    tool = copy.deepcopy(tool)
    props = tool["input_schema"]["properties"]
    for name, field in props.items():
        if "enum" in field:
            # The API rejects "enum" next to a type list, so a choice or null is an anyOf.
            props[name] = {"anyOf": [{"type": "string", "enum": field["enum"]}, {"type": "null"}]}
        else:
            props[name] = {**field, "type": [field["type"], "null"]}
    tool["input_schema"]["required"] = list(props)
    return tool


HAND_OFF = agent.TOOLS[1]
# The tools each run gets. "Not strict" drops strict from both tools, as T7 measured it.
# The third save_lead is the one measured in T7; app/agent.py now has it with a new description.
SCHEMAS = {
    "strict, optional fields": [STRICT_OPTIONAL, HAND_OFF],
    "not strict, optional fields": [without_strict(STRICT_OPTIONAL), without_strict(HAND_OFF)],
    "strict, required nullable fields": [required_nullable(STRICT_OPTIONAL), HAND_OFF],
}


def wrong_fields(lead):
    """Fields saved that the buyer never said, and stated fields saved wrong or not at all."""
    wrong = {name: lead[name] for name in NOT_SAID if lead[name] is not None}
    wrong |= {name: lead[name] for name, value in SAID.items() if lead[name] != value}
    return wrong


def main():
    load_env()
    client = anthropic.Anthropic()
    total = 0.0
    for label, tools in SCHEMAS.items():
        # The agent reads its module's TOOLS on each call.
        agent.TOOLS = tools
        wrong_runs = 0
        for run in range(RUNS):
            recorder = Recorder(client, agent.MODEL)
            db, bot = new_chat(recorder)
            bot.reply(BUYER, MESSAGE)
            wrong = wrong_fields(crm.find_by_telegram_id(db, BUYER))
            total += recorder.usd
            if wrong:
                wrong_runs += 1
                print(f"{label}, run {run + 1}: {wrong}")
        print(f"{label}: wrong in {wrong_runs} of {RUNS} runs")
    print(f"Total {total:.4f} USD")


if __name__ == "__main__":
    main()
