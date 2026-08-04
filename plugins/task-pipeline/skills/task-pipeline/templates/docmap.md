# Doc map — <project>

**One per project, not per run.** The four questions of
`references/documentation.md`, answered for this repository: where settled things
live, what each fact's single home is, what a change obliges, and what proves it.

Seeded by task-pipeline at stage 0 **only when absent**. Extend it whenever a new
document class appears; never let it grow a second copy of something stated
elsewhere — where another file already says it, this one holds a **pointer line**,
not a copy. A doc map that duplicates `AGENTS.md` is the first violation of the
rule it publishes.

## Contents

- Regime
- Registers
- Single source of truth
- Propagation matrix
- Gates
- Ratchets
- Terms
- Navigation

## Regime

`governed` — established <YYYY-MM-DD> by run `<topic>`, recorded as `DEC-0001`.

Governed scales by **volume**, never by dropping rules: a register with three
entries is a register. Nothing here is authored twice — every entry is transcribed
from an artefact the run already produced (the brief's *Decisions locked*, the
spec's contracts, an ADR).

## Registers

| Register | File | ID scheme | Append-only? | Guarded? |
|---|---|---|---|---|
| Decisions | `docs/DECISIONS.md` | `DEC-####` | yes | lease before write, where a mechanism exists |
| Open questions | `docs/OPEN_QUESTIONS.md` | `OQ-####` | yes (never delete a resolved row) | same |
| `<fill me>` | `<path>` | `<PREFIX-####>` | … | … |

> One decision home per project. If this repository already had `docs/adr/`, that
> is the register and the first row names it instead — never both.

## Single source of truth

Every fact has exactly one home; everything else links to it by id. A fact stated
in two places is a bug: collapse it to one home and link from the other.

| Fact | Home | Everything else |
|---|---|---|
| A settled decision | `docs/DECISIONS.md` | cites the `DEC-####` |
| `<the domain glossary>` | `CONTEXT.md` | links to the term |
| `<user-facing behaviour>` | `docs/ux/scenarios.md` | links to the scenario id |
| `<fill me>` | `<path>` | … |

## Propagation matrix

**The harvest ledger names what you read. This names what you owe.** A row's third
column names the check that notices when the row is not honoured — or the word
`review` **with a one-line reason why no check can decide it**. An empty third
column is a finding, not a blank.

| Change type | Update these | Checked by |
|---|---|---|
| New/changed **decision** | `docs/DECISIONS.md` + every doc in its `Consequences / affects:` line | gate §5 propagation |
| Question **resolved** | `docs/OPEN_QUESTIONS.md` → `Resolved→DEC-####`, the owning topic doc | gate §2 ids · gate §8 status vocabulary |
| **Scope** change | `<roadmap>`, `<mvp>`, the register | review — scope is a judgement, not a shape |
| `<new/changed entity or field>` | `<data model>` (canonical), `<glossary>` | `<fill me>` |
| `<user-facing behaviour>` | `<scenarios>` + `<flows>` + `<screens>`, same change | `<ux linter>` |
| `<fill me>` | … | … |

## Gates

| Gate | Command | When | Blocking? |
|---|---|---|---|
| Documentation | `bash scripts/check-docs.sh` | before the commit | yes |
| `<fill me>` | … | … | … |

Each gate states in its own header what it does **not** cover. Read that before
quoting a green as evidence.

## Ratchets

A named, counted set that may only shrink, printed beside the verdict on every run.
Raising a floor is a decision and belongs in the register.

| Ratchet | Floor variable | Current | Set on |
|---|---|---|---|
| Propagation backlog | `PROP_FLOOR` | 0 | <YYYY-MM-DD> |
| `<fill me>` | … | … | … |

## Terms

Only terms **declared here** are checked. A heuristic over every capitalised word
cries wolf, and a gate that cries wolf is removed by the third person who hits it —
so this table is the project's own list, and it may start with three rows.

| Term | Definition lives in | Anchor |
|---|---|---|
| `<Entity>` | `docs/DATA_MODEL.md` | `#entity` |
| `<fill me>` | `<the one document that defines it>` | `#anchor` |

Rules: **one definition per term**, the anchor resolves, and a document that uses the
term links to that anchor rather than restating it. A term with two definitions is
the same defect as a fact with two homes.

## Navigation

- One definition per entity, with an explicit anchor.
- A mention links to the **anchor**, not to the file.
- Indexes and summaries link; they never restate a rule. An index that falls behind
  lies with authority — a reader concludes the entry does not exist.
