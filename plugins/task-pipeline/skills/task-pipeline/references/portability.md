# Portability — what travels with the bundle, and what must not

**One job: keep every decision about *how the pipeline behaves* inside the bundle, and
every decision about *what a project decided* inside that project.** Get this backwards
in either direction and something breaks quietly: a workflow optimisation stranded in
one repository, or a skill that has quietly learned one project's answers.

## Contents

- The boundary
- The manifest — every workflow decision and its home
- The two checks, in both directions
- What a host project is allowed to hold
- Rationalizations

## The boundary

| Kind of decision | Example | Lives in | Travels? |
|---|---|---|---|
| **Workflow** — how the pipeline behaves anywhere | the gate types, the loop-guard caps, the Doc Loop's seven steps, the escalation rule, the routing boundary | `references/*.md`, `templates/*`, `pipeline.example.json` | **yes — this is the bundle** |
| **Project answer** — what *this* repository decided | which register it uses, its propagation matrix, its ratchet floors, its standing instructions | `docs/DOCMAP.md`, the register, `<artifacts>/retro.md`, the brief | **no — and correctly so** |

Two failures follow from confusing them, and they look nothing alike:

- **A workflow decision left in a project** is a fork of the doctrine that nobody
  named. The next project starts without it and nobody notices, because the first
  project still works.
- **A project answer absorbed into the skill** ends project-agnosticism. The bundle
  starts asserting things that are true in one repository and false in the next.

**The tell is the question it answers.** *"How does the pipeline behave?"* → bundle.
*"What did we decide here?"* → project. A rule that would be true in a repository you
have never seen belongs in the bundle even if you learned it in one.

## The manifest — every workflow decision and its home

Every row's home is a path **inside this skill**. A guard checks each one resolves;
a row pointing outside the bundle is the defect this file exists to catch.

| Workflow decision | Home |
|---|---|
| The stage list, ids, names, gate types | `pipeline.example.json` |
| Per-stage criteria, freedom levels, the run checklist | `references/stages.md` |
| What the intake grill asks, and the autonomy sweep | `references/grill.md` |
| **The escalation boundary** — what an agent may settle alone | `references/grill.md` |
| The knowledge harvest and its source ledger | `references/knowledge-sources.md` |
| The documentation system, the Doc Loop, supersede semantics | `references/documentation.md` |
| Gate types, the enforcement ladder, degrees of freedom, probing | `references/gates.md` |
| Deploy runbook template, per-platform verbs, the verification trio | `references/deploy-targets.md` |
| The Claude Code hook contract | `references/hooks.md` |
| First run in a project: greenfield and brownfield | `references/adoption.md` |
| The entry audit and what it inspects | `references/setup.md` |
| The ladder, seams, axis rotation, ratchets | `references/audit.md` |
| Loop detection and its caps | `references/loop-guard.md` |
| **What the run prints about itself** — the header block, the rail, the iteration line | `references/progress.md` |
| **What the run leaves running and leaves behind** — the eight classes, the `holds:` field, the teardown | `references/residue.md` |
| **The run mode** — item-by-item pacing, default off, what it never collapses | `references/continuity.md` |
| **The context budget** — the evidence rule and what a flush actually updates | `references/continuity.md` |
| **The board** — the work-list between runs, its computed priority, and the ledger seam it resolves | `references/backlog.md` |
| **The verification ledger** — what shipped, and whether a human ever confirmed it | `references/verification.md` |
| **Exposure** — the unconfirmed count as a named vector, never a probability, and the `checkup` mode | `references/exposure.md` |
| The retro: prune, cap, commits, archive | `references/retrospective.md` |
| Rules earned by failure | `references/learned.md` |
| **The routing default and its boundary** | `templates/routing-rule.md` |
| The seeded doc map, registers and gate | `templates/docmap.md`, `templates/decisions.md`, `templates/open-questions.md`, `templates/docgate.sh` |
| Which agent-introduced defects are found, and that the agent fixes them rather than the script | `templates/hygiene.sh`, `references/build.md` |
| What a stage-3/4 self-review must read back, and that its trace is computed numbers | `references/spec.md`, `references/planning.md`, `references/learned.md` |
| What a stage reads, and which host files bind it | `references/artifacts.md` |
| The design conversation, its hard gate, UI detection, user paths | `references/brainstorm.md` |
| Cutting a platform into modules, brick criteria, build order | `references/decomposition.md` |
| What a spec must lock, the UX-track order, the module dossier | `references/spec.md` |
| The zero-context plan format, parallel groups, set equality | `references/planning.md` |
| Workspace isolation, the subagent loop, who may write the register | `references/build.md` |
| The review rubric, diff packages, the three verdicts | `references/review.md` |
| **False success** — the class, its known shapes and its two rules | `references/gates.md` |
| **The canons** — what makes a claim documentation, and the index that routes to each | `references/documentation.md`, `../evidence-docs/SKILL.md` |
| **Effect verification** — the `verified-by:` contract and the rubric item that blocks | `references/build.md`, `references/review.md` |
| The TDD iron law and the suite gate | `references/tdd.md` |
| How the browser look is taken, and how a spec suite sits beside it | `references/browser.md` |
| The REQ coverage table, evidence rules, the closing question | `references/acceptance.md` |
| How the host project's own conventions are read | `references/conventions.md` |
| Which companions exist, what is required, self-currency | `references/companion-skills.md` |
| The code graph: queries, refresh, the graph↔docs divergence | `references/knowledge-graph.md` |
| How the graph's staleness is measured and stated in the ledger | `references/knowledge-graph.md` |
| How a CI run's verdict is established, and its three states | `references/conventions.md` |
| Model policy — tier not id, ask once at preflight | `references/model-tiering.md` |
| This boundary | `references/portability.md` |

