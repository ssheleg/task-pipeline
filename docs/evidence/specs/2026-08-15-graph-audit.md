# Graph audit of task-pipeline — 2026-08-15

Run `r-6e62c4dab`, from the umbrella brief
`sshlg-skills/docs/evidence/briefs/2026-08-15-graph-engineering.md`.

**The axis.** Read the whole pipeline as a graph and ask the two questions the source
material makes askable: *which declared dependencies do not carry data* (fake edges), and
*where does the pipeline converge outputs without a gate* (an unguarded convergence).
Source: `agent-stack/plugins/agent-stack/skills/agent-orchestrator/references/graph-engineering.md`,
itself pinned to `https://x.com/Mahaximus_/status/2082442856417956173`.

**Evidence tiers**, never inflated: **measured** here · **documented** upstream ·
**judgement**. Priority uses the family's board formula, `P = blast × (1 + age) / effort`.

## What the audit found sound, and that is a result

The macro graph — stages 0 → 10 — was walked edge by edge with the fake-edge test. **Nine
of its ten edges carry data**: the brief feeds the docs study, the fetched contracts feed
the design, the design feeds the spec, the spec feeds the plan, the plan feeds the build,
the code feeds the tests, green tests feed the deploy, the deploy feeds the post-deploy
check. The one questionable edge is F-4 below, and it is rejected.

`planning.md:52-57` already draws a dependency graph, groups tasks topologically and tags
`depends:`. `build.md:265-280` already refuses to fan out unless three conditions hold.
**The pipeline was graph-shaped before this material arrived**; what follows is where the
shape is declared but not enforced.

## Findings

| id | Finding | Evidence | Tier | Blast | Effort | P | Verdict |
|---|---|---|---|---|---|---|---|
| F-1 | **The fake-edge test exists as a checklist line, not as a procedure, and no gate reads it.** `planning.md:194-196` self-review item 5 asks the right question — *every `depends:` points at a task that really produces what's consumed* — but there is no procedure for answering it and no computed output. The stage-4 GATE (`planning.md:238-248`) checks set equality, placeholders, name consistency and file ownership, and **never checks whether an edge is real**. A plan can therefore serialise everything and pass every gate | `planning.md:52-57`, `:194-196`, `:238-248` | documented | 2 | 1 | 2.0 | **accept** |
| F-2 | **A fanned-out group has no convergence check.** `build.md:265-280` dispatches a group concurrently and reviews **each task against its own diff**; integration then catches *file* conflicts only (`:278-279`). Two implementers can each pass their own review and still contradict each other — task 1 renames a helper task 2 calls, two tasks add the same config key with different defaults, two tasks each satisfy the same REQ differently. `review.md`'s *cannot verify from diff* verdict already admits this class exists and hands it to the orchestrator with no procedure attached. The article's second failure mode, exactly | `build.md:265-280`, `:340-342` | documented | 3 | 1 | 3.0 | **accept** |
| F-3 | **The pipeline never says it is a static graph, or why.** Its shape is fixed and audited; that is its central property and it is written nowhere. Meanwhile it does have a dynamic element — the module map cut at stage 2 (`decomposition.md:61`, `:106`) and the program loop — and nothing names the boundary. An unstated design choice is indistinguishable from an oversight, and the next run to "improve" the pipeline into something that decides its own stages will find no rule against it | absence across `stages.md`, `planning.md`, `decomposition.md` | documented | 2 | 1 | 2.0 | **accept** |
| F-4 | **Stage 8 → 9 may be a fake edge.** Stage 9 (docs, wiki, graph) consumes the stage-0 source ledger and the stage-5 changes; it needs the *version* from stage 7, not the post-deploy result from stage 8 | `stages.md:508`, `:541` | judgement | 1 | 2 | 0.5 | **reject** — two reasons. A single agent session executes serially, so removing the edge buys no wall-clock; and a post-deploy check can change what stage 9 must write (an honest-degradation report is a documented fact). The edge is weak, not fake |
| F-5 | **The fan-out rule is stated with three conditions in one file and one condition in another.** `build.md:273-276` requires all three — same group, exclusive file ownership, own worktree. `stages.md:395-396` summarises it as *"fan out **only** when each implementer gets its own worktree; otherwise sequential"*, dropping the first two. A reader who takes the summary as the rule fans out two tasks that share a file, in separate worktrees, and meets the conflict at integration | `build.md:273-276` vs `stages.md:395-396` | **measured** | 2 | 1 | 2.0 | **accept** |
| F-6 | **`build.md` prefers a native tool for worktrees and says nothing about a native primitive for fan-out.** `build.md:72-76` already has the principle — *native tool first, because it owns placement and cleanup* — and applies it to one thing. A host that offers deterministic fan-out owns the concurrency cap, the per-agent isolation and the resume, all of which the doctrine currently asks the orchestrator to hand-roll | `build.md:72-76`, `:265-280` | documented | 1 | 1 | 1.0 | **accept, reduced** — stated harness-agnostically. Naming a vendor keyword would pin the doctrine to one host and rot: the keyword in the pinned article was renamed six weeks after publication |
| F-7 | **The plan's *Execution order* table cannot express what an edge carries.** `planning.md:97-101` has columns `Group / Tasks / Runs after`. "Runs after" is temporal, which is the exact confusion the fake-edge test exists to remove. There is nowhere to write the payload, so nowhere for its absence to show | `planning.md:97-101` | documented | 2 | 1 | 2.0 | **accept** — a `Carries` column is the cheapest possible mechanisation: an empty cell *is* the finding |
| F-8 | **The negative self-tests cannot restore `.git` in a submodule checkout, so two guards silently never fire.** `negatives.py:148` gates the restore on `os.path.isdir(_git_src)`. In every checkout of this repository **as a submodule** — which is how the family ships it — `.git` is a 48-byte file holding `gitdir: ../../.git/modules/skills/task-pipeline`, so the branch is skipped and both git-dependent guards report `fatal: not a git repository` and are counted as *did not fire*. Measured on a tree this run had not touched: `python3 test/negatives.py` → exit **1**, `FAIL: 2 guard(s) did not fire`. CI clones normally and is green, which is why it survived. The copy must also **strip `core.worktree`** from the copied config (`worktree = ../../../../skills/task-pipeline`), or git inside the snapshot would operate on the real working tree — the snapshot exists precisely to stop that | `test/negatives.py:143-150`; the module config's `core.worktree` | **measured** | 3 | 1 | 3.0 | **accept** — found while establishing the baseline, and it blocks stage 6 for any change made from a submodule checkout |

