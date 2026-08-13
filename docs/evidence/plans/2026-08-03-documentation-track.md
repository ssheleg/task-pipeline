# Plan — the documentation track, the gate doctrine, and the learning loop

**Spec:** [`../specs/2026-08-03-documentation-track-design.md`](../specs/2026-08-03-documentation-track-design.md)
(read §3 *Locked contracts* before writing anything — every exact string comes from
there). **Target release:** `v1.7.0`. **Repo:** `task-pipeline`.

**Scene, once, for every task below.** This repository is a *skill*, not an
application: almost every file is prose an agent reads and obeys. There is no build
step. `npm test` (= `python3 test/validate.py`) is the lint, the type-check and the
test in one; `npm run test:all` adds the negative self-tests that prove each guard
can fail. House rules: [`CLAUDE.md`](../../../CLAUDE.md),
[`CONTRIBUTING.md`](../../../CONTRIBUTING.md). Prose style: line-wrap at ~80
characters, state the rule then the failure it prevents, end every doctrine file
with a *Rationalizations* table. Never start a wrapped line with `>` (it becomes a
blockquote) and never hardcode a vendor model id.

**Working order inside every task (this is TDD for a prose repo):**

1. add the validator guard the task owns → `npm test` → **watch it fail** with the
   exact message you wrote;
2. write the content → `npm test` → green;
3. add the negative self-test to `.github/workflows/validate.yml` →
   `npm run test:negatives` → watch it pass **because the corrupted copy failed**;
4. commit.

A guard nobody watched fail is decoration. If step 1 passes immediately, the guard
is wrong — fix the guard, not the expectation.

**Dependency graph and parallel groups**

```
T1 ──► T2 ─┬─► T3 ─┬─► T7 ──► T8 ──► T9 ──► T10 ──► T11
           ├─► T4  │
           ├─► T5  │        (T3 = group B barrier: templates exist)
           └─► T6 ─┘
```

| Group | Tasks | May run in parallel? | Files owned (no overlap) |
|---|---|---|---|
| A | T1 | no — sets the baseline | branch only |
| B | T2, T4, T5, T6 | **yes** | T2 `references/documentation.md`; T4 `references/gates.md`; T5 `references/hooks.md`; T6 `references/retrospective.md` + `templates/retro.md` + `templates/retro-archive.md` |
| C | T3 | after B starts, before T7 | `templates/{docmap,decisions,open-questions,adr,hooks.example.json}` |
| D | T7 | no | `templates/docgate.sh` |
| E | T8, T9 | **yes** | T8 `SKILL.md` + `references/stages.md` + `pipeline.example.json`; T9 the six remaining references + `templates/brief.md` + `templates/README.md` |
| F | T10, T11 | no | validator/CI, then release surfaces |

---

## T1 — Branch and a recorded baseline

**Why.** CONTRIBUTING: *"Check the base is green first — if the repo already fails
your new rule, the self-test passes for the wrong reason and proves nothing."* The
baseline is the evidence that every later red is yours.

**Steps**

```bash
cd /Users/sshlg/DATA/task-pipeline
git checkout -b feat/documentation-track
npm run test:all
```

**Expected output** — both lines, in this order:

```
PASS: task-pipeline structure valid
... 20 negative self-tests, 0 unexpectedly green
```

(The second line's wording comes from `test/negatives.py`; what matters is a zero
exit code. Record the exact text in the commit body.)

**DoD.** On branch `feat/documentation-track`; `npm run test:all` exits `0`; the
output is pasted into the first commit body.

**Commit**

```
chore: baseline for the documentation track — test:all green at v1.6.1
```

---

## T2 — `references/documentation.md` (new built-in doctrine)

**Scene.** This is the file that carries the whole documentation practice. It is
what an agent on an unfamiliar project reads to learn *what documentation is for*
here: a register with ids, one home per fact, an obligation that fires on a change
type, and a gate that can say no. Nothing in the current skill states any of it.

**Owns:** `plugins/task-pipeline/skills/task-pipeline/references/documentation.md`
(new) and the V1/V10 guard halves that name it.

