# Contributing to task-pipeline

Thanks for taking the time. This repo ships a **skill**, not a program: almost
everything in it is prose that an agent reads and acts on. That makes two things
unusually important — the doctrine must not contradict itself across surfaces, and
the structural validator must stay able to fail.

## Getting set up

No build step, no dependencies. You need `python3` (validator), `node` ≥ 16 (npm
installer), and `bash`.

```bash
git clone https://github.com/ssheleg/task-pipeline
cd task-pipeline
npm test          # == python3 test/validate.py
```

`npm test` must print `PASS: task-pipeline structure valid` before you open a PR.

That proves the repo is well-formed. It does **not** prove the validator is
anything more than a decoration — for that, every guard has to be watched
rejecting a planted defect:

```bash
npm run test:negatives    # python3 test/negatives.py
npm run test:all          # both, in order
```

The corruptions live in [`.github/workflows/validate.yml`](.github/workflows/validate.yml)
and `test/negatives.py` reads them from there — never duplicated, because a second
copy of a corruption is a second thing to drift. The runner also tells a **broken
test** from a **guard that didn't fire**: if a planted defect changed nothing, the
validator passing means the test proved nothing, and it is reported as `BROKEN`
rather than as a failure of the guard.

**Corrupt files in python, never with `sed -i`.** BSD sed needs an argument GNU sed
refuses, and `0,/re/` does not exist on BSD at all — there it edits nothing
silently, and the test reads as a guard that failed. The validator rejects `sed -i`
in the workflow for exactly this reason: a self-test that only runs on CI cannot be
used while you are writing the guard, which is the moment it is worth most.

To try your change in a real agent:

```bash
./install.sh --force            # ~/.claude/skills/task-pipeline + the command
node bin/task-pipeline.js --force   # the same, through the npm installer
```

## Repository layout

| Path | What it is |
|---|---|
| `plugins/task-pipeline/skills/task-pipeline/SKILL.md` | the orchestrator — the entry point every agent reads first |
| `…/references/*.md` | the built-in stage doctrine (one file per stage or concern) |
| `…/templates/*.md` | skeletons seeded into a host project (brief, carry-over, `CONTEXT.md`, ADR) |
| `…/pipeline.schema.json` | the universal pipeline-config contract |
| `…/pipeline.example.json` | this plugin's own flow expressed against that contract |
| `plugins/task-pipeline/commands/task-pipeline.md` | the `/task-pipeline` slash command |
| `cursor/rules/task-pipeline.mdc` | the Cursor channel — **self-contained**, no relative links |
| `bin/task-pipeline.js`, `install.sh` | the two installers |
| `test/validate.py` | the structural validator |

## The invariants

These are what the validator enforces. Breaking one is not a style disagreement —
it ships a wrong pipeline to every install.

**1. Four-way version sync.** `package.json`, `.claude-plugin/marketplace.json`
(`plugins[0].version`), `plugins/task-pipeline/.claude-plugin/plugin.json` and the
top `## vX.Y.Z` heading in `CHANGELOG.md` must all carry the same version.

**2. The stage list lives on three surfaces and may not drift.** `SKILL.md`'s
table, `references/stages.md`'s per-stage sections, and `pipeline.example.json`.
Stage ids, names and **gate types** are compared across all three. Each stage's own
doctrine file states its gate type too (`## GATE (auto)` / `## GATE (manual)`) and
must agree with the config.

**3. Every human-facing description must name the flow's final stage, last.** The
package, marketplace, plugin, skill, command, Cursor-rule and README blurbs are the
only thing most people ever read. When a stage is added at the end, all of them
change. The validator derives the last stage from `pipeline.example.json` and holds
every blurb to it.

