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
| 4 | Agent on Claude, price list in the system prompt, 2 tools (save lead, hand off), `/manager` command, share-phone button, leads in SQLite, Telegram via long polling | Walking skeleton: Telegram -> agent -> lead | 1:15 |
| 5 | After-call webhook: simulated Ringostat-style payload with transcript -> find lead by phone -> remove personal data -> one Claude call -> call summary and qualification fields on the lead, unit-tested | The take-home's "check a sample webhook"; second half of the story | 0:30 |
| 6 | Eval runner: 10 cases judged by code, pass/fail, cost per conversation; one case is the end-to-end test | Proves "good" with numbers | 0:40 |
| 7 | README case study + "how I'd run this deployment", week by week (6-8 lines) + Telegram GIF with frame notes + 5 lines "what breaks at 10x" | What the founder opens; the role is delivery-first | 0:45 |
| | **Total** | | **~4:45** |

Decided: leads in a simulated CRM (SQLite), not Bitrix24 (Python stdlib, no server; Bitrix24 waits for polish). Price list in the system prompt, not a tool: about 12 rows fit, and the agent cannot skip a lookup and invent a price. Evals judged by code; no LLM judge in core. Each test case checks actions and data (tool calls, lead rows, exact prices), not wording: wording varies per run. No live bot: GIF.

## Polish (in order)

1. Tuning loop: simulated manager feedback -> change note -> one rule changed -> evals before/after.
2. Scope agreement (the change note from 1 is its example).
3. Go-live checklist: acceptance, 30-minute training, rollout in waves.
4. Delivery playbook: grows the README's week by week into which document when.
5. Weekly client status.
6. Pilot report against a baseline (simulated, labelled).
7. Risk register; remaining ADRs.
8. Real Bitrix24 instead of SQLite.
9. Price lookup tool instead of the price list in the prompt, for prices too many or too fresh for a prompt.
10. LLM judge for wording and tone, which code cannot check, as extra test cases.
11. "Notes for product" in the README.

## Grill decisions (2026-10-30)

1. Telegram via long polling: the bot runs only for the GIF and evals, so no public URL.
2. Model: Haiku 5.5 with a flat, step-by-step prompt (0.10/0.50 USD per M tokens, ~0.04 USD per eval run); Sonnet 5.5 (2/10 USD, ~0.74 USD per run) only if Haiku fails cases after one prompt fix. Source: platform.claude.com/docs/en/about-claude/pricing, seen 2026-10-30.
3. Every file in English; the bot replies in the buyer's language.
4. Client A (all numbers simulated): 2 residential complexes in Kyiv, 6 managers, ~400 inbound conversations a month, ~40% of CRM leads miss budget or rooms, median first reply 2 hours. Price list ~12 rows (flat types per complex, price per m2; payment: 100%, 12-month instalments, partner-bank mortgage). Policies: booking, viewings, what the agent never promises (discounts, completion dates).
5. One lead per buyer: the agent asks for a phone number during qualification; the after-call webhook finds the lead by phone, else creates a new lead. Ringostat sends no CRM lead id (help.ringostat.com webhook docs, seen 2026-10-30).
6. Redaction covers the call transcript only: code, not Claude: regex for phones and emails, plus the names we already know (from the lead found by phone, and from the payload if it carries one). Sending text to Claude to clean it would defeat the purpose. Telegram chats go to Claude as written; the spec says so. Names only in free text slip through: a known limit with its own test case. Redacting chats with placeholders is polish.
7. The agent says it is an AI in its first message and whenever asked; it never passes itself off as a human.
8. Handoff triggers: buyer asks for a person or sends `/manager` (any time, no Claude call); ready to view or book; question outside the price list and policies; complaint. The handoff tool sets lead status `handoff` with a reason; the buyer is told a manager writes within 15 minutes; manager notification is simulated (a log line). After handoff the agent only repeats that a manager is on it.
9. The after-call webhook simulates Ringostat's "call processed by AI" event: the after-call event has phone and recording link but no transcript. One Claude call on the redacted transcript writes the summary and the qualification fields, which Ringostat's own free-text summary does not fill.
10. Phone number: Telegram's share-phone button (`request_contact`) sends it in one tap as a field, not text, so our code saves it without passing it through Claude. The agent offers it during qualification and once more at handoff if the buyer ignored it; after an explicit refusal it never asks again and saves the lead by Telegram ID. Duplicate leads that remain are a risk in the spec; managers merge them in the real CRM.
11. No n8n: one webhook and one CRM fit in a few tested Python lines; one line in the README says why.
12. No speech-to-text of our own: Ringostat already transcribes calls, so ours would only duplicate a vendor feature.
13. The 10 test cases: (1) price question -> exact price; (2) partial qualification -> asks the rest, phone included -> right lead fields; (3) wants a viewing -> handoff "viewing"; (4) `/manager` -> handoff, no Claude call; (5) question outside price list and policies -> no invention, handoff "unknown"; (6) asks for a discount -> none promised; (7) "are you human?" -> says it is an AI; (8) writes in English -> answers in English; (9) call from a known phone -> summary and fields on that lead; (10) redaction -> no phone, email or payload name in the request to Claude. Unit tests cover the rest (unknown phone -> new lead; after handoff the agent only repeats that a manager is on it).
14. One Sonnet comparison run at the end of core (~0.74 USD): Haiku vs Sonnet pass rate and cost per conversation in the README.

## Steps

(Tickets, written in stage 2 of `docs/WORKFLOW.md`.)
