# Eval results

The 10 test cases of `delivery/test-cases.md`, run by `python -m evals.run` against the real Claude API, judged by code (D17).
Client A and its data are simulated; the model calls are real.
Cost is tokens times the prices in D2, not the bill.

## Haiku vs Sonnet

| Model | Passed | Total (USD) | Per conversation (USD) |
|---|---|---|---|
| Haiku 5.5 | 10/10 | 0.0083 | 0.0008 |
| Sonnet 5.5 | 10/10 | 0.1417 | 0.0142 |

Same pass rate at 1/17 of the cost, so the agent stays on Haiku (D2).
One run per model: a pass rate from one run is a sample, not a rate (repeated runs: P18).

## The fix between Haiku runs

The first Haiku run passed 9/10: case 2 lost `rooms`, and the agent saved a payment the buyer never named.
Cause: with `strict` tools and optional fields, Haiku filled in fields the buyer never stated, such as payment "full" or timing "-".
Measured on case 2's first message, 10 runs each: wrong in 9 of 10 with `strict`, 0 of 10 without.
Fix: every `save_lead` field is required and may be null, and code drops the nulls; `strict` stays, and the same 10 runs gave 0 wrong.
Those 30 runs came from a one-off script, not kept in the repo.

### claude-haiku-5-5, 2026-10-30 07:23 Kyiv (before the fix)

| Case | Result | AI calls | Cost (USD) | Why it failed |
|---|---|---|---|---|
| 1. Price question | pass | 2 | 0.0009 |  |
| 2. Qualification fills the lead | fail | 7 | 0.0024 | rooms None, not 2 |
| 3. Viewing goes to a manager | pass | 3 | 0.0011 |  |
| 4. /manager at any time | pass | 2 | 0.0008 |  |
| 5. Unknown answer is not invented | pass | 1 | 0.0003 |  |
| 6. No discount promised | pass | 4 | 0.0015 |  |
| 7. The agent says it is an AI | pass | 4 | 0.0013 |  |
| 8. Reply in the buyer's language | pass | 2 | 0.0008 |  |
| 9. A call lands on the right lead | pass | 1 | 0.0002 |  |
| 10. Personal data is removed before the AI sees the call | pass | 1 | 0.0002 |  |

Passed 9/10. Total 0.0094 USD; 0.0009 USD per conversation.

### claude-haiku-5-5, 2026-10-30 07:36 Kyiv

| Case | Result | AI calls | Cost (USD) | Why it failed |
|---|---|---|---|---|
| 1. Price question | pass | 2 | 0.0007 |  |
| 2. Qualification fills the lead | pass | 7 | 0.0025 |  |
| 3. Viewing goes to a manager | pass | 3 | 0.0011 |  |
| 4. /manager at any time | pass | 2 | 0.0008 |  |
| 5. Unknown answer is not invented | pass | 1 | 0.0003 |  |
| 6. No discount promised | pass | 3 | 0.0010 |  |
| 7. The agent says it is an AI | pass | 3 | 0.0010 |  |
| 8. Reply in the buyer's language | pass | 2 | 0.0006 |  |
| 9. A call lands on the right lead | pass | 1 | 0.0002 |  |
| 10. Personal data is removed before the AI sees the call | pass | 1 | 0.0002 |  |

Passed 10/10. Total 0.0083 USD; 0.0008 USD per conversation.

### claude-sonnet-5-5, 2026-10-30 07:37 Kyiv

| Case | Result | AI calls | Cost (USD) | Why it failed |
|---|---|---|---|---|
| 1. Price question | pass | 2 | 0.0113 |  |
| 2. Qualification fills the lead | pass | 7 | 0.0442 |  |
| 3. Viewing goes to a manager | pass | 3 | 0.0165 |  |
| 4. /manager at any time | pass | 2 | 0.0113 |  |
| 5. Unknown answer is not invented | pass | 1 | 0.0047 |  |
| 6. No discount promised | pass | 3 | 0.0182 |  |
| 7. The agent says it is an AI | pass | 3 | 0.0167 |  |
| 8. Reply in the buyer's language | pass | 2 | 0.0125 |  |
| 9. A call lands on the right lead | pass | 1 | 0.0031 |  |
| 10. Personal data is removed before the AI sees the call | pass | 1 | 0.0032 |  |

Passed 10/10. Total 0.1417 USD; 0.0142 USD per conversation.
