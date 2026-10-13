<sub>ssheleg skills — task-pipeline · agent-sync · evidence-docs · make-skill · copywriting</sub>

# L3: authority, waits and release acceptance doctrine

Base: [0fec61250e8e4314a96edc15887834e0e978f26d](https://github.com/ssheleg/task-pipeline/commit/0fec61250e8e4314a96edc15887834e0e978f26d), the corrected PR112
candidate reviewed separately in
[the state review](2026-10-13-pr112-state-review.md). This packet changes
instructions and one generated reference, not graph state or release automation.
The source of the requested deltas is the hub's
[L3 gap table](https://github.com/ssheleg/sshlg-skills/blob/392e8f3787d37a32ca1ebc261addee3cdea6994e/docs/evidence/specs/2026-10-13-pipeline-principles-gaps.md).

## Contract map

| Request | Source home and resulting rule |
|---|---|
| TP-1, blocked frontier | [waves.md](../../../plugins/task-pipeline/skills/task-pipeline/references/waves.md) and [continuity.md](../../../plugins/task-pipeline/skills/task-pipeline/references/continuity.md): inspect recorded reasons, put external waits on watchers and use durable triggers when needed. Exit 4 alone proves neither completion nor a human gate. |
| TP-3, findings outside the wave | The close pass fixes its own nodes. Other findings join the inventory; the closed hotfix lane remains the exception. |
| TP-4/5, specific standing authority | [SKILL.md](../../../plugins/task-pipeline/skills/task-pipeline/SKILL.md), command, Cursor rule, gates, continuity and stage 7 now agree: cite explicit authority naming the act, otherwise wait. A generic loop flag and a passing test cannot supply authority. Release authority does not silently authorize a separate deployment. |
| TP-7/9, release watchers | [deploy-targets.md](../../../plugins/task-pipeline/skills/task-pipeline/references/deploy-targets.md): tag-bound watchers continue stage 8 after success; reviewer notifications retain the verified direct link and a stable event id where the host names a channel. An unavailable channel is disclosed, not replaced by an invented recipient. |
| TP-8, installed acceptance | Verify published version, update existing installs in the authorized scope, read back versions/payloads and run supported consumer checks. Readable files, native discovery and model/task quality are separate claims. A package is not assigned an imaginary server health URL. |
| TP-10, project asks | [iteration.md](../../../plugins/task-pipeline/skills/task-pipeline/references/iteration.md): asks go to the owning Project through a declared board, with stable ids. If that board is unavailable, keep a pending submission locally; do not work around it via a session or foreign file. The canvas names durable owners. |
| TP-11, promotion follow-up | Stage 10 prints lesson candidates even without `retro.publish`; reuse or create a durable assessment row keyed by lesson id. Candidate status is not publication authority. |

The original gap table proposed a repository-issue fallback even when a
configured board was unavailable. That fallback is deliberately not adopted:
the current operator rule says to disclose an unavailable board rather than
work around it. A project's accepted handoff channel remains usable where no
board is declared and send authority already covers it.

## Checks and boundaries

- `python3 test/continuity_doc_test.py`: PASS, 21 checks.
- `python3 test/release_approval_test.py`: PASS, 20 checks.
- `python3 test/audit_regressions/fix-ed-01.01.py --sync` regenerated the
  evidence-docs projection; its read-only check passed all four assertions,
  including isolated link closure and byte equality with the source home.
- The installed make-skill auditor, `audit_skill.py --house` over the shipped
  task-pipeline skill: 19 PASS, zero GAP. Measured body budget is 4724 tokens
  with `tiktoken:cl100k_base`, within the 4750 working limit. Before this
  change it was 4714. Frontmatter, including the 887-character description,
  is byte-identical. This is a conformance check, not a token-savings claim.
- The canonical family brand linter ran read-only against its declared hub corpus:
  exit 2, 56 errors and 433 warnings. Those findings name the existing hub/site
  sources, not the edited member changelog. This is not a green brand verdict or
  a check of member source coverage; the shared pack documents the raw-HTML
  numeric-scan limitation. The narrow release-note edit was read against the
  canonical voice/terminology and its executable lesson tests.
- `git diff --check`: exit 0. No model or provider evaluation was performed.

The separate full `npm test` at the base PR116 candidate exited 0 with a clean
worktree. Its [machine receipt](2026-10-13-pr116-owner-full.json) and
[sanitized full output](2026-10-13-pr116-owner-full.txt) bind to that exact SHA,
not to this later doctrine diff. After all eligible hosted jobs passed in run
[38344001686](https://github.com/ssheleg/task-pipeline/actions/runs/38344001686), the reviewed fix merged through PR116 as
[52be1037](https://github.com/ssheleg/task-pipeline/commit/52be103706d3f53b22f2ca28e4896079b2d48b67) into `feat/release-iteration`.
It was not released. The original log hash is retained; only
literal checkout/home prefixes were sanitized. The external engine-redactor
case is explicitly skipped without its checkout. This packet has not rerun
the full owner suite or hosted checks.

## Independent-review follow-up

The parent review of [5e8890bb8c12e269399847593ce8376ba3eb14e6](https://github.com/ssheleg/task-pipeline/commit/5e8890bb8c12e269399847593ce8376ba3eb14e6) found
contradictory summaries left in the stage definition, loop-arming limit and gate
floor. Those paragraphs now recognize an existing act-specific authorization
with its source and scope. A generic loop flag still supplies none.

The review also found that the broad standing-authority exception grammatically
covered sign-ins, consents and payments. The human boundary in both waves and
iteration now states separately that sign-ins, consents, operator payments and
typed secrets remain human. The exception applies only to other outward acts
within their recorded authority. Question rounds batch only human-owned
questions; external waits get watchers and project-owned questions follow the
declared Project-board route. The loop summaries use the same classification.

Validation of the follow-up:

- `python3 test/continuity_doc_test.py`: the new section-scoped checks first
  failed against the prior source at the stage definition; corrected source
  passes **31** checks, up from 21. This is a bounded doctrine check, not a
  model-behavior evaluation.
- Five isolated copies each restored one prior reference from [5e8890b](https://github.com/ssheleg/task-pipeline/commit/5e8890bb8c12e269399847593ce8376ba3eb14e6)
  (`stages`, `continuity`, `gates`, `waves`, `iteration`); all five exited 1
  with their intended section-specific diagnostic. The working files were
  never changed by these negative controls.
- `python3 test/release_approval_test.py`: **20** checks pass.
- Generated evidence-docs gates reference refreshed through the existing
  `fix-ed-01.01.py --sync`; its read-only check passes **4** assertions.
- `git diff --check`: exit 0. No broad suite, provider or native-host test
  was rerun for this follow-up.

## Handoff and exact next task

Independent review must check that a standing instruction is an existing
act-specific grant, not an inferred override of human consent, payments or
unrelated deployments. Also check that a blocked frontier is never labelled
finished and that board unavailability does not authorize a different channel.
After review, integrate this packet into the accumulated release-iteration
candidate and run its final gates once. No publication or installed-update
claim belongs to this branch.

TP-2 (a distinct graph waiting state) and TP-6 (`release.authorized_by` schema)
remain separate implementation packets. This change documents the current
exit-4 limitation rather than pretending the new state exists. Remaining
native behavioral acceptance and package/install evidence stay open after a
documentation pass.

The Unreleased lesson bullet now states the conservative rebuild contract and names
`python3 test/lessons_test.py` as its evidence. Copywriting used the canonical
[family brand pack](https://github.com/ssheleg/sshlg-skills/tree/77215a5/docs/brand),
whose README explicitly owns release notes across family repositories. Voice,
terminology, facts and the Release note channel were read; no second member voice
was created. An earlier assumption that a missing local pack prevented this edit
was corrected after checking the shared pack's ownership.

Humanization: on, own pass; the factual correction retains product terms and the
source's causal direction, adds no unsupported number, and needed no stylistic
rewrite after drafting. This is a scoped prose reading, not a claim about authorship.

---

**Made with [ssheleg skills](https://github.com/ssheleg/sshlg-skills)**

- [`task-pipeline`](https://github.com/ssheleg/task-pipeline) — reconciled L3 doctrine with operator intent
- [`agent-sync`](https://github.com/ssheleg/agent-sync) — held task and file ownership
- [`evidence-docs`](https://github.com/ssheleg/task-pipeline) — traced claims and retained full gate evidence
- [`make-skill`](https://github.com/ssheleg/make-skill) — measured shipped skill budget and checked payload

- [`copywriting`](https://github.com/ssheleg/super-ux) — applied the shared family release-note voice to a factual correction
