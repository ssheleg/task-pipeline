# Design — artifact hygiene: the defects an agent leaves behind

**Run:** `artifact-hygiene` · 2026-08-05 · brief:
`docs/superpowers/specs/2026-08-05-artifact-hygiene-brief.md`

`templates/hygiene.sh` — a shipped, seeded, executable gate, sibling of
`templates/docgate.sh`, that finds the defect class an agent produces and no
existing check looks for.

**Every definition below was measured on this repository before it was written
down.** Two of the six were wrong on the first attempt and the measurement is what
said so — which is the rule `gates.md` states and the reason this section exists.

## Contents

- Global constraints
- What measurement changed
- The six checks — exact definitions
- The two modes
- Contract 1 — the script
- Contract 2 — the two repository fixes
- Contract 3 — doctrine wiring
- Contract 4 — guards and negative tests
- Contract 5 — propagation and version
- What this design deliberately does not do
- Verification
- Self-review

## Global constraints

Stages 4 and 5 consume this block verbatim.

- **macOS bash 3.2.** No `grep -P`, no `sed -i`, no `readarray`, no `mapfile`,
  no `${var,,}`. Verified on this host: `bash 3.2.57`. `grep -P` happens to work
  here and is still forbidden — it is absent on stock macOS `grep` in other setups,
  and `docgate.sh`'s own header bans it.
- **Portable set:** `grep -E`, `grep -c`, `grep -n`, `grep -l`, `awk`, `sed`
  (no `-i`), `while read`, `[ ]`, `case`.
- **Corrupt fixtures in Python, never `sed -i`** — the validator rejects it.
- Prose wraps at ~80 columns; a wrapped line never begins with `>`.
- **`npm test` must stay green after every task.**
- **R-001:** when a plant does not turn a check red, prove the plant landed in the
  text the check parses before touching the check.
- **R-002:** if any edit in a batch errors, re-verify **every** edit in that batch.
- No hardcoded vendor model ids anywhere.

## What measurement changed

| Check | First definition | Measured | Corrected definition |
|---|---|---|---|
| 2 placeholders | the word `TODO`/`TBD`/`FIXME`/`XXX` anywhere | **33 hits, 28 of them legitimate prose** — this is a doctrine repository whose own rule is *"a ratchet, never a TODO"*, so the word appears in ordinary sentences. Quoting/backticking catches only 5 of 33 | a **line-leading marker**, not a word. → **0 hits** |
| 6 empty section | a heading followed by any heading | **62 hits, all legitimate** — `# Changelog` → `## v1.11.0` is normal nesting | a heading followed by one of the **same or higher** level. → 4 hits |
| 6 empty section | *(second attempt)* | **the detector itself had a bug**: fenced lines were skipped entirely, so a section whose whole body is a code block looked empty | **fenced content counts as body.** → **2 hits**, both real findings |
| 1, 3, 4, 5 | as first written | 0, 0, 0, 0 on 94 files | unchanged |

The check-6 sequence is the point of the rule: a detector nobody measured would
have shipped flagging 62 legitimate headings, and the version that flagged only 4
still had a bug that measurement — not review — exposed.

## The six checks — exact definitions

Every check reports `file:line: <what>` and increments `FAIL`. None edits anything.

**1 — conflict markers.** A line matching `^(<<<<<<< |=======$|>>>>>>> )`.
False-positive surface: a document *about* merge conflicts. Named in `SCOPE`.
Measured: 0.

**2 — surviving placeholder.** A line matching
`^[[:space:]]*([#/*<!-]+[[:space:]]*)*(TODO|TBD|FIXME|XXX)\b`, i.e. the token as a
**line-leading marker**, optionally behind a comment introducer (`#`, `//`, `/*`,
`<!--`, `-`). **The word in mid-sentence prose is not a finding** — that distinction
is the whole check, and this repository is its worst case. Measured: 0.

