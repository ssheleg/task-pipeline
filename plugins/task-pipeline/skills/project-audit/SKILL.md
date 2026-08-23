---
name: project-audit
description: "Use when someone asks what is actually true of a whole project right now — what is finished, what is half-built, what is broken, and what nobody has looked at. Walks a cold start: discover what the project is, run a registry of probes chosen from that, read production evidence (published artefact against source, CI history, telemetry present or absent), then leave a self-contained HTML report and a JSON sidecar so the next audit can say what moved. Read-only: it proposes board rows and commits nothing. Triggers - 'project audit', 'audit the project', 'codebase audit', 'state of the project', 'what is unfinished', 'project health check', 'аудит проекта', 'проаудируй проект', 'состояние проекта', 'что не доделано', 'аудит кодовой базы'. Not for: auditing one deliverable inside a run (that is the pipeline's own ladder), reviewing a diff, or checking a skill's construction — say 'без диагностики' to opt out."
---

# Project audit — what is true of this project right now

**A gate asks whether an artifact is good. Acceptance asks whether anything on
the list was lost. Neither asks what the project actually is today**, and that
is the only question an operator has when they open a repository they have not
touched for a month.

This skill answers it from a cold start — no brief, no REQ table, no module map
required — and leaves two artefacts: a page a person reads, and a sidecar the
next audit reads.

## Contents

- What this is not
- The six phases
- Three verdicts, and why the third one exists
- The class that version checks cannot see
- The two artefacts
- What the script does and what you do
- Exit criterion
- Rationalizations

## What this is not

| | Owns | Reach for it when |
|---|---|---|
| [`references/audit.md`](../task-pipeline/references/audit.md) | the **method** — the L0→L7 ladder, seams, axis rotation | one deliverable is being walked inside a run |
| this skill | the **procedure** — cold start, probes, production, the report | a whole project is the subject |
| `/skill-audit` (make-skill) | a skill's construction against the standard | the thing audited is a skill or plugin |
| `/ux-audit` (super-ux) | code against documented scenarios | the question is user-facing behaviour |

**The method is not restated here.** Phase 4 below hands off to `audit.md` and
comes back; a second copy of the ladder would be a second rule, and the two
would disagree within a release.

## The six phases

Run them in order. Each writes into the same payload the report is rendered
from.

### 1. Discover — what this project IS, before anything is measured

`scripts/audit.py` answers this mechanically: languages, package managers,
monorepo shape, submodules, CI, deploy targets, declared telemetry, and the
version the project states about itself. It reads **committed** state — `git
ls-files`, never a directory walk — because a walk finds `node_modules` and
build residue, and reports a project no clone would produce.

The output is a profile, and the profile chooses the probes. Skipping this and
running a fixed checklist is how an audit produces the same nine findings on
every repository it is ever pointed at.

### 2. Probe — the registry, chosen from the profile

Every probe declares what it needs (`git`, `gh`, `npm`, `network`, a connected
MCP server). A need that is not met makes the probe **blind**, with the reason —
never absent, and never clean. The catalogue by stack, and what to add for a
project shape the script does not cover, is
[`references/probes.md`](references/probes.md).

### 3. Prod — the evidence that only exists outside the tree

This is the phase most audits skip, and the one that finds what the repository
cannot admit about itself:

- **the published artefact against the source** — see the next section;
- **CI history**: not "is it green" but what share of *release* runs failed, and
  whether a failure was noticed. `gh run list --limit 60 --json conclusion,name`
  is one command and it is the closest thing to a production log a package has;
- **telemetry, present or absent.** Absent is a finding only when something is
  deployed; for a library it is a design. Either way the report says which,
  because "no Sentry configured" and "no errors" must not render the same;
- **adoption**, where a registry serves it — downloads make "is this in prod"
  a measurement rather than an opinion;
- **connected MCP servers** — error trackers, analytics, hosting, databases.
  Ask what the project uses, use what is connected, and record the rest as
  blind. Read aggregates and pointers, never raw bodies (see *The two
  artefacts*).

### 4. Seams — hand off to the ladder

Now, and only now, walk `audit.md`'s ladder over the capabilities the discovery
found. Bottom-up, seam-ordered. Absences found here are findings like any other.

### 5. Report — two files, one command

`python3 scripts/audit.py --root <path>` writes both and opens the page. It is
the same script the probes live in, so what the report claims and what ran are
the same object.

### 6. Propose — rows, not edits

**This skill commits nothing.** Findings leave as board rows in the project's
own vocabulary, priced with the project's own formula —
`P = blast × (1 + age_runs) / effort` — and the operator accepts them. An audit
that edits while it reads cannot be re-run to check itself.

