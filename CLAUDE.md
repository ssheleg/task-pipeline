# CLAUDE.md — house rules for this repository

Conventions for any agent working in `task-pipeline`. This is the file the
pipeline's own stage-0 harvest reads first, so keep it true.

## What this repo is

A **skill**, not an application. Almost every file is prose an agent will read and
act on. There is no build step and no runtime service; the only executable code is
two installers and the structural validator.

Human-facing entry points: [`README.md`](README.md) (what it is),
[`CONTRIBUTING.md`](CONTRIBUTING.md) (how to change it),
[`CHANGELOG.md`](CHANGELOG.md) (why each release happened).

## Commands

| Job | Command |
|---|---|
| Test | `npm test` (= `python3 test/validate.py`) — must print `PASS: task-pipeline structure valid` |
| Prove the guards | `npm run test:negatives` — feeds every guard a planted defect and requires it to reject one; `npm run test:all` runs both. Corrupt files in **python, never `sed -i`** (not portable; the validator rejects it) |
| Lint | none separate; the validator is the lint |
| Install locally | `./install.sh` or `node bin/task-pipeline.js` — **both refuse when the Claude Code plugin is installed**, because a plain `~/.claude/skills/` copy shadows it; `--force` overrides deliberately |
| Behavioural evals | `python3 evals/run.py` — validates the suite and prints the protocol; it never reports a pass it did not observe |
| Deploy / release | push a `vX.Y.Z` tag → `.github/workflows/release.yml` (armed by the repo variable `RELEASE_ENABLED`) |
| Post-deploy check | the release workflow's own `npx` smoke test; then `npm view task-pipeline-skill version` |

`npm publish` runs in the release workflow's second job, armed per repository by the
variable `PUBLISH_NPMJS` (auth: the `NPM_TOKEN` secret — a **granular automation**
token — or npm trusted publishing via OIDC). Unarmed, it falls back to a human 2FA
step.

## Branch and commit policy

- Small doc/doctrine fixes land on `main`; anything that changes the stage list,
  the gates or a public contract goes on a branch and through a PR.
- **Conventional commits.** Append the version when the change ships one:
  `feat: <what changed>; v0.19.0`.
- Never force-push `main`. Never push a tag before `npm test` is green on the
  commit the tag points at.

## Invariants that must not drift

Full list with reasoning in [`CONTRIBUTING.md`](CONTRIBUTING.md) → *The
invariants*. (No count here on purpose: a hand-written one drifts, and this one
already had — it said sixteen while the list held twenty-four.) The two that bite
most often:

1. **Version sync — every surface below, no number in the name.** `package.json`,
   `.claude-plugin/marketplace.json` (`plugins[0].version`),
   `plugins/task-pipeline/.claude-plugin/plugin.json`, the top `## vX.Y.Z` heading in
   `CHANGELOG.md`, **and the `Version` row of `SKILL-CARD.md`**. This said *four-way*
   and listed four until 2026-08-08 while `test/validate.py` enforced five; the miss
   surfaced on a release bump, from the validator rather than from a reader. The list
   is the count — same reason invariant counts are not written down here.
2. **The stage list lives on every surface below, and the list is the count.** Three
   are compared mechanically — `SKILL.md`'s table, `references/stages.md` and
   `pipeline.example.json` (ids, names **and gate types**, plus each stage's own
   doctrine file). The rest enumerate the flow for a human and must name the final
   stage, last: `package.json`, `marketplace.json`, `plugin.json`, `SKILL.md`'s
   frontmatter description, the command, the Cursor rule and the README. Change one →
   walk all of them. (It said *nine surfaces* above a list of ten until 2026-08-08. A
   count of an enumeration inside one sentence cannot be computed from outside it, so
   unlike the numbers in the claim registry this one is **deleted**, not gated.)

Also: no hardcoded vendor model ids anywhere in the shipped skill (name the tier);
every `references/*.md` must be reachable from `SKILL.md`; the Cursor rule stays
self-contained with no relative links; every new validator guard needs a matching
negative self-test in `.github/workflows/validate.yml`.

3. **`npm test` reads git, and prints two disclosures.** Its verdict is followed by the
   claim-registry states, `learned.md`'s shape (rules · rules with an incident ·
   incident words · binding rows), and `unlooked: N` — what this run could not look at,
   listed. None of the three is a ratchet: no floor, no direction, **never a target**.
   One check compares `learned.md`'s high-water mark against **every value that file's
   history has held** (`git log -p`, last 80 commits) — comparing against `HEAD` was the
   first draft and never fired on a committed checkout, which is what CI runs. Outside a
   checkout it prints the skip rather than going quiet.

4. **Guard corpora are discovered, not listed.** Three hand-written lists each missed a
   shipped surface and none of the misses was found by the guard holding the list. A new
   surface joins a check by existing — see `_discover_md` in `test/validate.py`. If you
   add a corpus, give it a predicate, and give every exclusion a reason in the code.

5. **`npm test` now runs bash.** One guard **executes** `templates/docgate.sh` over
   a scratch project seeded from the templates and requires exit `0` — a scaffold
   whose own gate rejects its own seeds teaches every new project that the gate is
   noise. Touching any of `templates/{docmap,decisions,open-questions,retro}.md` or
   `docgate.sh` means running `npm test`, because the four are one contract.

## Docs to update in the same change

- `CHANGELOG.md` — a section per version, written as *what changed and why it
  mattered*, never a diff summary.
- `README.md` — when a user-visible capability, install path or stage changes.
- `references/artifacts.md` — when the repo layout changes.
- `docs/superpowers/retro.md` — when a run of the pipeline **on this repo**
  diverged: stamp the run first (its commit makes the cold-retirement trigger
  computable), then prune the standing instructions (retirement triggers, cap of ten,
  every deletion logged), then write the entry
  ([`references/retrospective.md`](plugins/task-pipeline/skills/task-pipeline/references/retrospective.md)).
- `docs/superpowers/` holds this repo's **historical** design records (v0.1.0).
  They carry a "superseded" banner; do not update them to the current shape and do
  not treat them as the source of truth.

## Knowledge graph

Optional here, recommended by the skill itself
([`references/knowledge-graph.md`](plugins/task-pipeline/skills/task-pipeline/references/knowledge-graph.md)).
If `graphify-out/` exists in this checkout, refresh it in the same change as the
docs (`/graphify . --update`) and check it against them — a hub no doc names, a doc
naming a file the graph no longer has. It is git-ignored and derived: never edit it
by hand. Not installed →
`uv tool install graphifyy` → `graphify install` → `/graphify .`.

## Knowledge wiki

This project's distilled knowledge lives in the operator's local Obsidian vault
under `projects/task-pipeline/`, managed with
[obsidian-wiki](https://github.com/ar9av/obsidian-wiki). The vault itself is
private; only the tool is public. Sync it with `wiki-update` at the end of a substantial
change — decisions and seams, not a diff summary.

## Style

- Line-wrap prose at ~80 characters; the doctrine files are read in narrow panes.
- State the rule, then the failure it prevents. Doctrine files end with a
  *Rationalizations* table — the excuse an agent will reach for is worth writing
  down alongside the rule.
- Markdown hazard: a wrapped line that **starts** with `>` becomes a blockquote.
  Reflow precedence chains like `code > docs > wiki > memory` so no line begins
  with the character.
