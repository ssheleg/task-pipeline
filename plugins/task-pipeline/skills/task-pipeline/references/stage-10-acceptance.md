# Stage 10 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 10 — Acceptance
- **What:** the closing stage — go back to the brief and account for **every**
  requirement. Doctrine: [`acceptance.md`](acceptance.md).
- **Every REQ this run shipped has a verification row, and every row names a REQ some
  brief carries.** Both directions: a shipped feature that entered no ledger and a
  ledger row about nothing are different failures ([`verification.md`](verification.md)).
- **The ledger's open rows are resolved onto the board.** Every carry-over row still
  `open` leaves with a `B-NNN` id on `<artifacts>/backlog.md`, and the ledger row
  is updated to name it ([`backlog.md`](backlog.md)). Both directions, because they are
  different failures: a ledger row pointing at an id nobody issued, and a board row
  traceable to nothing. Measured before this was built: across the ledgers in
  this repository, **twenty-four rows sat `open` with no home at all** — deferred out
  loud and filed nowhere. The first count said sixteen across six ledgers; it read the
  status column by position and was wrong wherever a ledger carried two of them. Then the board's priority is re-derived, because `age` moved while the
  run was happening. Every earlier gate asks
  "is this artifact good?"; none asks "does this still contain everything that was
  asked for?" The loss happens on the seams between stages, and this is where it
  surfaces.
- **Runs last**, after docs and wiki — those are deliverables too, and a REQ may
  name them.
- **The ladder walk runs FIRST** ([`audit.md`](audit.md)). The REQ table can only
  find what was named and lost; it cannot find what was never named, because a
  comparison needs two sides and an absence has one. So before the table: walk each
  REQ bottom-up through its rungs (decision → spec section → contract **and its
  failure behavior** → task → change → executed test → surface/docs), check the
  seam at each step, and order the findings **by seam, not by file**. On UI work
  designed visually, the frame is a **second, parallel statement of the same
  surface**: read it against the spec section that covers its `SCR-` id and against
  what shipped. The super-ux linter proves a frame link exists, is named right and
  is not stale — it cannot read the picture, so a frame promising a limit, a meter
  or a tier nobody built passes every lint there is. **Where the VISUAL track ran, the
  walk carries one more row: visual intent ↔ final render** — the director record (the
  brief's falsifier, the signature moment, the rubric written before any render) read
  against the **approved contact sheet**. On a `flagship`, `product` or `ad` surface the
  sheet is approved (`visual_gate.py sheet … --require-approval` exits 0), and the last
  `review:` line per surface — how many human rounds it took — is copied into the
  acceptance file, because `.task-pipeline/run.md` does not outlive the run
  ([`audit.md`](audit.md) → the `V→R` seam). An absence
  becomes a **new REQ row with its check** and *then* the table is written;
  appending after the table is how acceptance goes green over a gap. Findings that
  belong to a lower layer go back to that layer (spec → stage 3, plan → stage 4).
  Record the pass's two counts — new findings, and findings caused by this run's
  own fixes — so the next pass can tell whether the axis is exhausted.
- **How it runs:** built in. Read the brief's REQ table, the carry-over ledger in
  full, the plan's task statuses, git log, the final suite output, stage-8 notes and
  stage-9 doc changes (plus `docs/ux/scenarios.md` + `/ux-lint` for UI tasks). Write
  `<artifacts>/specs/YYYY-MM-DD-<topic>-acceptance.md` — one row per REQ,
  status `verified` / `partial` / `deferred` / `dropped`, each with **evidence** (a
  passing test name, `file:line`, a command and its output, or a scenario ID).
  "Done" without evidence is not done: downgrade to `partial` and say so rather
  than upgrading the claim.
- Then ask the operator the closing question out loud, list in hand: *here's what
  you asked for, here's what shipped, here's what's deferred and where it lives —
  what's missing?* Ask it even when the table is green; the operator holds context
  the brief never captured, and this is the cheapest moment in the run to hear it.
- **Several repositories: a submodule is finished when its parent says so.** A
  parent records each submodule as a **pointer to one commit**, and moving the
  submodule does not move the pointer — so the work is committed, pushed, CI green
  and done in its own roadmap, while a clone of the parent still gets the commit
  before it. Neither repo looks wrong alone; the disagreement lives between them,
  which is why it survives every check that runs inside one. Before closing, this
  reports nothing **for the parent as well as every submodule**:
  `git submodule status` (no line starting `+`), plus `git -C <repo> status
  --porcelain` and `git -C <repo> log @{u}..HEAD --oneline` per repo. With
  [agent-sync](https://github.com/ssheleg/agent-sync) installed,
  `/agent-sync finish` runs exactly that. The fix is two commands and the second is
  the forgotten one: `git -C <submodule> push`, then
  `git add <submodule> && git commit`.
- **The retrospective is the run's last act** ([`retrospective.md`](retrospective.md)),
  written to `<artifacts>/retro.md` — one file per project, not per run. The
  pipeline's gates are good at *this* run and blind across runs: the same class of
  failure can be caught, fixed and forgotten five times and nothing in the flow
  notices it is the same one. So, in this order: **stamp the run first** (one line,
  with its commit — and the only thing that makes the next step computable), **then
  prune** (every standing instruction against its three retirement triggers — it
  became a check, its surface is gone, it hasn't fired in five run stamps or in sixty days — and the
  list held to its cap of ten, every deletion logged **in the archive, with the
  commit that retired it**), then **write an entry only if
  the run diverged** (symptom · the stage it surfaced at · the stage that *owned* it
  · root cause · fix, mechanical before instruction before expiring note · the check
  that catches it next time). An entry whose class would be true in another project
  carries a `**Lesson:**` line, and **`scripts/lessons.py add --retro <retro> --entry
  <anchor>` puts it in the local lesson index** — and, where the session lists a shared
  store, `emit-observatory` → the tool → `record` ([`iteration.md`](iteration.md) → *The
  learning loop*). Every run stamps and prunes; a retro left empty after
  a messy run is the failure the file exists to stop. Stage 0 reads the standing
  instructions in full next time, which is why the cap is not negotiable.
