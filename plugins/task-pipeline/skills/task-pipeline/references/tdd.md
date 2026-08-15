# TDD — stages 5 and 6, built in

How every task in the build is implemented, and what stage 6 consolidates. Built
into this skill; nothing to install.

> Ported from the `test-driven-development` skill in
> [obra/superpowers](https://github.com/obra/superpowers) (MIT — see `LICENSE` →
> *Third-party*), with the stage-6 suite gate added.

## Contents

- The iron law
- Red → green → refactor
- The green from residue
- Tests that stay honest
- Stage 6 — consolidation and the suite gate
- When the thing under test is an agent
- When stuck
- What a case consumes, and why a timeout is unclassified
- Rationalizations
- Red flags — stop and start over

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

## The green from residue

`learned.md` rule 18. A suite that passes here and fails on a runner is usually not flaky and not
environment-specific — it is reading **state that accumulated on this machine** and is created from
nothing everywhere else. A database migrated once by hand months ago, a cache warmed by an earlier
run, rows a previous suite left behind, a checkout whose generated files were never regenerated.

Local state is *cumulative*; CI state is *constructed*. Every green obtained on the cumulative one
carries an unstated premise, and the premise is false in the only environment that matters.

Once per feature, and always before calling a suite green:

```bash
# whatever "new" means here — a fresh database, a clean volume, a new container, a fresh clone
docker compose down -v && docker compose up -d && <migrate> && <test>
```

Name the fresh instance in the report. "The suite is green" and "the suite is green against a
database created ten seconds ago" are different claims, and only the second one predicts CI.

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
- **A green suite is not a rendered page.** On a web front end the suite proves the
  code does what its assertions say; it cannot see a component that renders correctly
  and lands under a fixed header, a request that 404s while every unit test mocks it,
  or a console error that costs nothing at test time. Where a browser channel is
  connected — `playwright` **or** `chrome-devtools`, either one
  ([`companion-skills.md`](companion-skills.md)) — open the surface and read
  the console and the network log before calling it done — and **quote what you read**,
  not that you looked. Absent, the honest sentence is *"verified by reading the diff"*,
  which is a weaker claim and is recorded as one. Same family as a test that passes
  regardless of the production code: the assertion is real and it is pointed at
  something other than what a user reaches.
- **A browser test suite does not close this, either.** `playwright test` in CI is a
  suite whose runner happens to be a browser: it still asserts only what someone wrote
  down. It belongs to the coverage half of the gate, and the sentence above still needs
  a page that was opened and read. The two fail differently, which is the entire reason
  to keep both — and [`browser.md`](browser.md) separates them from a third thing they
  are both confused with, the Playwright **library**, which is an automation API and not
  a test framework at all.
- **The look that found it writes the assertion that keeps it found.** `generate-locator`
  on the element the look caught, then a spec around it, then `pause-at` to watch the
  new spec see what you saw ([`browser.md`](browser.md)). A browser finding fixed with
  no test behind it is a finding scheduled to return.

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

## When the thing under test is an agent

An agent's behaviour is not in its source. The code says what it is *allowed* to do;
only a run says what it did. So the artifact under test is the **execution record**, and
the suite above needs one more tier before *green* means anything.

Three tiers, and they do not carry equal authority at the gate:

| Tier | Fixture | Asserts | At the gate |
|---|---|---|---|
| **Step** | one serialized model call with its prompt, tools and context | the decision — tool chosen, argument shape | **blocks** |
| **Turn** | one whole execution | the trajectory, the final response, **and the state change** | **blocks** |
| **Thread** | a scripted multi-turn session | what carried across turns, checked after **every** turn, failing fast | **reports** |

Two rules the ordinary suite does not need:

- **Assert the side effect, not the sentence.** An agent that says it saved the
  preference and did not passes trajectory and response and is broken. The memory row,
  the written file, the created record — inspect the thing, not the prose about it.
