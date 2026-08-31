# Adoption — bringing a project onto the pipeline

**One job: get a repository to the state where stage 0 has something true to read.**
The pipeline assumes a documentation system exists or gets seeded
([`documentation.md`](documentation.md)). This file is what to do on the first run in
a project — and the two entry conditions are not the same problem.

## Contents

- Two entry conditions
- A new project — the seed is the whole of it
- An existing project — the register starts today
- Why history is not back-filled
- What good looks like the day after
- Rationalizations

## Two entry conditions

| | Greenfield | Brownfield |
|---|---|---|
| What exists | nothing, or a README | code, history, opinions, and docs that are partly true |
| The hard part | none — seeding is mechanical | **the decisions already exist and none of them are written down** |
| Failure if done wrong | a register nobody starts using | a gate that is red on day one, switched off on day two |
| First run's deliverable | the feature, with the system seeded on the way | **the system itself** — adoption is its own run |

**On a brownfield project, adoption is a run, not a preamble.** Give it a brief, a
REQ table and an acceptance, exactly like a feature. A doc system introduced as a
side effect of somebody else's task is a doc system with no owner.

## A new project — the seed is the whole of it

Stage 0 phase 1b already does it before the first interview question. Nothing to
prepare:

```
docs/DOCMAP.md          the map: registers, single homes, propagation matrix, gates, ratchets
docs/DECISIONS.md       the register — DEC-####, append-only
docs/OPEN_QUESTIONS.md  OQ-####, closed status vocabulary
scripts/check-docs.sh   the gate, ten sections
```

Three things are true on day one and worth knowing:

- **The gate is green immediately.** Sections whose input does not exist yet print
  `dormant`, which is visible and passing ([`gates.md`](gates.md) → *Progressive
  arming*). The skill proves this mechanically: its own validator seeds a scratch
  project from these templates and requires exit `0`.
- **Both floors are `0`,** because there is no history to forgive.
- **The register's first entry is the decision to document this way.** A register
  that starts with a real entry is a register somebody has already used once.

Then run the task. There is no separate adoption step.

## An existing project — the register starts today

Seven steps. Step 3 is the one that decides whether adoption survives contact with
the repository.

### Step 1 · Inventory — what is already here

Answer the four questions of [`documentation.md`](documentation.md) against reality,
not against the templates:

```bash
ls docs/DECISIONS.md docs/adr/ docs/OPEN_QUESTIONS.md docs/DOCMAP.md 2>/dev/null
ls scripts/check-docs.sh .github/workflows/ 2>/dev/null
grep -rl "ADR\|decision record\|DEC-" docs/ README.md CONTRIBUTING.md 2>/dev/null | head
```

**One decision home, and you are looking for the one that already exists.** A
populated `docs/adr/` *is* the register — record it in the doc map and use it. Never
seed a second one beside it; that is the fork the SSOT rule exists to prevent.

A project whose decisions live in a CHANGELOG with reasons, or in commit messages
nobody will migrate, has a decision home too. Write down which it is. The choice
being *unrecorded* is the defect, not the choice.

### Step 2 · Seed what is missing

Usually the map and the gate; often the register already exists in some shape.

```bash
cp <skill>/templates/docmap.md         docs/DOCMAP.md               # only if absent
cp <skill>/templates/docgate.sh        scripts/check-docs.sh        # only if absent
cp <skill>/templates/exposure.sh       scripts/exposure.sh          # only if absent
cp <skill>/templates/hygiene.sh        scripts/check-hygiene.sh     # only if absent
cp <skill>/templates/stage-coverage.sh scripts/stage-coverage.sh    # only if absent
cp <skill>/templates/convergence.sh    scripts/check-convergence.sh # only if absent, and only where the project pins components
chmod +x scripts/check-docs.sh scripts/exposure.sh scripts/check-hygiene.sh \
         scripts/stage-coverage.sh scripts/check-convergence.sh
```

The last three are the scripts the later gates run — stage 5 runs
`check-hygiene.sh` after every task, stage 10 runs `stage-coverage.sh` before the
coverage table and `check-convergence.sh` where components are pinned
([`../templates/README.md`](../templates/README.md) is the full seeding map). A
fresh host that skips them reaches gates whose commands do not resolve, which
reads as a broken gate rather than a skipped seeding.

**Seeding never overwrites.** An existing brief, register or map is the project's
memory; the template is a skeleton.

### Step 3 · Baseline the ratchets — the step that decides adoption

Run the gate **before** deciding anything, and read what it actually says:

```bash
bash scripts/check-docs.sh; echo "exit=$?"
```

On a repository with history this is red, often loudly — the practice this skill
comes from measured **162 missing propagations across 73 decisions** on its first
run. That number is not a to-do list. Fixing it blind would add 162 citations nobody
verified, and failing on it every day makes the gate something people switch off,
which costs more than the rows it would have caught.

So set the floors to **today**, and only ever lower them:

