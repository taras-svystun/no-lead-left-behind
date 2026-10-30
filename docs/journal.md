# Journal

Newest at the bottom.

## 2026-10-29: Project setup

Created CLAUDE.md, GLOSSARY.md, docs/PLAN.md, README.md and .gitignore. Project type: product. Recorded the two build roles (planner/implementer and critic) and the public-repo rules. Next: grilling round, then the plan.

## 2026-10-30: Prepare for the grill

Cut the target from 1-2 days to a 5-6 hour core plus polish after applying. Wrote `docs/BRIEF.md` (stable needs), `docs/WORKFLOW.md` (session roles and the critic prompt), the proposed core / polish scope and 8 open questions in `docs/PLAN.md`, and `docs/agents/issue-tracker.md` so the Matt Pocock skills find the spec and tickets without their setup step. Cut: live Telegram bot (GIF instead). Next: the grill session.

## 2026-10-30: Cut the core to ~4 hours

- Core target 2-4 h (6 max); discovery merged into the spec; call webhook moved to polish 1.
- Leads in SQLite, not Bitrix24: stdlib, no server; Bitrix24 is polish 9.
- Critic prompt: added Bloat, Drift, a closing "Keep" sentence, and an ask-before-apply round.
- Terse-writing rule added to CLAUDE.md.

## 2026-10-30: Critic on the setup (stage 0)

No estimate in the plan. Findings and Taras's calls:

- Applied: call webhook back in core (row 5, 0:30): CLAUDE.md, README and brief all promised it; it is a third of the take-home.
- Applied: README gets "how I'd run this deployment" week by week (+0:15): the role is delivery-first. Core now ~4:45.
- Applied: glossary says "no LLM judge in core"; SQLite is named the simulated CRM.
- Applied: critic prompt asks only for game-changing findings, 2-4 sentences each, none allowed: Taras found the small ones padded.
- Declined: a budget line for setup and the GIF: estimates are rough anyway; a Telegram test account exists.
- Applied: price list in the system prompt, not a price tool (-0:15; core ~4:30); price lookup tool is polish 9.
- Applied: test cases check actions and data, not wording; the LLM judge for wording stays as polish 10.
- Taras's edit: critic prompt no longer weighs the time budget or says that zero findings is fine.
- Critic prompt: "nothing game-changing" allowed again; Risk line cut (budget no longer weighed); Bloat merged into Simplify.
- CLAUDE.md: every session ends with the next stage or ticket and its exact prompt from WORKFLOW.md.

## 2026-10-30: Grill (stage 1)

No estimate in the plan for the grill. Decisions are in `docs/PLAN.md`, "Grill decisions"; the key ones:

- One lead per buyer, matched by phone: Ringostat sends no CRM lead id (help.ringostat.com, 2026-10-30).
- The after-call webhook simulates Ringostat's "call processed by AI" event: only that event carries the transcript.
- Redaction covers the call transcript only; Telegram chats reach Claude as written, said openly in the spec.
- Haiku 5.5 first (~0.04 USD per eval run), Sonnet 5.5 if Haiku fails; one Sonnet comparison run for the README (platform.claude.com pricing, 2026-10-30).
- AI disclosure always; `/manager` at any time; share-phone button offered twice at most, then refusal respected.
- Rejected: n8n (one webhook does not need a platform); our own speech-to-text (Ringostat already transcribes).
- Glossary opens with the whole story in 8 steps: Taras asked for one picture of the terms before building.
- 10 test cases: 8 for the agent, 2 for the after-call webhook (lead match, redaction).
- Story moved from the glossary to `docs/STORY.md`: Taras needed it once; every session reads the glossary.
- Redaction names: those on the lead found by phone, not only the payload's; Ringostat's payload name field is unconfirmed.
- Polish 8: local name detection for redaction; polish 13: local chat model, only as an eval comparison. Urgent: confirm Ringostat's name field.

## 2026-10-30: Spec, test cases and tickets (stage 2)

Estimate 1:20 for spec and test cases; took about 0:30 of writing after the grill.

- Every chat creates its lead in code on the first message, not by the agent: a skipped tool call cannot lose a lead.
- Fixed price row for the cases: North, 2 rooms, 62 m2, 1,450 USD/m2, 89,900 USD.
- Phone numbers in examples use +380000000001: no real number in a public repo.
- Case 7 checks wording by pattern (AI|ШІ|штучн|бот): the disclosure matters enough to break the "actions, not wording" rule once.
- Tickets 1-8 in `docs/PLAN.md`, total ~4:45; ticket 6 waits on the Ringostat name check.
- Ringostat call webhooks (after call, processed by AI) carry no caller name, only phone and employee name; client names come only in messenger events (help.ringostat.com parameter sheets EN/UK/RU, 2026-10-30; `docs/research/ringostat-webhook-name-fields.md`). So the simulated payload has no caller name and redaction takes names from the lead found by phone. No estimate in the plan; took about 5 minutes.
- Redaction also removes the manager's name (`employee_fio`): it is personal data and appears in the transcript. Test case 10 checks it.
- The critic is told its stage in one line: the prompt fits both reviews, and guessing the scope wastes its attention.

