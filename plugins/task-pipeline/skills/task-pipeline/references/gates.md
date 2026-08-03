# Gates — the two axes, and how to build one that cannot lie

**One job: turn a rule into something that can say no.** [`audit.md`](audit.md)
says a class seen twice *belongs in a script*; this file is where that script comes
from — how it is written, where it runs, how it is armed, how it is proven, and
what you must know **before** you quote its green as evidence.

**Boundary, so this file does not become a second source.** The *law* lives
elsewhere and is not restated here:

| The law | Lives in | This file adds |
|---|---|---|
| A check must be watched failing before it is trusted | [`audit.md`](audit.md) *Exit criterion*, [`learned.md`](learned.md) 4–5 | the executable recipe |
| Ratchet, never TODO | [`audit.md`](audit.md) §3, [`learned.md`](learned.md) 7 | floor variables, and where the count is printed |
| A gate's exit code is part of its output | [`learned.md`](learned.md) 11 | where the verdict block goes |
| A checker with false positives is worse than none | [`learned.md`](learned.md) 10 | how to measure before shipping |
| A generator seeds green | [`learned.md`](learned.md) 9 | progressive arming |
| A class that repeats twice becomes a gate | [`audit.md`](audit.md) §1 | the six-step recipe |

---

## Contents

- Axis A — the stage gate type
- Axis B — the enforcement mechanism
- Axis C — degrees of freedom
- Progressive arming
- Before you run a check
- Anatomy of a project gate
- Writing the check itself
- Probing — plant, run, restore
- The false-positive budget
- Ratchets
- Where a gate runs
- Adding a check to an existing gate
- Rationalizations

## Axis A — the stage gate type

From [`../pipeline.schema.json`](../pipeline.schema.json), one per stage:

| Type | Meaning | Failure to respect it |
|---|---|---|
| `auto` | the orchestrator verifies the `check` itself, pass/fail, and stops on fail | advancing on an unverified check |
| `manual` | wait for the operator's **explicit** go | treating an auto verification as the approval |

**An auto gate never substitutes for a required manual approval.** A green table is
not the operator confirming it is what they asked for, and no amount of checking
makes it one. Which stages are manual is the **operator's** decision, recorded in
their `pipeline.json`; the framework fixes no stage count and no gate assignment.

## Axis B — the enforcement mechanism

Where a rule actually lives. A rule climbs this ladder; it does not start at the top.

| Rung | Mechanism | Costs | Promote when |
|---|---|---|---|
| 1 | **Doctrine line** in a reference file | reading attention | it was violated once |
| 2 | **Review question** at a named gate | a person's time, every run | no check can decide it — and say *why*, in one line |
| 3 | **Script check** in the project's gate | writing it once | the class has occurred **twice** |
| 4 | **CI step** | minutes per push | it must hold for people who never run it locally |
| 5 | **Hook** ([`hooks.md`](hooks.md)) | latency on every tool call | the failure is cheaper to prevent than to detect, and the target is an edit an agent is making now |

A rule may sit on several rungs. What it may never do is **pretend** to be on a
higher one: a doctrine line that reads as if it were enforced is the same failure as
a gate that prints `FAIL` and exits `0` — both report a world they are not looking
at.

**Rung 2 is where honesty is bought.** "No check can decide this" is a legitimate,
common answer. Written down with its reason, it is a finding somebody can later
disprove. Left unwritten, it is indistinguishable from an omission.

---

## Axis C — degrees of freedom

Axis B says how hard a rule bites. This one says how much latitude the *instruction*
leaves, and it is a separate choice: a low-freedom instruction guarded by nothing is
a wish, and a high-freedom instruction behind a blocking hook is a bottleneck.

Match the level to how **fragile** the step is, not to how important it feels:

| Level | Shape | Use when | Example here |
|---|---|---|---|
| **high** | prose direction, no prescribed sequence | many routes reach a good answer and context decides | stage 2 — the design conversation |
| **medium** | a named order with room inside each step | the sequence is fixed, the content is judgement | stage 0 — two phases, adaptive questions |
| **low** | run exactly this, in this order, no variation | the operation is fragile, irreversible, or must be identical every time | stage 5's TDD order · stage 7's deploy · stage 9's matrix walk |

The picture worth keeping is an **open field versus a narrow bridge**. In the field,
say where to go and let the agent find the route. On the bridge there is one safe way
across, and the guardrails are the instruction.

**Over-constraining costs as much as under-constraining and is harder to see.** A
high-freedom step written as low freedom produces an agent that follows the letter
past the point where the letter stopped fitting — and reports success, because it did
what it was told. Where a step is genuinely open, say so out loud; that sentence is
what stops the next reader from hardening it.

