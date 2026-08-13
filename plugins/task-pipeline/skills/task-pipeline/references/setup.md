# Setup — the entry audit, before the first feature

**One job: find out what is already wrong with this project's documentation before
building on top of it.** [`audit.md`](audit.md)'s ladder runs at the *end* of a run,
over the change. This runs at the *start*, over what is already there — and until
this file existed, nothing did.

**Offered, never imposed.** Stage 0 asks once, when `docs/DOCMAP.md` is absent or its
regime line is older than the project's last release. The answer — including "no" —
is recorded in the brief's autonomy sweep and never asked again.

## Contents

- When it runs
- First it says where the paperwork lives
- What it inspects
- The finding shape
- The output is a fix plan, not a lecture
- The inward check — what this project holds that belongs upstream
- The offer to install the routing rule
- Rationalizations

## When it runs

| Situation | What happens |
|---|---|
| First run in a repository, no `docs/DOCMAP.md` | [`adoption.md`](adoption.md) seeds; this audit runs against what the seeding found |
| Existing project, doc map present but stale | offered once at stage 0 |
| The operator asks for it — `/task-pipeline setup` | runs as the whole task; stages 3–5 produce findings and fixes rather than a feature |
| Every subsequent run | **not offered again.** The recorded answer stands until the doc map changes |

**Never as a recurring tax.** A check that runs before every feature is a check people
learn to dismiss. Once per project state, then it is the gate's job.

## First it says where the paperwork lives

Before any pass, one line naming **the resolved artifact root and why it resolved that
way** ([`artifacts.md`](artifacts.md) → *the root is resolved, not spelled*). Not a
finding — orientation, and the answer to the only question a rename can leave behind:

```
artifacts: docs/superpowers/   (legacy name, resolved because the directory exists and
                                carries a register — the default is now docs/evidence/,
                                and moving is optional: npx task-pipeline
                                migrate-artifacts --dry-run)
artifacts: docs/evidence/      (default)
artifacts: docs/runs/          (configured — pipeline.json → paths.artifacts)
artifacts: docs/evidence/      (default, and the directory already exists without a
                                register — STOP AND ASK before writing into it)
```

A project on the legacy name is **not behind and is never warned about it on a run**;
this line exists so nobody has to guess which of the two directories a gate will read.
Where records sit in both, the leftover is named here too — a partial migration is a
state somebody chose, not a fault.

## What it inspects

Seven passes, cheapest first. Each either reports `ok`, a finding, or **`skipped —
<why>`**; a silent pass is indistinguishable from a clean one.

1. **The decision home.** Exactly one, and the doc map names it. Two homes is a fork;
   zero is a project whose decisions live only in commit messages.
2. **Register integrity.** Ids unique and never renumbered · status vocabulary closed
   · supersede/contradict targets annotated · no resolved question deleted.
3. **Propagation.** Every document named in an entry's `Consequences / affects:` line
   cites that entry — ratcheted, so history is a printed number and not a wall of
   failures ([`adoption.md`](adoption.md) → *Baseline the ratchets*).
4. **The matrix.** It contains the **meta-row** — *a new document or rule* — without
   which it cannot catch the change type the project makes most often. Every row has
   a *Checked by* cell — a check, or `review` **with the
   reason no check can decide it**. An empty cell is a finding, not a blank.
5. **Terms.** Every term the doc map declares resolves to exactly one definition, and
   the definition's home actually contains it. **Only declared terms are checked** —
   a heuristic over every capitalised word cries wolf, and a gate that cries wolf is
   removed by the third person who hits it ([`gates.md`](gates.md) → *The
   false-positive budget*).
6. **The UX chain**, when the project has a user-facing surface: scenarios exist,
   trace to stories and flows, and the linter passes. A project with screens and no
   scenarios is building interface before behaviour.
7. **The gate itself.** It exists, it runs, it exits non-zero on a planted defect, and
   its verdict prints its ratchets. **An unproven gate's green is worth nothing** —
   plant one defect and watch it fail before quoting it as evidence.

## The finding shape

Every finding carries three things and nothing else:

```
docs/ARCHITECTURE.md:214  cites DEC-0081 (retired, superseded twice) without saying so
   → add the marker beside the citation, or replace it with the live decision
   seam: L1→L2 (the decision reached the doc and then stopped being true)
```

`file:line` · the minimal fix · the seam it belongs to. **Ordered by seam, never by
file** — a file-ordered list reads as noise; a seam-ordered one tells you which layer
of the project's own process is leaking.

## The output is a fix plan, not a lecture

The audit ends with `<artifacts>/plans/YYYY-MM-DD-doc-audit.md` — the findings
turned into tasks the pipeline can run, in the order that makes them terminate:

1. everything the gate can enforce **after** the fix, so the class stops recurring;
2. the ratchet floors, baselined at today;
3. the rest, largest seam first.

An audit that hands over a list and no plan is a list somebody will read once.

**Nothing is fixed during the audit.** Reading and repairing in one pass is how a
pass starts finding its own edits ([`audit.md`](audit.md) → *Every pass changes the axis, not the effort*).

## The inward check — what this project holds that belongs upstream

The other direction, and the one nobody runs by themselves
([`portability.md`](portability.md) → *The two checks*).

Read the host's `CLAUDE.md`/`AGENTS.md`, its doc map and its standing instructions,
and ask of each rule: **would this be true in a repository I have never seen?**

- **Names a path, a command, a person, a service** → it is this project's answer.
  Leave it.
- **Names none of those** → it is a workflow decision wearing a project's clothes.
  Report it, and propose it upstream to the bundle rather than copying it by hand
  into the next project.

That hand-copy is the fork: performed once per project, until two of them disagree and
neither is wrong.

## The offer to install the routing rule

If the operator's configuration carries no routing rule, offer to append
[`../templates/routing-rule.md`](../templates/routing-rule.md) — the version that
travels with the bundle.

**Offer, never write.** It is the operator's configuration, and appending to it
without asking is the same class of act as pushing to a repository nobody asked you
to touch. Print the diff, ask once, record the answer.

## Rationalizations

| Excuse | Reality |
|---|---|
| "The docs are fine, we'd know" | You would know about the contradictions. Absences have one side, and nobody notices a decision that was never written. |
| "Let's audit after we ship this feature" | Then the feature is built on the part that was wrong, and the audit's first finding is the feature. |
| "This will take a week" | Seven passes, most of them mechanical, and the ratchet step means you fix nothing today. What takes a week is the fix plan — and that is work you were going to do blind otherwise. |
| "We'll fix things as we find them" | Then the pass starts finding its own edits and never terminates. Read, then plan, then fix. |
| "The gate is green, so the docs are good" | The gate proves what it checks. Read its scope header, and plant a defect before quoting its green. |
| "Our conventions are ours, upstream doesn't need them" | Some of them are, and the inward check leaves those alone. The ones naming no path and no command are the pipeline's, and keeping them local costs you every future project. |
