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
