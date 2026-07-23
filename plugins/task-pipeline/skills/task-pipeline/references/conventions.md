# Host conventions (stages 6–9)

The orchestrator is project-agnostic. For tests / lint / deploy / docs / wiki it reads the
**host project's `CLAUDE.md` / `AGENTS.md` first**, then falls back to detection.
Prefer explicit host instructions over detection; if a step's convention can't be
found, surface it and **ask** rather than guessing.

## Lint + test
- `CLAUDE.md` usually names the commands. Else detect: `package.json` scripts
  (`npm test` / `npm run lint`), `pyproject.toml` / `ruff` (`ruff check`), `pytest`,
  `Makefile` targets, `.golangci.yml`, `cargo test`.
- **UI projects:** the super-ux linter (`python3 docs/ux/lint.py` / `/ux-lint`) is
  part of lint — run it too; it must pass (no UX drift).

## Deploy / release
- `CLAUDE.md` deploy section (e.g. deploy-from-main rule, Heroku auto-deploy on
  push, `Procfile`). Else detect: `Procfile` / heroku remote, `Dockerfile`,
  `.github/workflows/*.yml`, Vercel / Netlify config. **Never invent a deploy
  path** — if none is discoverable, ask.
- **Release automation is project-configurable and individually toggleable.** If
  the project declares a `release` block (see `pipeline.schema.json`; this repo's
  own is in `pipeline.example.json`) with `enabled: true`, that block's `steps`
  are the deploy, and its `verify` list is the stage-8 post-deploy check. Off (or
  omitted) → no release automation; deploy by the host convention above. This
  repo's reference implementation is `.github/workflows/release.yml`, armed per
  repo via the `RELEASE_ENABLED` variable — copy and adapt it, don't assume it.

## Post-deploy logs
- Heroku: `heroku logs -a <app>`. Docker / k8s: `docker logs` / `kubectl logs`.
  CI: the workflow run. Hit the health endpoint if one is defined.

## Docs + wiki
- Host self-update rules (module docs, runbooks, agent-self cards, etc.) — update
  in the same change. Wiki: the `wiki-update` skill (resolves the vault via
  `~/.obsidian-wiki/config`). Fix dangling links.