**3 — unterminated code fence.** A markdown file whose count of lines matching
`^[[:space:]]*```` ``` ```` is odd. False-positive surface: a fence deliberately
shown unclosed as an example. Measured: 0.

**4 — truncation stub.** A line matching
`(\.\.\. existing code|\[TRUNC|rest of (the )?file unchanged|unchanged\.\.\.)`.
Measured: 0.

**5 — duplicated adjacent block (the R-002 mechanisation).** Two consecutive blocks
of **3 or more** non-blank lines, separated by blank lines, that are byte-identical.
Three lines is the floor because two-line repeats occur legitimately (table rows,
list pairs). Measured: 0 across `.md`, `.py`, `.sh`, `.json`, `.js`.

**6 — empty section.** A heading of level *N* followed, with **no body of any kind
between them — including fenced content**, by a heading of level ≤ *N*. Measured
after the fence fix: 2, both real (see contract 2).

## The two modes

| Mode | Trigger | Tolerance |
|---|---|---|
| **diff** | `HYGIENE_BASE` set, or a git repo with an upstream — scans `git diff --name-only $BASE...HEAD` plus unstaged changes | **zero.** Any finding fails. This run wrote it; this run fixes it |
| **tree** | default when no base resolves | **ratchet floor** per check, `HYGIENE_FLOOR_<N>`, default 0. A count at or below its floor prints and passes; above it fails. A floor may only fall |

Both modes print their counts in the VERDICT line, so a green never reads as "there
was nothing".

**Progressive arming**, exactly as `docgate.sh` does it: a check whose input does not
exist (no markdown files, no git repository for diff mode) prints
`dormant: <check> — no <input>` and does **not** fail.

## Contract 1 — the script

`plugins/task-pipeline/skills/task-pipeline/templates/hygiene.sh`, seeded into a host
project beside `docgate.sh`. It carries every contract the validator already enforces
on its sibling:

- a `SCOPE:` header naming what it does **not** check — prose meaning, code
  correctness, style, spelling, another repository, and **the false-positive surface
  of each of the six**;
- `EXIT CODE IS THE OUTPUT`; the **VERDICT block is last and nothing runs after it**;
- the bash-3.2 portability note;
- progressive arming, stated in the header;
- env-overridable inputs: `HYGIENE_BASE`, `HYGIENE_FLOOR_1`…`HYGIENE_FLOOR_6`,
  `HYGIENE_EXCLUDE` (default `graphify-out/`);
- a final line of **computed** numbers, one per check;
- the same ownership sentence: *"Seeded by task-pipeline. IT IS YOURS NOW: extend it
  here, section by section. Each section is independent and removable."*

## Contract 2 — the two repository fixes

Check 6's two findings are fixed rather than absorbed into a floor, so the shipped
floor is **0** for all six.

- **`evals/RESULTS.md`** — `## Runs` has no body. Add one line saying what the
  section holds. A real, if mild, instance of the defect.
- **`plugins/task-pipeline/skills/task-pipeline/templates/retro.md`** — the
  retirement record `### 2026-05-04 · retired R-000 — became a check …` is a heading
  with no body, **and that is the template's own design**: a retirement is one line.
  The fix is structural, not cosmetic: **a one-line record is a list item, not a
  heading.** A heading promises a section. Convert it to a bullet under a
  `### Retirements` heading that has a body.

The second one is why check 6 earns its place: it found a shape mistake in a shipped
template that every project using this skill copies.

## Contract 3 — doctrine wiring

- **`references/build.md`** — the stage-5 task loop runs the gate in **diff mode
  after each implementer reports `DONE`, before the review**. A finding is a
  `DONE_WITH_CONCERNS` at best: fixed in the same task, or carried over explicitly.
  **The script never edits; the agent fixes.** That obligation is the doctrine half
  and no check can decide it.
- **`references/stages.md`** — §5, §6 and §9 gate criteria name the gate and its
  printed counts.
