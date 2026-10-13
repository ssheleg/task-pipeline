<sub>ssheleg skills — task-pipeline · agent-sync · evidence-docs</sub>

# PR112: independent semantics review and conservative state fixes

Reviewed 2026-10-13, exact candidate
`a77c990dc32b0505a49a51da1ef38112f24d7243` (PR112 after the PR115 fixture
repair). Review checkout: isolated branch `fix/pr112-conservative-state`.
The original author's worktree and branch were not changed. This receipt is
acceptance evidence for a bounded change, not a claim that every pipeline gap
or the operator's whole system goal is complete.

## Original objective and scope

The operator asked for a survey of unfinished work, a target system and
context-complete agent tasks, then build/check/fix waves until an independent
observer can confirm the intended result. The related Fabric principles add
continuation across waits, release iterations and lessons shared across runs.
The hub's committed [L3 gap table](https://github.com/ssheleg/sshlg-skills/blob/392e8f3787d37a32ca1ebc261addee3cdea6994e/docs/evidence/specs/2026-10-13-pipeline-principles-gaps.md)
separates these requirements from previously identified follow-up requests.

The review read PR112's new iteration doctrine, continuity, stage/command/wave
changes, lesson index, inventory assignment, graph certification changes and
their component tests. It did not rerun the full npm suite or hosted CI. The
prior PR115 verdict covered fixture targeting and CLI admission only; it did
not certify this larger payload.

## Findings observed before correction

1. **Unknown lesson sources became measured zero.** Seed a valid lesson through
   `lessons.py add`, then run `rebuild --roots <missing-directory>`: exit 0,
   the prior nonempty index becomes zero bytes, and no source warning prints.
   Repeating with an unreadable retro also exits 0 and erases the projection,
   although this time `not read` prints. Discovery used `os.walk` without an
   error callback; `cmd_rebuild` replaced the index even after source failures.
2. **An ambiguous plan was accepted.** Two nodes with the same id, or different
   canvas ids with the same `graph_id`, reach `sync-graph` successfully. A
   synthetic pair with waves 2/4 and risks R3/R1 generated multiple revisions
   and a hybrid final wave 4/risk R3. `load_plan` validated fields but not node
   identity or effective target uniqueness.
3. **An unsuccessful operation could change state.** Default `sync-graph`
   changed present nodes before reporting an absent target and exiting 1;
   the original test explicitly expected this. `assign --write` similarly
   cleared prior derived assignments before returning 1 for an unclaimed or
   unplaced item. This contradicted the advertised refusal-without-write
   contract and made a caller's retry start from changed state.

All plants used synthetic files and disposable Git repositories. The first
new preservation and duplicate-plan controls failed on the original source;
then the assignment control independently failed before its correction.
No real lesson index, host configuration, foreign repository or provider was
written by these controls.

## Corrected contract

- [lessons.py](../../../plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py)
  collects discovery/read/parse/commit problems and refuses an incomplete
  rebuild **before** opening the index session, migration, lock directory or
  replacement. Missing/non-directory roots, unreadable subtrees/retros,
  malformed artifact configuration and unresolved lesson evidence are not an
  empty corpus. Remaining readable sources are still scanned so their errors
  can be reported together.
- The caller still selects rebuild scope through `--roots` and `--depth`.
  A complete, explicitly selected empty scope may produce an empty projection.
  Rebuild is not an additive merge of arbitrary outside roots. The canonical
  retro remains the source; existing corrupt-index backup and future-format
  preservation behavior remains covered by the component suite.
- [waves.py](../../../plugins/task-pipeline/skills/task-pipeline/scripts/waves.py)
  rejects repeated node ids, repeated effective graph targets and malformed
  `graph_id`. A multi-repository plan must supply an unambiguous projection for
  this graph; `--only-present` cannot disambiguate two meanings for one target.
- Default graph sync rejects absent targets before changing any node.
  `--only-present` remains the explicit supported partial projection. An
  incomplete assignment prints its gaps but does not replace the inventory.
  Complete assignment, carried items and successful recuts retain their
  existing behavior.

The source homes [iteration.md](../../../plugins/task-pipeline/skills/task-pipeline/references/iteration.md)
and [waves.md](../../../plugins/task-pipeline/skills/task-pipeline/references/waves.md)
state these boundaries in the same change.

## Checks actually run

| Check | Observed result |
|---|---|
| New isolated preservation and plan controls before fixes | Failures reproduced, including zero-byte index and changed inventory |
| `python3 test/lessons_test.py` | PASS, 101 cases |
| `python3 test/waves_test.py` | PASS, 85 cases |
| `python3 test/continuity_doc_test.py` | PASS, 21 cases |
| `python3 test/validate.py` | PASS; three disclosed unlooked categories retained |
| `git diff --check` | Exit 0 |

The new functions `conservative_rebuild_controls` and
`conservative_plan_controls` add 16 component cases in total. Existing tests
were corrected where they explicitly endorsed partial writes. Positive
controls retain readable-empty rebuild, explicit partial graph projection,
complete assignment, idempotence, risk lowering with a reason, and carried
inventory items. The lesson suite prints its external engine-redactor case as
SKIPPED because `OBSERVATORY_ENGINE_DIR` is unset; no live Observatory/provider
integration or native-model quality is claimed.

## Business-semantics verdict and exact next task

The reviewed doctrine supplies the requested survey/design/build/verify/
release/post-release/next-pool loop. Risk-based passing rounds, the adversarial
R3 round and a separate release gate have explicit source homes. Continuity
recognizes standing authority and durable waits without inventing authority.
Lessons are an advisory/reusable projection of canonical retros; a successful
script does not prove that a model used the right lesson or performed a blind
review. Those remain behavioral acceptance questions.

**The original candidate requires the state fixes above before acceptance.**
Once another reviewer accepts this fix, integrate it into PR112, combine the
separately reviewed PR114 change under its owner, then run the accumulated
candidate's required local and eligible hosted gates. Merge, version, release
and installed readback remain the coordinator's next tasks. A pushed fix
branch is neither a release nor proof of installed behavior.

The L3 requests for distinct waiting-node state, explicit release authority
fields, package install/readback doctrine, cross-project ask routing and
promotion follow-up are not silently closed by PR112. Retain them in their
owning backlog and evaluate them as the next packet. Do not rewrite the full
release design inside this bounded lossless-state correction.

---

**Made with [ssheleg skills](https://github.com/ssheleg/sshlg-skills)**

- [`task-pipeline`](https://github.com/ssheleg/task-pipeline) — reviewed release iteration and repaired state transitions
- [`agent-sync`](https://github.com/ssheleg/agent-sync) — held the isolated review task lease
- [`evidence-docs`](https://github.com/ssheleg/task-pipeline) — bound claims to counterexamples and component checks