**Step 1 — the guard first.** In `test/validate.py`, extend the built-in-doctrine
list (the loop with the comment *"The pipeline is self-contained: every stage's
doctrine ships inside the skill"*, currently ending `"knowledge-sources.md",
"audit.md",`) so it reads:

```python
    "knowledge-sources.md", "audit.md",
    "documentation.md", "gates.md", "hooks.md",
```

Run `npm test`. **Expected failure** (three lines, because T4 and T5 have not run):

```
FAIL: task-pipeline structure invalid
 - missing built-in stage doctrine: references/documentation.md
 - missing built-in stage doctrine: references/gates.md
 - missing built-in stage doctrine: references/hooks.md
```

If T4/T5 are running in parallel and have landed, only the first line appears. Both
are correct; what is not correct is a green run.

**Step 2 — write the file.** Required sections, in this order. Content comes from
spec §3.1–§3.5, §3.7, §3.8; write it as doctrine (rule, then the failure it
prevents), not as a summary of the spec.

| # | Heading | Must contain |
|---|---|---|
| 1 | `# Documentation — the system, not the by-product` | the one-job line; that docs are a deliverable with a gate |
| 2 | `## The inventory — four questions, answered before the first line of work` | where decisions live · what each fact's single home is · what a change of type X obliges · what proves it. Names `docs/DOCMAP.md` as where the answers land |
| 3 | `## Registers and ids` | the two permitted shapes (spec §3.2 — register **or** ADR set, never both); detection order; *reference by id, never by copying the text*; ids are never renumbered |
| 4 | `## Single source of truth` | one home per fact; a fact in two places is a bug, collapse and link; the cross-repository form — the owning repo decides, a consumer repo describes, and where they disagree the consumer is wrong |
| 5 | `## The Doc Loop` | the seven steps of spec §3.4, numbered, each with the failure it prevents; the line **"finishing the chat answer is not finishing the task"**; that it fires at *any* stage |
| 6 | `## Changing your mind` | append-only; status-line-only edits; partial supersede annotates both sides; the three markers table (spec §3.2.2) with the 204-of-275 measurement; no retro-classification |
| 7 | `## The propagation matrix` | the five-step build procedure (spec §3.5); the `Consequences / affects:` → citation rule; **the ratchet**, with the 162-across-73 measurement and why failing on all of it makes the gate get switched off |
| 8 | `## Navigation` | one definition per entity; an anchor per definition; a mention links to the **anchor**, not the file; indexes never restate a rule — they rot and a reader believes them |
| 9 | `## Intent and as-built` | spec §3.7's table; reconcile before **and** after; the gap is the finding; the tool is optional, the discipline is not |
| 10 | `## Registers are shared state` | spec §3.8; reserve-before-mint; lease-before-write; **`ungated` is an honest state and must be said out loud** |
| 11 | `## Where this binds in the pipeline` | table: stage 0 inventory + reconcile · any stage → the Doc Loop · stage 9 propagation sweep + gate · stage 10 evidence. Links `stages.md`, `gates.md` |
| 12 | `## Rationalizations` | at least eight rows — see below |

Rationalizations to include verbatim in spirit (the excuse an agent will actually
reach for):

| Excuse | Reality |
|---|---|
| "It's a small project, a register is overkill" | A register with three entries costs three minutes and is the only reason the fourth decision can be found. The overhead people mean is *ceremony*, and none of it is required here. |
| "I'll write the decision up at the end" | At the end you remember the outcome and not the alternatives you rejected, which is the only part with any value later. |
| "The spec already says it" | A spec is per-run and gets superseded by the next one. A decision outlives every artefact that mentions it. |
| "I updated the docs I touched" | The matrix names the docs you did **not** touch. That is the entire point of having one. |
| "Two docs saying the same thing is harmless" | Until they disagree, and then both are unusable and nobody knows which moved. |
| "I'll just fix the old decision's text" | Then the reason someone chose it is gone, and the next person re-litigates it from scratch. Supersede, never edit. |
| "Nobody else is working in this repo right now" | You cannot know that from inside your session, and the cost of being wrong is two agents minting one id. |
| "The gate is green, the docs are fine" | The gate proves what it checks. Read its scope header before quoting it as evidence. |

**Step 3 — the negative self-test.** Add to `.github/workflows/validate.yml`, in
the style of the existing steps (corrupt a **copy**, in python, never `sed -i`):

```yaml
      - name: Negative self-test — missing documentation doctrine
        run: |
          rm -rf /tmp/neg && cp -R . /tmp/neg
          rm /tmp/neg/plugins/task-pipeline/skills/task-pipeline/references/documentation.md
          if (cd /tmp/neg && python3 test/validate.py); then
            echo "guard did not fire"; exit 1
          fi
```

Then `npm run test:negatives` and confirm the new step is listed and passes.

**DoD.** File is ≥1500 bytes with all twelve sections; `npm test` green;
`npm run test:negatives` green and the new step named in its output; the file is
reachable from `SKILL.md` **after T8** (it is expected to be flagged unreachable
until then — see the note in T8).

> **Known interim red.** `validate.py` fails any `references/*.md` that
> `SKILL.md` cannot reach. T2/T4/T5 therefore cannot be committed alone. **Land
> group B and T8's SKILL.md link edit in one commit**, or add the SKILL.md
> reference line as the first step of each of T2/T4/T5 (preferred — it is one line
> each and keeps every commit green).

**Commit**

```
docs(doctrine): documentation as a governed system — registers, SSOT, the Doc Loop
```

---

## T3 — the seeded templates

**Scene.** These are the files the pipeline writes into a host project the first
time it runs there. They must be useful at three entries and must not require
anything to be filled in before the first real decision — otherwise the gate seeds
red and the project learns on day one that the gate is noise.

**Owns:** `templates/docmap.md`, `templates/decisions.md`,
`templates/open-questions.md`, `templates/hooks.example.json`, and the field-set
edit to `templates/adr.md`.

**Step 1 — the guards.** In `test/validate.py`, after the existing `tpl_dir`
block, add:

```python
    # The doc map is the host project's own copy of the documentation contract:
    # where decisions live, what each fact's home is, what a change obliges, and
    # what proves it. A seeded map missing the matrix seeds a project with a
    # register and no obligation — which is the state the register exists to end.
    docmap = os.path.join(tpl_dir, "docmap.md")
    if not os.path.isfile(docmap):
        fail("missing template: templates/docmap.md (the host project's doc map)")
    else:
        _dm = open(docmap, encoding="utf-8").read()
        for _h in ("Regime", "Registers", "Single source of truth",
                   "Propagation matrix", "Gates", "Ratchets", "Navigation"):
            if not re.search(r"^##\s+" + re.escape(_h) + r"\b", _dm, re.M):
                fail(f"templates/docmap.md: missing the '## {_h}' section")
        if "Checked by" not in _dm:
            fail("templates/docmap.md: the propagation matrix must carry a "
                 "'Checked by' column — a row nothing enforces is a wish, and the "
                 "column is where 'review' has to be written out loud")

    # Two permitted shapes of ONE decision home (spec 3.2). If they disagree on
    # fields, a project that picks the other shape silently loses a rule.
    _dec = os.path.join(tpl_dir, "decisions.md")
    _adr = os.path.join(tpl_dir, "adr.md")
    if not os.path.isfile(_dec):
        fail("missing template: templates/decisions.md (the decision register)")
    elif os.path.isfile(_adr):
        _d, _a = open(_dec, encoding="utf-8").read(), open(_adr, encoding="utf-8").read()
        for _field in ("Status", "Consequences / affects", "Source",
                       "Refines", "Contradicts", "Supersedes"):
            if (_field in _d) != (_field in _a):
                fail(f"templates: {_field!r} is in only one of decisions.md / "
                     "adr.md — the register and the ADR shape are two spellings of "
                     "one contract, so a field in one and not the other is a fork")
```

`npm test` → **expect** `missing template: templates/docmap.md (…)` and
`missing template: templates/decisions.md (…)`.

**Step 2 — write the templates**, exactly to spec §3.1/§3.2/§3.3.

- `templates/docmap.md` — the seven sections; every table has a header row and
  **one worked example row** plus one `<fill me>` row; `## Regime` pre-filled with
  `governed` and the sentence that governance scales by volume, never by dropping
  rules; `## Gates` pre-filled with `bash scripts/check-docs.sh · pre-commit ·
  blocking`; a note under `## Propagation matrix` that a `Checked by` cell may be
  `review` **only with a one-line reason**.
- `templates/decisions.md` — the `**Next free ID:** \`DEC-0001\`` header, the
  format block of spec §3.2.1, one worked `### DEC-0001` entry recording the
  project's own choice of documentation regime (so the register starts non-empty
  and self-describing), and the append-only rule with the three markers table.
