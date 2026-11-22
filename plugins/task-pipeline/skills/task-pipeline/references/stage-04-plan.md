# Stage 4 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 4 — Plan
- **How it runs: [`planning.md`](planning.md)** — built into this skill →
  `<artifacts>/plans/YYYY-MM-DD-<topic>.md` (same slug as the brief and the
  spec). Zero-context tasks, exact
  paths, complete code in every step, TDD steps with expected output, DoD each,
  dependency graph + parallel groups, non-overlapping file ownership, and the
  Global Constraints block copied verbatim from the spec.
- `gate` ends the spec loop's verification ([`spec-protocol.md`](spec-protocol.md) →
  *The loop*).
- **Spec, then board, then build:** the plan's rows reach the board first, and
  `spec_protocol.py gate <spec> --board <backlog> --plan <plan>` passes before stage 5.
