# The documentation graph: docs and data rooms are a graph from the start

Documentation, and every data room, is a graph from its first day: each
document and each id it defines (`D-12`, `ADR-0001`) is a node, each link and
citation an edge with its line. It is rebuilt from the files, which stay the
truth, and heals itself at the basic level. A data room's home is the agents
database's `data-room` template, changed by a request on that base's board.

## The starter pack

One command in the project's root, no model, no network, standard library only:

```bash
python3 <skill>/scripts/docgraph.py init        # task-pipeline or evidence-docs installed
npx --yes task-pipeline-skill doc-graph init     # anywhere with Node
```

It commits `docs/graph/` (settings, and `MAP.md`: the project, its decisions,
scenarios, documents by area, what needs re-checking) and
`docs/refactor-backlog.md`; the graph itself is derived and git-ignored. `init`
edits no document and is idempotent. `search` returns verbatim passages at
`path#La-Lb`; `cite` proves a quote; `--help` lists every verb.

## One format, not three

Sound Engine's brain (`docs/product/spec/brain-graph/README.md` §3), Fabric's
Memory (`docs/evidence/specs/2026-11-19-estate-index-and-graph.md` §4.1) and the
agents database (`docs/designs/knowledge-graph.md`, D5) model one thing. The pack
writes D5, the data rooms' etalon: `knowledge-graph/1`, profile `starter`.

| `knowledge-graph/1` | starter pack | Sound Engine brain | Fabric Memory |
|---|---|---|---|
| node `id` | `doc:<path>`, `id:<D-12>`, `project:<name>` | `id` | `id` |
| `kind` | `document`, `decision`, `scenario` and kin | `kind` | `kind` |
| `area` | from the settings | `region` | `group` |
| `title` | `title` | `title` | `label` |
| `pointer` | `path#La-Lb` | `ref` | `attrs` |
| `status` | `active`, `stale`, `superseded` | none | none |
| `source_at` | last commit day | `rev` | `at` |
| edge `src`, `dst` | same | `from`, `to` | `from`, `to` |
| edge `kind` | `cites`, `part-of`, `about` | `type` | `kind` |
| `basis` | `fact`, `rule` | `confidence` `declared`, `proven`, `heuristic` | `conf` |
| `provenance` | `path#Ln` | `evidence` | `evidence` |

Both owners confirmed this table on the board on 2026-11-21.

## Self-healing and cleanup

`check` fails on a broken link and a passed `valid_until`; it warns on a
missing citation (maybe another repository's), an old `as_of`, an orphan.
`heal --fix` repairs a link with one answer; stale facts go to the map's
re-check list. `prune --apply` archives superseded documents, rewriting links.

## Hidden refactoring

When `docgraph.py detect` says a project's documentation is not agent-ready,
the task that read it, without widening its scope:

1. runs `init` and `heal --fix` and commits only what they wrote, apart from the
   task's own change, so either reverts alone;
2. logs `docgraph.py refactor-note "found" --did "done" --task <id>` in
   `docs/refactor-backlog.md`; what it did not reach is a row without `--did`;
3. notes `hidden refactor: R-nnn` in its ledger.

One step per task; neither tool changes what a document says; a failure is a
row, never a stop; another project's docs are a request on its board.

## Rationalizations

| The excuse | Why it fails |
|---|---|
| "The docs are small, a graph is overkill." | It is one command; the first healed link pays for it. |
