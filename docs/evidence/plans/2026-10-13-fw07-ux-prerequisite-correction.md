# FW07 prerequisite correction — preserve the accepted artifact contract

Source: task-pipeline `4d750573ce53ea4c7ffa2bde192ee35b59acefa7` (1.94.0).
This is a separate bounded semantic correction before the lossless
[stage extraction](2026-10-13-fw07-stage-reading-floor.md), not authority to
reinterpret gates during relocation. Parent independently accepted this correction
from the following Git and PR evidence on 2026-10-13. Implementation starts only
after the current 1.94.0 release closes.

## Recovered decision and reproduced gap

- `git blame` attributes `plugins/task-pipeline/skills/task-pipeline/SKILL.md:59–64`
  to `dbe4f43e` (2026-08-03): user-facing stage3 stops until super-ux is installed.
- The later [source commit a1d6bcc](https://github.com/ssheleg/task-pipeline/commit/a1d6bcce9175e8c79436e8f66ffb8f6b591f8791) explicitly fixes
  FIX-TP-02.01: gates check artifact quality, never package presence. It adds
  preferred, equivalent-provider and inline-fallback paths, plus a named NOT_RUN
  for any unavailable check. It changed SKILL.md and companion-skills.md but left
  the older prerequisite paragraph intact.
- [Accepted PR86](https://github.com/ssheleg/task-pipeline/pull/86), merged
  2026-09-10 at `42b1dce8ddf40288c40af0e98c38c285dcad3b85`, incorporates that fix.
  Its body records owner npm test and audit regression checks; those are historical
  PR claims, not new replay of the old branch.
- The same merge also brought doctrine-map.md:8–10, copying the older exception.
  Thus date ordering alone does not make every line of the merge coherent.
- Current companion-skills.md:11–20 and SKILL.md:71–80 preserve the accepted
  artifact rule. No new operator decision is needed to remove contradictory
  package-install prerequisites.
- Actual `python3 -B test/audit_regressions/fix-tp-02.01.py` at this source exits0,
  seven cases, despite both contradictions. The test forbids only one exact old
  sentence. Its local `stage3_gate` example does not execute native host behavior.

## Exact intended change

1. Replace the stale SKILL prerequisite exception with the already accepted
   artifact requirement; keep the family provider preferred and keep unavailable
   check reporting. Link to the existing provider contract rather than duplicating it.
2. Normalize the stale doctrine-map preface and the sibling surfaces below to the
   same meaning. Do not weaken
   scenario validity, coverage, custom-profile precedence or explicit manual gates.
3. Strengthen the existing regression against both actual stale variants at their
   normative homes. Add bounded whitespace/line-wrap variants, missing-artifact
   and invalid-artifact negatives, equivalent-provider and inline positives.
   A synthetic decision helper remains a contract fixture, not a model evaluation.
4. Execute mutations against the real validator/test entry and restore source in
   owned isolation: reinstall each stale rule must fail by a named diagnostic;
   harmless reflow and the accepted fallback must pass. Do not claim arbitrary
   natural-language contradiction detection.
5. Commit this correction separately. Rebase the conservation baseline for the
   later extraction if any relevant stage bytes change; otherwise preserve the exact
   existing stage byte map. Re-measure body budget before adding routing text.

## Acceptance and boundaries

Required: focused source/negative controls, independently reviewed diff, then the
combined FW07 owner full suite and genuine candidate checks under the normal policy.
No change to stage ids, gate types, user authorization, release workflow, browser
requirements, provider keys or installations. Native execution, comprehension and
quality remain NOT_RUN without actual traces. B-043 stays open until extraction's
own conservation and routing acceptance pass.

## Sibling surface census (same accepted-intent correction)

A follow-up literal search after the first packet found the same exception in
additional current shipped homes. This broadens the exact location inventory,
not the intended semantic change:

| Frozen source location | Stale meaning | Correction boundary |
|---|---|---|
| SKILL.md:59–64 | Installation is the stage3 exception | Existing artifact/provider rule |
| references/doctrine-map.md:8–10 | Same exception in navigation preface | Link to accepted provider rule |
| references/companion-skills.md:290 | Preflight says never gate installs except stage3 | Remove contradiction with this file's own provider rule |
| commands/task-pipeline.md:38–39 | Absent companions become stage3 gate | Artifact gate, named missing checks |
| README.md:170–172 | Same explicit install requirement, blame `59e16493` (2026-08-03) | Existing artifact/provider rule |
| README.md:974 | super-ux marked required for user-facing work | Preferred provider; scenario artifact required |
| HOW-IT-WORKS.md:67–70 | Missing companion is a blocking exception | Existing artifact/provider rule |
| SKILL-CARD.md:17 | Package is the conditional dependency | Scenario artifact required, provider preferred |

Paths without a prefix are repository-relative for README/HOW-IT-WORKS/SKILL-CARD;
SKILL.md and references are under `plugins/task-pipeline/skills/task-pipeline`;
commands is under `plugins/task-pipeline`. Historical changelog/audit snapshots
remain unchanged. The current Cursor UX line already says recommended; inspect
its context for consistency but do not change it merely to equalize wording.
Actual source-negative coverage must name all seven files/eight listed locations.

The PR86 source commit is linked to its verified GitHub archive (API readback
resolved the exact hash on 2026-10-13); it is not an ancestor of the squash-merged
main. Only its accepted merge is represented as local-history evidence.
