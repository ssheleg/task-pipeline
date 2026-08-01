# templates

Skeletons task-pipeline seeds into a host project. Two are **seeded files** — the
**brief** (the stage-0 intake artifact) and the **retro** (created at the first
stage-10 close-out, then appended to for the life of the project). The spec and plan
have no skeleton here — their required structure is prescribed inline by
`references/spec.md` and `references/planning.md`; the `docs/ux/*` skeletons come
from `super-ux`.

| Template | Seeded to | Stage |
|---|---|---|
| `brief.md` | `docs/superpowers/specs/YYYY-MM-DD-<topic>-brief.md` | 0 — intake grill |
| `carryover.md` | `docs/superpowers/specs/YYYY-MM-DD-<topic>-carryover.md` | 0 seeds, all stages append, 10 reads |
| `context.md` | `CONTEXT.md` at the repo root (or per context) | 0 — grill, domain awareness |
| `adr.md` | `docs/adr/NNNN-<slug>.md` | 0 — grill, hard-to-reverse decisions |
| `retro.md` | `docs/superpowers/retro.md` — **one per project, not per run** | 10 writes (prune → stamp → entry), 0 reads the standing instructions in full |

`context.md` and `adr.md` are **format references**, not files to copy wholesale:
the grill writes `CONTEXT.md` entries and ADRs in their shape, lazily — only once
there is a resolved term or a decision worth recording.

Seeding rule (per the ssheleg canon): create a template copy **only when the
target is absent**; never overwrite an existing brief. The rule is hardest and most
important for `retro.md`: it is the only artifact that accumulates across runs, so
overwriting it with the skeleton destroys every lesson the project has bought —
seed it once, then read, prune and append.