**4. No hardcoded vendor model ids.** Anywhere in the shipped skill, the README,
the command or the Cursor rule. Generations ship, tiers get renamed, and the
operator may be on another provider — name the **tier** ("the most capable model
available"), never a string. Stage configs use the provider-agnostic tokens
`default` / `inherit`.

**5. Every `references/*.md` must be reachable from `SKILL.md`**, directly or
transitively. Progressive disclosure means an agent loads only what it is pointed
at; an unreferenced file is dead context that ships and is never read.

**6. The default flow runs on the built-in doctrine.** `pipeline.example.json`'s
`skills[]` may not name an external provider (`superpowers:*`, `grill-me`, …).
Substituting one is a host project's call in *their* `pipeline.json`, never the
shipped default.

**7. Stage 0 is mandatory and manual; stage 10 is manual and demands evidence;
the stage-4 gate is a set comparison.** These three are the spine — the validator
asserts each of them in the shipped config.

**8. `SKILL.md` frontmatter stays under 1024 characters**, the description opens
with `Use when …`, and it carries Russian trigger aliases beside the English ones.

**9. Relative links resolve.** Every relative markdown link in every file outside
a fenced code block must point at a path that exists.

## Adding or changing doctrine

- **Change one idea per PR.** These files are read by agents under load; a PR that
  edits eight references for three unrelated reasons is unreviewable.
- **Update every surface in the same change.** If you touch the stage list, the
  gate types or the review verdict count, walk `SKILL.md`, `references/stages.md`,
  `pipeline.example.json`, the command, the Cursor rule and the README before you
  commit. The validator catches much of this — do not rely on it to think for you.
- **A new guard needs a negative self-test.** If you teach `test/validate.py` a new
  rule, add a step to `.github/workflows/validate.yml` that corrupts a copy and
  asserts the validator fails, then watch it with `npm run test:negatives`. A guard
  nobody proved can fail is decoration. **Check the base is green first** — if the
  repo already fails your new rule, the self-test passes for the wrong reason and
  proves nothing.
- **Keep the Cursor rule self-contained.** It gets copied into foreign projects;
  relative links break there. Restate, don't link.
- **Prose style:** state the rule, then the failure it prevents. Every doctrine
  file ends with a *Rationalizations* table for a reason — the excuse an agent will
  reach for is more useful to write down than the rule itself.

## Commits and pull requests

- **Conventional commits:** `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`.
  Append the version when the change ships one: `feat: … ; v0.19.0`.
- Fill in the PR template: what changed, which surfaces you updated, validator
  output.
- CI must be green. It is fast and dependency-light on purpose.

## Releasing (maintainers)

1. Bump the version in **all four** places (see invariant 1) and write the
   `CHANGELOG.md` section — what changed and *why it mattered*, not a diff summary.
2. `npm test` green, commit, push.
3. Tag `vX.Y.Z` and push the tag. With the repo variable `RELEASE_ENABLED=true`,
   [`.github/workflows/release.yml`](.github/workflows/release.yml) re-runs the
   validator, checks the tag against the manifests, cuts a GitHub release from that
   CHANGELOG section, and smoke-tests `npx` from a clean checkout.
4. `npm publish` stays a **human step** (2FA) and is intentionally not automated.
5. Refresh the local installs: `claude plugin marketplace update task-pipeline` →
   `claude plugin update task-pipeline@task-pipeline` →
   `npx skills update task-pipeline --global --yes`, then restart the agent.


### The family catalogue moves with the release

`sshlg-skills` — the launcher that installs and updates the whole ssheleg family — pins every
member's version in its own `skills.json`. **A release that does not bump that pin is invisible.**
`npx sshlg-skills list` keeps reporting the previous version, `update` keeps installing it, and
anyone comparing their install against `list` is told the wrong number with nothing to reveal it.

So a release is not finished at `npm publish`:

```bash
# in ssheleg/sshlg-skills
#   1. bump this member's "version" in skills.json
#   2. bump the launcher's own version, changelog, tag
npm publish --access public
npx --yes sshlg-skills@latest list   # the new number must appear here
```

## License

By contributing you agree that your contributions are licensed under the
[MIT License](LICENSE), and that any third-party material you bring in is
compatible and gets its notice added to `LICENSE` → *Third-party*.
