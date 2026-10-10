# Portable host delivery — 2026-10-09

Candidate v1.90.1 from `33a7066388912d66501989e3a9760fedc1dc0bf5`.
The four tier procedures now travel inside `task-pipeline/assets/`; a test compares
their exact bodies with plugin agents. Host-specific frontmatter stays in agents/.
The local `project-audit/references/portable-method.md` carries the standalone floor;
no sibling install or remote instructions are needed. Hook capability is distinct
from registration and verified refusal by this package's adapter.

## Validation

- Final regression test on the old pinned snapshot: exit 1 for absent portable
  verifier; [captured output](host-portability-red.txt).
- Candidate `python3 test/audit_regressions/host-portability.py`: exit 0, isolated
  payload closure, missing-procedure negative, and offline JSON/HTML produced by
  the actual collector with no companion installed.
- The collector fixture is a committed README-only repository with no deployment
  or provider receipt. It proves packaging and actual artifact production. It
  does not measure a model's judgment of the new prose: that is NOT_RUN.
- make-skill 0.29.1 `audit_skill.py --house --quiet`: task-pipeline and project-audit
  each 0 GAP / 19 PASS after the draft exceeded headroom and was corrected.
- Both `claude plugin validate ... --strict` commands: exit 0.
- `npm test` on [a121c38c69db8a4d998a4af9202141fc97ad65c8](https://github.com/ssheleg/task-pipeline/commit/a121c38c69db8a4d998a4af9202141fc97ad65c8): exit 0 after reviewer corrections.
  See `host-portability-checks.json` for the source identity and log hash.
- Review corrected three contract regressions before delivery: HTML remains opt-in,
  detector acceptance requires planted-defect proof plus opening/closing work-list
  measurement, and inline tier readings cannot certify independent contexts.

No model/provider calls, host configuration changes, release or installation are
part of this source commit. Next: independent review, normal release and parent pin/readback verification. Existing project work is kept.

## v1.90.2 publication recovery

The [v1.90.1 release run](https://github.com/ssheleg/task-pipeline/actions/runs/38003499991)
passed 430 planted-defect guards, 15 property checks, 18 certification mutations,
and the remaining code checks, then failed `npm run test:docs`: four cited source
commits resolved but were not ancestors of the squash-merged tag. The source PR
and local tagged full suite had passed before squash; complete-tree equality did
not establish the ancestry that docgate checks. A local reproduction on the
merged history also exited 1 with those same four citations.

The historical candidate and receipt commits remain explicit immutable GitHub
links. Their identities and original test hashes in `host-portability-checks.json`
are unchanged. No known-dead exemption, gate relaxation, published-tag move, or
replacement of historical test identities is used. The v1.90.1 tag stays public;
its failed workflow did not reach GitHub release/npm publication.

The v1.90.2 patch changes version surfaces and repository evidence only; shipped
skill/runtime payload files are byte-identical to v1.90.1 except plugin manifest
version metadata. Required source CI, independent review and release gates still
apply. After normal squash integration, docgate must run on the actual merged
commit before first pushing the v1.90.2 tag. Publication/registry readbacks remain
pending and will be recorded in the owning family integration report.

Focused recovery checks (before commit): docgate exit 1 on merged v1.90.1 with
those four unreachable references, then exit 0 after the link correction;
`npm test` exit 0; strict plugin and marketplace validation exit 0. Git comparison
of 109 plugin files found only the plugin manifest version changed. Both remote
historical commit URLs returned the exact requested full SHA. Required source CI
and the locally tagged full release suite remain separate pending gates.

Recovery `npm test` log SHA-256: 8dff4393a4883e8f732eb2f2be17c6599ff1f71320e62783496b8cb0d15844d2.
Failed v1.90.1 release-step log SHA-256: 7da95727201bc7347f2aa8d3e02e6b70ee2cb29f8ab36e1a474923ccc1d0f00e.
