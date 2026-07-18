# Host conventions (stages 6–8)

The orchestrator is project-agnostic. For lint / deploy / docs / wiki it reads the
**host project's `CLAUDE.md` / `AGENTS.md` first**, then falls back to detection.
Prefer explicit host instructions over detection; if a step's convention can't be
found, surface it and **ask** rather than guessing.

## Lint + test
- `CLAUDE.md` usually names the commands. Else detect: `package.json` scripts
  (`npm test` / `npm run lint`), `pyproject.toml` / `ruff` (`ruff check`), `pytest`,
  `Makefile` targets, `.golangci.yml`, `cargo test`.

## Deploy
- `CLAUDE.md` deploy section (e.g. deploy-from-main rule, Heroku auto-deploy on
  push, `Procfile`). Else detect: `Procfile` / heroku remote, `Dockerfile`,
  `.github/workflows/*.yml`, Vercel / Netlify config. **Never invent a deploy
  path** — if none is discoverable, ask.

## Post-deploy logs
- Heroku: `heroku logs -a <app>`. Docker / k8s: `docker logs` / `kubectl logs`.
  CI: the workflow run. Hit the health endpoint if one is defined.

## Docs + wiki
- Host self-update rules (module docs, runbooks, agent-self cards, etc.) — update
  in the same change. Wiki: the `wiki-update` skill (resolves the vault via
  `~/.obsidian-wiki/config`). Fix dangling links.
