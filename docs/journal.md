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
