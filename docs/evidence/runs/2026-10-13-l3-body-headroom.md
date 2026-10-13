# R09 working-budget headroom restoration

Status: bounded prose change; peer review and integration pending. Base
[adb82f7c97a4a82b7d2bd8f8f17fee97a111ab8b](https://github.com/ssheleg/task-pipeline/commit/adb82f7c97a4a82b7d2bd8f8f17fee97a111ab8b) includes the separately reviewed L3
packets and the still-pending TP2 graph waits. No description, authority clause,
stage gate, runtime script or provider/native behavior change is claimed.

## Source requirement

Hub `docs/evidence/briefs/2026-10-11-integration-waves.md`, R09, requires the
description to stay at most 900 characters and the body to retain at least 100
tokens under its limit. The owning plan's W2-C calls for moving named body
sections to references. The original limit is made concrete by task-pipeline's
`docs/HANDOFF.md` Wave 2 and B-120 in `docs/evidence/backlog.md`: the accepted
reading was 4646/4750, explicitly beyond the requested 100-token margin. It is
the 4750 working budget, not the separate 5000 hard ceiling.

Current body 4724/4750 had only 26 tokens spare even though the house auditor
returned no GAP. That was insufficient for R09. The three explanatory grill
bullets duplicated sections already in `references/grill.md`: Domain awareness,
The autonomy sweep and The design destination. Their entry paragraph now tells
the reader to load that reference at stage 0, retaining resolved-term writeback,
pre-resolving later-stage interruptions, and file/team per Figma surface before
drawing. Full procedures remain at their existing canonical homes. All other
SKILL.md bytes, including description and authority/kernel/gate text, are unchanged.
README's derived whole-file line count was recomputed from splitlines, 271→270.

## Measured checks

The installed make-skill 0.31.1 `scripts/audit_skill.py` was run before and after:
`audit_skill.py plugins/task-pipeline/skills/task-pipeline --house --json`.
Both runs exited 0 with zero GAP, using `tiktoken:cl100k_base`; those house passes
alone do not prove the extra R09 margin. The explicit arithmetic check does:

| Measure | Before | After | R09 result |
|---|---:|---:|---|
| Description characters | 887 | 887 | ≤900 |
| Body tokens | 4724 | 4639 | 85 fewer |
| Spare below working 4750 | 26 | 111 | ≥100 |

`python3 -B test/continuity_doc_test.py` passed 31 cases. The first structural
run correctly refused the stale README line count; it was recomputed, not waived.
Final `python3 -B test/validate.py` exited 0 after that correction; the same
three existing unlooked conditions remain. No model-based quality
or token-spend saving is inferred from this deterministic body count.

Exact next task: review the one-paragraph displacement and source procedures,
then integrate after TP2 and remeasure the combined PR112/PR114 feature before
release. Description/token metrics remain a separate acceptance layer from live
Observatory handoff, native skill loading and artifact quality.
