# no-lead-left-behind

A public showcase of one AI-agent deployment for a fictional client, run end to end: delivery documents plus the smallest working system (Telegram -> Claude agent -> CRM lead, and an after-call webhook with personal data removed).

- `GLOSSARY.md`: the project's words. Use them in code, docs and commits.
- `docs/PLAN.md`: the plan and what we agreed. Read it when starting a step.
- `docs/journal.md`: what each finished step did and why, and what the critic cut.
- `docs/adr/`: decisions that are hard to undo. Read before changing the CRM contract, the personal data removal, or the eval judge.

## Who reads it, where it runs

- Readers: a startup founder (opens the README for 3 minutes) and a non-technical client (reads the docs in `docs/`). Write each doc for its reader.
- Runs on Taras's Mac and free tiers only. Anthropic API budget: about 3 USD in total. Anything that costs money: stop and name the free alternative first.

## Rules of this project

- The 10 test cases in `docs/` are the contract. Spec and tests come before code; the eval runner runs the same 10 cases.
- Every component earns its place: one job, one sentence for a non-technical person, the alternative rejected, the price paid. No vector DB, runtime multi-agent, framework, dashboard or Kubernetes unless a test case needs it.
- 80/20: build the 20% that solves the client's main pains (slow answers, lost leads, empty CRM). Cut the rest gladly.
- Boring, readable Python. Taras must be able to explain every line.
- Honest numbers: anything simulated is labelled "simulated".
- Public repo: no real personal data, no secrets, no real company names, no mention of the employer Taras applies to. Secrets live in `.env`, never committed.
- Tests come with the first code: unit tests, plus at least one end-to-end test (Telegram update in -> lead in CRM).

## How we build: two roles

- **Planner / implementer**: writes the plan, then builds it step by step.
- **Critic**: an independent agent (fresh context, no stake in the plan). It reviews the plan once before building, and again after every two or three steps, to cut and simplify toward what gives the most value. Its findings and what we changed go in `docs/journal.md`.

These are roles in how we build the project, not agents inside the product: the product has one agent.

## Finishing a step

- The critic's findings for that step, if it ran, are in the journal.
- Stop after each step for Taras's review before starting the next.
