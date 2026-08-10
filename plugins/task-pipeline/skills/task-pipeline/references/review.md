# Review — the rubric and the prompts, built in

Used by stage 5's per-task reviews, its scoped re-reviews and its final
whole-branch review ([`build.md`](build.md)). Built into this skill; nothing to
install.

> Ported from the `requesting-code-review` skill and the reviewer prompts in
> [obra/superpowers](https://github.com/obra/superpowers) (MIT — see `LICENSE` →
> *Third-party*), condensed into one rubric plus three copy-paste prompts, with the
> external helper scripts replaced by plain git commands so the doctrine works on
> any agent.

## Contents

- The diff package
- Reviewer inputs
- Controller rules
- The rubric
- The independent reader — dispatched by a stage, and read by its output
- Prompt — task review
- Prompt — scoped re-review
- Prompt — final whole-branch review

## The diff package

A reviewer never re-derives the diff with a dozen git calls, and the diff never
enters **your** context. Write it to one file and pass the path (`$WORKSPACE` is
this plan's git-ignored directory, `.task-pipeline/build/<plan-basename>/` — see
[`build.md`](build.md)):

```bash
{ git log --oneline "$BASE..$HEAD"
  echo
  git diff --stat "$BASE..$HEAD"
  echo
  git diff -U10 "$BASE..$HEAD"
} > "$WORKSPACE/review-task-$N-$(git rev-parse --short "$HEAD").md"
```

`BASE` is the commit you recorded **before** dispatching the implementer — never
`HEAD~1`, which silently drops every commit but the last of a multi-commit task.
For a scoped re-review, `BASE` is the head the previous review saw. For the final
review, `BASE` is `git merge-base "$BASE_BRANCH" HEAD` — the base branch recorded
in the stage-0 brief, which is not always `main`.

Never dispatch a reviewer without a diff file.

## Reviewer inputs

Four things, three of them paths:

1. The **task brief** file — what was required.
2. The **implementer report** file — what was done, with the test evidence.
3. The **diff package** path.
4. The **Global Constraints** that bind this task — copied **verbatim** from the
   plan: exact values, exact formats, stated relationships ("same layout as X",
   "matches Y"). This block is the reviewer's attention lens.

## Controller rules

- **Never pre-judge.** Don't tell a reviewer to ignore something, don't cap a
  severity, don't explain why a finding would be a false positive. If your prompt
  contains "don't flag", "at most Minor", or "the plan chose this" — stop: you're
  buying yourself a shorter loop with an unreviewed defect. Let the finding come and
  adjudicate it in the loop.
- **Don't ask a reviewer to re-run tests** the implementer already ran on the same
  code; the report carries the evidence.
- **No open-ended directives** ("check all uses", "run race tests if useful")
  without a concrete, task-specific reason.

## The rubric

Review in this order; stop reading the diff only when you've covered all of it.

1. **Spec compliance.** Every requirement in the brief: met, partially met, or
   missing. Anything built that the brief did *not* ask for is scope creep — flag
   it, even when it's nice.
2. **REQ satisfaction.** Read the task's `Implements:` requirement statements, not
   just its instructions, and judge the diff against **those**. A task can satisfy
   every line of its brief and still miss the requirement it exists to deliver —
   that gap is invisible one level down, which is why it is asked for here.
3. **Correctness.** Logic errors, off-by-one, wrong operator, unhandled `None`/nil,
   race conditions, resource leaks, wrong error propagation. State the concrete
   input or state that produces the wrong output — a finding without a failure
   scenario is an opinion.
4. **Global constraints.** Exact values, formats and relationships from the
   constraints block. Approximations are failures.
5. **Test honesty.** Tests assert on real behavior, not on mocks. No test that
   passes regardless of the production code. No `skip`/`xfail`/commented assertion
   smuggling a red suite past a gate. New behavior has a covering test; the failure
   path has one too.
6. **Effect verification.** Claims about the world outside the diff — a migration
   run, a job cancelled, a file moved, a service restarted, an artifact published —
   carry evidence that the **state was re-read**, not that the command returned
   success. A report asserting an effect with no `verified-by:` line is an
   unverified claim, and it is **Important**, not Minor
   ([`gates.md`](gates.md) → *False success*).
7. **Error handling and degradation.** Every external call (network, DB, file, MCP,
   API) handles failure, and the failure is reported honestly rather than swallowed.
8. **Boundaries and clarity.** One responsibility per unit; names that say what the
   thing is; no duplication of a logic block that should be shared; nothing left
   dead.
9. **Security.** No secrets in code, logs or fixtures; input validated at the
   boundary; no new injection or path-traversal surface.
10. **Docs in the same change.** Module docs, runbooks and (for UI work) the
   super-ux layers updated alongside the code, not deferred.

**Severities:**

- **Critical** — wrong behavior, data loss, security hole, a red or dishonest test
  suite. Blocks.
- **Important** — a real defect or spec gap that will bite: missing requirement,
  unhandled failure path, a magic value the constraints named. Blocks.
- **Minor** — style, naming, a nit with no behavioral consequence. Never blocks;
  goes to the ledger.
- **⚠️ Cannot verify from diff** — the requirement lives in unchanged code or spans
  tasks. Not a blocker for the reviewer; the controller resolves it.

Formatting nits that don't change meaning are not findings. Praise is not a
finding either.

## The independent reader — dispatched by a stage, and read by its output

**One job: stop *"a reader was requested"* from standing in for *"a reader
reported"*.** Those are different facts and they look identical in a transcript.

