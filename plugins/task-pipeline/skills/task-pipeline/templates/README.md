# templates

Skeletons task-pipeline seeds into a host project. Two are **seeded files** — the
**brief** (the stage-0 intake artifact) and the **retro** (created at the first
stage-10 close-out, then appended to for the life of the project). The spec and plan
have no skeleton here — their required structure is prescribed inline by
`references/spec.md` and `references/planning.md`; the `docs/ux/*` skeletons come
from `super-ux`.

| Template | Seeded to | Stage |
|---|---|---|
| `brief.md` | `docs/evidence/specs/YYYY-MM-DD-<topic>-brief.md` | 0 — intake grill |
| `carryover.md` | `docs/evidence/specs/YYYY-MM-DD-<topic>-carryover.md` | 0 seeds, all stages append, 10 reads |
| `verification.md` | `docs/evidence/verification.md` | 8 writes a row per shipped REQ, 10 requires it, a human fills `Human` |
| `backlog.md` | `docs/evidence/backlog.md` | 0 seeds when absent, any stage appends, 10 resolves and re-derives |
| `run.md` | `.task-pipeline/run.md` — **git-ignored**, one per run | 0 seeds it, every gate appends a verdict, every repeating pass a `touch:` line |
| `context.md` | `CONTEXT.md` at the repo root (or per context) | 0 — grill, domain awareness |
| `adr.md` | `docs/adr/NNNN-<slug>.md` | 0 — grill, hard-to-reverse decisions |
| `docmap.md` | `docs/DOCMAP.md` — **one per project** | 0 — the documentation inventory |
| `decisions.md` | `docs/DECISIONS.md` — the decision register | 0 seeds it, the Doc Loop appends |
| `open-questions.md` | `docs/OPEN_QUESTIONS.md` | 0 seeds it, the Doc Loop resolves rows |
| `docgate.sh` | `scripts/check-docs.sh` | 0 seeds it · 9 runs it · 10 proves it |
| `hygiene.sh` | `scripts/check-hygiene.sh` | 0 seeds it · **5 runs it after every task** · 6 and 9 run it · 10 proves it |
| `stage-coverage.sh` | `scripts/stage-coverage.sh` | 0 seeds it · **10 runs it before the coverage table** — every stage the flow declares must carry a verdict, or the flow stops declaring one it merges |
| `hooks.example.json` | the project's `.claude/settings.json` | 0 — offered, never installed silently |
| `routing-rule.md` | the operator's `CLAUDE.md` — **offered by `setup`, never written silently** | 0 / `setup` |
| `retro.md` | `docs/evidence/retro.md` — **one per project, not per run** | 10 writes (stamp → prune → entry), 0 reads it in full |
| `retro-archive.md` | `docs/evidence/retro/YYYY-QN.md` | 10 rotates into it, 0 **queries** it |

The documentation-track templates (`docmap.md`, `decisions.md`,
`open-questions.md`, `docgate.sh`) are seeded **together**, and they are useful at
three entries: the register opens with the decision that established it, and the
gate exits `0` on exactly those seeds. A scaffold that seeds red teaches everyone on
day one that the gate is noise, so this repo's own validator runs the seeded gate
over a scratch project on every `npm test` and fails if it is not green.

`context.md` and `adr.md` are **format references**, not files to copy wholesale:
the grill writes `CONTEXT.md` entries and ADRs in their shape, lazily — only once
there is a resolved term or a decision worth recording.

Seeding rule (per the ssheleg canon): create a template copy **only when the
target is absent**; never overwrite an existing brief. The rule is hardest and most
important for `retro.md`: it is the only artifact that accumulates across runs, so
overwriting it with the skeleton destroys every lesson the project has bought —
seed it once, then read, prune and append.
