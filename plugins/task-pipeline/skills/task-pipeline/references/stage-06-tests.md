# Stage 6 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 6 — Tests
- **What:** consolidate test coverage for the change: confirm new functionality
  has tests (written test-first in stage 5), update/repair existing tests the
  change touched, and add edge-case + failure-path tests per DoD.
- **Invoke:** the host test runner (see `conventions.md` → *Lint + test*); the
  built-in [`tdd.md`](tdd.md) cycle for any uncovered gap — failing test first,
  same as stage 5.
