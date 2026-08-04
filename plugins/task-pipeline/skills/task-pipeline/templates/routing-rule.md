# Routing rule — the portable version

**Copy this into the operator's `CLAUDE.md`** (global `~/.claude/CLAUDE.md`, or a
project's, or both). `setup` **offers** to append it; it never writes to an
operator's configuration silently.

**Why it is a file and not just the skill's description.** A skill's `description`
raises the odds the model selects it and cannot make selection mandatory — the choice
stays with the model, case by case. Only an instruction makes routing binding. That
instruction therefore has to be *installed*, which is exactly how a workflow decision
ends up living outside the bundle ([`../references/portability.md`](../references/portability.md)).
Shipping it as a template is what lets it travel.

**Keep the exclusions identical** to the skill's `description` and to the
`should_not_trigger` evaluations. Three copies of one boundary that drift are worse
than no boundary.

---

## Routing — repo-changing work goes through the pipeline

**When `task-pipeline` is installed, any work that CHANGES THE REPOSITORY goes
through it** — without being asked for. A feature, a fix, a refactor, a migration, an
integration, a rewrite, an adoption, a hardening pass; in any language and any
phrasing. Saying *"run this through the pipeline"* is an accelerator, not a
precondition.

**The boundary is "changes the repository", and it cuts both ways.** Not through the
pipeline:

- a question and its answer, an explanation, reading or mapping code;
- a typo, a one-line edit, a mechanical rename;
- reconnaissance or measurement that commits nothing.

Running ten gated stages for one character is the fastest way to teach an agent to
route around the pipeline entirely.

**The opt-out is "без пайплайна" or "quick".** It applies to a task that *would*
qualify: do it directly, and **say out loud** that the cycle was skipped at the
operator's request — never silently.

**A borderline case is named, not silently chosen.** *"Clean up the error handling"*
can be a two-line fix or a day's refactor. State which route you are taking and why,
in one line.

**Escalation while running.** Decide alone while the cost of being wrong stays inside
the repository and is reversible. Escalate a price, a legal posture, a promise made to
somebody outside the team, anything that spends money or reputation, any change to
what a customer's data is used for, and any irreversible outward act. The tell is the
**cost of being wrong**, not the size of the change.
