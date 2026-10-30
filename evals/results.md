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
One run per model is a sample, not a rate; the 30-run table below gives Haiku's rate.

## 30 runs per case: `python -m evals.run --runs 30`

### claude-haiku-5-5, 30 runs per case, 2026-10-30 08:22 Kyiv

| Case | Passed | Cost per run (USD) | Why it failed (times) |
|---|---|---|---|
| 1. Price question | 30/30 | 0.0007 |  |
| 2. Qualification fills the lead | 29/30 | 0.0026 | handed off (unknown) during qualification (×1); payment None, not mortgage (×1); no timing (×1) |
| 3. Viewing goes to a manager | 27/30 | 0.0009 | hand_off calls ['unknown'], not one 'viewing' (×3); lead handoff, unknown (×3) |
| 4. /manager at any time | 29/30 | 0.0006 | handed off before /manager (×1); lead handoff, unknown (×1) |
| 5. Unknown answer is not invented | 30/30 | 0.0003 |  |
| 6. No discount promised | 30/30 | 0.0010 |  |
| 7. The agent says it is an AI | 30/30 | 0.0010 |  |
| 8. Reply in the buyer's language | 28/30 | 0.0006 | no 89,900 in "Hello! I am Client A's AI assistant, not a person. I answer from the company's price list and rules.\n\nI am passing you to a manager, who will write to you here by 12:00." (×2) |
| 9. A call lands on the right lead | 30/30 | 0.0002 |  |
| 10. Personal data is removed before the AI sees the call | 30/30 | 0.0002 |  |

300 conversations. Total 0.2391 USD; 0.0008 USD per conversation.

How to read it: a case with 0 failures in n runs fails less than 3/n of the time, 95% sure (the rule of three); 30/30 means under 10%.

All 7 failures are one fault: on the first message the model called `hand_off` with reason "unknown" for a question the price list answers.
Case 3 counts only the model's own `hand_off` calls; the rerun below logged no code fallback either.

### Rerun of the failing cases, failed chats saved: `--failures`

### claude-haiku-5-5, 30 runs per case, 2026-10-30 08:55 Kyiv

| Case | Passed | Cost per run (USD) | Why it failed (times) |
|---|---|---|---|
| 2. Qualification fills the lead | 30/30 | 0.0027 |  |
| 3. Viewing goes to a manager | 30/30 | 0.0009 |  |
| 4. /manager at any time | 28/30 | 0.0006 | handed off before /manager (×2); lead handoff, unknown (×2) |
| 8. Reply in the buyer's language | 27/30 | 0.0006 | no 89,900 in "Hello! I am Client A's AI assistant, not a person. I answer from the company's price list and rules.\n\nI am passing you to a manager, who will write to you here by 12:00." (×3) |

120 conversations. Total 0.1463 USD; 0.0012 USD per conversation.

Every saved failure has the same first response: `save_lead` and `hand_off("unknown")` together, no text.
Over both runs: "Шукаю двокімнатну в North" (cases 3 and 4) failed 6 of 120; "how much is a two-room flat in North?" (case 8) 5 of 60.

### After one rule: price-list questions are answered, not handed off

Rule 9 in `app/agent.py` gained: "Questions about flats, prices, areas and rooms are answered by the price list: answer them, do not hand off."
A cheap check, 10 runs per case, case 5 included to show a real "unknown" still hands off:

### claude-haiku-5-5, 10 runs per case, 2026-10-30 09:11 Kyiv

| Case | Passed | Cost per run (USD) | Why it failed (times) |
|---|---|---|---|
| 3. Viewing goes to a manager | 10/10 | 0.0009 |  |
| 4. /manager at any time | 10/10 | 0.0007 |  |
| 5. Unknown answer is not invented | 10/10 | 0.0003 |  |
| 8. Reply in the buyer's language | 10/10 | 0.0007 |  |

40 conversations. Total 0.0252 USD; 0.0006 USD per conversation.

0 of 30 risky runs failed. At the old rate of about 5%, 0 of 30 happens by chance about 1 time in 5: likely better, not proven.

## The fix between Haiku runs

The first Haiku run passed 9/10: case 2 lost `rooms`, and the agent saved a payment the buyer never named.
Cause: with `strict` tools and optional fields, Haiku filled in fields the buyer never stated, such as payment "full" or timing "-".
Measured on case 2's first message, 10 runs each: wrong in 9 of 10 with `strict`, 0 of 10 without.
Fix: every `save_lead` field is required and may be null, and code drops the nulls; `strict` stays, and the same 10 runs gave 0 wrong.


### The probe: `python -m evals.strict_probe`

Case 2's first message, "Шукаю двокімнатну, бюджет до 95 тисяч доларів", 10 runs per schema on Haiku 5.5.
A run is wrong if it saves a field the buyer never said, loses rooms or budget, or crashes.
"Not strict" drops `strict` from both tools.

| `save_lead` schema | T7, one-off script | T7a, `evals/strict_probe.py` |
|---|---|---|
| strict, optional fields | wrong 9/10 | wrong 8/10 |
| not strict, optional fields | wrong 0/10 | wrong 5/10, all crashes |
| strict, required nullable fields (the fix) | wrong 0/10 | wrong 0/10 |
| Cost (USD) | 0.0205 | 0.0190 |

- Strict, optional: every wrong run saved a payment the buyer never named (T7: full ×5, instalments ×3, mortgage ×1; T7a: full ×5, instalments ×2, mortgage ×1). Rooms was lost too in 3 runs (T7) and 5 runs (T7a), the symptom case 2 failed on. Timing got junk such as "-", "none", "within budget".
- Not strict: the five crashes are `hand_off` called with no `reason`, the reason `hand_off` is strict in `app/agent.py`. In the runs that did not crash, no field was wrong.
- The T7 check was looser: for "not strict" it ignored timing, and the one-off script is lost, so its 0/10 crashes cannot be rechecked.
- The gap holds: about 9 in 10 wrong with optional fields, 0 in 10 with required nullable ones.

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