Every stage in [`stages.md`](stages.md) declares its level and its reason, on the
line under its heading.

## Progressive arming

A gate seeded into a young project has almost nothing to check yet, and a gate that
starts red teaches everyone on day one that it is noise ([`learned.md`](learned.md)
rule 9). So each section reports one of four states and only one of them fails:

| State | Means | Fails? |
|---|---|---|
| `ok` | the check ran and passed | no |
| `dormant: … — no <artefact> yet` | the input does not exist yet | no |
| `skip: … — <why>` | the input exists, the check could not run here | no |
| `ERR` | the check ran and found something | **yes** |

`dormant` and `skip` are **printed, never silent** — that is the whole reason they do
not quietly become permanent.

They also force one more obligation on the verdict line: it must report **what the
run actually looked at**. Every section dormant is indistinguishable from a gate
blind to the shape in front of it, and exit 0 alone cannot tell those two apart.

## Before you run a check

Four preconditions. Skipping any of them turns a run into a claim.

1. **The base is green** — or its known-red baseline is *recorded*. A new guard
   added to an already-red base passes for the wrong reason and proves nothing.
2. **The check has been probed.** Green from a check nobody has watched fail is
   worth nothing. If you did not plant the defect, you do not know what the green
   means.
3. **You have read its scope header** and know what it does **not** cover. A gate
   is evidence for exactly the surface it walks; quoting it beyond that is how
   "the gate is green" becomes a false statement made in good faith.
4. **You have read the ratchet floors.** A pass with a floor that was quietly
   raised is a pass over the thing the floor was hiding.

---

## Anatomy of a project gate

Ten properties. Each one is here because its absence has shipped.

| Property | Rule | The failure it prevents |
|---|---|---|
| **Exit code** | non-zero on **any** failure | a gate that appended a check *after* its verdict block printed `FAIL` and returned `0`; CI was green over it for an unknown period |
| **Verdict last** | nothing may run after the verdict block | the same failure, from the other end |
| **Scope header** | states what the gate does **not** cover | a green quoted as proof of a surface nobody walked |
| **Portability** | POSIX + bash 3.2: no `grep -P`, no `sed -i`, no `readarray` | BSD `sed -i` needs an argument GNU refuses, and `0,/re/` does not exist there — it silently edits nothing and the check reads as a guard that failed to fire |
| **Ratchet floors** | `<NAME>_FLOOR` variables at the top; counts printed beside `OK` | a backlog that grows back without anyone explaining why |
| **Skips are printed** | a check that could not run says so | a submodule not checked out silently removing coverage |
| **Progressive arming** | a section with no input artefact prints `dormant: … — no <artefact> yet` and does **not** fail | a freshly seeded project starting red, which teaches everyone on day one that the gate is noise |
| **Computed, never restated** | derive every count at check time | two documents quoting a total that went stale |
| **Both directions** | any two-layer mapping is checked each way | four fully-specified entities with no schema anywhere — found only by the direction that felt redundant |
| **Named location** | every error prints file **and** line | a finding nobody can act on |

Shape:

```bash
#!/usr/bin/env bash
# check-docs.sh — the documentation gate for <project>.
# SCOPE: walks <what>. Does NOT check <what>.
# Portable to macOS bash 3.2: no grep -P, no sed -i, no readarray.
set -u
FAIL=0
PROP_FLOOR=${PROP_FLOOR:-1}          # ratchet: raising it is a decision

# ---------- 1. <name> ----------
...                                   # ok: / ERR: / skip: / dormant:

# ---------- VERDICT — nothing runs after this block ----------
if [ "$FAIL" -ne 0 ]; then echo "FAIL: <gate>"; exit 1; fi
echo "OK: <gate> — backlog: $BACKLOG (floor $PROP_FLOOR) · registers: $DECS decisions · $OQS open"
exit 0
```

---

## Writing the check itself

- **Pick the unit and say what it costs.** A check that scopes to a table *row*
  will let one marker in that row exempt everything else in it. That is a real
  blind spot; measured and accepted beats unmeasured and denied, so write it in the
  comment.
- **Prefer a deterministic rule to a heuristic.** A parity-based check for
  unbalanced markup produced six false positives out of six on a real corpus and
  was discarded. If the rule cannot be stated exactly, that is information.
- **Never infer from strings the environment also produces.** Matching `"claude"`
  in a process command line matched the throwaway shell of every tool call.
- **Compute the count you print.** A number restated in prose is a number that will
  be wrong; derive it from the source at check time so the two cannot disagree.

---

## Probing — plant, run, restore

The law is [`audit.md`](audit.md)'s exit criterion. The procedure is this, and it is
not optional for a check you intend to trust:

