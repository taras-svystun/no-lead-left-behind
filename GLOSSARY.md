# Glossary: no-lead-left-behind

A public showcase of one AI-agent deployment for a fictional residential developer in Kyiv.

- **Client A**: the fictional client, a residential developer in Kyiv. Never a real company.
- **Buyer**: a person who writes in Telegram or calls about buying a flat.
- **Manager**: the client's human sales person, who takes over from the agent.
- **Lead**: a record in the CRM for one buyer, with their contact and what they want.
- **Simulated CRM**: the core's stand-in for the client's CRM, one SQLite table; Bitrix24 replaces it in polish.
- **Agent**: the one Claude-based assistant that answers buyers in Telegram.
- **Tool**: an action the agent can call: create lead, hand off. Price lookup joins in polish.
- **Handoff**: the agent stops and passes the buyer to a manager.
- **Qualification**: the questions that tell how serious a buyer is and what they need (budget, rooms, timing, payment method).
- **After-call webhook**: the message the telephony system sends to us after each phone call ends.
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
