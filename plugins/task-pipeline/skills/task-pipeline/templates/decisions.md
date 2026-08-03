# Decisions — <project>

**Append-only.** Every settled thing that shapes the product, the architecture, the
scope, security, data, pricing or process. Doctrine:
`references/documentation.md`.

**Next free ID:** `DEC-0002`

Reading *"Next free ID"* is **not** reserving it — a second agent reading it in the
same minute gets the same answer. Reserve it, then write.

## Format

```markdown
### DEC-0007 — <one line, in the present tense>

- **Date:** 2026-08-03
- **Status:** Accepted
- **Context:** what forced the choice
- **Decision:** what was chosen, stated so it can be obeyed
- **Consequences / affects:** `docs/SECURITY.md`, `docs/DATA_MODEL.md`
- **Source:** run `2026-08-03-<topic>` · commit `a1b2c3d`
- **Supersedes:** DEC-0004
```

| Field | Rule |
|---|---|
| `Status` | `Accepted` · `Superseded by DEC-####` · `Reversed` · `Accepted · **Partially superseded by DEC-####** — <one line>` · `Accepted · **Refined by DEC-####**` |
| `Consequences / affects` | every document that must change. **Each one must cite this id** — the gate checks it |
| `Source` | the run that produced it **and the commit**; the commit is what survives a rename |
| edge markers | `Refines:` additive, target needs no annotation · `Contradicts:` a named clause falls, target **must** be annotated · `Supersedes:` the whole target retires, target **must** be annotated |

**To change your mind:** add a new entry, edit **only the status line** of the old
one, leave its body intact. Never renumber. Never delete.

---

### DEC-0001 — Documentation is governed: registers, a doc map and a gate

- **Date:** <YYYY-MM-DD>
- **Status:** Accepted
- **Context:** this repository had no addressable home for settled things, so
  decisions lived in chat and in per-run specs and were re-litigated every time
  somebody new arrived.
- **Decision:** decisions live here with stable `DEC-####` ids, append-only; open
  questions live in `docs/OPEN_QUESTIONS.md`; `docs/DOCMAP.md` holds the single
  homes, the propagation matrix and the gate; `scripts/check-docs.sh` enforces the
  mechanical half and runs before every commit.
- **Consequences / affects:** `docs/DOCMAP.md`, `docs/OPEN_QUESTIONS.md`
- **Source:** run `<topic>` · commit `<sha>`
