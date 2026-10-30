# The story: one buyer, start to finish

For a reader new to the project. Terms in bold are defined in `GLOSSARY.md`.

Picture Client A's sales office as a desk with a box of index cards. Each card is one **lead**: one buyer, how to reach them, what they want. The box is the **CRM**. Today managers answer late and forget to fill the cards, so the box is half empty.

1. Olena writes in Telegram: "How much is a 2-room flat?" The **agent** answers in seconds. Its first words say it is an AI. It quotes only from the **price list**, like a shop assistant reading the price tag, never guessing.
2. It asks a few **qualification** questions: budget, rooms, timing, how she pays, her phone. Like a clinic's intake form.
3. Each time it learns something, it writes it on Olena's card with the **save lead** tool (a **tool** is an action the agent does, not just says). Telegram gives every account a fixed number, the **Telegram ID**, so the bot knows the chat is Olena's. Her card is labelled with that ID, and with her phone if she gave it.
4. Olena wants a viewing. The agent does a **handoff**: it marks the card "for a manager", writes why, and tells her a manager will write within 15 minutes (at night: by 12:00). She can also send `/manager` at any moment.
5. The next day Olena phones the office. The phone system transcribes the call and sends us an **after-call webhook**. A webhook is a doorbell: another system rings our address when something happens. This one carries her phone number and the transcript.
6. We look for a card with that phone. Found: the call lands on the same card. If she never gave her phone in Telegram, no card matches, and we start a new one: two cards for one Olena, a **duplicate lead**. That is the price of not insisting on the phone.
7. Before the transcript goes to Claude, we black out her name, phone and email (**redaction**), like blacking out names before sending a file to an outside expert. Claude reads the rest and writes a **call summary** plus budget, rooms and timing onto the card.
8. The **eval runner** replays the 10 **test cases**, an exam for the agent. Code checks what the agent did (which tools it called, what is on the card, the exact price), not how it phrased things, and adds up the cost.

Three pains, three fixes: slow answers become instant answers; no conversation is lost, because each one is a card; the box fills itself.

