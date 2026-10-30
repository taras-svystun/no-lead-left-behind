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
- Pending Taras's answer: price list in the system prompt instead of a price tool; test cases written as checks on actions and data, not wording.
