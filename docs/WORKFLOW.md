# Workflow: how we build this

We build in separate working sessions. Each session has one role and starts with an empty context. Files carry everything from one session to the next, never chat history.

**Why a fresh context for each role:** a reviewer who watched the plan being made inherits its reasoning and its blind spots. A reviewer who sees only the goals and the result judges the plan the way the founder will.

**Why files and not chat:** a file can be read, corrected and handed to the next session in full. A chat gets summarised and loses detail.

## The stages

The order follows Matt Pocock's skills (grill-with-docs -> to-spec -> to-tickets -> implement -> code-review). We merge spec and tickets into one stage, because the client spec *is* the build spec.

| # | Stage | Session | Reads | Writes |
|---|---|---|---|---|
| 1 | **Grill** | Planner | `CLAUDE.md`, `docs/BRIEF.md`, `docs/PLAN.md`, `GLOSSARY.md` | decisions and answers into `docs/PLAN.md`; terms into `GLOSSARY.md`; hard decisions into `docs/adr/` |
| 2 | **Spec + tickets** | Planner (same session) | the same, plus the grill results | `delivery/spec.md`, `delivery/test-cases.md`; tickets (numbered steps with a check each) in `docs/PLAN.md` |
| 3 | **Critic on the plan** | Critic (new session) | `docs/BRIEF.md`, `docs/PLAN.md`, `delivery/` | findings in `docs/journal.md`; Taras decides; the planner or Taras updates `docs/PLAN.md` |
| 4 | **Implement** | Implementer (new session per one or a few tickets) | `CLAUDE.md`, the ticket in `docs/PLAN.md`, `delivery/spec.md`, `delivery/test-cases.md` | code, tests, journal entry, commit |
| 5 | **Critic on the build** | Critic (new session, every 2-3 tickets) | `docs/BRIEF.md`, `docs/PLAN.md`, the diff since the last critic run | findings in `docs/journal.md`; cuts and fixes go back to stage 4 |

Taras reviews after each stage before the next one starts.

## How to start each stage

1. **Grill.** New session: `/mattpocock-skills:grill-with-docs`. If that command isn't found, run `/mattpocock-skills:grilling`, then `/mattpocock-skills:domain-modeling`. Say: "Grill me on docs/PLAN.md, open questions first."
2. **Spec + tickets.** Same session, after the grill: "Write delivery/spec.md and delivery/test-cases.md, then the core tickets in docs/PLAN.md, as WORKFLOW.md stage 2 says."
3. **Critic on the plan.** New session, paste the critic prompt below.
4. **Implement.** New session: "Implement ticket N from docs/PLAN.md." Optionally `/mattpocock-skills:tdd`.
5. **Critic on the build.** New session, paste the critic prompt below. Also run `/mattpocock-skills:code-review` against the last critic commit.

## The critic prompt

> You are the critic for this project. You did not write the plan or the code, and you owe them nothing.
> Read `docs/BRIEF.md` (the goals and constraints), then `docs/PLAN.md` and `delivery/` (and, for a build review, `git diff <last-critic-commit>..HEAD`).
> Judge one thing: does this give Taras the most value for the least work, against the brief?
> Report, most important first, one line each:
> 1. **Cut**: what can go, or move from core to polish, and the time it saves.
> 2. **Missing**: what the brief needs and the plan lacks.
> 3. **Simplify**: what can be done with fewer parts.
> 4. **Risk**: what could make the core miss its time budget.
> Change nothing except one new entry in `docs/journal.md` with your findings. Then stop: Taras decides what to apply.
