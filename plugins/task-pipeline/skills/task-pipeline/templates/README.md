# templates

Skeletons task-pipeline seeds into a host project. Only the **brief** is a seeded
file (it is the stage-0 intake artifact). The spec and plan have no skeleton here —
their required structure is prescribed inline by `references/spec.md` and
`references/planning.md`; the `docs/ux/*` skeletons come from `super-ux`.

| Template | Seeded to | Stage |
|---|---|---|
| `brief.md` | `docs/superpowers/specs/YYYY-MM-DD-<topic>-brief.md` | 0 — intake grill |
| `context.md` | `CONTEXT.md` at the repo root (or per context) | 0 — grill, domain awareness |
| `adr.md` | `docs/adr/NNNN-<slug>.md` | 0 — grill, hard-to-reverse decisions |

`context.md` and `adr.md` are **format references**, not files to copy wholesale:
the grill writes `CONTEXT.md` entries and ADRs in their shape, lazily — only once
there is a resolved term or a decision worth recording.

Seeding rule (per the ssheleg canon): create a template copy **only when the
target is absent**; never overwrite an existing brief.