- `templates/open-questions.md` — the header, the five-column table of spec §3.3
  with one worked row, the closed status vocabulary, and the *never delete a
  resolved question* rule.
- `templates/adr.md` — add the missing fields so the two shapes agree: `Status`
  with the same vocabulary, `Consequences / affects:`, `Source:` (run + commit) and
  the three edge markers. Do **not** change its existing structure otherwise.
- `templates/hooks.example.json` — one worked hook, and only one: run the docs
  gate before `git commit`, `PreToolUse` on `Bash` with
  `"if": "Bash(git commit *)"`. Include the `exit 2` contract in a comment field
  (`"_note"`), and a second `_note` stating that the file goes in the project's
  `.claude/settings.json` and that hooks do not exist outside Claude Code.

**Step 3 — negative self-tests.** Two steps: delete `templates/docmap.md`; and
strip the `Checked by` header from a copy. Both must make `validate.py` exit
non-zero.

**DoD.** `npm test` green; both negative steps proven; every template's tables have
a header row and at least one non-placeholder example.

**Commit**

```
feat(templates): doc map, decision register, open questions, hook example
```

---

## T4 — `references/gates.md` (new built-in doctrine)

**Scene.** `audit.md` already says a class seen twice *"belongs in a script — the
host's lint, its CI, its check runner"* and stops. This file is the *how*: what a
gate is, where it runs, how it is written so it cannot lie, how it is proven, and
what you must know **before** you run one. It is the answer to the user-facing
question "как соблюдать гейты и как создавать гейт".

**Owns:** `references/gates.md` (new).

> **Boundary, and it is binding — spec §2.1.1.** `audit.md` and `learned.md`
> already own probes, ratchets, exit codes, false positives and seeds-green **as
> law**. This file owns the **procedure** and links to them in one line each. Write
> the commands, the placement rules and the recipes; do **not** re-argue why a
> probe is needed. A second statement of one law is the exact defect this release
> ports a rule against.

**Step 1.** The guard is already in place from T2 (`"gates.md"` in the doctrine
list). Confirm `npm test` fails with
`missing built-in stage doctrine: references/gates.md`.

**Step 2 — write the file.** Sections, in order:

| # | Heading | Must contain |
|---|---|---|
| 1 | `# Gates — the two axes, and how to build one that cannot lie` | one-job line |
| 2 | `## Axis A — the stage gate type` | `auto` / `manual` from `pipeline.schema.json`; an auto gate never substitutes for a required manual approval; who decides which is which (the operator) |
| 3 | `## Axis B — the enforcement mechanism` | the five-rung promotion ladder of spec §3.9 as a table, with the promotion trigger per rung; the rule that a rule may sit on several rungs but **must not pretend** to be on a higher one |
| 4 | `## Before you run a check` | four preconditions: the base is green (or its known-red baseline is recorded); the check has been probed; you have read its **scope header** and know what it does not cover; the ratchet floors are read so a "pass" is not a floor that was quietly raised |
| 5 | `## Anatomy of a project gate` | the property table of spec §3.6: exit code is output · verdict printed last, **no check after it** · portability (bash 3.2, no `grep -P`/`sed -i`/`readarray`) · ratchet floor variables · **skips are printed, never silent** · a scope header · seeds green. Each property names the incident: the gate that printed `FAIL` and exited `0` with CI green over it for an unknown period; the scaffold whose gate failed on its own seeds |
| 6 | `## Writing the check itself` | compute, never restate; check both directions of any two-layer mapping (the direction that feels redundant is the one that finds things); prefer a deterministic rule to a heuristic; scope the unit (a table **row**, a paragraph) and say what that costs |
| 7 | `## Probing — plant, run, restore` | the exact loop with commands; assert on **`$?`**, not on a `FAIL` line; **doubt the probe first** (four of five probe failures on the source project were the probe, not the check); record the probe log |
| 8 | `## The false-positive budget` | measure over the real corpus **before** shipping; a parity check that produced six false positives out of six was discarded for a deterministic rule; a gate that cries wolf is removed by the third person who hits it |
| 9 | `## Ratchets` | a named, counted set that may only shrink, printed beside the verdict; floor variables; raising a floor is a decision; a ratchet nobody prints is a TODO with a better name |
| 10 | `## Where a gate runs` | table: **local pre-commit** (fast, skippable, the author's), **CI** (authoritative, holds for people who never run it locally), **hook** (agent-time, blocks the edit — link `hooks.md`), **stage gate** (the pipeline's own, `auto`/`manual`). Cost and limit per row |
| 11 | `## Adding a check to an existing gate` | the six-step recipe: name the class → find the unit → write the deterministic predicate → measure false positives → plant/restore → wire the count into the verdict line |
| 12 | `## Rationalizations` | ≥ 7 rows |

**Step 3.** Negative self-test: delete `references/gates.md` from a copy, assert
non-zero.

