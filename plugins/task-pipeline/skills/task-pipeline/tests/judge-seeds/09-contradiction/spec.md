# Spec: the board exports its open tasks as a CSV file

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

1. **The command.** `board export --project <id> --out <file>` writes every task of the project whose state is `backlog`, `running` or `review` to `<file>` and exits 0. A project id that does not exist exits 2 and writes nothing.
2. **The columns.** The file is UTF-8 CSV with a header row and exactly these four columns, in order: `id`, `title`, `state`, `owner`, `updated_at` (ISO 8601 UTC). Fields with a comma, a quote or a newline are quoted as RFC 4180 says.
3. **The order.** Rows are sorted by `updated_at`, newest first; equal times are sorted by `id` ascending.
4. **An existing file.** When `<file>` exists the command refuses with exit 1 unless `--force` is given; with `--force` it replaces the file atomically (write to a temporary file, then rename).

## Data and contracts

The CSV has three columns: `id`, `title`, `state`. Exit codes: 0 written, 1 unknown project, 2 file exists.

## Boundaries

Not changed: the board's storage and its states. Out of scope: closed tasks, other formats.

## Acceptance

| Fact | Check |
|---|---|
| 1 | a project with 3 open and 2 done tasks gives a file with 3 data rows; an unknown id exits 2 and leaves no file |
| 2 | the header row equals `id,title,state,owner,updated_at`; a title with a comma round-trips through Python's csv module |
| 3 | three tasks with two equal times come out in the order the fact names |
| 4 | a second run without `--force` exits 1 and the first file is unchanged; with `--force` the file is replaced |
| installed and observed | the owner runs the released command on their machine and opens the file in a spreadsheet |

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

