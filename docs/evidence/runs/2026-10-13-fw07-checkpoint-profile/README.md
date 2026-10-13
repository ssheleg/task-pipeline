# FW07 checkpoint profile correction — frozen source packet

Objective: keep recovery checkpoints inside the selected project profile, preserving
existing local ledger, constraints, lease and tool-argument contracts. Parent authorized
this bounded correction after the actual offline reproducer; it is separate from
extraction PR123 and requires independent source review and aggregate admission.

## Reproduced baseline

Source: [accepted main](https://github.com/ssheleg/task-pipeline/commit/78c42124db910c56e74c8fbd524bdc9a4f8fb6c9).
The unchanged `scripts/stage_checkpoint.py` loads only its bundled example in
`_stages`, builds a numerically sorted eleven-stage plan and computes `sid + 1`.
An isolated project containing a three-stage `pipeline.json` (Collect, Build,
Accept) and a ledger whose last line is `stage: 2 Accept — gate auto — verdict pass
— 2026-10-13T10:00:00Z` produces exit 0, all eleven default plan stages,
`enter stage 3 Spec` as its next action and `close=false`.
This is a wrong checkpoint payload, not an observed live Observatory write.

## Consumers and boundaries

- `SKILL.md` config contract and selected-profile preflight: stage numbers belong
  to the selected profile; only its declared stages/gates run.
- `pipeline.schema.json`: stages are ordered; `state`, `skills`, `gate` required;
  `id` and human `name` optional. Unknown mandatory capabilities cannot be ignored.
- `scripts/stage_checkpoint.py emit`: reads ledger, builds tool arguments, carries
  saved constraints/credential names; `record` persists tool response and lease.
- `references/continuity.md` Part 3 instructs actual use of emit/record/latest.
- `hooks/memory-nudge.sh` reminds only; it does not select stages or call providers.
- `references/artifacts.md`: configured `paths.artifacts` controls project documents;
  the run ledger remains `.task-pipeline/run.md`. Do not conflate these roots.
- `scripts/graph.py` has a config digest for its own handoff reader; it is not this
  writer's profile compiler. No graph execution/profile semantics change here.

## Frozen bounded contract

1. Resolve the project from the standard ledger location, or an explicit
   `--project-root` for a relocated ledger (Git root may establish it otherwise).
   A canonical project `pipeline.json` selects the profile; genuinely absent config
   uses the bundled example. Existing unreadable/malformed config is a refusal.
2. Preserve declared array order, using explicit nonnegative integer ids or their
   array ordinals for the existing numeric ledger syntax; label from name or state.
   Require unambiguous ids/states and supported gate shapes. Reject unsupported
   mandatory extensions and unrepresentable/mismatched ledger stages explicitly.
   This checkpoint reader is not a universal schema/compiler or gate executor.
3. A passed stage advances to the next declared stage. The final passed stage
   closes; failed/unknown verdict stays open. A final skipped stage remains open
   for confirmation instead of inventing a successor or new completion authority.
4. Persist selected profile identity and semantic digest in local memory state,
   scoped to the run identity. Same-run profile change must refuse before output
   or state changes; restore the selected profile or start a separately identified
   run after reconciling existing workflow state. Retain binding on record.
5. Keep tool argument field shapes, default step ids, constraints, credential-name
   validation, lease handling and idempotent retries. Bind new custom-profile
   payload identity to its profile; never echo credentials or raw config errors.
6. Tests exercise actual CLI: default/no config, custom overlapping ids, nonnumeric
   ordering, omitted ids/names, configured artifacts, relocated ledger, malformed,
   unreadable/missing selected source, unknown capabilities, ambiguous ids, mismatched
   ledger, retries, profile drift and record persistence. Missing ledger remains a
   refusal. Offline tool answers are fixtures, never live-provider acceptance.

Implementation and focused results follow in later source-bound sections. Broad
suite and genuine candidate CI remain pending the coordinator's serial slot.