**DoD.** ≥1500 bytes, twelve sections, `npm test` green, negative step proven,
linked from `SKILL.md` (one line, see T2's interim-red note).

**Commit**

```
docs(doctrine): gates — the two axes, the anatomy, the probe, the ratchet
```

---

## T5 — `references/hooks.md` (new built-in doctrine)

**Scene.** The pipeline has never mentioned hooks. A hook is the only mechanism
that can stop a bad edit *before* it happens, and it is also the one whose failure
mode is silent: any exit code other than `2` is non-blocking, so **a crashing guard
fails open** and the project believes it is protected.

**Owns:** `references/hooks.md` (new).

**Step 2 — write the file.** Sections:

| # | Heading | Must contain |
|---|---|---|
| 1 | `# Hooks — agent-time enforcement, and the limit first` | **the limit before the capability**: hooks exist only in Claude Code; on other agents the same rules run as a self-check and the run is recorded **`ungated`**; never describe a project as protected when its agents run elsewhere |
| 2 | `## The events` | `SessionStart` (matcher `startup\|resume`) · `PreToolUse` · `PostToolUse` · `SessionEnd`. One line each on what it is for |
| 3 | `## The PreToolUse contract` | block by **exit 2 with the reason on stderr** (stdout ignored), or **exit 0 with the deny JSON** — show both, the JSON exactly. Then the sentence that matters: *any other exit code is non-blocking, so write the guard to exit 2 on its own internal errors or it silently stops guarding* |
| 4 | `## What the hook receives` | the stdin payload fields: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `tool_name`, `tool_input`, `tool_use_id` |
| 5 | `## Where it lives` | project `.claude/settings.json` vs a plugin's `hooks/hooks.json` with `${CLAUDE_PLUGIN_ROOT}`; **a globally installed plugin must exit 0 immediately when the project has no config for it**, or installing it changes every other project |
| 6 | `## Matchers` | tool-name matchers (`Edit\|Write\|MultiEdit\|NotebookEdit`), `"*"`, and the `if` form for a specific Bash command (`Bash(git commit *)`) |
| 7 | `## Performance` | a `PostToolUse` hook on `*` runs after **every** call — it must be a no-op in the common case; throttle with a timestamp file; if it becomes slow, fix the throttle, never remove the hook |
| 8 | `## What belongs in a hook, and what does not` | hook = cheap, deterministic, about an **edit an agent is making now**. Not in a hook: the full test suite, anything needing the network on every call, anything whose answer needs a human. Cross-reference `gates.md` rung 5 (as a real relative link, once that file exists) |
| 9 | `## Debugging` | the symptom→cause table (guarded edits go through → the guard crashed; everything denied → no config or no lease; session start slow → backend unreachable, must time out and degrade), and the one-liner that runs the guard by hand with a sample payload |
| 10 | `## Removing them` | delete the block; everything still available as a command; the board records `ungated` from then on |
| 11 | `## Leases are not reimplemented here` | `agent-sync` owns guarded registers and leases; this skill ships doctrine and one example. Two implementations of one lease will disagree, and the disagreement is invisible |
| 12 | `## Rationalizations` | ≥ 5 rows |

**Worked example** in §3 and §5 must match `templates/hooks.example.json` exactly —
they are the same file in two places, so state that and keep them in sync.

**Step 3.** Negative self-test as in T4.

**DoD.** ≥1500 bytes; the deny-JSON block is valid JSON; `npm test` green.

**Commit**

```
docs(doctrine): hooks — the contract, the fail-open hazard, the portability limit
```

---

## T6 — the learning loop: retro with commits, an archive, and a bounded read

**Scene.** The retro already exists and is well-shaped; three things are wrong with
it. `SKILL.md` says the *file* is read in full while `knowledge-sources.md` says the
*standing instructions* are — and the file also holds an unbounded Log, so the two
readings differ by an unbounded amount (spec §6 F1). Evidence is `file:line`, which
rots at the next edit. And nothing carries a commit, so a lesson cannot be traced
back to the change that earned it.

**Owns:** `references/retrospective.md`, `templates/retro.md`,
`templates/retro-archive.md` (new).

**Step 1 — the guards.** In `test/validate.py`, inside the existing `retro = open(...)`
block, add after the `"Retire when"` check:

```python
    # A lesson without the commit that earned it is a lesson nobody can reopen:
    # file:line evidence rots at the next edit, a SHA carries the diff, the
    # message and the parent forever. `git show <sha>` reconstructs the incident.
    for _col in ("Commit", "Fired at"):
        if _col not in retro:
            fail(f"templates/retro.md: the standing-instruction table must carry a "
                 f"'{_col}' column — evidence that survives a rename is a commit, "
                 "not a line number")
    if not os.path.isfile(os.path.join(tpl_dir, "retro-archive.md")):
        fail("missing template: templates/retro-archive.md — the in-force file is "
             "capped and read in full, so the history needs a home that is queried "
             "instead of read")
```

And a drift guard beside the autonomy-sweep one (same failure class — one file is
what the agent reads, the other what it writes):

```python
    # retrospective.md defines the standing-instruction columns; templates/retro.md
    # is where they get written. A column in one and not the other is a field that
    # is either never asked for or never recorded.
    _retro_doc = os.path.join(refdir, "retrospective.md")
    if os.path.isfile(_retro_doc):
        _rd = open(_retro_doc, encoding="utf-8").read()
        for _col in ("Commit", "Fired at", "Retire when"):
            if (_col in _rd) != (_col in retro):
                fail(f"retro column {_col!r} appears in only one of "
                     "references/retrospective.md and templates/retro.md")
```

`npm test` → expect three failures (`Commit`, `Fired at`, missing archive).

**Step 2 — content.**

*`templates/retro.md`* — replace the standing table header with the eight columns of
spec §3.10 and update the example row; add a `Commit` column to *Run stamps*; retitle
the log section `## Recent log — entries from the last five run stamps` and add one
line under it: older entries move to `docs/superpowers/retro/YYYY-QN.md` at the
prune, and *moving is not deleting*.

*`templates/retro-archive.md`* — new: a header naming the quarter, the note that the
file is **append-only and queried, never read in full**, one worked entry with every
required field including `Commit`, and one worked retirement line
(`### 2026-05-04 · retired R-000 — became a check (\`npm run lint:paths\`) · a1b2c3d`).

*`references/retrospective.md`* — four edits:

1. In the artifact table, split the row into the two artefacts of spec §3.10 and
   state exactly what stage 0 reads in full (**standing instructions + run stamps +
   the recent-log window**) and what it *queries* (the archive).
2. New section `## Every lesson carries its commit` — the required-fields table
   gains `Commit`; the paragraph explaining why a SHA and not a `file:line`; the
   rule that **every SHA in either file must resolve** and that the docs gate
   checks it (`git rev-parse --verify --quiet <sha>^{commit}`), which is learned
   rule 14 applied to history.
3. New section `## Rotation — the archive is how pruning stops losing things` —
   at the prune, entries older than the last five stamps move to the quarter file;
   the archive is append-only; a retirement writes its line **there** with its
   trigger and its commit; resurrection of a retired rule is a grade-1 fix *with its
   history attached*.
4. In `## The loop closes at stage 0`, add that the archive is **queried by the
   task's nouns** during the harvest — it is a source like any other, and it is the
   one that answers *"have we been bitten by this before?"*.

**Step 3.** Negative self-tests: strip the `Commit` column from a copy of
`templates/retro.md`; delete `templates/retro-archive.md`. Both must fail.

**DoD.** `npm test` green; three negative steps proven; no remaining sentence
anywhere in the file claiming the whole retro file is read in full.

**Commit**

```
feat(retro): commits as evidence, an archive for the pruned, a bounded read
```

---

## T7 — `templates/docgate.sh` — the portable gate skeleton

**Scene.** This is the artefact that makes the practice reproducible instead of
described. It is seeded to `scripts/check-docs.sh` in the host project and extended
there. It must exit `0` on a project seeded from T3's templates — a gate that seeds
red teaches everyone on day one that it is noise.

**Owns:** `templates/docgate.sh`.

**Step 1 — the guards.** In `test/validate.py`, after the templates block:

```python
    # The gate travels to macOS (bash 3.2) and to whatever CI the host runs. The
    # three constructs below are the ones that fail silently rather than loudly:
    # `sed -i` needs an argument on BSD and `0,/re/` does not exist there at all.
    gate = os.path.join(tpl_dir, "docgate.sh")
    if not os.path.isfile(gate):
        fail("missing template: templates/docgate.sh (the seeded docs gate)")
    else:
        _g = open(gate, encoding="utf-8").read()
        for _bad, _why in ((r"grep\s+-[a-zA-Z]*P", "grep -P is not on macOS"),
                           (r"\bsed\s+-i\b", "sed -i is not portable"),
                           (r"\breadarray\b", "readarray is bash 4+")):
            if re.search(_bad, _g):
                fail(f"templates/docgate.sh: uses a non-portable construct ({_why})")
        if "SCOPE" not in _g:
            fail("templates/docgate.sh: no SCOPE header — a gate quoted as evidence "
                 "must state what it does not cover")
        _tail = _g[_g.rfind("\n# ---------- "):] if "\n# ---------- " in _g else ""
        if "exit" not in _g.split("VERDICT")[-1]:
            fail("templates/docgate.sh: nothing exits after the verdict block — the "
                 "exit code is part of the output, and a gate that prints FAIL and "
                 "exits 0 has been shipped before")
```

**Step 2 — write the script.** Structure:

```bash
#!/usr/bin/env bash
# check-docs.sh — the documentation gate for <project>.
# Seeded by task-pipeline (references/gates.md). Extend it here; it is yours now.
#
# SCOPE: this gate checks the umbrella's own markdown ... and does NOT check <...>.
# Portable to macOS bash 3.2: no grep -P, no sed -i, no readarray.
set -u
FAIL=0
# ---------- ratchet floors — raising one is a decision, lowering is free ----------
PROP_ENFORCE_FROM=${PROP_ENFORCE_FROM:-1}
...
```

Then the ten sections of spec §3.6, each as `# ---------- N. <name> ----------`,
each printing either `ok: <name>` or `ERR: <detail>` and setting `FAIL=1`, each
printing `skip: <name> — <why>` when it cannot run. Finally:

```bash
# ---------- VERDICT — nothing may run after this block ----------
if [ "$FAIL" -ne 0 ]; then echo "FAIL: documentation gate"; exit 1; fi
echo "OK: documentation gate — propagation backlog: $PROP_BACKLOG (floor $PROP_ENFORCE_FROM) · unmarked residue: $RESIDUE"
exit 0
```

Implementation notes that are contracts, not suggestions:

- **Sections 1–4 and 8–9 are fully implemented** and project-agnostic (links, id
  definition, next-free-id, counts, status vocabulary, commit-SHA resolution).
- **Sections 5–7 and 10 ship implemented against the seeded template shapes** and
  carry a one-line comment naming what a host project must adjust.
- **Progressive arming (spec §1.2 D1).** A section whose input artefact does not
  exist yet prints `dormant: <name> — no <artefact> yet` and **does not set
  `FAIL`**. Dormant is visible so it is not forgotten and green so day one is not
  red; it arms by itself when the artefact appears. This is what makes
  always-governed survivable on a three-file repository, so it is a contract, not a
  convenience — implement it as one helper (`dormant_if_absent <name> <path>`) used
  by every section that has an input.
- **The register size is printed on every run** (`3 decisions · 0 open questions`),
  so an empty register reads as *checked and empty* rather than *never set up*.
- Section 9 resolves every `` `[0-9a-f]{7,40}` `` token that appears in
  `docs/superpowers/retro*` via `git rev-parse --verify --quiet "$sha^{commit}"`,
  and **skips with a printed reason** when the repo has no git dir.
- Every section's error message names the file **and** the line.

**Step 3 — prove it seeds green, then prove each section can fail.** This is V9 and
it is the only executed guard in the repo. Add to `test/validate.py`:

```python
# A generator seeds green (references/learned.md, rule 9). A scaffold whose own
# gate rejects its own templates teaches every new project that the gate is noise.
import subprocess, tempfile
_seed = tempfile.mkdtemp()
os.makedirs(os.path.join(_seed, "docs/superpowers"), exist_ok=True)
os.makedirs(os.path.join(_seed, "scripts"), exist_ok=True)
for _src, _dst in (("docmap.md", "docs/DOCMAP.md"),
                   ("decisions.md", "docs/DECISIONS.md"),
                   ("open-questions.md", "docs/OPEN_QUESTIONS.md"),
                   ("retro.md", "docs/superpowers/retro.md")):
    _p = os.path.join(tpl_dir, _src)
    if os.path.isfile(_p):
        open(os.path.join(_seed, _dst), "w", encoding="utf-8").write(
            open(_p, encoding="utf-8").read())
_gate_dst = os.path.join(_seed, "scripts/check-docs.sh")
if os.path.isfile(gate):
    open(_gate_dst, "w", encoding="utf-8").write(open(gate, encoding="utf-8").read())
    _r = subprocess.run(["bash", "scripts/check-docs.sh"], cwd=_seed,
                        capture_output=True, text=True)
    if _r.returncode != 0:
        fail("templates/docgate.sh seeds RED on a freshly seeded project "
             f"(exit {_r.returncode}): {_r.stdout.strip()[-400:]} {_r.stderr.strip()[-200:]}")
shutil.rmtree(_seed, ignore_errors=True)
```

(add `import shutil` at the top if absent).

Then the **probe log**: for each of the ten sections, plant a defect in the scratch
seed, run the gate, assert non-zero, restore, assert zero. Record the ten results in
the commit body. **If a probe does not make the gate fail, doubt the probe first** —
prove your edit landed in the text the section actually parses.

**DoD.** `npm test` green including the seed-green execution; the ten-line probe log
is in the commit body; the script has no non-portable construct.

**Commit**

```
feat(templates): docgate.sh — a portable documentation gate that seeds green
```

---

## T8 — wire the track into the three mechanically-compared surfaces

**Scene.** `SKILL.md`'s table, `references/stages.md` and `pipeline.example.json`
are compared by the validator on ids, names and gate types, and three other guards
check that a concept named in `SKILL.md`'s close-out also appears in
`acceptance.md`, `stages.md` and the config. **No stage id, name, order or gate type
changes in this task** — only gate *prose* and doctrine links.

**Owns:** `SKILL.md`, `references/stages.md`, `pipeline.example.json`.

**Step 1 — `SKILL.md`.**

1. Built-in doctrine table (the one starting `| Stage | Built-in doctrine |`): add
   three rows —
   `| 0 + 9 + any decision · The documentation system | references/documentation.md |`,
   `| 6–10 + any check you write · Gates | references/gates.md |`,
   `| any agent-time enforcement · Hooks | references/hooks.md |`.
2. New paragraph after *"Three artifacts close a run, not two"*, titled
   **"Documentation is a deliverable, and it has a gate."** State: the inventory at
   stage 0, the Doc Loop at any stage, the propagation sweep at stage 9, and that
   *"docs in sync"* is now an artefact and a command rather than an assertion.
3. In *How to run* step 5 (the cross-cutting bullet list), add: **when anything is
   settled — scope, contract, name, policy — run the Doc Loop
   (`references/documentation.md`) before the run moves on; a decision that lives
   only in the spec dies with it.**
4. Stage-table gate cells for 0, 9 and 10: append the clauses of spec §4.
5. `## References` list: three new lines, in the same style as the rest.
6. Fix F1 while here: the phrase *"`docs/superpowers/retro.md`, read in full"*
   becomes *"the retro's standing instructions, run stamps and recent log — read in
   full; the archive is queried"*.
7. Fix F2 while here: *"Every stage's doctrine ships inside this skill"* becomes
   *"Every stage's **doctrine** ships inside this skill; stages 1 and 6–9 additionally
   run the host's own commands and optional tools, and **no stage blocks on an
   install** (stage 1 falls back to web search; the wiki and the graph are
   recommendations)."*

**Step 2 — `references/stages.md`.**

- Stage 0: a new bullet **Phase 1b — the documentation inventory** (what it
  answers, that it writes/reads `docs/DOCMAP.md`, that the regime is `governed`,
  that an existing `docs/adr/` is the register and is never duplicated) and **Phase
  1c — reconcile intent against as-built**. Extend the `**GATE (manual)**` line
  with spec §4.1.
- Stage 9: replace *"docs in sync with code"* in the `**GATE (auto)**` line with
  spec §4.2's clauses; add a bullet *The propagation sweep* above the existing
  ledger bullet, explaining the difference in one sentence — **the ledger names
  what you read, the matrix names what you owe**.
- Stage 10: extend the `**GATE (manual)**` line with spec §4.3.
- New cross-cutting section at the end, beside *the loop guard* and *the audit*:
  `## Cross-cutting — the Doc Loop`, three bullets (it fires at any stage; its
  seven steps live in `documentation.md`; the commit is step 7 and the run is not
  done before it).
- Add the carry-over print to the stage 6, 7 and 9 gate lines (F8): *"the
  carry-over count is printed beside this verdict"*.

**Step 3 — `pipeline.example.json`.**

- stage `intake`: append to `gate.check` — the doc inventory, the doc map, the
  regime, the reconcile, the retro read/query split. Add `task-pipeline:documentation`
  to `skills[]`.
- stage `docs-wiki`: append the §4.2 clauses; add `task-pipeline:documentation` and
  `task-pipeline:gates` to `skills[]`; keep the existing ledger and graph text.
- stage `acceptance`: append the §4.3 clauses (docs gate probed, ratchets printed,
  retro prune→stamp→entry→rotation with commits).
- **Do not touch** any `id`, `state`, `name`, `model` or `gate.type`.

**Step 4 — extend the anchor guard (V10).** In `test/validate.py`, the loop over
`(("submodule", …), ("ladder", …), ("retro", …))` gains two entries:

```python
        ("propagation", "the stage-9 propagation sweep"),
        ("doc map", "the stage-0 documentation inventory"),
```

and its per-surface list gains `references/documentation.md`. Run `npm test`;
**expect it to fail** until steps 1–3 have put both anchors on every surface. That
failure is the guard doing its job.

**DoD.** `npm test` green; `python3 -c "import json;json.load(open('plugins/task-pipeline/skills/task-pipeline/pipeline.example.json'))"`
exits `0`; the stage-id/name/gate-type comparison still passes (it will, since none
changed); two new negative steps (strip `propagation` from `stages.md`; strip
`doc map` from the config) proven.

**Commit**

```
feat(stages): the documentation track binds at 0, 9 and 10
```

---

## T9 — the remaining references and the brief

**Scene.** These are the edits that make the track *reachable from where an agent
actually is*, plus five pre-existing defects from spec §6 that live in the same
files.

**Owns:** `references/knowledge-sources.md`, `references/conventions.md`,
`references/companion-skills.md`, `references/audit.md`, `references/learned.md`,
`references/grill.md`, `templates/brief.md`, `references/artifacts.md`,
`templates/README.md`.

**`knowledge-sources.md`**

- Source table: add row `| 4a | **The decision register** | \`docs/DECISIONS.md\` or \`docs/adr/\` (the doc map says which) | what has already been settled, and what it superseded |`
  and row `| 7a | **The retro archive** | \`docs/superpowers/retro/\` | have we been bitten by this class before? — **queried**, never read in full |`.
- Under *Rules for the list*, add: **the register is read for the task's nouns and
  for anything the design will contradict** — a run that contradicts an accepted
  decision without superseding it is the failure the register exists to prevent.
- F5: in *Precedence when two sources disagree*, split the rule in two —
  *for what **is**: code, then host docs and ADRs, then the wiki, then memory.
  For what **should be**: the register outranks the code, because a decision not yet
  built is still the decision, and the gap between them is a finding rather than a
  tie-break.*
- In *Close the loop*, add the register and the doc map as rows stage 9 updates.

**`conventions.md`** (F7) — new section `## Documentation regime` between *Docs +
wiki* and *Issue tracker*: how to detect the host's register (`docs/DECISIONS.md`,
`docs/adr/`, a doc map, a section in `AGENTS.md`), where the gate command is named,
what to do when there is none (**seed it — spec D1**), and the rule that the
project's own `CLAUDE.md`/`AGENTS.md` wins over anything detected.

