# Stage 5 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 5 — Dev
- **How it runs: [`build.md`](build.md)** — built into this skill: isolate the
  workspace (native worktree tool first, git fallback, baseline tests), keep a
  ledger under `.task-pipeline/build/<plan>/` so a compacted context can resume,
  then one fresh implementer subagent per task with a file-based brief and report,
  a review after every task ([`review.md`](review.md)), and a five-round fix loop
  with an explicit breaker. TDD per task ([`tdd.md`](tdd.md)): failing test →
  watch it fail → minimal impl → watch it pass → commit. Pin subagents to the
  run's confirmed model (`model-tiering.md`). The plan's parallel groups fan out
  **only when all three hold** — the tasks share no `depends:`, their file ownership
  is exclusive per the plan, and each implementer gets its own worktree; otherwise
  sequential. A group that did fan out gets **one convergence check over all its
  reports and diffs together, before the first worktree is integrated**
  ([`build.md`](build.md) §4.2a) — a per-task review reads one diff and cannot see a
  contradiction that exists only between two of them.
- **Web front end? The task's own surface is checked in a browser, not in the diff.**
  Where a browser channel is connected — `playwright` **or** `chrome-devtools`, either
  one, whichever answers first (**how**: [`browser.md`](browser.md); which:
  [`companion-skills.md`](companion-skills.md)): after a
  task that changes a rendered surface, load it, take a snapshot and read the
  console and the network log **before the task is marked DONE** — a component can be
  correct and land under a fixed header, and a review of the diff cannot see that.
  **What the look finds is fixed in this task, or parked with the ruling the GATE below
  requires — never parked silently** — a browser finding filed without a ruling is the
  diff-review verdict wearing a screenshot; the look was worth taking only if it can
  still change the code or is on record as deliberately not doing so. Absent, say the surface was verified by reading
  the diff and treat it as the weaker claim it is. **On a surface whose brief names a
  `surface_class`, the project linter runs here too**, after each task that changes a
  rendered surface — `python3 scripts/visual_gate.py lint <dir>`; an S1 finding is
  fixed in the task, and NOT_RUN (exit 3) is recorded as such
  ([`browser.md`](browser.md) → *The visual half*). **With Figma on, the token drift
  probe runs beside it** after a task that touches the token file or a tokenised
  component: `python3 scripts/visual_gate.py tokens --figma <variables.json> --css
  <tokens.css>`. A FAIL is fixed in the task, renaming one side to match the other.
  No export is NOT_RUN, recorded as such. A component whose API the task changed
  updates its Code Connect mapping in the same change
  ([`build.md`](build.md) → *Code Connect, kept*). A slop marker caught while the
  implementer is dispatched costs a line; caught on the contact sheet it costs a round. Stage 6 repeats this over the whole tree; this one catches it while the
  implementer that wrote it is still dispatched. The matrix pointed this companion at
  stages 5–6 from the day it was added and **this stage had never named it** — found by
  the guard comparing the two, not by a reader.
- **Domain companions, where the task is on their ground** — recommended, never a
  gate ([`companion-skills.md`](companion-skills.md)): `sheleg-dev` when the build
  wires money, tracking, sign-in or page speed; `agent-stack` when the thing being
  built is an agent system; `telegram-dev` when Telegram is the platform rather
  than the transport. Absent, the build ships on the host's own doctrine and the
  close-out names the seam nobody checked.
- **Integration closes the stage:** sync with the base branch, re-run the full suite
  on the result, land it the project's way (merge, or a PR — outward, so it needs a
  go), remove the worktree. Stages 7–9 act on the integrated result, so a branch the
  operator chose to leave unmerged is recorded as such.
