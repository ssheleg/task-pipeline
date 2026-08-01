# Host conventions (stage 0 harvest, stages 6–10)

The orchestrator is project-agnostic. For tests / lint / deploy / docs / wiki it reads the
**host project's `CLAUDE.md` / `AGENTS.md` first**, then falls back to detection.
The same files are the stage-0 harvest's first stop — they are where a project
names its doc repos, its knowledge base and its house rules
([`knowledge-sources.md`](knowledge-sources.md)).
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
- **Start from the stage-0 source ledger** ([`knowledge-sources.md`](knowledge-sources.md)):
  the sources the harvest read are the sources this stage updates. Anything the run
  proved stale is already listed there with what's wrong.
- Host self-update rules (module docs, runbooks, agent-self cards, etc.) — update
  in the same change. Fix dangling links.
- **The design destination, on a project with no `docs/ux/`.** When the work uses
  Figma but super-ux isn't in play, there is no `foundation.md` to hold the file, so
  the brief is canonical — and a brief is per-run. Write the team and the file URL
  into the host's own docs (`CLAUDE.md`, or the README) in this change, so the next
  run reads the destination instead of creating a second file
  ([`grill.md`](grill.md) → *The design destination*).
- **The code graph:** [graphify](https://github.com/Graphify-Labs/graphify) —
  `/graphify . --update` when `graphify-out/` exists, in the same change as the docs
  and the wiki ([`knowledge-graph.md`](knowledge-graph.md)). It is derived, so
  `graphify-out/` is git-ignored unless the project's own `CLAUDE.md` says the team
  commits it. A project that uses a different graph/index tool names its refresh
  command there, and that wins.
- **Wiki:** [obsidian-wiki](https://github.com/ar9av/obsidian-wiki) — the
  `wiki-update` skill (resolves the vault via `~/.obsidian-wiki/config`). Detect it
  the same way the harvest does; if absent, recommend it once
  (`pip install obsidian-wiki` → `obsidian-wiki setup --vault <path>`) and continue.
  A project may of course use a different knowledge base — then its own
  `CLAUDE.md` names the sync command, and that wins.
- **Docs in another repository** (a docs repo, a submodule, a sibling checkout the
  project names): updating it is **outward** — propose the change, get an explicit
  operator go, open a PR there. Never push to a repo the task didn't name.

## Issue tracker (stage 10)

Acceptance parks what wasn't delivered: every `deferred` REQ and every unresolved
carry-over row needs a **home** — an issue, a backlog entry, a ticket id. Read the
host's convention (`CLAUDE.md` usually names the tracker and the id format; else
detect: a `.github/ISSUE_TEMPLATE/`, a Linear/Jira reference in recent commits, a
`TODO.md`). Never invent a tracker, and never close a run on "we'll remember it" —
if no tracker exists, write the row into the repo's backlog file and say where it
went.
