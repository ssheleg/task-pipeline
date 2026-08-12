---
name: evidence-docs
description: "Use when writing or reviewing anything that will be read as true — a decision record, a README, an acceptance report, a runbook, a changelog entry, an audit finding, or any claim that something was verified. Applies the ten canons of evidence-backed documentation — what makes a claim documentation rather than an assertion — and routes to the doctrine that enforces each one. Also use when a project needs a documentation gate, a decision register, a propagation matrix, or a retrospective that outlives its author. Triggers - 'documentation gate', 'decision record', 'ADR', 'acceptance report', 'runbook', 'is this verified', 'доказательная документация', 'записать решение', 'отчёт о приёмке', 'раннбук', 'чем это подтверждено', 'доки в синхроне'. Not for: drafts, chat answers, commit messages or code comments — say 'без доков' to opt out."
---

# Evidence-backed documentation

**A claim is documentation only when it carries the means to check it.** This skill is
the standard and the map: ten canons, and where each is defined, enforced and seeded.

It is a **navigator, not a second copy**. Every law below has exactly one home — that is
canon 3, and a navigator that restated the doctrine would break the rule it is indexing.
The full statement of each canon, its rationale and its enforcement live in
[`documentation.md`](../task-pipeline/references/documentation.md) → *The canons*.

## The ten canons

1. **A claim carries its address** — `file:line`, a command with its output, a test name; a lesson names its commit.
2. **Numbers are computed, never restated.**
3. **Every fact has exactly one home** — others link, never restate.
4. **A reference resolves from where the document is read** — not from where it lives.
5. **Green nobody watched turn red is not evidence.**
6. **A check proves its scope and nothing beyond it.**
7. **Silence is not a pass** — ask what a mechanism prints when it did not look.
8. **An estimate is never announced as a measurement** — a rule states its evidence condition.
9. **What was not checked is printed beside what was.**
10. **The document ships in the change that made it true** — and a correction is appended, never written over.

They are **epistemic**: what makes a claim documentation. The operational layer — what to
do at a given trigger, with a check and an exit criterion — is
[`learned.md`](../task-pipeline/references/learned.md). When the two seem to say the same
thing, the canon is the *why* and the rule is the *how*.

## Where next

| You are about to… | Read | Because |
|---|---|---|
| set a project's documentation up from nothing | [`documentation.md`](../task-pipeline/references/documentation.md) → *The inventory* | four questions answered before the first line of work |
| record a decision so it survives its author | *Registers and ids* + [`templates/decisions.md`](../task-pipeline/templates/decisions.md) | append-only ids, edge markers, one decision home |
| change something and not orphan the docs | *The Doc Loop* + *The propagation matrix* | which documents a change owes, starting with the meta-row |
| decide where a fact belongs | *Single source of truth* | two homes disagree the day one of them is updated |
| build a check that cannot lie | [`gates.md`](../task-pipeline/references/gates.md) | three axes, the enforcement ladder, progressive arming, probing |
| trust a mechanism that reports success | [`gates.md`](../task-pipeline/references/gates.md) → *False success* | the failure that removes the reason to look |
| wire a check into the agent's own tooling | [`hooks.md`](../task-pipeline/references/hooks.md) | the hook contract, and why a crashed guard **allows** the action |
| audit documentation a project already has | [`setup.md`](../task-pipeline/references/setup.md) | seven passes, cheapest first, output is a fix plan |
| carry a lesson to the next run | [`retrospective.md`](../task-pipeline/references/retrospective.md) | stamp first (the cold trigger reads it), then prune to a cap of ten; every lesson names its commit |
| seed a gate into a host project | [`templates/docgate.sh`](../task-pipeline/templates/docgate.sh) | it seeds **green**: dormant where there is no input yet |
| claim that an **agent** behaves | `tdd.md` → *When the thing under test is an agent* — named rather than linked, because this navigator's out-of-directory links break wherever a packager ships this skill alone | the address is a trace id and the assertion that ran (canon 1); a judge nobody watched disagree is a green nobody watched turn red (canon 5) |
| take a whole change through to acceptance | [`task-pipeline`](../task-pipeline/SKILL.md) | this skill is the standard; that one is how a change reaches the repository |

## When this applies

**The boundary is "it will be read as true."** A decision record, a README, an acceptance
report, a runbook, a changelog for users, an audit finding, a claim that something was
verified.

**Not through this skill:** a draft, thinking out loud, an answer in chat, a commit
message, a code comment. Demanding a `file:line` for "let me check that" is the fastest
way to teach an agent to route around the rule where it actually protects something.

**Refusal phrase — "без доков" / "on my word".** It works on a task that would otherwise
pass through here: do it directly and **say out loud** that the claim is unbacked, rather
than presenting an estimate as a measurement (canon 8).

## The one test

Before a document ships, read it for the sentence that would embarrass you if someone
asked *"how do you know?"* — and either give that sentence its address, or delete it.
Everything above is that question, made mechanical.
