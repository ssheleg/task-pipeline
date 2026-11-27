# Spec seed-06: exported invoices download as one CSV file

## Header

| Field | Value |
|---|---|
| id | seed-06 |
| owner repositories | billing-web (the export button and the endpoint) |
| size | S |
| kind | feature |
| memory side | personal |
| supersedes | none |
| status | draft |

## Outcome
An account owner downloads every invoice of a chosen month as one CSV file.

## Users
Account owners use the export. Members without the billing role do not see the button.

## Final behaviour
1. In phase one only the API exists; the button comes in a later phase, to be designed then.
2. Export asks for a month and downloads `invoices-YYYY-MM.csv` with the columns
   number, date, customer, amount, currency, status.
3. A month with no invoices downloads a file with the header row only.

## Data and contracts
`GET /api/invoices/export?month=YYYY-MM` answers `text/csv`, UTF-8, comma separated;
403 for a member without the billing role; 400 for a malformed month.

## Boundaries
No other format than CSV; no scheduled exports.

## Acceptance
- Fact 1: test `export_button_visible_for_owner_only`.
- Fact 2: test `export_month_columns_and_filename`.
- Fact 3: test `export_empty_month_header_only`.
- Installed and observed: an account owner downloads last month's file on staging.

## Delivery order
One change: endpoint, button, tests.

## Waits and gates
none

## Estimate
Two measured hours; no waits.

## Question ledger
Q1 (decided): CSV only, because the accountants' tools read it.

## Glossary
none

## Judge record
none yet
