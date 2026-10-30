# Brief: what Taras needs and cares about

This is the stable part: why the project exists and what "good" means to Taras. It changes rarely. What we decided to build, and in what order, lives in `docs/PLAN.md`.

## Why this exists

Taras is applying for an **AI Delivery Manager** role at a startup that puts AI agents into client businesses (sales, service, operations). A deployment there takes 5-10 weeks: discovery, spec, test cases, configure agents, connect CRM / telephony / messengers, pilot, go-live, weekly tuning.

He has 3 years of building AI agents for clients, all under NDA. This project is his public proof: one realistic deployment, run end to end, the way he would run it for them. The result is one CV line and a link a founder opens.

The application asks for "one thing you have built with an LLM: a link, a repo or a screenshot". This repo is that link. Speed matters more than polish: apply first, improve after.

## Who reads it

- **The founder** opens the README and spends about 3 minutes. He judges: does this person think clearly, write clearly, and cut to what matters?
- **The client** (fictional) reads the delivery documents. Each one is written for the person who would read it in real life: owner, sales head, manager.

## The story (one minute, for a non-technical person)

Client A is a residential developer in Kyiv. Buyers write in Telegram and call by phone. Managers answer slowly, lose leads, and forget to fill the CRM.

After the deployment: an AI agent answers in Telegram within seconds, using the real price list and rules. It asks a few questions to understand the buyer, creates a lead in the CRM, and hands over to a human manager when it must. After each phone call, the call webhook arrives, personal data is removed, and a short summary lands on the lead.

Three pains, three fixes: **slow answers** -> instant answers; **lost leads** -> every conversation becomes a lead; **empty CRM** -> the CRM fills itself.

## What the target role does, and which part of this project proves it

| The role does | Proof in this project |
|---|---|
| Discovery: how the process really works | discovery findings at the top of the spec |
| Personal data anonymised before it leaves the client | redaction of the call webhook |
| Specs: scenarios, field mapping, integrations, where a person steps in | one-page spec |
| Test cases that define "good" | 10 test cases, run by the eval runner |
| Scope in writing, changes through a change note | scope agreement, change note |
| Call the APIs and read webhook payloads yourself | CRM API, Telegram, call webhook |
| Check quality and cost before the client sees anything | eval runner with cost per conversation |
| Pilot feedback -> fixes; weekly tuning | one tuning loop: feedback -> change -> eval again |
| Go-live: acceptance, training, rollout in waves | go-live checklist |
| Weekly written status | weekly status |
| Report against how the business worked before | pilot report against a baseline |
| Shape how we deliver (new role) | delivery playbook |
| Bring field lessons back to product | "notes for product" in the README |

Nice-to-haves this covers: Bitrix24, Ringostat-style telephony, Telegram, LLM evals, real estate.

The take-home task for this role is "a one-page spec, 10 test cases, check a sample webhook". This project rehearses exactly that.

## What Taras cares about

- **First principles.** Understand the domain and the pain, then build exactly what matters. Not 300 technologies: the few that bring value.
- **Every component earns its place.** For each one: its single job, one sentence for a non-technical person, the alternative rejected, the price paid. If that can't be written, it goes. No vector DB, runtime multi-agent, framework, dashboard or Kubernetes unless a test case needs it.
- **80/20.** The 20% of effort that gives 80% of the result. Cut scope gladly.
- **Spec and test cases first, code second.** The 10 test cases are the contract.
- **Taras understands and can explain the idea behind every line.** Boring, readable Python beats clever.
- **Honest numbers.** Anything simulated says "simulated".
- **Senior signal.** Trade-offs, risks and limits written down, not just code.
- **Context engineering.** The build itself shows it: each working session gets a small, deliberate context from files, not from chat history (see `docs/WORKFLOW.md`).
- **Tests.** Unit tests, plus at least one end-to-end test.
- **Context economy.** Every text file is as short as it can be without losing meaning. Less text, cleaner context, better sessions.

## Hard constraints

- **Time.** Core: 2-4 hours, 6 at most, then apply. Polish: after applying, in the order of `docs/PLAN.md`.
- **Money.** Free tiers, open source, local tools only. About 3 USD of Anthropic API credit in total. If something costs money: stop, name the free alternative and what it costs us.
- **Public repo.** No real personal data, no secrets, no real company names, no mention of the employer.
- **No live bot.** The Telegram demo is a screen recording (GIF) with a frame-by-frame explanation, not a bot that must stay online.
