# no-lead-left-behind

A public showcase of one AI-agent deployment for a fictional client, run end to end: delivery documents plus the smallest working system (Telegram -> Claude agent -> CRM lead, and an after-call webhook with personal data removed).

- `docs/BRIEF.md`: why the project exists, who reads it, what Taras cares about, hard constraints. Read it at the start of every session.
- `docs/WORKFLOW.md`: the build stages and which session does what. Read it to know your role and which files to read and write.
- `docs/PLAN.md`: scope (core / polish), open questions, tickets. Read it when starting a step.
- `delivery/`: the client-facing documents (discovery, spec, test cases, ...). The spec and test cases are also the build spec.
- `GLOSSARY.md`: the project's words. Use them in code, docs and commits. Matt Pocock skills that ask for `CONTEXT.md` use this file.
- `docs/journal.md`: what each finished step did and why, and the critic's findings.
- `docs/adr/`: decisions that are hard to undo. Read before changing the CRM contract, the personal data removal, or the eval judge.
- `docs/agents/issue-tracker.md`: where Matt Pocock skills find the spec and tickets.

## Rules of this project

- The 10 test cases in `delivery/test-cases.md` are the contract. The eval runner runs the same 10 cases.
- Every component earns its place (see the brief). Core first; anything not in the core waits for polish.
- Boring, readable Python. Taras must be able to explain every line.
- Anything simulated is labelled "simulated".
- Public repo: no real personal data, no secrets, no real company names, no mention of the employer Taras applies to. Secrets live in `.env`, never committed.
- Tests come with the first code: unit tests, plus at least one end-to-end test.
- Anthropic API budget is about 3 USD in total: check the cost before any run that calls the API in a loop.

## Finishing a step

- The journal entry says how long the step took against its estimate in `docs/PLAN.md`.
- Stop after each step for Taras's review before starting the next.