The rule this implements has been a standing instruction since 2026-08-08: **a change
that adds or widens a check gets an independent reader before merge**, because your own
probes exercise only the shapes you already thought of. Its retirement condition, written
at birth, was that the reader be *dispatched by a stage rather than by the repository
happening to run a bot on pull requests*. This section is that stage.

**It happened.** Four pull requests of almost nothing but check work were opened on one
day; the review application reported **`skipping`** on every one, and twenty-two new
guards merged with the author's own probes as their only reading. Nothing was violated.
Nothing read the reviewer's output either.

### Who counts as the reader, in order

1. **A subagent this run dispatches** — the only option whose execution the run can
   observe end to end. Give it the diff package, the rubric, and the sentence *"the
   author wrote both the check and its probes; find what neither could see."*
2. **A review bot on the pull request** — acceptable, and it is a **third party with no
   contract**: it may skip, rate-limit, or answer about a stale commit. Read its
   verdict, not the fact that it was triggered.
3. **A person.**

### The three states, and one of them is not silence

Record exactly one, beside the gate verdict:

```
reader: 6 findings, 4 confirmed        — read, and it had something
reader: none found                     — read, and it did not
reader: NO READER — <why>              — nobody read it
```

**`NO READER` is a printed state, never an omission.** It carries the same law as
`dormant` and `skip` ([`gates.md`](gates.md) → *Progressive arming*): a mechanism that
prints nothing when it looked at nothing is indistinguishable from one that looked and
found nothing. Where the change added or widened a check, `NO READER` is also carried
into the close-out as an open requirement rather than a footnote — reporting a gap is
honest and is not a fix.

### What the reader is asked

Not *"review this."* The dispatch names the blind spot it exists to cover:

- the probes and the checks were written from **one model of the problem** — where does
  that model not reach?
- which shapes does the check's **scope** exclude, and is any of them shipped?
- is there a form of the defect that has **no pair to compare** — a single cell, a lone
  directive, an absence?

Those three questions come from findings no author-written probe has ever produced here.

## Prompt — task review

> You are reviewing one task of an implementation plan. Read, in order:
> `<brief path>` (the requirements), `<report path>` (what the implementer did and
> the test evidence), `<diff package path>` (commits, stat, full diff).
>
> Global constraints binding this task:
> ```
> <verbatim block>
> ```
>
> Produce three verdicts, all required:
> 1. **Spec compliance:** ✅ or ❌. List every requirement as met / partial /
>    missing, and list anything implemented that was not asked for.
> 2. **REQ satisfied:** ✅ or ❌ per `Implements:` id. The brief quotes each
>    requirement's statement — judge the diff against **that statement**, not
>    against the task's instructions. A task can follow every instruction and still
>    miss the requirement it exists to deliver; say so when it does.
> 3. **Code quality:** approved or not. Findings only, each as
>    `severity — file:line — the defect — the failure scenario (concrete input or
>    state → wrong result)`. Severities: Critical, Important, Minor. Use
>    `⚠️ cannot verify from diff` for anything you can't judge from the diff alone.
>
> Review against the rubric: correctness, global constraints, test honesty (tests
> assert real behavior, not mocks; no skipped/empty assertions), error handling and
> honest degradation, boundaries and naming, security and secrets, docs updated in
> the same change. No praise, no formatting nits that don't change meaning. Do not
> re-run the tests the report already covers. Return the verdicts and findings as
> your final message — nothing else.

## Prompt — scoped re-review

> A previous review of this task raised the findings below. The implementer has
> since pushed fixes. Read `<brief path>`, `<report path>` (its fix report is
> appended at the end) and `<fix diff package path>` — the fix diff **only**.
>
> Open findings:
> ```
> 1. <finding>
> 2. <finding>
> ```
>
> For each finding return `ADDRESSED` (with the `file:line` that resolves it) or
> `NOT ADDRESSED` (with what's still wrong). Then flag any **new** Critical or
> Important breakage introduced by this fix diff. Out-of-scope observations about
> code this diff didn't touch: list them separately as deferred minors — they are
> not part of this verdict. End with: all findings addressed / N still open.

## Prompt — final whole-branch review

> Review this entire branch before merge. Read `<diff package path>` (merge-base to
> HEAD) and `<spec path>`.
>
> Findings deferred or parked during implementation:
> ```
> <the ledger's minor + parked lines>
> ```
>
> Judge the branch as a whole: does it deliver the spec; do the pieces fit; is
> anything half-migrated, duplicated across tasks, or left dead; are the tests
> honest and the suite genuinely green; is error handling consistent; are docs in
> sync. Triage the deferred/parked list: which of those must be fixed before merge,
> which can stand and why. Findings only, with severity and a concrete failure
> scenario each. Return the findings as your final message.

**A ruling that parks a finding is a decision.** *"This stands, and here is why"* is
exactly the sentence a future reader will hit in the code and re-litigate, so a
ruling that outlives the run goes through the **Doc Loop**
([`documentation.md`](documentation.md)) — via the report and the ledger, written by
the orchestrator after integration, never by a subagent
([`build.md`](build.md) → *4.1a Decisions settled inside a task*).

Run the final review on the **run's confirmed model** like everything else
([`model-tiering.md`](model-tiering.md)). It is the one review that sees the whole
change, so if the run is on a tier below the most capable one available, say so and
offer to escalate just this dispatch — a recommendation stated out loud, never a
silent switch (`build.md` → *Models*).

**An empty result is not a clean result** (`learned.md` rule 19). A verification command that printed nothing did not verify anything — the instrument and the subject fail identically, because both produce an empty string. Assert the output is non-empty and shaped as expected before any finding is closed on it, and quote the output rather than the conclusion.
