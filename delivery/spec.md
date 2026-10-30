# Spec: AI sales agent for Client A

For: Client A's owner and head of sales. Client A, its figures and its data are simulated.

## What we found (discovery)

1. About 400 buyer conversations a month: 60% in Telegram, 40% by phone.
2. Managers answer Telegram in 2 hours (median); chats after 19:00 wait until morning, and some are never answered.
3. 40% of CRM leads have no budget or rooms; calls reach the CRM only if the manager remembers.
4. Most chats ask the same things: price, sizes, payment options, how to book a viewing.
5. Managers keep the final word on discounts, bookings and anything not in the price list.

## Goal and pilot targets

Every buyer gets an answer within a minute, at any hour, and every conversation becomes a complete lead.

| Measure | Today | Pilot target |
|---|---|---|
| First reply in Telegram | 2 hours (median) | under 1 minute |
| Conversations that become a lead | unknown | 100% of Telegram chats |
| Leads with budget and rooms | 60% | 80% |
| Calls with a note on the lead | when remembered | every processed call |

## Scope

In: Telegram chat agent; leads in the CRM; handoff to managers; a summary of each phone call on its lead.

Out: booking or payment by the agent; discounts; completion dates; outbound messages; other messengers.

## How it works

**Telegram chat.** The agent says first that it is an AI assistant and never poses as a human. It answers in the buyer's language, from the price list and the policies only. It asks for budget, rooms, timing, payment method and phone. For the phone it shows a "Share phone" button twice at most: with its first reply and with the handoff message. The button disappears once the phone is shared, and the agent never insists. Every chat creates a lead with its first message, so a buyer who stops after two messages is still a lead; the agent adds what it learns as it goes.

**Handoff.** The agent passes the buyer to a manager when the buyer asks for a person or sends `/manager` (any time), wants a viewing or a booking, asks what the price list and policies do not answer, or complains. The lead gets status `handoff` and the reason; the buyer is told a manager will write within 15 minutes, or by 12:00 if they write between 19:00 and 9:00. After that the agent only repeats that a manager is on it.

**After a phone call.** The telephony system sends the caller's phone and a link to the call's transcript. We skip a call we have already processed, because the telephony system resends a webhook it thinks was lost. We find the lead by phone, or create one. We remove names, phone numbers and emails from the transcript, then the AI writes a short summary and fills budget, rooms, timing and payment method on the lead.

## Call webhook fields

The "call processed by AI" event, from the telephony system's parameter sheet. Keys marked simulated have no public example.

| Payload field | Key | Used for |
|---|---|---|
| Call ID | `call_id` (simulated) | skip a repeated delivery |
| Caller's number | `caller` | find the lead; stored as +380… whatever the format |
| Employee | `employee_fio` | redaction only; not stored |
| AI result file (.vtt) | `transcript_url` (simulated) | the transcript: time codes stripped, redacted, not stored |
| Short summary | (simulated) | not used: it fills no lead field |

## Lead fields

| Field | From | Example |
|---|---|---|
| Source | chat or call | `telegram` |
| Telegram ID | Telegram | `512339871` |
| Name | buyer | Olena |
| Phone | Share phone button, chat, or call | +380000000001 |
| Complex, rooms | buyer | North, 2 |
| Budget (USD) | buyer | 90,000 |
| Timing | buyer | within 3 months |
| Payment method | buyer | full / instalments / mortgage |
| Status | agent | `new` or `handoff` |
| Handoff reason | agent | `person`, `viewing`, `unknown`, `complaint` |
| Call summary | after-call webhook | "Asked about 2-room flats in North, mortgage, wants a viewing on Saturday." |

## Personal data

- Call transcripts are cleaned before the AI sees them: phone numbers and emails by pattern, plus the names we already know: the buyer's from the lead, the manager's from the call data.
- Telegram chats reach the AI as the buyer wrote them; the buyer is told up front they are talking to an AI. A phone shared with the button is saved by our code and does not reach the AI.
- The full phone number and name stay in the CRM, which is where managers need them.

## Risks and limits

- A name said only in passing on a call ("my wife Iryna") is not removed. Local name detection is planned.
- A buyer who never shares a phone and later calls gets a second lead; managers merge duplicates.
- The agent can be wrong; anything not in the price list or policies goes to a manager instead of a guess.

## Acceptance

The pilot starts when all 10 test cases in `test-cases.md` pass.
