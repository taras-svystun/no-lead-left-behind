# Do Ringostat webhooks carry the caller's name?

Date checked: 2026-10-30.

## Verdict

- **"Call processed by AI" event: no caller or contact name.** The official parameter sheets (EN, UK, RU) list no caller-name field for this event. The only person name in it is the employee's name. [S1, S4, S5, S6]
- **Plain "After call" event: no caller or contact name.** Same sheets, same result: the caller is identified only by phone number. The employee's name is there. [S4, S5, S6, S7]
- Client first and last name exist only in the messenger events, not in call events. [S4, S5, S6]

## Name-like fields

How to read the sheets: each row is a parameter, each column an event; an empty cell means "sent", a "—" means "not sent" (inference from the layout; the sheet has no legend).

The sheets give display labels, not JSON keys. The JSON keys come from one example payload in the incoming-call article [S7]. A dash in the key column means no public source names the key.

| Field (label) | JSON key | Events that send it | What it holds | Source (checked 2026-10-30) |
|---|---|---|---|---|
| Employee / Співробітник / Сотрудник | `employee_fio` | Incoming: after call, when taking the call, processed by AI. Outgoing: after call, processed by AI. | Name of the employee who handled the call ("John Smith"; UK/RU: "ПІБ/ФИО співробітника", full name). | S4, S5, S6, S7 |
| Employee ID | `manager_id` | Incoming: after call, rating menu, when taking the call, processed by AI. | Employee ID in the project (a number, not a name). | S4, S7 |
| (no label in sheet) | `manager` | Shown in the "when taking the call" example. | A list of numbers ("4411;4416;..."), not a name. | S7 |
| Employee email | — | Incoming: after call, when taking the call, processed by AI. | Employee email in Ringostat. | S4 |
| Department | — | Incoming: after call, when taking the call, processed by AI. | Name of the employee's department ("Sales"). | S4 |
| Caller's number (outgoing tab) | `caller` (incoming example) | Outgoing: all events. | For outgoing calls: "the login and the name of the SIP account that made a call", that is the employee side. For incoming calls it is the client's phone number. | S4, S7 |
| Responsible employees | — | Outgoing: after call, processed by AI. | List of employee IDs. | S4 |
| Numbers pool name | `pool_name` | Incoming: all events. | Name of the number pool (a source or channel), not a person. | S4, S7 |
| Call forwarding scheme name | `scheme` | Incoming: all events. | Name of the forwarding scheme, not a person. | S4, S7 |
| Google Analytics client ID | `gaid` | Incoming: all events. | A web-analytics visitor ID, not a name. | S4, S7 |
| Client's sentiment | — | Incoming and outgoing: processed by AI only. | Text about the client's mood, not a name. | S4 |
| Dialogue quality: Opening | — | Incoming and outgoing: processed by AI. | A score. Its description says the employee should "name the customer by name or ask for the customer's name"; it is a quality criterion, not a name field. | S4 |
| Client's first name / Client's last name | — | Messenger events only (dialog start, dialog end, taken into work, contact details given). | The client's name in the messenger. Not in any call event. | S4, S5, S6 |
| Username | — | Messenger events only. | Client's messenger username. | S4 |
| Employee (messenger) | — | Messenger events only. | Manager name, only if the manager opened the dialog. | S4, S5, S6 |
| Form fields / Дані форми | — | Website form event only. | Form contents, which may include a name field ("name, email, phone number, etc."). | S4, S5, S6 |

No field named or described as caller name, contact name, client name, CRM contact name, or caller "fio" appears in any call-event tab of the three sheets. [S4, S5, S6]

## What the "processed by AI" event carries

Call metadata, same as after call (all marked as sent in the AI column) [S4]:

- Caller's number, destination number, number in E.164 format.
- Call ID, project ID, call date, call date in microseconds, call type, call counter, unique call flag.
- Connected with (number or SIP login that answered), employee ID, employee, employee email, department, employee extension number.
- Call status, call duration, waiting and conversation duration, proper call, repeated call.
- Conversation recording link (ogg and wav), recording presence, call card link.
- UTM source, channel, campaign, content, keyword; landing page, last visited page, referrer, visitor IP, user agent, GA IDs, custom tracking entities, Roistat visit ID.
- Extension number entered in the IVR, numbers pool name, forwarding scheme name, insertion type.
- Not sent in the AI event: call value, call category, forward location, real waiting time.

