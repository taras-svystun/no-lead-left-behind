# Plan: no-lead-left-behind

## Purpose

Show how Taras runs one AI-agent deployment end to end, smallest version that solves slow answers, lost leads and an empty CRM. Why and for whom: `docs/BRIEF.md`.

## Phases

- **Core** (2-4 hours, 6 at most): small but finished; then apply.
- **Polish**: after applying, in the order below, as time allows.

## Core (proposal for the grill; times are estimates)

| # | Piece | Why | Est. |
|---|---|---|---|
| 1 | `delivery/spec.md`, one page, opening with 5 lines of discovery findings | The take-home task; discovery merged in, no separate file | 0:40 |
| 2 | `delivery/test-cases.md`: 10 given / when / then cases | The contract | 0:40 |
| 3 | Knowledge files: fictional price list and policies | Agent answers from data, not invention | 0:15 |
| 4 | Agent on Claude, 3 tools (price lookup, create lead, hand off), leads in SQLite, Telegram via long polling | Walking skeleton: Telegram -> agent -> lead | 1:15 |
| 5 | Call webhook: sample Ringostat-style payload -> remove personal data -> note on the lead, unit-tested | The take-home's "check a sample webhook"; second half of the story | 0:30 |
| 6 | Eval runner: 10 cases judged by code, pass/fail, cost per conversation; one case is the end-to-end test | Proves "good" with numbers | 0:40 |
| 7 | README case study + "how I'd run this deployment", week by week (6-8 lines) + Telegram GIF with frame notes + 5 lines "what breaks at 10x" | What the founder opens; the role is delivery-first | 0:45 |
| | **Total** | | **~4:45** |

Decided: leads in a simulated CRM (SQLite), not Bitrix24 (Python stdlib, no server; Bitrix24 waits for polish). Evals judged by code; no LLM judge in core. No live bot: GIF.

## Polish (in order)

1. Tuning loop: simulated manager feedback -> change note -> one rule changed -> evals before/after.
2. Scope agreement (the change note from 1 is its example).
3. Go-live checklist: acceptance, 30-minute training, rollout in waves.
4. Delivery playbook: grows the README's week by week into which document when.
5. Weekly client status.
6. Pilot report against a baseline (simulated, labelled).
7. Risk register; remaining ADRs.
8. Real Bitrix24 instead of SQLite.
9. LLM judge for answer quality, as extra test cases.
10. "Notes for product" in the README.

## Open questions for the grill

1. **Telegram: long polling or webhook?** Recommended: long polling (the script asks Telegram for new messages; no public URL).
2. **Claude model within 3 USD?** Recommended: the cheapest current model that passes the 10 cases; check prices first.
3. **Language of delivery documents?** Recommended: README in English; client documents in Ukrainian, as in real life.
4. **Client details** (size, managers, projects, prices, what the CRM holds today)? Recommended: planner proposes a fictional set, Taras corrects.
5. **Which 10 test cases?** Recommended: planner drafts from the spec's scenarios (price question, qualification, lead created, handoff, unknown answer, off-topic, ...), Taras edits.
6. **Call webhook: how to remove personal data, and who writes the summary?** Recommended: regex for phones and emails plus the names the payload itself carries; summary by one Claude call on the already-redacted transcript, which shows why removal comes first (cost under 0.01 USD).

## Steps

(Tickets, written in stage 2 of `docs/WORKFLOW.md`.)
