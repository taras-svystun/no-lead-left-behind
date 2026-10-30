# Glossary: no-lead-left-behind

A public showcase of one AI-agent deployment for a fictional residential developer in Kyiv.

## The story

Picture Client A's sales office as a desk with a box of index cards. Each card is one **lead**: one buyer, how to reach them, what they want. The box is the **CRM**. Today managers answer late and forget to fill the cards, so the box is half empty.

1. Olena writes in Telegram: "How much is a 2-room flat?" The **agent** answers in seconds. Its first words say it is an AI. It quotes only from the **price list**, like a shop assistant reading the price tag, never guessing.
2. It asks a few **qualification** questions: budget, rooms, timing, how she pays, her phone. Like a clinic's intake form.
3. Each time it learns something, it writes it on Olena's card with the **save lead** tool (a **tool** is an action the agent does, not just says). Telegram gives every account a fixed number, the **Telegram ID**, so the bot knows the chat is Olena's. Her card is labelled with that ID, and with her phone if she gave it.
4. Olena wants a viewing. The agent does a **handoff**: it marks the card "for a manager", writes why, and tells her a manager will write within 15 minutes. She can also send `/manager` at any moment.
5. The next day Olena phones the office. The phone system transcribes the call and sends us an **after-call webhook**. A webhook is a doorbell: another system rings our address when something happens. This one carries her phone number and the transcript.
6. We look for a card with that phone. Found: the call lands on the same card. If she never gave her phone in Telegram, no card matches, and we start a new one: two cards for one Olena, a **duplicate lead**. That is the price of not insisting on the phone.
7. Before the transcript goes to Claude, we black out her name, phone and email (**redaction**), like blacking out names before sending a file to an outside expert. Claude reads the rest and writes a **call summary** plus budget, rooms and timing onto the card.
8. The **eval runner** replays the 10 **test cases**, an exam for the agent. Code checks what the agent did (which tools it called, what is on the card, the exact price), not how it phrased things, and adds up the cost.

Three pains, three fixes: slow answers become instant answers; no conversation is lost, because each one is a card; the box fills itself.

## Terms

- **Client A**: the fictional client, a residential developer in Kyiv. Never a real company.
- **Buyer**: a person who writes in Telegram or calls about buying a flat.
- **Manager**: the client's human sales person, who takes over from the agent.
- **Lead**: a record in the CRM for one buyer, with their contact and what they want. One buyer, one lead: a call from the same phone lands on the same lead.
- **CRM**: the client's system that holds all leads, the box of cards.
- **Simulated CRM**: the core's stand-in for the client's CRM, one SQLite table; Bitrix24 replaces it in polish.
- **Agent**: the one Claude-based assistant that answers buyers in Telegram.
- **Telegram ID**: the fixed number Telegram gives each account; how the agent recognises a buyer in chat.
- **Duplicate lead**: two leads for one buyer, made when a call's phone matches no existing lead.
- **Tool**: an action the agent can call: save lead, hand off. Price lookup joins in polish.
- **Price list**: Client A's flat types, prices and payment options; the agent quotes only from it.
- **Policies**: Client A's rules for booking and viewings, and what the agent never promises.
- **Handoff**: the agent stops and passes the buyer to a manager. The buyer can ask for it at any time with `/manager`.
- **AI disclosure**: the agent says it is an AI, first thing and whenever asked. It never poses as a human.
- **Qualification**: the questions that tell how serious a buyer is and what they need (budget, rooms, timing, payment method).
- **After-call webhook**: the message the telephony system sends to us after a phone call is processed, carrying the caller's phone and the transcript.
- **Webhook**: a message another system sends to our address when something happens there.
- **Transcript**: the text of a phone call, made by the telephony system.
- **Call summary**: a short note plus qualification fields written onto the lead from one call's redacted transcript.
- **Personal data removal (redaction)**: replacing names, phone numbers and similar data with placeholders before text leaves our system.
- **Test case**: one given / when / then scenario that defines good behaviour. There are 10; the eval runner runs them.
- **Eval runner**: the script that runs the 10 test cases against the agent and reports pass/fail and cost. Judged by code in core; an LLM judge for answer quality comes in polish.
- **Baseline**: how the client's process performs before the deployment, to compare the pilot against.

## Build process

- **Core**: the part built first (2-4 hours), enough to apply with.
- **Polish**: everything after applying.
- **Delivery documents**: the client-facing documents in `delivery/`.
- **Planner / implementer / critic**: the three session roles in `docs/WORKFLOW.md`. One AI, separate fresh sessions.
- **Ticket**: one numbered step in `docs/PLAN.md`, with its check.