AI parameters (sent only in the AI event, per the sheet) [S1, S4]:

- Short summary, client's sentiment, employee's sentiment, general sentiment, recommended actions.
- File with the AI result (.vtt): the full transcript with time codes.
- Summary, title, keywords, key points, sentiment, mistakes, good points, next steps.
- Dialogue quality: opening, history, presentation, closing, score, review.
- Parasite words, obscene language.
- Review required: score and details.
- Follow-up: main points and next steps.
- Own parameters: custom AI analytics parameters.

The help article for the AI event lists only six of these (short summary, three sentiments, recommended actions, .vtt file) and points to the sheet for the full list. [S1, S2, S3]

The outgoing tab has the same AI parameters under "The outgoing call processed by AI". [S4]

## Cannot be confirmed

- Whether the caller's name appears inside the AI text fields (summary, transcript, key points) when the caller says it on the call. Inference: likely, because the AI summarises the spoken conversation, but no source says so.
- Whether a CRM integration adds a caller-name field to webhooks. No source says it does. The contact-sync API sends names *into* Ringostat (`fullName`) for the Smart Phone contact book and call log, not out through webhooks. [S8]
- The exact JSON keys for most fields. Only the incoming "when taking the call" example names keys; no example payload exists for the AI event or the after-call event. [S7] The webhook UI's "Show sample" button would settle it but needs an account. [S9]
- The sheet has no legend; "empty cell = sent, — = not sent" is inference from its layout.
- The EN and UK sheets differ in places: for example, the UK sheet marks the "Dialogue quality" fields as not sent after call, while the EN sheet leaves those cells empty; and the UK sheet marks "Employee" as not sent when taking the call, while EN leaves it empty. [S4, S5]
- The UK and RU help pages link to different sheets than the EN page. [S2, S3]
- WebFetch could not open the UK and RU help pages (redirect loop); they were read with curl instead.

## Sources

- S1: Webhooks: event "Call processed by AI" (EN). https://help.ringostat.com/en/articles/9281387-webhooks-event-call-processed-by-ai
- S2: Same article (UK). https://help.ringostat.com/uk/articles/9281387
- S3: Same article (RU). https://help.ringostat.com/ru/articles/9281387
- S4: Official parameter sheet, EN (linked from S1 and S7). Tabs read: incoming calls (gid 365333506), outgoing calls (gid 1873383353), messenger (gid 1523312460), forms (gid 151902980), call category (gid 421829203), call statuses (gid 595072918). https://docs.google.com/spreadsheets/d/1UbCN8GecOpIj4-PIzucGinwecUz5zEv0ZDhTsDUWffY/edit#gid=365333506
- S5: Official parameter sheet, UK (linked from S2). https://docs.google.com/spreadsheets/d/1kGsry50NsMJh47gpCWXI3hL7HUs_MHskyb8pYDQWHTY/edit#gid=0
- S6: Official parameter sheet, RU (linked from S3). https://docs.google.com/spreadsheets/d/1odsHfRc5RilHX2VRNA52rTnqUwwuubBn3WxPH6o3VIQ/edit#gid=618431719
- S7: Incoming call event, with example JSON. https://help.ringostat.com/en/articles/6559993
- S8: API: sending information to Ringostat Smart Phone and contact book. https://help.ringostat.com/en/articles/9221318-api-ringostat-sending-information-to-ringostat-smart-phone-and-contact-book
- S9: How to set up the Ringostat integration using webhooks. https://help.ringostat.com/en/articles/6313229-how-to-realise-the-ringostat-integration-using-webhooks
- S10: Data transfer in webhooks (event list, about 40 parameters, no field list). https://help.ringostat.com/en/articles/6518985-integration-using-data-transfer-in-webhooks