## What is deliberately not changed

- **The stage list, the stage count and every gate type.** This audit changes gate
  *criteria* in one place (stage 4) and doctrine text elsewhere. Nothing renumbers,
  reorders or retypes a stage.
- **Any vendor's orchestration keyword.** F-6's reduction is the rule, not an omission.
- **Stage 8 → 9.** F-4, rejected above with its reasoning, so the next auditor finds the
  answer rather than the question.

## Verification for each accepted finding

| id | Verified by |
|---|---|
| F-1 | `planning.md` carries the numbered procedure; the `## Self-review` template carries an `Edges:` line; the stage-4 GATE names it in `planning.md`, `stages.md` and `SKILL.md`'s table |
| F-2 | `build.md` §4.2 carries the group convergence check with its five catches and its ledger line |
| F-3 | `planning.md` carries the static-graph statement, names the two dynamic elements, and states the auditability rule |
| F-5 | `stages.md:395-396` states all three conditions; `grep` shows the two files agree |
| F-6 | `build.md` §4.2 names the preference without naming a product |
| F-7 | `planning.md`'s *Execution order* table has a `Carries` column and the sentence that an empty cell is a fake edge |
| F-8 | `python3 test/negatives.py` from **this submodule checkout** exits 0 with 0 guards not fired; the fix is watched failing by restoring the `isdir`-only branch |

### F-8, measured — and one wrong reading corrected on the way

| Run | State | Result |
|---|---|---|
| baseline, alone | `isdir`-only | exit **1** — `FAIL: 2 guard(s) did not fire`, both `fatal: not a git repository` |
| the two guards alone, without the fix | `isdir`-only | `high-water mark lowered` → did not fire · `spoken for by a tag` → broken |
| the two guards alone, with the fix | fixed | both **PASS** |
| full suite, with the fix, run A | fixed | exit **0** — `all 318 guards provably reject their planted defect · 9 property check(s)` |
| full suite, with the fix, run B | fixed | exit **0** — identical |

**Three intermediate runs disagreed with each other (1, 2 and 3 guards down, plus
property checks silent) and that was not the subject.** They overlapped: a suite run
was started while another was still going, and every step copies the repo into a
**fixed** `/tmp` path, so two concurrent suites overwrite each other's scratch. The
runner's own comment says so — *"collisions only happen between two SUITE runs"* — and
two hypotheses were tested and disproved before that was found: duplicate scratch paths
(325 steps, 325 distinct paths, 0 collisions) and parent/child path nesting (0). The
instrument was fine; the operator was running two of them. Recorded because the wrong
reading — *"the suite is flaky"* — would have justified shipping over a red.
