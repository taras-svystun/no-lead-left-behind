# Glossary: no-lead-left-behind

A public showcase of one AI-agent deployment for a fictional residential developer in Kyiv.

The whole flow as one story: `docs/STORY.md`.

## Terms

- **Client A**: the fictional client, a residential developer in Kyiv. Never a real company.
- **Buyer**: a person who writes in Telegram or calls about buying a flat.
- **Manager**: the client's human sales person, who takes over from the agent.
- **Lead**: a record in the CRM for one buyer, with their contact and what they want. One buyer, one lead: a call from the same phone lands on the same lead.
- **CRM**: the client's system that holds all leads, the box of cards.
- **Simulated CRM**: the core's stand-in for the client's CRM, one SQLite table; Bitrix24 replaces it in polish.
- **Agent**: the one Claude-based assistant that answers buyers in Telegram. The one word for it everywhere, client documents included (D20).
- **Telegram ID**: the fixed number Telegram gives each account; how the agent recognises a buyer in chat.
- **Allowed list**: the Telegram IDs the demo bot answers (`TELEGRAM_ALLOWED_IDS` in `.env`); anyone else would spend the API budget.
- **Call ID**: the telephony system's id for one call; a second webhook with the same id is a repeat and is skipped.
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

- **Core**: the part built first (2-4 hours), enough to apply with: tickets T1-T8.
- **Polish**: everything after applying: items P1-P14 in `docs/PLAN.md`.
- **Delivery documents**: the client-facing documents in `delivery/`.
- **Planner / implementer / critic**: the three session roles in `docs/WORKFLOW.md`. One AI, separate fresh sessions.
- **Ticket**: one build item in `docs/PLAN.md`, `## Tickets`, named T1, T2, …, with its why, check and blockers.
- **Polish item**: a planned piece after applying, named P1, P2, …; it becomes a ticket when its turn comes.
- **Decision**: a settled choice in `docs/PLAN.md`, `## Decisions`, named D1, D2, ….
- **Step**: any finished piece of work, a ticket or a single request; not a numbered item.
