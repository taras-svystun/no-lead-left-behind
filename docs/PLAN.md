# Plan: no-lead-left-behind

## Purpose

Show how Taras runs one AI-agent deployment end to end: delivery documents a client and a founder can read, plus the smallest working system that solves the client's main pains (slow answers, lost leads, empty CRM). Why and for whom: `docs/BRIEF.md`.

## Two phases

- **Core** (5-6 hours, 8 at most): enough to put the link in the CV and apply. It must be honest and finished, not half of everything.
- **Polish** (after applying, while the application is under review): more delivery documents and depth.

## Proposed scope

This is a proposal for the grill, not a decision. Times are estimates.

### Core

| # | Piece | Why it is in the core | Est. |
|---|---|---|---|
| 1 | `delivery/discovery.md`, half a page: roles, the real process, data sources, gaps | Shows discovery thinking; the spec rests on it | 0:30 |
| 2 | `delivery/spec.md`, one page: scenarios, CRM field mapping, integrations, where a person steps in | The take-home task, rehearsed | 0:45 |
| 3 | `delivery/test-cases.md`: 10 given / when / then cases | The contract; the take-home task | 0:45 |
| 4 | Knowledge files: fictional price list and policies | The agent must answer from real data, not invent | 0:20 |
| 5 | Agent on Claude with 3 tools (price lookup, create lead, hand off), CRM with the Bitrix24 lead contract, Telegram adapter run locally | The walking skeleton: Telegram -> agent -> lead | 1:30 |
| 6 | Call webhook: sample payload -> remove personal data -> note on the lead | "Check a sample webhook" and "anonymise before it leaves" | 0:45 |
| 7 | Eval runner: the 10 cases, pass/fail, cost per conversation; one case doubles as the end-to-end test | Proves "good" with numbers | 1:00 |
| 8 | README as a 3-minute case study + Telegram GIF with frame notes + 5 lines on "what breaks at 10x" | What the founder actually opens | 0:45 |
| | **Total** | | **~6:20** |

### Polish (after applying, most valuable first)

1. One tuning loop: simulated manager feedback -> change note -> one rule changed -> eval again, before/after numbers.
2. Scope agreement + the example change note (reused from 1).
3. Go-live checklist: acceptance criteria, 30-minute manager training, rollout in waves.
4. Delivery playbook: week by week across 5-10 weeks, which document when.
5. Weekly client status.
6. Pilot report against a baseline (simulated, labelled).
7. Risk register; ADRs not already written in the grill.
8. "Notes for product" in the README.
9. Real Bitrix24 instead of the mock, if the core used a mock.
10. LLM judge for answer quality, if the core judged by code only.

### Cut entirely

- Live, always-online Telegram bot (a GIF replaces it).
- Separate planner and critic agents inside the product (they are build roles, see `docs/WORKFLOW.md`).

## Open questions for the grill

Decisions that shape the core. Each has a recommended answer to accept or change.

1. **CRM: real Bitrix24 or a mock with its contract?** Recommended: a mock in core (a JSON file shaped like Bitrix24 `crm.lead.add`), real Bitrix24 in polish. Saves sign-up and API surprises; the contract stays the same.
2. **Telegram in core, or a terminal chat?** Recommended: Telegram, run locally with long polling (the script asks Telegram for new messages, so no public URL is needed). The GIF from real Telegram is the most convincing frame for the founder.
3. **Where does the call transcript come from?** Ringostat-style payloads carry call data and a recording link, not text. Recommended: the sample payload includes a transcript field, labelled "simulated: speech-to-text assumed done".
4. **How is personal data removed?** Recommended: rules (patterns) for phone numbers, emails and card numbers, plus the buyer's name taken from the payload itself. Limit written down: unusual forms ("my number is zero nine seven...") slip through.
5. **How do the evals judge?** Recommended: by code in core (which tool was called, which fields the lead got, whether handoff happened). An LLM judge only in polish. Code checks cost nothing and never disagree with themselves.
6. **Which Claude model, within 3 USD?** Recommended: the cheapest current model that passes the 10 cases; check prices before the first call.
7. **Language of the delivery documents?** Recommended: README in English for the founder; client documents in Ukrainian, as in real life. Alternative: everything in English, so the founder reads it all.
8. **The client's details:** size, number of managers, projects, price range, what the CRM holds today. Recommended: the planner proposes a realistic fictional set, Taras corrects.

## Steps

(Tickets, written in stage 2 of `docs/WORKFLOW.md`.)