```bash
cp -R . /tmp/probe && cd /tmp/probe
python3 - <<'PY'                       # plant IN PYTHON, never sed -i
p = "docs/DECISIONS.md"
s = open(p).read().replace("DEC-0001", "DEC-9999", 1)
open(p, "w").write(s)
PY
bash scripts/check-docs.sh; echo "planted -> exit=$?"   # MUST be non-zero
cd - && bash scripts/check-docs.sh; echo "clean -> exit=$?"  # MUST be 0
```

**Assert on `$?`, not on a `FAIL` line in the output.** A line on stdout is a
decoration; the exit code is what CI reads.

**Doubt the probe before you doubt the check.** On the project this comes from,
**four of five** silent probes were the probe's fault: one added a *definition*
where the check looks for an unresolved *reference*; one edited a string whose
whitespace did not match; one hit the first prose mention instead of the table row;
one flipped a row whose cell was already empty, so nothing was planted. A silent
check is a claim about two things, and the probe is the one to doubt first — prove
your edit landed in the text the check actually parses.

**Record the probe.** One line per section, in the change that ships the check.
Otherwise the next reader has to redo it to know whether it was ever done.

---

## The false-positive budget

Run a new heuristic over the **real corpus** before shipping it and count the false
positives. Zero, or replace the heuristic with a deterministic rule.

The budget is not perfectionism. A gate that cries wolf is switched off by the
third person who hits it, and after that it protects nothing while still appearing
in the pipeline as a control. A noisy check is worse than no check, because it also
consumes the credibility of the checks beside it.

---

## Ratchets

A **ratchet** is a named, counted set that may only shrink, printed on every run.

- Its floor is a **variable at the top of the script**, so raising it is a visible
  edit and a decision.
- Its count is printed **beside the verdict**, so `PASS` never reads as *verified*
  — it reads as *"green, and here is exactly what was not looked at"*.
- A ratchet that grew needs a sentence in the run log saying why.

```
GATE 9 docs: PASS — propagation backlog: 121 (was 162) · unmarked residue: 0
```

A ratchet nobody prints is a TODO with a better name.

---

## Where a gate runs

| Place | Good at | Limit |
|---|---|---|
| **Local pre-commit** | fast feedback for the author | skippable, and skipped exactly when someone is in a hurry |
| **CI** | authoritative; holds for people who never run it locally | minutes late, and it checks out the repo in a shape the author's machine never has — rehearse that shape |
| **Hook** ([`hooks.md`](hooks.md)) | stops the edit *before* it happens | Claude Code only; a crashing hook **fails open** |
| **Stage gate** (this pipeline) | judgement, and the things only a person can answer | it is the run's own memory, not the repository's |

The four are not alternatives. The same rule can be a hook for the agent, a
pre-commit for the human and a CI step for the record — what it must never be is
*declared* in one place and *enforced* in none.

---

## Adding a check to an existing gate

1. **Name the class** — the shape, not the instance. "This id is undefined" is an
   instance; "an id referenced and never defined" is a class.
2. **Find the unit** the check will parse: a line, a table row, a paragraph, a
   file. Write down what that unit will miss.
3. **Write the predicate deterministically**, with the file and line in the error.
4. **Measure it** over the real corpus; zero false positives or rewrite it.
5. **Plant, run, restore** — both directions observed, and recorded.
6. **Wire its count into the verdict line**, with a floor if it cannot be zero yet.

Step 6 is the one that gets skipped, and it is the one that makes the check
survive: a number beside `OK` is read every run, and a check nobody sees the output
of is deleted in the next refactor by someone who assumed it was dead.

---

## Rationalizations

| Excuse | Reality |
|---|---|
| "The check is green, that's evidence" | Only if you have seen it red. An unproven check is a decoration that reports success. |
| "It printed FAIL, so it failed" | CI reads `$?`. A gate has shipped that printed `FAIL` and exited `0`, and nobody noticed for an unknown number of runs. |
| "I'll write the check later, the rule is documented" | Then it is on rung 1 and behaves like rung 3 in everyone's head. That gap is the whole failure. |
| "It's one occurrence, a note is enough" | It is. On the second, the note becomes a script — that is the rule, and the third occurrence is proof it was ignored. |
| "The heuristic mostly works" | Measure it. Six false positives out of six on a real corpus is what "mostly" felt like from inside. |
| "The gate would be red on day one, so I'll add it later" | Make the section dormant instead. Dormant is visible and green; "later" is neither. |
| "I raised the floor to get the build green" | Then say so in the log, in the same commit. A floor raised silently is a ratchet running backwards. |
| "A hook is overkill, CI catches it" | CI catches it after the edit, the commit and the push. If the point is to stop the edit, CI is the wrong rung — and if it is not, do not pay the latency. |