```bash
# PROP_FLOOR is an ID THRESHOLD: entries numbered >= it must have propagated.
# Set it to the next free id — from now on the rule binds, and the history
# becomes one printed number.
PROP_FLOOR=$(grep -o 'Next free ID:\**\s*`\?DEC-[0-9]*' docs/DECISIONS.md \
             | grep -o '[0-9]*$' | sed 's/^0*//')

# RESIDUE_FLOOR is a COUNT: unmarked citations of retired decisions, as measured
# right now.
RESIDUE_FLOOR=$(bash scripts/check-docs.sh 2>&1 \
                | grep -o 'residue [0-9]*' | grep -o '[0-9]*' | head -1)
```

Write both into the top of `scripts/check-docs.sh` and into `docs/DOCMAP.md` →
*Ratchets*, with the date. Re-run; the gate is now **green on today's state** and
red only on what happens next.

**Why this is not cheating.** A ratchet is a named, counted set that may only shrink,
printed beside every verdict ([`audit.md`](audit.md) → *What can't be fixed now
becomes a ratchet, never a TODO*). The backlog stays visible on every single run —
it just stops blocking work it was never going to fix today. A gate that starts red
teaches everyone on day one that it is noise
(`references/learned.md` rules 9 and 10).

### Step 4 · Build the propagation matrix

Not from the template — from what this project actually has. The five steps are in
[`documentation.md`](documentation.md) → *The propagation matrix*. Start with three
rows you can name today; a matrix with three true rows beats one with twenty
imported ones.

The third column is not optional: name the check that would notice, or write
`review` **with the one-line reason no check can decide it**.

### Step 5 · Record the adoption itself

The first entry in the register is the decision to adopt — regime, decision home,
where the map lives, what the floors were set to and on what date. It costs two
minutes and it is the cheapest possible demonstration that the register works, to
the next person who wonders whether anyone actually uses it.

### Step 6 · Arm the gate

Local first, then the one that binds people who never run it locally:

```bash
echo 'bash scripts/check-docs.sh' >> .git/hooks/pre-commit   # local, skippable
# CI: add the same line to the workflow that already runs the tests
```

Optionally at agent time, which is the only rung that can stop a bad edit *before*
it lands — `templates/hooks.example.json`, and read
[`hooks.md`](hooks.md) first for the fail-open hazard.

### Step 7 · Several agents — add the leases

Only when more than one agent works the repository. Then the registers become shared
state ([`documentation.md`](documentation.md) → *Registers are shared state*) and a
coordination tool arbitrates: `guardedFiles` must list every register **plus
`docs/DOCMAP.md` and `<artifacts>/retro.md`**, which are equally shared and
equally lossy under a concurrent write.

Without such a tool the run is **`ungated`** and must say so. The discipline still
applies; only the arbitration is missing.

## Why history is not back-filled

The decisions already exist — in the git log, in the code, in somebody's memory. The
temptation is to reconstruct them into the register so it looks complete.

Don't. A reconstructed decision carries a *guess* about why it was made, in a
register whose whole value is that entries are true. One invented rationale is worse
than a hundred absent ones, because absent ones are visibly absent and an invented
one is indistinguishable from a real one forever.

**The rule: an old decision enters the register the day somebody is about to
contradict it.** At that moment the reason is being discussed anyway, the person
holding the context is in the room, and the entry writes itself honestly — with the
new decision beside it.

## What good looks like the day after

- `bash scripts/check-docs.sh` exits `0`, prints its ratchet counts, and says which
  sections were `dormant` or `skipped`.
- `docs/DOCMAP.md` answers the four questions, and its propagation matrix has no
  empty *Checked by* cell.
- The register has at least one entry: the adoption.
- The gate runs in CI, not only on the adopter's laptop.
- The next task runs through the pipeline normally, and stage 9 has a matrix to walk
  instead of a sentence to interpret.

Anything not true yet is a carry-over row with a home, not a promise.

## Rationalizations

| Excuse | Reality |
|---|---|
| "We'll adopt it properly when things calm down" | The backlog only grows, and the floors you would set today are the smallest numbers you will ever get to set. |
| "The gate is red, this clearly doesn't fit our repo" | The gate is red because it is measuring history nobody promised to fix. That is what step 3 is for, and it takes one command. |
| "Let's back-fill the last two years of decisions first" | Then the register's first hundred entries are guesses, and nobody can tell them from the real ones. Start today; back-fill exactly one entry at the moment it is contradicted. |
| "We already have ADRs, so we need to migrate to DECISIONS.md" | You do not. An existing ADR set *is* the register. Migrating is its own decision with its own entry — never a side effect of adopting. |
| "We'll set the floors to zero, it's more honest" | It is more honest for about a day, after which the gate is disabled and you have neither the floor nor the check. A printed backlog is the honest thing that survives. |
| "The matrix needs to be complete before it's useful" | Three true rows catch three real classes. Twenty imported rows catch nothing and teach everyone that the matrix is decoration. |
| "One agent works here, so leases are overkill" | Correct — skip step 7 and say so. Adopting coordination nobody needs is how a project learns to route around the parts it does need. |
