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
- `npm test` on `a121c38c69db8a4d998a4af9202141fc97ad65c8`: exit 0 after reviewer corrections.
  See `host-portability-checks.json` for the source identity and log hash.
- Review corrected three contract regressions before delivery: HTML remains opt-in,
  detector acceptance requires planted-defect proof plus opening/closing work-list
  measurement, and inline tier readings cannot certify independent contexts.

No model/provider calls, host configuration changes, release or installation are
part of this source commit. Next: independent review, normal release and parent pin/readback verification. Existing project work is kept.
