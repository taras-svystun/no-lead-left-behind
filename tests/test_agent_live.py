"""End-to-end: case 1 against the real Claude API. Costs about 0.001 USD; skipped without a key."""

import os
from datetime import datetime

import anthropic
import pytest

from app import agent, crm

# Haiku 5.5, USD per token (D2).
INPUT_PRICE, OUTPUT_PRICE = 0.10 / 1e6, 0.50 / 1e6
BUYER = 512339871


class CostCounter:
    """Wraps the real client and adds up what each request costs."""

    def __init__(self, client):
        self.client = client
        self.messages = self  # the agent calls client.messages.create(...), so .messages is this object
        self.usd = 0.0

    def create(self, **request):
        response = self.client.messages.create(**request)
        self.usd += response.usage.input_tokens * INPUT_PRICE + response.usage.output_tokens * OUTPUT_PRICE
        return response


@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="needs ANTHROPIC_API_KEY")
def test_case_1_price_question_quotes_the_price_list_for_under_a_cent():
    db = crm.connect(":memory:")
    client = CostCounter(anthropic.Anthropic())
    bot = agent.Agent(db, client, now=lambda: datetime.now(agent.KYIV))

    reply = bot.reply(BUYER, "Скільки коштує двокімнатна в North?")

    print(f"\n{reply.text}\ncost: {client.usd:.5f} USD")
    assert "89 900" in reply.text or "89,900" in reply.text
    assert crm.find_by_telegram_id(db, BUYER) is not None
    assert client.usd < 0.01