- **`references/gates.md`** — the gate is added as a worked example of the probe
  recipe and the ratchet floor, beside the documentation gate.
- **`references/artifacts.md`** — `templates/hygiene.sh` added to the layout.
- **`templates/README.md`** — the new seeded file described, with the warning that it
  is the host's to extend.

## Contract 4 — guards and negative tests

- `test/validate.py`: the template guards that today cover `docgate.sh` — presence,
  `SCOPE:` header, VERDICT-last, portability constructs — are extended to cover
  `hygiene.sh` **by iterating over a list of gate scripts** rather than by copying the
  block. A copied guard is a guard that drifts.
- `npm test` **executes** `hygiene.sh` over the same seeded scratch project it already
  builds for `docgate.sh`, and requires exit 0.
- `.github/workflows/validate.yml`: **one negative self-test per check** — six — each
  planting that check's defect into a scratch copy and requiring rejection, plus one
  for the VERDICT-last contract on the new file. Seven new steps.
- `test/negatives.py`: `MIN_EXPECTED` recomputed from the workflow by counting
  `- name: Negative self-test` steps. Do not restate a number from this document.

## Contract 5 — propagation and version

Four-way sync to **1.12.0**. `CHANGELOG.md` records what changed and why it mattered,
including that two of the six definitions were wrong before measurement. Plus
`README.md`, `CONTRIBUTING.md` → *The invariants* (one row per new guard concept),
`references/portability.md` manifest, `references/artifacts.md`,
`templates/README.md`, and `cursor/rules/task-pipeline.mdc` — marked **`review`** by
the propagation matrix because it changes how an agent behaves in a foreign project.

## What this design deliberately does not do

- **Does not auto-fix.** None of the six is safely machine-fixable.
- **Does not lint style, format or spelling.** Those have owners.
- **Does not modify `docgate.sh`.** Its `SCOPE` excludes code; this one needs code.
- **Does not scan `graphify-out/`** — generated, git-ignored, not authored.
- **Does not add a seventh check speculatively.** Six are measured; a seventh would
  be guessed.

## Verification

| REQ | Verified by |
|---|---|
| REQ-001 | the extended template guards, probed by removing the `SCOPE:` header from a copy |
| REQ-002…REQ-007 | one negative self-test per check, each plant proven to land before its exit code is read (R-001) |
| REQ-008 | the VERDICT line prints per-check counts and the active floors; both modes exercised in the scratch run |
| REQ-009 | cross-surface stage guard + `review` for the prose |
| REQ-010 | **`review`** — no check can decide whether an agent acted on a finding. Stated plainly rather than implied |
| REQ-011 | `npm test` executes the gate over the scratch project and requires exit 0 |
| REQ-012 | `npm run test:all` green; `MIN_EXPECTED` recomputed from the workflow |
| REQ-013 | `npm test` reach, manifest and citation guards; the Cursor rule is `review` |
| REQ-014 | the four-way version guard |

## Self-review

- **REQ coverage:** 14 in the brief, 14 covered by a contract above, difference ∅.
- **Named checks:** 9 named in *Verification*; 7 are mechanical and named to a real
  guard or workflow step; **2 are marked `review` on purpose** (REQ-010, and the
  Cursor rule inside REQ-013) — neither is asserted as mechanical.
- **Decisions:** checked against the brief's D1–D5. No contradiction. D5 said "six
  checks, additions free" and this spec adds none.
- **Cost:** 1 new script, 7 new workflow steps, 1 guard extended (not copied), 2
  repository fixes, 7 propagation surfaces. At stage 0 the estimate was "a sibling
  script plus propagation" — grown by the two repository fixes, which measurement
  found and which are three lines each. **Proportionate.**
- **Placeholders:** 0. **Ambiguity:** 1 found and resolved inline — "duplicated
  block" now names its 3-line floor and its blank-line separator rule.
- **Definitions measured before being written:** 6 of 6; 2 corrected by the
  measurement.
