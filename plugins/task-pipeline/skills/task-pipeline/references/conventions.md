# Host conventions (stage 0 harvest, stages 6–10)

The orchestrator is project-agnostic. For tests / lint / deploy / docs / wiki it reads the
**host project's `CLAUDE.md` / `AGENTS.md` first**, then falls back to detection.
The same files are the stage-0 harvest's first stop — they are where a project
names its doc repos, its knowledge base and its house rules
([`knowledge-sources.md`](knowledge-sources.md)).
Prefer explicit host instructions over detection; if a step's convention can't be
found, surface it and **ask** rather than guessing.

## Contents

- Lint + test
- Deploy / release
- Post-deploy logs
- The CI verdict — read the run, never assume it
- Docs + wiki
- Documentation regime (stage 0, then 9 and 10)
- Issue tracker (stage 10)

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
  Hit the health endpoint if one is defined. **CI: the workflow run — and a run is
  checked by reading it, below.**

## The CI verdict — read the run, never assume it

A push either triggered a run or it did not, and either way **the run's own reply is
the only evidence** ([`gates.md`](gates.md) → *False success*). "CI is green" written
without a command behind it is a sentence that prints the same whether it looked or
not.

This is not hypothetical. On 2026-08-06 this repository's `validate` was
`completed/failure` on a push to `main` and on a release tag. The failure was
**correct** — the *Every v\* tag must be contained in main* guard firing on a tag that
was not yet an ancestor — and nothing in this bundle obliged anyone to read it. A
guard nobody reads is a fail-open hook with extra steps.

```bash
# authenticated
gh run list --branch <branch> --limit 1 \
  --json databaseId,name,status,conclusion,headSha
gh run view <databaseId> --log-failed        # only when conclusion != success
```

```bash
# unauthenticated fallback — public repo, no token needed
curl -s "https://api.github.com/repos/<owner>/<repo>/commits/<sha>/check-runs"
```

**Two paths on purpose.** A credential problem must not end the check: this repo's
`gh` token expired mid-run the same night, and `gh auth status` reported it invalid
from a **cached** verdict while `gh api user` succeeded. Probe credentials with a
live call, never with the status command.

**Three states, and the third is why this is written down:**

| State | Condition | Record |
|---|---|---|
| **concluded** | a run exists for this sha, `status == completed` | the conclusion and run id — and on any non-`success`, the **quoted failing step** |
| **in progress** | a run exists, not finished | wait and re-read. *"It was still running when I looked"* is a report, not a verdict |
| **no run found** | no run for this sha | say so out loud — a project without CI is a legitimate state and **not a green one** ([`gates.md`](gates.md) → *Progressive arming*) |

**Read the log, not just the verdict.** A conclusion says *that* it failed; only the
log says *what*. In the incident above the log named the guard, the orphan tag and the
one-line fix — a bare "CI failed" would have handed the next reader a search the log
had already finished. On any non-`success`: read the failing step and quote the line
that names the failure.

**It reports; it does not block.** Same shape stage 8 already uses for deploy logs — a
red run the operator has seen and ruled on is a decision, a red run nobody printed is
the failure. Blocking would also make a project *without* CI cheaper to ship from than
one with it.

**Promote it when it breaks** ([`gates.md`](gates.md) → *Axis B*): this sits at rung 2,
a criterion in the stage gates. Promote it to a script the first time a run is observed
closing a stage with an unread CI verdict.

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

## Documentation regime (stage 0, then 9 and 10)

The host's `CLAUDE.md`/`AGENTS.md` wins over anything detected — read it first.
Then detect, in this order ([`documentation.md`](documentation.md)):

| Look for | Means |
|---|---|
| `docs/DOCMAP.md` | the inventory has been done; read it, extend it, do not re-seed |
| `docs/adr/` with at least one `NNNN-*.md` | **that is the register.** Record it in the doc map; never seed a second decision home beside it |
| `docs/DECISIONS.md` | the register shape; note its id scheme and its "Next free ID" line |
| a decisions/ADR section inside `AGENTS.md` or `CONTRIBUTING.md` | the rules live there; the doc map holds a **pointer**, not a copy |
| a `check-docs`, `lint:docs`, `docs` target in `package.json`/`Makefile`/CI | the documentation gate already exists — use it, and read its scope header |
| none of the above | **seed the set**: `docmap.md`, `decisions.md`, `open-questions.md` and `docgate.sh` from [`../templates/`](../templates/README.md), and record the seeding as the register's first entry |

Two rules that are not negotiable when seeding: the gate must exit `0` on the seeds
themselves, and the registers must be useful at three entries. A project whose gate
is red on day one has learned that the gate is noise, and nothing later un-teaches
that.

## Issue tracker (stage 10)

Acceptance parks what wasn't delivered: every `deferred` REQ and every unresolved
carry-over row needs a **home** — an issue, a backlog entry, a ticket id. Read the
host's convention (`CLAUDE.md` usually names the tracker and the id format; else
detect: a `.github/ISSUE_TEMPLATE/`, a Linear/Jira reference in recent commits, a
`TODO.md`). Never invent a tracker, and never close a run on "we'll remember it" —
if no tracker exists, write the row into the repo's backlog file and say where it
went.
