"""The Telegram bot: long polling (D1), the "Share phone" button, the /manager menu. The agent does the thinking."""

import json
import logging
import os
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import anthropic

from app import crm
from app.agent import KYIV, Agent

ROOT = Path(__file__).parent.parent
CRM_FILE = ROOT / "crm.sqlite"
# Telegram holds each getUpdates request open up to this many seconds until a message comes (long polling).
POLL_SECONDS = 30
# The command menu next to the text field; /manager works at any time (D8).
# One menu for every buyer, in Ukrainian: Client A sells in Kyiv.
COMMANDS = [{"command": "manager", "description": "Зв'язатися з менеджером"}]

# Button labels follow the buyer's language, like the agent's fixed texts (D3).
SHARE_PHONE = {"uk": "Поділитися номером", "en": "Share phone"}


def handle_update(update, agent, telegram, allowed_ids):
    """Answer one Telegram update."""
    message = update["message"]
    sender = message["from"]["id"]
    # In a group the "Share phone" button cannot work, and the chat is not one buyer's.
    if message["chat"]["type"] != "private":
        return
    # The bot is public: anyone else would spend the API budget.
    if sender not in allowed_ids:
        logging.info("Ignored Telegram ID %s: not on the allowed list", sender)
        return
    contact = message.get("contact")
    own_contact = contact is not None and contact.get("user_id") == sender
    if not own_contact and "text" not in message:
        # Stickers, photos, voice, someone else's contact: the agent reads text only.
        return
    chat_id = message["chat"]["id"]
    # "typing..." in the chat header until our reply comes, so the buyer knows the message arrived.
    telegram.call("sendChatAction", chat_id=chat_id, action="typing")
    started = time.time()
    if own_contact:
        reply = agent.share_phone(sender, contact["phone_number"])
    else:
        reply = agent.reply(sender, message["text"])
    # Telegram's "date" is when the buyer sent it: the log shows whether a wait was ours or the network's.
    logging.info(
        "Answered %s: received %.0f s after sending, agent took %.1f s",
        sender, started - message["date"], time.time() - started,
    )
    params = {"chat_id": chat_id, "text": reply.text}
    if reply.phone_saved:
        # Telegram keeps a reply keyboard on screen until a message removes it.
        params["reply_markup"] = {"remove_keyboard": True}
    elif reply.ask_phone:
        label = SHARE_PHONE[agent.language(sender)]
        params["reply_markup"] = {"keyboard": [[{"text": label, "request_contact": True}]], "resize_keyboard": True}
    telegram.call("sendMessage", **params)


class Telegram:
    """The Telegram Bot API over plain HTTPS: one method, one JSON request."""

    def __init__(self, token):
        self.url = f"https://api.telegram.org/bot{token}/"

    def call(self, method, **params):
        request = urllib.request.Request(
            self.url + method,
            data=json.dumps(params).encode(),
            headers={"Content-Type": "application/json"},
        )
        # The read timeout must outlast the long poll.
        with urllib.request.urlopen(request, timeout=POLL_SECONDS + 10) as response:
            return json.load(response)["result"]


def load_env(path):
    """Put KEY=VALUE lines from .env into os.environ; a variable already set wins."""
    for line in path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_env(ROOT / ".env")
    allowed_ids = {int(value) for value in os.environ["TELEGRAM_ALLOWED_IDS"].split(",") if value.strip()}
    telegram = Telegram(os.environ["TELEGRAM_BOT_TOKEN"])
    agent = Agent(crm.connect(CRM_FILE), anthropic.Anthropic(), now=lambda: datetime.now(KYIV))
    telegram.call("setMyCommands", commands=COMMANDS)
    logging.info("Bot started; CRM in %s", CRM_FILE)
    offset = 0
    while True:
        try:
            updates = telegram.call("getUpdates", offset=offset, timeout=POLL_SECONDS, allowed_updates=["message"])
        except OSError:
            # A network blip must not stop the bot; urllib's errors are all OSErrors.
            logging.exception("getUpdates failed; trying again in 5 seconds")
            time.sleep(5)
            continue
        for update in updates:
            # Telegram forgets updates below the offset we send next, so move it before handling:
            # an update that crashes is not fetched again.
            offset = update["update_id"] + 1
            try:
                handle_update(update, agent, telegram, allowed_ids)
            except Exception:
                logging.exception("Update %s failed; the bot keeps running", update["update_id"])


if __name__ == "__main__":
    main()
