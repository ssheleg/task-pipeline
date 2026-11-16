# Spec: the stages and gates doctrine

Components: `references/stages.md`, `gates.md`, `stage-NN-*.md`, `finish-line.md`,
`residue.md`, `loop-guard.md`, `certification.md`, `learned.md`, `acceptance.md`,
`build.md`, `planning.md`, `spec.md`, `review.md`, `tdd.md` (under
`plugins/task-pipeline/skills/task-pipeline/`). Loaded one section at a time as a stage
starts. Checklist: [`../README.md`](../README.md). Read at 1.104.3.

## What changes, and why

P-02 and P-03 are clean everywhere. The problems are stops, history and weight.

**Unwanted stops (P-04).** Fifteen places tell the agent to ask or wait where no human
gate exists, and several contradict `stage-00-intake.md:79-84` (decide under delegation)
and `stages.md:157` (standing authorization counts):

| Where | Text today | Becomes |
|---|---|---|
| `build.md:18-19` | stop for "a genuine ambiguity" | decide by recorded decisions, then goal, then safest reversible option; record it |
| `build.md:69-70` | "ask once before creating" a worktree | create it (the default is decidable) |
| `build.md:95-96` | red baseline: "let the operator decide whether to proceed" | record the known-red baseline (`gates.md:197`) and continue |
| `build.md:331`, `:346` | "escalate to the operator" when the plan is wrong | re-plan at stage 4 |
| `loop-guard.md:172`, `:197` | "the operator decides" which governs; "stop and report BLOCKED" | decide by the same order; BLOCKED only at a human gate |
| `tdd.md:191` | "Still stuck → ask the operator" | park the node with its evidence and continue |
| `stage-02-brainstorm.md:10-12` | no code before the operator approves the design | add "or the standing authorization recorded in the brief" |
| `spec.md:303-308` | "Review it and tell me if anything should change … otherwise wait" | a statement: spec committed at path, reviewed by reader, continuing to the plan |
| `stages.md:270` | "NOT_RUN stops and asks" | record NOT_RUN, hold that check, continue other work |
| `stages.md:502` | map revision "operator-approved" | add the delegation clause |
| `stage-00-intake.md:116` | "asks once where to seed" | seed at the default and record it |
| `finish-line.md:33` | widening scope "with the operator's go" | add the delegation clause |
| `acceptance.md:150-151`, `gates.md:619-621` | deferred and dropped need the operator's agreement | align with `stages.md:477`: "or, under a host delegation, the agent's recorded decision" |

Wanted stops stay as they are: manual gates, deploy and outward acts without a go,
drawing in Figma, a Figma file that does not resolve (narrowed to the visual track), the
round budget, NOT_RUN on a release impact card, a missing stage route.

**History (P-10).** Fourteen "since/until 1.x" notes and dated sentences in loaded files
(`stages.md:6,18,45,203,319,324,357,378,468,481`, `gates.md:66,381,645`,
`finish-line.md:28,79`, `loop-guard.md:52,79,90`, `certification.md:5,258,285,308`,
`spec.md:92,145`, `acceptance.md:99-104,238,479`, `build.md:244-249`).

**Weight (P-09).** About 55% of `learned.md`, 40% of `gates.md` and 25-30% of
`stages.md`, `residue.md`, `certification.md`, `acceptance.md` is incident narrative or
justification; the stage 0 and stage 10 gates are single bullets of 32 and 57 lines.

## How (this unit)

1. Rewrite the fifteen unwanted stops as in the table, each keeping the human-gate list.
2. Delete the history sentences that no test pins (the free ones; see below).
3. Fix `acceptance.md` numbering (7a after 8; the unnumbered paragraph inside the list).
4. A lint rule `unwanted-stop` in `test/prompt_lint.py`: flags "ask the operator", "let
   the operator decide", "otherwise wait", "escalate to the operator" in a paragraph with
   no human-gate or delegation clause.

Deferred, filed as board rows: moving incident narratives to one archive reference
(`references/incidents.md`) with pointers left behind; splitting the stage 0 and stage 10
gate bullets into one criterion per line; renaming terms for one concept per word
("hand-back" vs "closing statement" vs "close-out"); trimming bold in `learned.md`,
`stage-09`, `stage-03`.

## Must not change (consumers)

- Stage routing: `^## (\d+) — (.+)$` headings, one `**On entry or resume:**` line before
  `- **GATE (` (`test/stage_routes.py:11,37-57`; `validate.py:2425-2441`).
- `## Contents` equals the `##` headings for every file over 100 lines (`validate.py:274-300`).
- Review cap "**3 review rounds** per artifact" and "3 rounds per artifact" (`validate.py:5694-5713`).
- `residue.md`'s dated incident text and the bold rule lines (negatives 333-356;
  `anchors_test.py:190-451`).
- `learned.md` rule rows and "**Numbers issued so far: N.**" (`validate.py:567-570,915-960`).
- `acceptance.md`'s AP-1 owner line, "**reported, never ended**", the two required
  sections, the retro order (negatives 134-145, 174, 335-361).
- `stages.md` stage 10: "**the hand-back is written**", "Either way the verdict carries a
  `publish:`" (negatives 314, 315, 330; `validate.py:7350`).
- `gates.md` title, the False success section and rules, the near-miss sentence
  (negatives 092-096, 146, 182, 320).
- `spec.md`/`stage-03-spec.md` scenario-artifact sentences (`fw07_prerequisites.py:66-80`).
- Each doctrine file stays at 1500 bytes or more (`validate.py:243-261`).

## Risks

- A needle lost in a cut: each sentence is grepped in `test/` before it is removed.
- A stop loosened too far: every rewritten stop keeps the human-gate list and the
  outward-act floor; the new `unwanted-stop` rule guards against regression.

## Verification

`npm test`, the negatives of each touched file (`npm run test:negatives`), prompt lint
rebaseline (lower only).