## Three verdicts, and why the third one exists

`clean` · `finding` · `blind`. The vocabulary is closed; a fourth value is
refused at construction.

**`blind` is the whole design.** Without it, a probe that could not look and a
probe that found nothing produce the same empty section, and a reader takes the
second meaning every time. This is `audit.md`'s *silence is not a reading*
raised from a command to a probe: a zero exit with no output has not answered.

The page renders the blind list as a section of its own, never an appendix.
**An audit's blind spots are part of its result.**

## The class that version checks cannot see

**One version string, more than one tree.** A package's channels do not all
serve the same thing: a registry serves the **tag**, while a plugin marketplace
and a skills CLI serve the **branch tip**. When the branch has moved past the
tag without a version bump, every channel answers the same number and ships
different code.

Measured in this family on 2026-08-22: npm served one file at 4344 lines while
the marketplace served it at 4575, and all three channels reported `1.15.0`. The
pin checker was green throughout — correctly, because it compared the two
strings.

**So compare trees, never labels**, and compare the pair that can actually
disagree. The first draft of this probe compared the registry tarball against
the tag and reported clean: those agree by construction, because the registry
publishes *from* the tag. A tautology returning green is the *false success*
shape — a mechanism trusted by its own reply.

Two more traps, both of which shipped in the first draft and are now fixtures:

- **A path in one channel and not the other is packaging, not divergence.** A
  tarball ships what its `files` allowlist permits; counting `.github/` as a
  disagreement produced 22 findings where one file had moved.
- **Compare only when both sides claim the same version.** A branch already
  bumped past its tag makes no common claim, and is `blind`, not `clean`.

## The two artefacts

`docs/audit/<date>-audit.html` and `docs/audit/<date>-audit.json`.

**The page carries aggregates and pointers, never raw bodies.** Counts, top
classes, trends, and a link to the issue in its own system — never a stack
trace, a log line or a row of data. The report is a file people forward, and a
report that cannot be shared is one nobody writes twice.

**A secret is reported by place and class, never by value.** `file:line`, which
credential it is, and the remedy. The value appears in neither artefact nor on
stdout: an audit must not become the second place a credential leaks. Redaction
is total rather than a prefix — half a credential plus its context is often
enough to finish.

**The sidecar is what makes this a ratchet rather than a snapshot.** Each
finding carries an id derived from its probe and its place, so it survives a
rewording; the next run prints what closed, what is new, and what has now
survived three audits. That last number is itself a finding: a defect nobody
picks up is a decision nobody wrote down.

## What the script does and what you do

| The script | You |
|---|---|
| discovery, the registry, mechanical probes, both artefacts, the diff | the seam walk, MCP evidence, judgement about what a finding means |
| refuses a fourth verdict, redacts secrets, excludes its own output | deciding severity and effort, writing the remedy that fits this project |

The split is not tidiness. **A judgement encoded in a script becomes a gate
nobody agreed to**; a mechanic left in prose becomes a step nobody runs. Both
have shipped in this family and both are on its boards.

Run the script first, read its blind list, then spend your reading where it
could not look.

## Exit criterion

An audit is finished when:

1. every probe has a verdict, and every `blind` one names why;
2. the page and the sidecar are written and the page has been opened;
3. **every number in the report was produced by a command this run executed** —
   a restated count is an assertion (`evidence-docs`);
4. at least one figure was **re-derived by a differently-shaped command** and
   both were printed. Re-running the same command is a spell-check of the first
   run;
5. the proposed rows are printed for the operator, with nothing written.

## Rationalizations

| Excuse | Reality |
|---|---|
| "The tests pass, so the project is healthy" | Tests compare what somebody thought to write down. This phase 3 exists because the sharpest defect in this family was invisible to a green suite in every repository it touched. |
| "There's no Sentry, so there are no errors to report" | Those are the same empty section and opposite facts. That is what `blind` is for. |
| "The versions match, so the channels agree" | Measured: three channels, one version string, 231 lines of difference. Compare trees. |
| "I'll note the raw log lines so we have context" | Then the report cannot be shared, and it will not be written again. Aggregate and point. |
| "I found a credential — I'll paste it so we can check it's live" | The report becomes the second leak. Place and class; rotation is the remedy. |
| "Findings should just be fixed while I'm in there" | An audit that edits while it reads cannot re-run to check itself, and the next run cannot tell a fix from a rewording. |
| "It's the same nine checks every time, so I can skip discovery" | Then the instrument returns the same answer for every input, which is a fact about the instrument and not about the project. |
| "No findings — clean bill" | Only against the probes that ran. Read the blind list before saying that sentence out loud. |
