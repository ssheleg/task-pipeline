# FW07 — local-tag-aware release admission packet

Source-only proposal, 2026-10-13. No implementation, tag mutation, complete suite,
publication or installed behavior is claimed by this packet. Owner source is
[78c42124](https://github.com/ssheleg/task-pipeline/commit/78c42124db910c56e74c8fbd524bdc9a4f8fb6c9).
The objective is to execute the existing release obligation against the exact
locally tagged candidate, while preserving every published tag and all failed evidence.

## Recovered failure and authority

The actual failed release is
[run 38386280311](https://github.com/ssheleg/task-pipeline/actions/runs/38386280311).
Its immutable annotated v1.94.0 object is
`9def0fa8fe361b9abc71e2ecefd09b14f83c9421`, pointing at the owner source above.
The release job failed its first structural check because v1.94.0 appeared in no
run stamp or bold no-stamp declaration; publish was skipped. The coordinator's
[admission correction and preserved outputs](https://github.com/ssheleg/sshlg-skills/tree/85d1758e02cbf1759be861a7af2108d267c339a3/docs/evidence/completion-1013/tp-current-gate)
explain the mistaken substitution of PR evidence for the complete local gate.
The remote tag must never be moved or deleted. A stopped earlier full run remains
stopped, and a passing branch check is not converted into a passing tagged run.

The source also contains a real instruction conflict:

| Source at the frozen owner commit | Observed meaning |
|---|---|
| `pipeline.json` stage 7 gate.check | Chains the full suite before `git tag -a`, then tag push. |
| `docs/evidence/retro.md` R-010 | Explicitly says tag locally first, run the release suite, then inspect unlooked disclosures. |
| `plugins/task-pipeline/hooks/release-gate.sh` outward() | Treats local `git tag` creation as an outward act and gates it on the run ledger. It does not bind an exact tag object to a complete local suite receipt. |
| `.github/workflows/release.yml` | Checks out the selected tag, checks annotation and default-branch reachability, then runs `npm run test:all`. This release check correctly refused the source. |
| `test/validate.py` release-gap section | Uses local `git tag -l v* --sort=v:refname`, and reads run stamps and bold no-stamp declarations. It discloses unusable Git or absent tags in unlooked. |
| `CONTRIBUTING.md` | Describes structural versus negative/full checks, but is not the sole release authority. |

R-010 and the stricter tagged-tree observation govern the proposed correction.
This is not a new operator approval requirement. The release author still must
obey current project authority and any actual environment approval; a mechanism
cannot manufacture either.

## Minimal policy correction, separate from the patch release

Proposed stage-7 wording: prepare an owned, unpublished annotated candidate tag at
the exact accepted commit; run `npm run test:all` with that tag visible; inspect the
release-stamp unlooked disclosure; publish only the same tag object after the exact
successful receipt and source/ref recheck. Chain admission and the outward push so
a failed or interrupted suite cannot be followed by publication. “Do not publish
before the complete tagged-tree gate passes” replaces the ambiguous “never tag
before the suite.” No short test command or tree-equivalent PR result substitutes.

The hook's local-candidate treatment needs a separate bounded design and tests.
Do not simply remove all tag recognition: tag pushes, release creation and npm
publication remain outward acts. A proposed helper must offer an explicit local
prepare operation and an independently checked publish operation, so the hook can
recognize the narrow preparation path without granting publication. This packet
makes no claim that a generic shell hook is an unbypassable security boundary.

Fresh's separate v1.94.1 metadata/no-stamp repair owns its candidate and receipt.
This plan does not edit that repair, its local tag, its ledger or its release gate.
Resolve this policy wording in a separately reviewed change; do not silently widen
that patch candidate.

## Proposed implementation contract

1. Use an isolated Git directory, not only an isolated working tree. A task-owned
   full clone fetches published tags and the actual default branch. Validate a clean
   exact commit, version agreement, full history and default-branch reachability.
   Do not trust an arbitrary directory or caller-supplied success file.
2. Prepare only an explicitly owned, unpublished annotated candidate tag. Verify
   remote absence before creation. Existing remote tags are immutable, including
   failed versions. Adopting an existing local tag requires its recorded owner,
   annotation object and peeled commit to agree; ambiguous ownership refuses.
3. Execute the repository's fixed complete `npm run test:all` command with that tag
   visible. Capture exit, interruptions and disk-stop outcomes without pipelines
   laundering status. Preserve full output; check the release-gap observation and
   disclosed unlooked conditions. No subset or caller-selected replacement suite.
4. A successful receipt records repository/remote identity, commit/tree, tag name,
   annotation object and peel, package/suite-definition identity, command, start/end,
   exit, log digest and checked unlooked disposition. Failed/incomplete receipts
   cannot admit publication. A receipt is execution evidence, not a signature of
   operator authority or proof against a hostile local process.
5. Immediately before the outward push, recheck candidate source cleanliness,
   commit/tree, tag object/peel, remote state and default-branch reachability.
   Changed source, changed tag, absent/truncated/mismatched receipt, or failed gate
   refuses. Push the explicit single verified ref, never all tags or force.
6. A normal merge that changes the accepted commit invalidates the prior result.
   Recreate only the task-owned unpublished candidate after comparing its prior
   object; rerun the exact tagged-tree gate. Never retarget a published ref. Failed
   preparation or test leaves recoverable ownership/evidence, not a claimed release.

The source scanner sees **all local version tags**, not only tags ancestral to HEAD.
Git worktrees share these refs. A sibling candidate can therefore change an older
checkout's release-gap inputs. This is a source-derived interference risk, not an
executed new defect claim. The proposed full clone avoids sharing unpublished refs;
it must still include all published release history and the candidate itself. Do
not “fix” the guard by filtering away history merely to obtain a passing result.

## Frozen acceptance for the next implementation wave

Use task-owned local bare remotes and bounded fixture suites through a test seam;
the production entry must keep the complete fixed owner command. No real remote tag
or provider operation is needed to test refusal and receipt identity.

| Control | Required result |
|---|---|
| Missing, lightweight, wrong-commit or unowned existing candidate | Refuse before publication; preserve foreign refs. |
| Published tag already exists, including failed v1.94.0 | Refuse mutation; no delete/force/update. |
| Dirty source, shallow/missing history or unreachable accepted commit | Refuse with the missing prerequisite recorded. |
| Tag absent while branch suite passes | Cannot become tagged-tree acceptance. |
| Suite nonzero, interrupted or disk-stopped | Failure retained; no push. |
| Release-gap check unlooked | No tagged-tree admission from exit zero alone. |
| Tag/source/receipt changed after passing | Refuse the outward operation. |
| Complete clean exact candidate and valid receipt | One explicit tag ref reaches the fixture remote. |
| Shared worktree has another unpublished version tag | Demonstrate input interference; dedicated clone has only fetched published tags plus its owned candidate. |
| Local prepare and actual outward push through hook | Preparation route works under its explicit contract; outward gate remains enforced. |
| Normal squash/merge produces a different SHA | Prior evidence stays historical; new exact candidate requires its own complete result. |

Each failure must be demonstrated before claiming its guard works. Independently
review source/ref ownership and hook admission separately from the full owner suite.
Native Claude/Codex hook execution, race resistance and adversarial receipt integrity
are not established by these subprocess fixtures. Production publication still needs
all release jobs and immutable npm payload readback after normal integration.

## Handoff

Completed: recovered the failed release evidence, identified the conflicting stage-7
chain and R-010 requirement, mapped the hook/workflow/validator consumers, and froze
this proposed contract. No source or workflow implementation changed.

Exact next task: coordinator reviews this packet and chooses the minimal policy and
helper interface. Then an isolated implementation branch adds source-first negative
controls, reconciles the stage-7 wording and narrow hook route together, obtains
independent review, and enters the serialized complete owner gate. Keep FW07 stage
extraction, checkpoint correction and the v1.94.1 metadata repair distinct.
