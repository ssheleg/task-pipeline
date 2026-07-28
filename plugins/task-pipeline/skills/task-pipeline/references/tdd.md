# TDD — stages 5 and 6, built in

How every task in the build is implemented, and what stage 6 consolidates. Built
into this skill; nothing to install.

> Ported from the `test-driven-development` skill in
> [obra/superpowers](https://github.com/obra/superpowers) (MIT — see `LICENSE` →
> *Third-party*), with the stage-6 suite gate added.

## The iron law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

**If you didn't watch the test fail, you don't know it tests the right thing.**

The same law governs every other check in the run — a gate's `check`, a lint rule,
a host script, a detector written during an audit. A check nobody has seen fail is
a decoration that reports success. [`audit.md`](audit.md) → *Exit criterion* is
this rule raised from one test to the whole pipeline.

Wrote code before the test? Delete it and start from the test. Not "keep it as
reference", not "adapt it while writing tests", not "look at it once more". Delete
means delete — code you kept is code the test was written to fit.

**Always:** new features, bug fixes, refactors, behavior changes.
**Exceptions, and only with the operator's say-so:** throwaway prototypes,
generated code, pure configuration.

Thinking "skip TDD just this once"? That thought is the rationalization, not the
exception.

## Red → green → refactor

**RED — write one failing test.** One behavior, a name that describes that
behavior, real code rather than mocks wherever mocks are avoidable.

**Verify RED — run it and watch it fail. Mandatory.** Confirm it *fails* rather
than *errors*, that the message is the one you expected, and that it fails because
the feature is missing — not because of a typo or a bad import. A test that passes
immediately is testing behavior that already exists: fix the test.

**GREEN — the simplest code that passes.** No extra options, no "while I'm here"
refactor of the neighbors, no configuration surface nobody asked for. YAGNI.

**Verify GREEN — run it and watch it pass. Mandatory.** The new test passes, the
other tests still pass, and the output is pristine — no stray warnings or errors.
Test still fails → fix the code, never the test. Another test broke → fix it now.

**REFACTOR — only once green.** Remove duplication, improve names, extract helpers.
Tests stay green. No new behavior enters here.

Then the next failing test.

## Tests that stay honest

- **Before writing a test, name the production change that would make it fail.**
  Can't name one? The test asserts nothing useful.
- **Assert on real behavior, never on mock behavior.** `expect(mock).toHaveBeenCalled()`
  proves the mock works. Understand a dependency's side effects before mocking it —
  a mock that lies is worse than no test.
- **One thing per test.** An "and" in the name means two tests.
- **Test-only helpers live in test utilities**, never as extra branches or flags in
  production classes.
- **Edge cases and failure paths are part of the task**, not a follow-up ticket:
  empty input, boundary values, the network call that fails, the timeout.

## Stage 6 — consolidation and the suite gate

Stage 5 wrote the tests task by task. Stage 6 makes the whole thing true:

- New functionality has tests (written test-first in stage 5) — fill any gap now,
  the same way: failing test first.
- Tests the change touched are updated or repaired, not deleted around.
- Edge-case and failure-path coverage matches each task's DoD.
- The test command is the one recorded in the brief's autonomy sweep; "green" means
  what the brief says it means (including a known-red baseline, if one was
  recorded).

**GATE (auto):** the **full** suite is green — not just the new tests. New and
changed code is covered. No `skip` / `xfail` / commented-out assertion smuggles a
red suite past the gate. A partial or red run never advances to deploy; report it
honestly instead.

## When stuck

| Problem | What it means |
|---|---|
| Don't know how to test it | Write the API you wish existed, then the assertion. Still stuck → ask the operator. |
| The test is too complicated | The design is too complicated. Simplify the interface. |
| Everything has to be mocked | The code is too coupled. Inject dependencies. |
| Setup is enormous | Extract helpers; if it's still huge, the design is the problem. |
| Fixing a bug | Write the failing test that reproduces it first. The test proves the fix and prevents the regression. |

## Rationalizations

| Excuse | Reality |
|---|---|
| "Too simple to test" | Simple code breaks. The test costs 30 seconds. |
| "I'll test after" | Tests written after pass immediately, which proves nothing. You never watched it fail, so you never proved it can catch the bug. |
| "Tests after achieve the same thing — spirit, not ritual" | Tests-after answer "what does this do?"; tests-first answer "what should this do?" After-the-fact tests are biased by the code that already exists. |
| "I already tested it manually" | Ad-hoc, unrepeatable, no record of what was covered. "Worked when I tried it" is not coverage. |
| "Deleting X hours of code is wasteful" | Sunk cost. The real choice is rewriting with TDD versus keeping code you can't trust. |
| "Just exploring first" | Fine — throw the exploration away and start with TDD. |
| "The existing code has no tests either" | You're improving it. Add tests for what you touch. |
| "TDD will slow me down" | TDD is the fast path: bugs caught before commit, refactors without fear. The shortcut ends in production debugging. |

## Red flags — stop and start over

Code before test · test written after implementation · test passed on the first run
· can't explain why it failed · "tests later" · "just this once" · "keep it as
reference" · "it's about spirit not ritual" · "this case is different because…"

All of them mean the same thing: delete the code, start from the failing test.