**The routing rule is the row worth watching.** A skill's `description` raises the
odds it is selected and cannot make selection mandatory — only an instruction in a
`CLAUDE.md` can. That instruction is therefore *installed*, not shipped, which is
exactly how a workflow decision ends up living outside the bundle. The template above
is the fix: the rule travels as a file, and [`setup.md`](setup.md) **offers** to
append it. Offers, not writes — it is the operator's configuration.

## The two checks, in both directions

One direction is not enough, for the same reason
[`learned.md`](learned.md) rule 2 gives: a comparison needs two sides and an absence
has one.

**Outward — does every workflow decision have a home here?** Mechanical: every path
in the manifest resolves inside the bundle, and no row names a path outside it. Run
by the validator on every commit. This catches *"we decided it and forgot to put it
anywhere portable"*.

**Inward — is this project holding something universal?** Judgemental, and it is
[`setup.md`](setup.md)'s job: read the host's `CLAUDE.md`/`AGENTS.md`, its doc map
and its standing instructions, and ask of each rule — *would this be true in a
repository I have never seen?* If yes, it is a workflow decision wearing a project's
clothes, and it should be proposed upstream rather than copied to the next project by
hand. This catches *"the optimisation lives in one repo and dies there"*.

Neither check can be skipped in favour of the other. The outward one is cheap and
constant; the inward one runs when a project is audited, and it is the only one that
can find a rule nobody ever wrote down as portable.

## What a host project is allowed to hold

Not a restriction — a list of what *should* stay local, so the inward check does not
flag it:

- the answers in `docs/DOCMAP.md`: which register, which homes, which matrix rows;
- the ratchet **values** — floors are measurements of one repository's history;
- standing instructions that name this project's paths, commands or people;
- the deploy target, the test command, the branch policy;
- everything in `docs/ux/` — this project's users, flows and scenarios.

A standing instruction that names **no** path, command or person is a candidate for
the bundle. That is the cheapest inward test there is, and
[`retrospective.md`](retrospective.md) already states the rule it serves: a lesson
true in any repository belongs in the pipeline's own doctrine, not in one project's
retro.

## Rationalizations

| Excuse | Reality |
|---|---|
| "It's in our CLAUDE.md, that's good enough" | Good enough for this repository on this machine. The next project starts without it, and nobody notices because this one still works. |
| "I'll copy the rule into the next project when I get there" | That is the fork, performed by hand, once per project, until two of them disagree and neither is wrong. |
| "The skill should just learn our conventions" | Then it stops working for anyone else, including you on the next repository. Conventions are answers; the bundle carries questions and procedures. |
| "This rule is obviously universal, it doesn't need a home" | Every rule is obvious to the person who just learned it. The manifest is one line; the fork is permanent. |
| "The manifest will go stale" | It is checked, not trusted: every path resolves or the build fails. A stale row is a red build, not a quiet lie. |