**`companion-skills.md`** (F9) — add to the matrix:
`| **agent-sync** (\`/agent-sync\`) | guarded registers, id reservation, lease, \`finish\` | **Recommended** — never a gate; absent → the run is \`ungated\` and says so | \`npx sshlg-skills install\` |`,
and a preflight line in the block in the same style as the wiki and the graph. Also
add the three built-in doctrine rows to the *Built in* table.

**`audit.md`** (F4) — in *§1 A class that repeats twice becomes a gate*, add one
sentence with the link: *how to write, place, probe and own that check is
`gates.md` (write it as a real relative link in `audit.md`, where it resolves);
"put it in a script" without a place to put it is how the
third instance ends up in the ledger too.* In the ladder table, L1's artefact
becomes *"the locked decision — a register entry, an ADR or a `CONTEXT.md` term"*.

**`learned.md`** (F6) — **the incident is already narrated** at line 121, in *the
one instruction that would have prevented the most* ("a coordination plugin
reporting a lease held by an identity that belonged to a different session"). Do
**not** repeat that narration. Add the missing table row and one incident paragraph
that *cross-references* it, because the file's own preamble says a rule belongs in
the table once it has a check — and this one does. Add rule 15 to the table:

```
| 15 | **Identity before coordination** | any lease, lock, claim or run id | ask what two instances with the same identity would do | two instances demonstrably get two identities |
```

and its incident paragraph: a coordination plugin derived one run id **per
checkout**; a hook has the session id in its environment and a plain shell command
does not, so the second session in a checkout adopted the first one's identity — a
full day of work was performed holding another session's leases, and the
end-of-work check offered to release *theirs*. It was invisible from inside:
`whoami` reported a lease and a run id, both plausible, both somebody else's. Add
the follow-on in one line: do not infer identity from strings the environment is
also free to contain (matching `"claude"` in a process command line matched the
throwaway shell of every tool call). Extend *Where these bind*: a row
`| 0 Inventory · 9 Docs · any register write | 8, 14, 15 |`.

**`grill.md`** — autonomy-sweep table: add a row **between** the `0 Harvest` and
`1 Docs` rows:

```
| 0 Docs regime | where decisions live (register or ADR set — never both), who may write it, the gate command and its ratchet floors, and whether this run may raise a floor |
```

Add a short subsection `### The documentation regime` after *The design
destination*, stating that a project with no register gets one seeded (D1) and that
the seeding is recorded as the first decision in it.

**`templates/brief.md`** — the same row, same position, in the `## Autonomy` table
(the validator compares the **stage numbers** the two tables cover, so both must
carry a `0`-prefixed row — they already do; keep the wording aligned anyway). Add a
new section `## Documentation` after `## Knowledge sources` with four filled lines:
regime · register + id scheme · doc map path · gate command(s) and ratchet floors.

**`artifacts.md`** — add to the host-project tree: `docs/DOCMAP.md`,
`docs/DECISIONS.md`, `docs/OPEN_QUESTIONS.md`, `docs/superpowers/retro/YYYY-QN.md`,
`scripts/check-docs.sh`; and to the stage→artifact map: stage 0 writes/reads the doc
map, stage 9 writes the registers, stage 10 rotates the archive.

**`templates/README.md`** (F10) — list every template, seeded target and stage.

**Guard for F10.** In `test/validate.py`:

```python
    # A template that ships and is not listed is a template nobody seeds.
    _readme = open(os.path.join(tpl_dir, "README.md"), encoding="utf-8").read()
    for _t in sorted(os.listdir(tpl_dir)):
        if _t in ("README.md",) or _t.startswith("."):
            continue
        if _t not in _readme:
            fail(f"templates/README.md does not list {_t!r} — an unlisted template "
                 "is one nobody knows to seed")
```

**DoD.** `npm test` green; the F10 guard proven by a negative step that adds a
stray template file to a copy; every `references/*.md` still reachable from
`SKILL.md`; no relative link broken.

**Commit**

```
docs: wire the doc track into harvest, conventions, companions, audit and the brief
```

---

## T10 — the Cursor channel, and the validator's own honesty pass

**Scene.** `cursor/rules/task-pipeline.mdc` is copied into foreign projects, so it
must be **self-contained** — restate, never link. It is also the surface most likely
to be forgotten, which is why it has its own task.

**Owns:** `cursor/rules/task-pipeline.mdc`, `test/negatives.py`,
`.github/workflows/validate.yml` (final pass).

**Steps**

1. Add to the Cursor rule, in its own voice and with **no relative links**: the doc
   inventory at stage 0, the Doc Loop's seven steps in one compact list, the
   propagation sweep at stage 9, the gate's exit-code rule, and the hook's
   Claude-Code-only limit.
2. `test/negatives.py`: raise `MIN_EXPECTED` from `20` to the new count of steps in
   the workflow. **Do not guess** — run `python3 test/negatives.py --list`, count,
   set the number.
3. Run `npm run test:all`. Then run it once more with one negative step deliberately
   broken (point it at a file that does not exist) and confirm the runner reports it
   rather than passing quietly — the runner's own probe.

**DoD.** `npm run test:all` green; `--list` shows every new step; the Cursor rule
has zero `](./` or `](../` occurrences.

**Commit**

```
docs(cursor): the doc track, self-contained for foreign projects
```

---

## T11 — release: README, CHANGELOG, four-way version bump

**Owns:** `README.md`, `CHANGELOG.md`, `package.json`,
`.claude-plugin/marketplace.json`, `plugins/task-pipeline/.claude-plugin/plugin.json`,
`CLAUDE.md`, `CONTRIBUTING.md`.

**Steps**

1. `README.md`: two new sections after *The audit ladder* —
   **"Documentation is a deliverable"** (the inventory, the map, the loop, the
   sweep, the gate; a short before/after of what *"docs in sync"* now means) and
   **"Gates and hooks"** (the two axes, the promotion ladder, the seeded gate, the
   fail-open warning). Extend *The retrospective* with the commit/archive change.
   Add the new files to *Documentation map*.
2. `CHANGELOG.md`: a new `## v1.7.0` section written as **what changed and why it
   mattered**, including the probe log summary from T7 (ten sections, ten planted
   defects, ten non-zero exits) and the ten §6 findings with their disposition.
3. Bump the version to `1.7.0` in all four manifests.
4. `CLAUDE.md` → *Invariants*: note that the doc track adds a seeded-gate execution
   guard, so `npm test` now runs bash. `CONTRIBUTING.md` → *The invariants*: add
   invariant 10 — **a seeded template must keep the seeded gate green** — and fix
   **F11** in invariant 6, which currently claims the shipped config names no
   external provider while it names eleven. Reword it to the rule the validator
   actually enforces: *no external provider may **substitute for built-in stage
   doctrine** (stages 2, 3-spec, 4, 5, 6, 10); the optional tools (`context7`,
   `wiki-query`/`wiki-update`, `graphify`, `figma`) and the UI-required `super-ux:*`
   track are named deliberately and are the enumerated exceptions.*
5. `npm run test:all`.
6. Verify every human-facing blurb still names the final stage last (the validator
   does this; read its output rather than assuming).

**DoD.** `npm run test:all` green; four manifests and the CHANGELOG heading all read
`1.7.0`; README's *Documentation map* lists `documentation.md`, `gates.md`,
`hooks.md` and the five new templates.

**Commit**

```
feat: the documentation track, gate doctrine and a traceable retro; v1.7.0
```

---

## T12 — the closing audit of the skill itself (the "challenge" pass)

**Scene.** The operator asked that nothing be forgotten, missed or half-done. This
task runs the skill's **own** ladder walk (`references/audit.md`) against the skill,
which is the only pass that can find what was never written.

**Steps**

1. **Bottom-up ladder, one rung at a time**, treating each spec §3 contract as a
   REQ: L0 the contract → L1 the doctrine that states it → L2 the surface that
   enforces it (`stages.md` / config / validator) → L5 the file in the tree → L6 the
   guard **and its negative test, executed** → L7 the README/Cursor surface a user
   reads. Order findings **by seam**, not by file.
2. Run the two counts of `audit.md` (new findings vs findings caused by this
   change's own edits) and record them.
3. For every §6 finding F1–F10, state `verified` (with the commit) / `partial`
   (with what is missing and where it is tracked) / `deferred` (with a home).
4. Write `docs/superpowers/specs/2026-08-03-documentation-track-acceptance.md`:
   one row per spec contract and per finding, each with **evidence** — a guard name,
   a command and its output, or a `file:line`. *"Done"* without evidence is
   downgraded to `partial`, never upgraded.
5. Run the retro on this run itself: prune → stamp (with this run's commit) →
   entry only if the run diverged. It is the first run of the new format, so the
   commit columns must be filled, not left as placeholders.

**DoD.** The acceptance file exists; every contract has a status and none is
`unknown`; both audit counts are printed; the retro is written in the new shape with
resolvable SHAs; `npm run test:all` green on the final commit.

**Commit**

```
docs(acceptance): REQ coverage and the ladder walk for v1.7.0
```

---

## T13 — ship it: PR, merge, tag, release

**Authorized by the operator on 2026-08-03** for this repository and this release:
commit, push, tag, publish. Follow `CONTRIBUTING.md` → *Releasing* exactly; it is
the documented procedure and it is short.

1. `npm run test:all` on the final commit — green, output recorded.
2. Push the branch; open a PR with the template filled in (what changed, which
   surfaces, validator output); merge it into `main`. The branch route is the
   repo's own policy for anything touching gates or a public contract.
3. `git tag v1.7.0 && git push origin v1.7.0`. `RELEASE_ENABLED=true` re-runs the
   validator against the tag, checks the tag against all four manifests, cuts the
   GitHub release from the CHANGELOG section and smoke-tests `npx` from a clean
   checkout; the second job publishes to npm under `PUBLISH_NPMJS=true`.
4. **Watch the run, do not assume it.** `gh run watch`, then verify from outside:
   `npm view task-pipeline-skill version` must print `1.7.0`.

**DoD.** Tag pushed; both workflow jobs green; `npm view` reports `1.7.0`; the
GitHub release exists with the CHANGELOG body.

---

## T14 — the release reaches the catalogue

**Scene.** `sshlg-skills` pins every family member's version in its own
`skills.json`. A release that does not bump that pin is **invisible**: `list` keeps
reporting the old number, `update` keeps installing it, and anyone comparing their
install against `list` is told the wrong number with nothing to reveal it. This
happened before and is documented in `CONTRIBUTING.md`. The checkout is at
`/Users/sshlg/DATA/sshlg-skills`.

1. Bump this member's `version` in `skills.json` to `1.7.0`.
2. Bump the launcher's own version + changelog, commit, tag, `npm publish --access public`.
3. Verify from outside: `npx --yes sshlg-skills@latest list` prints `1.7.0` for
   `task-pipeline`.

**DoD.** `list` reports the new number. Until it does, the release is not finished.

---

## T15 — refresh the local installs

The operator's standing rule: a released skill's local copies are updated in the
same run, not on request.

```bash
claude plugin marketplace update task-pipeline && claude plugin update task-pipeline@task-pipeline && npx --yes skills update task-pipeline --global --yes
```

Then tell the operator to restart Claude Code — skills load at session start, so
the session that updates is never the session that gets it.

**DoD.** All three commands green; the restart is stated, not assumed.

---

## Human steps (the only one)

**Restarting Claude Code** after T15. Everything else in this plan is autonomous
under the authorization recorded in T13.