## 2026-10-30: Critic on the plan (stage 3)

No estimate in the plan for the critic; took about 0:15. Applied, all accepted by Taras:

- Webhook is checked, not only processed (+0:20): skip repeated call IDs (Ringostat resends), phones normalised to E.164 (Telegram sends `380…`), transcript read from the `.vtt` link as the real event sends it, payload-to-lead field table in the spec. It is the take-home's "check a sample webhook".
- Phone button shown by code twice at most (first reply, handoff), no refusal detection (-0:15): the model-side refusal rule had no test case.
- README gets one line on how it was built, with a link to `docs/WORKFLOW.md`: the brief lists context engineering, and the founder sees only the README.
- Core now ~4:50.
- `/manager` keeps its name and gets a Ukrainian description in the command menu: a first-time buyer reads the description, not the name; `/call_human` would promise a phone call (Taras's call).
- WORKFLOW.md names two loops: planning (stages 0-3, once per scope) and build (stages 4-5, all the time): Taras wants to know at a glance which stage comes next.
- Code tickets start with `/mattpocock-skills:implement`: it drives `tdd`, which confirms what it tests with Taras first, and forbids redesign mid-build; ticket 2 has no code, so plain text.
- Build critic runs after tickets 4, 7 and 8, not every 2-3: those change the project's shape.
- The build critic also reads the journal since its last run: drift hides in small decisions, and they are written there.

## 2026-10-30: Knowledge files (ticket 2)

Estimate 0:15; took about 0:10.

- Two complexes, North and River, 4 flat types each, plus 3 payment methods: 11 rows. One 2-room row per complex, so "двокімнатна в North" has one answer.
- No year, quarter or percentage anywhere: cases 5 and 6 fail on them, and the agent repeats what its prompt holds. So instalments are "12 equal payments" and the mortgage terms are the bank's.
- Same total for every payment method: a cheaper price for full payment would be a discount the agent could quote.
- For ticket 7: case 6's "no total below 89,900" also fails a fair answer that offers a cheaper flat (River, 2 rooms, 69,600). Check only the North 2-room price, or accept totals that are other rows of the list.

## 2026-10-30: Done steps get a ✅

A done step in `docs/PLAN.md` gets ✅ before its name: Taras sees progress at a glance. The rule is one line in CLAUDE.md, because implementer sessions read CLAUDE.md, not the journal.

## 2026-10-30: Unique IDs in the plan

No estimate in the plan; took about 0:15.

- Tickets, polish items and decisions are T1-T8, P1-P13, D1-D19: four lists all numbered from 1 let "ticket 3" mean two things to Taras and to agents.
- `## Steps` became `## Tickets`; "step" now means any finished piece of work (GLOSSARY).
- The Core table went: it repeated the tickets under other numbers; each ticket now carries its "Why", the total moved to Tickets, the "Decided" paragraph became D15-D19.
- Order is Tickets -> Polish -> Decisions: what is worked on now comes first, reference last.
- T1 marked ✅: Taras approved it and the critic ran; "Status:" fields dropped, the ✅ is the one signal.
- D6 no longer says the free-text name limit has "its own test case": test-cases.md lists it as a known limit, not a case.
- References updated in CLAUDE.md, GLOSSARY.md, WORKFLOW.md and docs/agents/issue-tracker.md; journal entries before this one keep the old numbers.

## 2026-10-30: Review cards and ⏳

Taras missed that T1 awaited his approval: the request was a status line in the plan, and approving meant reading a client document. Now a ticket that needs him gets ⏳ and a review card in chat (up to 5 decisions, one line each); a session blocked by a ⏳ ticket shows the card and stops. Rejected: a summary atop `spec.md`: it would mix the client's document with notes for Taras.
- P14 added, chat redaction: D6 promised it in polish, but no P item held it.
- Case 6 check changed from "no total below 89,900" to "every USD total is a price list row": the old check failed a fair answer that offers River's cheaper 2-room flat (found in T2).

## 2026-10-30: Day and night handoff message; one word "agent"

- T1 review card: Taras accepted 4 of 5 decisions. The 15-minute promise broke at night (discovery: chats after 19:00 wait until morning), so code picks the handoff message by Kyiv hour: 15 minutes from 9:00 to 19:00, else "by 12:00" (D8; T4 +0:10, core ~5:00). Kept in core, not polish: it is one `if`, and the model need not know the time.
- "Agent" stays the one word, client documents included (D20): "chatbot" for clients and "agent" elsewhere would be two names for one thing.
- Polish reordered: chat redaction moved next to name detection (P9); Bitrix24, price tool, LLM judge, product notes, local model are now P10-P14. Entries above keep the old numbers.

## 2026-10-30: T3 simulated CRM

Estimate 0:15; took about 0:30 (a guess from session length), the extra being the code review and its fixes.

- `app/crm.py`: one `leads` table with the spec's fields; functions take the connection, so tests use `:memory:` and the bot a file.
- Field names are checked in Python (they go into the SQL), values by the table's CHECK: one rule, no second list of allowed values.
- `create_lead` takes no phone: T6 creates a call lead, then `update_lead(phone=...)`; one write path normalises the phone.
- Review: a foreign caller crashed `find_by_phone`, so any number is now kept as E.164 and only text with no digits raises; T6 must catch that for a withheld number.
- Review: `update_lead` with no fields raised an SQL error; now a clear `ValueError`.
- For T6: the call ID store is not in T3; T6 adds its own `processed_calls` table, not a column on leads.
- For T5/T7: the end-to-end test CLAUDE.md asks for comes with the first full flow; T3 has unit tests only.
- Not fixed: updating a lead id that does not exist does nothing silently; ids only come from `create_lead`.

## 2026-10-30: T4 agent

Estimate 0:40; took about 1:00 (a guess from session length), the extra being the two-axis review and its fixes.

- `reply` returns `Reply(text, ask_phone)`, not `str`: the bot must know when to show "Share phone" (D10), and code decides it from the CRM (first reply, or the reply that hands off; never once a phone is on the lead).
- Disclosure and fixed texts follow the buyer's first words: any Cyrillic letter -> Ukrainian, else English; a Ukrainian disclosure would fail case 8 (Taras's call).
- A shared phone is saved by code; the AI gets only a note that it was shared, so it goes on asking (Taras's call).
- When the model calls `hand_off`, the buyer gets only the fixed day/night text and no AI call follows: nothing invented, the chat never returns to the model (Taras's call).
- Manual tool loop, not the SDK's tool runner: the handoff must stop the loop, and the runner is beta.
- No `strict` on the tools: save_lead's fields are all optional; the CRM's CHECK rejects a bad value and the AI gets an error result.
- Safe default: an empty reply, a refusal or 5 AI calls in one turn -> handoff `unknown`; a manager beats a guess or an endless bill.
- Chats live in memory: a restart forgets the chat, the lead stays.
- `/start` and `/manager@Bot` handled in code, no AI call (review).
- Review: text written next to a save_lead call was lost, and an empty follow-up handed off by mistake; now every text of the turn reaches the buyer.
- Review, prompt: completion dates named under "unknown" (case 5); "are you human?" is not a manager request (case 7); the agent asks once for the phone (spec).
- Not fixed: the reason and payment values sit in three places (CRM CHECK, tool schema, prompt), one per reader; `_save_lead` catches `sqlite3.IntegrityError`, so P10 must map Bitrix24 errors there.
- Live case 1: 0.00055 USD per chat; Haiku 5.5 accepts `effort: low`. The first run handed off instead of quoting the price, then 26 runs in a row passed; the cause is unknown, so no fix. The code-forced handoff now logs its own warning, so T7 shows which path fires.
- For T5: keep the "Share phone" keyboard on screen until the phone is shared, since the agent asks late; Telegram's `language_code` could pick the disclosure language after `/start`, which is Ukrainian today.

## 2026-10-30: One list of critic runs

- The critic ran after T4, T7 and T8 per WORKFLOW, but the implementer took "what next" from PLAN, which had no such list, and sent Taras to T5. Now each ticket that gets a critic ends with "Then: critic" in PLAN; WORKFLOW points there and holds no ticket numbers.
- Critic after T5, not T4 (Taras's call): T4 alone is a module with no front door; after T5 the walking skeleton is whole, and the critic still reads T4's journal lines.
- Stage 5 no longer runs code-review again: `implement` already reviews every ticket against the whole repo.
- T5 gets a whitelist, `TELEGRAM_ALLOWED_IDS` in `.env`: the bot is public, anyone else would spend the API budget. IDs stay out of the repo.

## 2026-10-30: T5 Telegram bot

Estimate 0:15; took about 0:50 (a guess from session length), the extra being the review fixes and a quoted token in `.env`.

- Telegram over stdlib `urllib`, not a library: three API methods, no dependency, every line explainable.
- Tests at one seam, `handle_update`, with fake Claude and fake Telegram and the real agent and CRM: the end-to-end test CLAUDE.md asks for. The HTTP part is checked live (Taras's call).
- The "Share phone" keyboard stays on screen until a phone reaches the lead, by button or typed: the agent returns `phone_saved`, the bot removes the keyboard.
- Button label in the buyer's language; the agent's `language` is public for it. The `/manager` menu is Ukrainian only: one menu for every buyer.
- Ignored without a reply: IDs not on the allowed list, group chats, stickers and other non-text, someone else's contact.
- Review: a contact sent before any text crashed; now it creates the lead and gets the AI disclosure. A failed `getUpdates` stopped the bot; now it logs and retries in 5 seconds.
- `.env` values take no quotes: a quoted token made Telegram answer 404; Taras removed the quotes, so `load_env` stays plain.
- Live: `getMe` and `setMyCommands` work; queued chats from both allowed IDs created leads 1 and 2 in `crm.sqlite` with no send errors.
- Not done: the GIF needs Taras's screen; due before T8.
- Not fixed: the agent's rule 7 says "Share phone" in English while the Ukrainian button reads "Поділитися номером"; the model translates.
