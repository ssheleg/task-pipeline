# Open questions — task-pipeline

Everything undecided, with an owner and what it blocks. This register was established on 2026-08-11,
when `B-009` measured that this project recorded `none` for it while the skill it
ships tells every host project to keep one. Doctrine: `references/documentation.md`. Answers land in [`DECISIONS.md`](DECISIONS.md), which this project did not have until `OQ-0001` and `OQ-0002` needed somewhere to resolve to. A question is
**never deleted** — the question is the history of the answer, and deleting it is
how the same thing gets re-argued a quarter later.

**Next free ID:** `OQ-0004`

Reserve the id before you write it; reading this line is not reserving it.

Status is a closed vocabulary: `Open` · `Resolved→DEC-####` · `Dropped (<why>)`.
Anything else reads as answered when it is not, and every check on that row skips
in silence.

| ID | Question | Owner | Blocks | Status |
|---|---|---|---|---|
| OQ-0001 | Can `SURFACED` be checked at all? It is defined as what a run learned by accident — recoverable from no artefact — so *"nothing surfaced"* is a quiet decision by construction. The `hand:` line records that a hand-back happened, never that it was complete | operator | whether the hand-back's own gate means anything beyond its presence | Resolved→DEC-0001 |
| OQ-0002 | Which of the 250 guards without a neighbour probe read a **scoped span**? The list cannot be computed from the code as written, so `B-057`'s remaining half has no work-list | operator | `B-057`, and the fourth consecutive release caught by a reader rather than a check | Resolved→DEC-0002 |
| OQ-0003 | Playwright MCP as a second browser path beside chrome-devtools: is it a **second** recommended companion or **the** one where a project already runs it in CI? A pasted note of ~6 lines did not reach the agent and may hold the answer | operator | `B-056` | Resolved→DEC-0004 |

**When one resolves:** flip the status to `Resolved→DEC-####` in the **same
change** as the decision that answers it, and leave the row where it is.
