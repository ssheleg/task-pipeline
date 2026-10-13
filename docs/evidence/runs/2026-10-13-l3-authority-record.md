<sub>ssheleg skills — task-pipeline · agent-sync · evidence-docs</sub>

# L3 TP-6: record the source of release authority

Base: `40070a0765e16423cf0c78c54b51a811c290fb62`, the reviewed L3 doctrine
candidate in [PR117](https://github.com/ssheleg/task-pipeline/pull/117).
Requested contract: TP-6 in the hub's
[principles gap table](https://github.com/ssheleg/sshlg-skills/blob/392e8f3787d37a32ca1ebc261addee3cdea6994e/docs/evidence/specs/2026-10-13-pipeline-principles-gaps.md).

## Change and authority boundary

The optional `release.authorized_by` field in
[pipeline.schema.json](../../../plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json)
records a nonblank, single-line source locator for an existing grant. Empty,
whitespace-only, multiline and non-string values are refused. Existing
configurations remain valid when the field is absent. The example configuration
contains no fabricated grant.

[Stage 7](../../../plugins/task-pipeline/skills/task-pipeline/references/stages.md)
and [the release approval doctrine](../../../plugins/task-pipeline/skills/task-pipeline/references/deploy-targets.md)
require reading the source and checking the issuer's authority, currentness, act
and scope. A locator is not authorization. A missing, unreadable or ambiguous
source cannot establish a grant. Absence means inspect existing recorded
authority before asking, rather than asking again solely because this new field
is unset. `approval: checks` and `release.authorized_by` remain separate facts.
Human-only actions stay human; release authority does not cover an unrelated
deployment or message.

No release script reads this new field. Like the existing approval-mode setting,
it is a declarative input to the agent's stage-7 decision. Schema validation
proves the locator's shape only, not its truth, the source's existence or an
issuer's authority. No actual release, host setting or private grant was changed.

## Verification

- `python3 test/release_approval_test.py`: the added case first failed at
  `release.authorized_by has an explicit source-locator contract` on the base.
  Corrected source passes **41** checks, up from 20. `jsonschema` was available:
  full example documents accept two locator forms and absence, and refuse
  eleven invalid values, including trailing LF and CR. Section-scoped checks
  require both doctrine homes to distinguish a locator from authority.
- `python3 test/continuity_doc_test.py`: **31** checks pass.
- `python3 test/validate.py`: exit 0, structure valid. Its existing three
  `unlooked` categories remain disclosed (coordination, backlog citations,
  routed triggers). No broad-suite or model-behavior verdict is inferred.
- `git diff --check`: exit 0.

## Next task and integration

Review this packet independently, then integrate after PR117 using normal required
checks. The full local gate of PR117 belongs to its exact earlier source; it does
not certify this schema addition. No release or installed acceptance is claimed.

TP-2 remains separate: add an explicit watched-wait node state and a distinct
`next` outcome without turning a human/mixed frontier into a wait-only result.
The current execution-authority commands already use exit 5 for lease contention;
use an unambiguous new `next` code rather than describing 5 as globally waiting.
A pending consumer held transitively by watched waits needs classification across
wave boundaries. Waiting metadata is a record of a watcher, not proof that it is
alive or that its eventual action is authorized.

Before adding wait/resume mutations, address the existing lock contract explicitly:
`graph.py` class `held` currently continues unlocked when `fcntl` is unavailable
or a lock raises `OSError`. Reusing that helper alone would not establish a
fail-closed concurrency guarantee. Reproduce the bounded failure and choose the
compatibility behavior with the owner before changing unrelated mutation verbs.

---

**Made with [ssheleg skills](https://github.com/ssheleg/sshlg-skills)**

- [`task-pipeline`](https://github.com/ssheleg/task-pipeline) — bounded schema and doctrine packet
- [`agent-sync`](https://github.com/ssheleg/agent-sync) — task lease
- [`evidence-docs`](https://github.com/ssheleg/task-pipeline) — source-bound validation receipt
