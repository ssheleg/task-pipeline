# Spec: phase one of the board's CSV export

## Header

| Field | Value |
|---|---|
| id | `board-csv-export` |
| owner repositories | board-service (the export command and its tests) |
| size | S |
| kind | feature |
| memory side | `personal` |
| supersedes | none |
| status | `draft` |

## Outcome

The owner, 2026-11-20 (chat with the board agent): «хочу выгрузку открытых задач в CSV». When this is done the owner opens the file in a spreadsheet and sees every open task of one project.

## Users

One kind: the board's owner, who runs the command on their own machine. No other user kind touches it: the command is local and writes a local file.

## Final behaviour

1. **Phase one.** For now the command prints the open tasks' ids to the terminal, one per line; the CSV file, its columns, its order and the refusal to overwrite come in a later phase.
2. **A first step.** This phase is a prototype to learn whether the owner uses it; the finished export is planned after it.

## Data and contracts

The CSV columns above. Exit codes: 0 written, 1 file exists without `--force`, 2 unknown project.

## Boundaries

Not changed: the board's storage and its states. Out of scope: closed tasks, other formats.

## Acceptance

| Fact | Check |
|---|---|
| 1 | the command prints one id per open task |
| 2 | the owner tells us after a week whether it helped |
| installed and observed | the owner runs the prototype |

## Delivery order

1. board-service: the command, its tests and the README line (by 2026-11-30).

## Waits and gates

none: no other project and no human gate.

## Estimate

Kind feature, size S: one piece, p50 0.8 h, p85 3.6 h.

## Question ledger

None open. Tactics decided here: RFC 4180 quoting, atomic replace with `--force`.

## Glossary

- Open task: a task whose state is `backlog`, `running` or `review`.
- Project id: the board's id of a project, as `board projects` lists it.

## Judge record

