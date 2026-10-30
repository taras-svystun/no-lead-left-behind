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
| 4 | Agent on Claude, price list in the system prompt, 2 tools (save lead, hand off), `/manager` command, share-phone button, leads in SQLite, Telegram via long polling | Walking skeleton: Telegram -> agent -> lead | 1:00 |
| 5 | After-call webhook: simulated Ringostat-style payload -> skip repeats by call ID -> find lead by phone (E.164) -> remove personal data -> one Claude call -> call summary and qualification fields on the lead, unit-tested | The take-home's "check a sample webhook"; second half of the story | 0:50 |
| 6 | Eval runner: 10 cases judged by code, pass/fail, cost per conversation; one case is the end-to-end test | Proves "good" with numbers | 0:40 |
| 7 | README case study + "how I'd run this deployment", week by week (6-8 lines) + Telegram GIF with frame notes + 5 lines "what breaks at 10x" | What the founder opens; the role is delivery-first | 0:45 |
| | **Total** | | **~4:50** |

Decided: leads in a simulated CRM (SQLite), not Bitrix24 (Python stdlib, no server; Bitrix24 waits for polish). Price list in the system prompt, not a tool: about 12 rows fit, and the agent cannot skip a lookup and invent a price. Evals judged by code; no LLM judge in core. Each test case checks actions and data (tool calls, lead rows, exact prices), not wording: wording varies per run. No live bot: GIF.

## Polish (in order)

1. Tuning loop: simulated manager feedback -> change note -> one rule changed -> evals before/after.
2. Scope agreement (the change note from 1 is its example).
3. Go-live checklist: acceptance, 30-minute training, rollout in waves.
4. Delivery playbook: grows the README's week by week into which document when.
5. Weekly client status.
6. Pilot report against a baseline (simulated, labelled).
7. Risk register; remaining ADRs.
8. Local name detection in redaction (NER model or a small local LLM, next to the regex), measured on a test case with a name only in free text: closes the known redaction limit without sending data out.
9. Real Bitrix24 instead of SQLite.
10. Price lookup tool instead of the price list in the prompt, for prices too many or too fresh for a prompt.
11. LLM judge for wording and tone, which code cannot check, as extra test cases.
12. "Notes for product" in the README.
13. Local open-source chat model as an eval experiment: run the same 10 cases, compare pass rate and cost with Haiku. Not a replacement unless it passes.

## Grill decisions (2026-10-30)

