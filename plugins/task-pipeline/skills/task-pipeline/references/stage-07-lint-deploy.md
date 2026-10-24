# Stage 7 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 7 — Lint + deploy
- Read host conventions (`conventions.md`): run the linter; fix failures. The suite
  is already green from stage 6 — re-run it if code changed since. For UI projects,
  the **super-ux linter** (`python3 docs/ux/lint.py` / `/ux-lint`) is part of lint —
  it must pass too (no UX drift merges). Then deploy per the project's convention;
  if the project defines release automation (`pipeline.json` → `release`, toggle
  on), that is what "deploy" runs here. **No runbook, or one too thin to act on?
  Write it first** ([`deploy-targets.md`](deploy-targets.md)) — a deploy performed
  from inference about the project is one nobody can repeat or roll back, and the
  operator is standing at this gate anyway. That reference also carries the CLI
  verbs per target for when the runbook names a platform you have to recall.
- **Before the tag, the publish or the deploy, write the release impact card** when the
  project has users (`pipeline.json` → `release.users` is not `none`; absent counts as
  `external`): seed `templates/release-impact.md` to
  `<artifacts>/specs/YYYY-MM-DD-<topic>-release-impact.md`, answer its four sections, link
  the runbook's rollback rather than copy it, and run `python3 scripts/release_impact.py
  check <card.md> --pipeline pipeline.json` to exit 0 ([`release-impact.md`](release-impact.md)).
