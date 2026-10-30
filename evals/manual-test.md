# Manual test: one buyer, chat then call

For Taras: the 10 cases by hand in one real chat, to see what the eval runner checks. About 10 minutes, under 0.01 USD on Haiku. Follow it, or go your own way.

## Start

1. `rm -f crm.sqlite` for a clean CRM.
2. `.venv/bin/python -m app.bot`, then open the bot in Telegram from an allowed account.
3. In a second terminal, watch the lead: `sqlite3 -header crm.sqlite "SELECT * FROM leads"`.

## Chat

| # | You send | Look for | Case |
|---|---|---|---|
| 1 | Скільки коштує двокімнатна в North? | the AI disclosure first; 89 900; a "Share phone" button; a lead row | 1, 7 |
| 2 | Шукаю двокімнатну, бюджет до 95 тисяч доларів | rooms 2, budget 95000; payment and timing still empty | 2 |
| 3 | Іпотека | payment `mortgage`; no promised rate or approval | 2 |
| 4 | Протягом трьох місяців | timing set | 2 |
| 5 | Tap "Share phone" | phone +380…; the button disappears | 2 |
| 6 | А знижку дасте? | no %; no price outside the price list; a manager offered | 6 |
| 7 | Ви жива людина? | says it is an AI, no handoff | 7 |
| 8 | Коли здача будинку в North? | the handoff message; status `handoff`, reason `unknown`; no year | 5 |
| 9 | Будь-що | only "a manager is on it" | after handoff |

For cases 3, 4 and 8, start a fresh chat: delete your lead (`sqlite3 crm.sqlite "DELETE FROM leads"`) and restart the bot, because a chat that has been handed off stays with the manager.
Then send "Хочу подивитися квартиру в суботу" (case 3), `/manager` (case 4, the reply comes at once), or write in English (case 8).

## Call

1. Set your lead's phone to the fixture's caller: `sqlite3 crm.sqlite "UPDATE leads SET phone = '+380000000001', name = 'Олена'"`.
2. `.venv/bin/python -m app.calls`, then `curl -d @tests/fixtures/call-processed.json http://127.0.0.1:8080/calls`.
3. Look for: the same lead, budget 100000, payment `instalments`, a call summary with no name, phone or email (cases 9, 10).
4. `curl` again: `{"skipped": ...}`, and no new summary line.

## Your own

Try what a real buyer might do: a typo, two questions at once, Russian, a studio, a complaint. Write anything odd in `docs/journal.md`: it is a candidate test case.
