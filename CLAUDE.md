# no-lead-left-behind

A public showcase of one AI-agent deployment for a fictional client, run end to end: delivery documents plus the smallest working system (Telegram -> Claude agent -> CRM lead, and an after-call webhook with personal data removed).

- `docs/BRIEF.md`: why the project exists, who reads it, what Taras cares about, hard constraints. Read it at the start of every session.
- `docs/WORKFLOW.md`: the build stages and which session does what. Read it to know your role and which files to read and write.
- `docs/PLAN.md`: tickets (T), polish items (P), decisions (D). Read it when starting a ticket.
- `delivery/`: the client-facing documents (spec, test cases, ...). The spec and test cases are also the build spec.
- `GLOSSARY.md`: the project's words. Use them in code, docs and commits. Matt Pocock skills that ask for `CONTEXT.md` use this file.
- `docs/journal.md`: what each finished step did and why, and the critic's findings.
- `docs/adr/`: decisions that are hard to undo. Read before changing the CRM contract, the personal data removal, or the eval judge.
- `docs/agents/issue-tracker.md`: where Matt Pocock skills find the spec and tickets.

## Rules of this project

- Write tersely in every file: one sentence per fact, the deciding reason only. Journal: one line per decision ("Used SQLite, not Bitrix24: no server, stdlib").
- The 10 test cases in `delivery/test-cases.md` are the contract. The eval runner runs the same 10 cases.
- Every component earns its place (see the brief). Core first; anything not in the core waits for polish.
- Boring, readable Python. Taras must be able to explain every line.
- Anything simulated is labelled "simulated".
- Public repo: no real personal data, no secrets, no real company names, no mention of the employer Taras applies to. Secrets live in `.env`, never committed.
- Tests come with the first code: unit tests, plus at least one end-to-end test.
- Anthropic API budget is about 3 USD in total: check the cost before any run that calls the API in a loop.

## Finishing a step

- The journal entry says how long the step took against its estimate in `docs/PLAN.md`.
- Mark a done ticket in `docs/PLAN.md` with ✅ before its name.
- A ticket that needs Taras's approval gets ⏳ before its name and ends with a review card in chat: up to 5 decisions to confirm, one line each with a link; name a file to read in full only when it must be, and why. A session whose ticket is blocked by a ⏳ ticket shows that card and stops.
- Stop after each step for Taras's review before starting the next.
- End each session with what comes next (stage or ticket) and the exact command or prompt from `docs/WORKFLOW.md` to start it.
