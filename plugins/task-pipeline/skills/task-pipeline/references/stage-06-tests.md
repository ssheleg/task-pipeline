# Stage 6 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 6 — Tests
- **What:** consolidate test coverage for the change: confirm new functionality
  has tests (written test-first in stage 5), update/repair existing tests the
  change touched, and add edge-case + failure-path tests per DoD.
- **Invoke:** the host test runner (see `conventions.md` → *Lint + test*); the
  built-in [`tdd.md`](tdd.md) cycle for any uncovered gap — failing test first,
  same as stage 5.
- **Where the actor branch is armed, the agent surface is proven at two levels**
  ([`agent-surface.md`](agent-surface.md) → *The agent tester*). The gate: the
  proving call through a real client (local stdio where nothing is deployed) and
  the contract tests, each exiting 0. The judgment, where owed (an R3 node, a
  `public` surface): the agent tester's pass B, `pass^k` with k = 3, transcripts
  kept as fixtures. Parity is read by the super-ux v5 lint and `/ux-audit`.