- **A model judging a model is not a check until it has been calibrated.** Label the
  same traces by hand, measure the agreement, and only then let it score unattended.
  This is canon 5 with a different subject: a judge nobody has watched disagree is a
  green nobody has watched turn red. Cheap deterministic checks — schema, exact match,
  business rule, tool-call correctness — run first and take everything they can decide,
  because they cost nothing and cannot drift.

**The suite is grown, never authored.** Every production failure and every thumbs-down
is minimised to the smallest input that still reproduces it, filed into the tier that
isolates it, and **kept there permanently** — a fixed defect that silently returns is
the whole reason this rule exists.

**GATE (auto):** step and turn tiers green, and every fixture added by this change
present in the suite. Thread results and any online, reference-free checks are
**reported beside the verdict, not folded into it** — canon 9, which is why a
non-blocking tier still has to print.

**What this gate does not cover:** anything the fixtures do not contain. An offline
suite proves you did not regress the cases already known; it cannot speak for inputs
nobody has seen, which is canon 6 and the reason production observation is a stage-8
concern rather than a stage-6 one.

For building the suite this gate reads — the primitives, the tiers, judge design,
annotation queues and simulated users — see the `agent-evals` skill in the
`agent-stack` plugin.

## When stuck

| Problem | What it means |
|---|---|
| Don't know how to test it | Write the API you wish existed, then the assertion. Still stuck → ask the operator. |
| The test is too complicated | The design is too complicated. Simplify the interface. |
| Everything has to be mocked | The code is too coupled. Inject dependencies. |
| Setup is enormous | Extract helpers; if it's still huge, the design is the problem. |
| Fixing a bug | Write the failing test that reproduces it first. The test proves the fix and prevents the regression. |

## What a case consumes, and why a timeout is unclassified

Reported from another project after hours spent reading environmental noise as product
defects. An end-to-end suite registered a fresh account in every case. The product
rate-limits registration to a handful per minute per address. **A suite of twenty-odd
cases cannot avoid tripping its own product's limiter.**

A throttled registration does not fail loudly. The form never advances, the case sits
until its own timeout, and it reports **as a timeout** — which reads exactly like
slowness. Cold compilation, hydration and a stale cache were each investigated and each
was independently true; none was the cause.

**A check that cannot run to completion in its own environment reports noise, and noise
costs more than silence, because it looks like data.** Silence gets investigated. Noise
gets interpreted.

The neighbouring rule this bundle already has — *a check counts only where it runs* — is
about **availability**: does the guard execute on the gate. This is about **capacity**:
the harness is part of the system under test, and a suite that exhausts a production limit
is measuring the limit.

**So at the tests gate, name what each case consumes from the product** — accounts,
rate-limited endpoints, external quota, seats, tokens — and confirm the suite's total
stays under the product's own bound. Where it cannot, the suite **shares** the resource
across cases instead of acquiring it per case.

**Where the bound comes from, and what to do when it does not exist.** In order: the
product's own configuration or code; the provider's documented limit; the operator. Write
the answer into the brief's source ledger like any other fetched fact — a limit an agent
remembered is a limit nobody can check. **Where none of the three answers, the row reads
`bound: unknown` and the count goes to `unlooked`** rather than to a guess: this file's
whole argument is that an unmeasured resource reports as a timeout, and an unmeasured
*bound* does the same one level up.

**And it does not override *The green from residue*.** That rule is about state a case
inherits — a database, a volume, a clone — and it still says acquire fresh. This rule is
about a resource **the product itself meters**. Where the two meet, the product's bound
wins and the suite shares that one resource while everything else stays fresh; say which
resource is shared and why.

**And a timeout in an end-to-end suite is an unclassified result, not a slow one.** Before
it is read as a performance signal the resource question above must have an answer, or the
run is interpreting its own harness. In the reporting project this was also the most
likely reason that suite had never once finished inside its CI time cap — so the cost was
not only the hours, it was every defect the suite never got far enough to find.

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