1. Telegram via long polling: the bot runs only for the GIF and evals, so no public URL.
2. Model: Haiku 5.5 with a flat, step-by-step prompt (0.10/0.50 USD per M tokens, ~0.04 USD per eval run); Sonnet 5.5 (2/10 USD, ~0.74 USD per run) only if Haiku fails cases after one prompt fix. Source: platform.claude.com/docs/en/about-claude/pricing, seen 2026-10-30.
3. Every file in English; the bot replies in the buyer's language.
4. Client A (all numbers simulated): 2 residential complexes in Kyiv, 6 managers, ~400 inbound conversations a month, ~40% of CRM leads miss budget or rooms, median first reply 2 hours. Price list ~12 rows (flat types per complex, price per m2; payment: 100%, 12-month instalments, partner-bank mortgage). Policies: booking, viewings, what the agent never promises (discounts, completion dates).
5. One lead per buyer: the agent asks for a phone number during qualification; the after-call webhook finds the lead by phone, else creates a new lead. Ringostat sends no CRM lead id (help.ringostat.com webhook docs, seen 2026-10-30).
6. Redaction covers the call transcript only: code, not Claude: regex for phones and emails, plus the names we already know (the buyer's from the lead found by phone, the manager's from the payload's `employee_fio`; Ringostat sends no caller name). Sending text to Claude to clean it would defeat the purpose. Telegram chats go to Claude as written; the spec says so. Names only in free text slip through: a known limit with its own test case. Redacting chats with placeholders is polish.
7. The agent says it is an AI in its first message and whenever asked; it never passes itself off as a human.
8. Handoff triggers: buyer asks for a person or sends `/manager` (any time, no Claude call); ready to view or book; question outside the price list and policies; complaint. The handoff tool sets lead status `handoff` with a reason; the buyer is told a manager writes within 15 minutes; manager notification is simulated (a log line). After handoff the agent only repeats that a manager is on it.
9. The after-call webhook simulates Ringostat's "call processed by AI" event: the after-call event has phone and recording link but no transcript. One Claude call on the redacted transcript writes the summary and the qualification fields, which Ringostat's own free-text summary does not fill.
10. Phone number: Telegram's share-phone button (`request_contact`) sends it in one tap as a field, not text, so our code saves it without passing it through Claude. Code, not the agent, shows the button twice at most: with the first reply and with the handoff message; it disappears once shared. No refusal detection: the agent never insists, and a lead without a phone stays keyed by Telegram ID (critic, stage 3). Duplicate leads that remain are a risk in the spec; managers merge them in the real CRM.
11. No n8n: one webhook and one CRM fit in a few tested Python lines; one line in the README says why.
12. No speech-to-text of our own: Ringostat already transcribes calls, so ours would only duplicate a vendor feature.
13. The 10 test cases: (1) price question -> exact price; (2) partial qualification -> asks the rest, phone included -> right lead fields; (3) wants a viewing -> handoff "viewing"; (4) `/manager` -> handoff, no Claude call; (5) question outside price list and policies -> no invention, handoff "unknown"; (6) asks for a discount -> none promised; (7) "are you human?" -> says it is an AI; (8) writes in English -> answers in English; (9) call from a known phone -> summary and fields on that lead; (10) redaction -> no phone, email or payload name in the request to Claude. Unit tests cover the rest (unknown phone -> new lead; after handoff the agent only repeats that a manager is on it).
14. One Sonnet comparison run at the end of core (~0.74 USD): Haiku vs Sonnet pass rate and cost per conversation in the README.

## Steps

Code lives in `app/`, tests in `tests/`, evals in `evals/`, knowledge files in `knowledge/`. Every chat creates its lead in code on the first message; the agent's `save_lead` only fills fields, so no chat can be lost to a skipped tool call.

1. **Spec and test cases** (0:40 + 0:40). `delivery/spec.md`, `delivery/test-cases.md`. Check: Taras approves; the critic (stage 3) has run. Blocked by: nothing. Status: written, awaiting review.
2. **Knowledge files** (0:15). `knowledge/price_list.md` (~12 rows, both complexes) and `knowledge/policies.md`, both labelled simulated. Check: every price used in the test cases is in the list (North, 2 rooms, 62 m2, 1,450 USD/m2, 89,900 USD); completion dates and discounts are absent. Blocked by: 1.
3. **Project skeleton and simulated CRM** (0:15). `.venv`, `requirements.txt`, `.env.example`; `app/crm.py`: one SQLite table with the spec's lead fields; create by Telegram ID, update fields, find by phone, set handoff; every phone is normalised to E.164 (+380…) on write and on lookup, because Telegram sends `380…` and Ringostat `+380…`. Check: unit tests pass for each function and for the phone match across formats. Blocked by: 1.
4. **Agent** (0:30). `app/agent.py`: `reply(telegram_id, text) -> str`, no Telegram inside. System prompt built from the knowledge files, flat and step by step for Haiku 5.5; tools `save_lead` and `hand_off`; in code, not the model: the fixed AI disclosure, `/manager`, the shared phone, when the phone button shows, the after-handoff reminder. Check: unit tests with a fake AI client for each in-code rule; one live chat for case 1 costs under 0.01 USD. Blocked by: 2, 3.
5. **Telegram bot** (0:15). `app/bot.py`: long polling, "Share phone" button (`request_contact`), the command menu with `/manager` described in Ukrainian ("Зв'язатися з менеджером", via `setMyCommands`), calls `agent.reply`. Check: a chat from the test account creates a lead in SQLite; GIF recorded here. Blocked by: 4.
6. **After-call webhook** (0:50). `app/redact.py` (phones, emails, the lead's and the manager's names -> `[PHONE]`, `[EMAIL]`, `[NAME]`); `app/calls.py`: simulated payload modelled on Ringostat's "call processed by AI" event (fixture and a local `.vtt` transcript in `tests/fixtures/`), skip a call ID already processed, find or create the lead by phone, read the `.vtt` and strip time codes, redact, one AI call returns the summary and fields as JSON, update the lead; a stdlib HTTP endpoint so `curl` can post the fixture. Check: unit tests for redaction (Ukrainian phone formats, email, known name), `.vtt` parsing, lead match, unknown phone -> new lead, repeated call ID -> no second AI call; `curl` of the fixture updates a lead. Blocked by: 3. Payload fields follow the spec's "Call webhook fields" table and `docs/research/ringostat-webhook-name-fields.md`; no caller name.
7. **Eval runner** (0:40). `evals/run.py` runs the 10 cases on a fresh SQLite file, prints pass/fail per case, cost per conversation and the total. Estimate the cost before the first run. Check: 10/10 pass on Haiku (switch the agent to Sonnet only if it still fails after one prompt fix); one Sonnet run for the comparison; results saved in `evals/results.md`. Blocked by: 4, 6.
8. **README case study** (0:45). Problem, before/after, the flow, "how I'd run this deployment" week by week (6-8 lines), the GIF with frame notes, Haiku vs Sonnet table, "what breaks at 10x" (5 lines), the n8n line, limits, one line on how it was built (fresh session per role, a critic; link to `docs/WORKFLOW.md`). Check: Taras reads it in about 3 minutes and can retell it. Blocked by: 5, 7.
