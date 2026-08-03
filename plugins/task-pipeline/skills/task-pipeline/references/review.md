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
6. **Error handling and degradation.** Every external call (network, DB, file, MCP,
   API) handles failure, and the failure is reported honestly rather than swallowed.
7. **Boundaries and clarity.** One responsibility per unit; names that say what the
   thing is; no duplication of a logic block that should be shared; nothing left
   dead.
8. **Security.** No secrets in code, logs or fixtures; input validated at the
   boundary; no new injection or path-traversal surface.
9. **Docs in the same change.** Module docs, runbooks and (for UI work) the
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
([`build.md`](build.md) → *§4.1a*).

Run the final review on the **run's confirmed model** like everything else
([`model-tiering.md`](model-tiering.md)). It is the one review that sees the whole
change, so if the run is on a tier below the most capable one available, say so and
offer to escalate just this dispatch — a recommendation stated out loud, never a
silent switch (`build.md` → *Models*).
