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
it ships a wrong pipeline to every install. Numbered in reading order; the numbers
are labels, not priorities.

**1. Version sync across every manifest surface.** `package.json`,
`.claude-plugin/marketplace.json` (`plugins[0].version`),
`plugins/task-pipeline/.claude-plugin/plugin.json`, the top `## vX.Y.Z` heading in
`CHANGELOG.md` **and `SKILL-CARD.md`'s Version row** must all carry the same version.
The invariant was called *four-way* until 2026-08-08 while listing five surfaces and
while the validator enforced five — a name that counts is a number, and it drifts like
one. The list is the count.

**2. The stage list lives on three surfaces and may not drift.** `SKILL.md`'s
table, `references/stages.md`'s per-stage sections, and `pipeline.example.json`.
Stage ids, names and **gate types** are compared across all three. Each stage's own
doctrine file states its gate type too and must agree with the config.

**3. Every human-facing description must name the flow's final stage, last.** The
package, marketplace, plugin, skill, command, Cursor-rule and README blurbs are the
only thing most people ever read. The validator derives the last stage from
`pipeline.example.json` and holds every blurb to it.

**4. No hardcoded vendor model ids.** Anywhere in the shipped skill, the README, the
command or the Cursor rule. Name the **tier**, never a string; stage configs use the
provider-agnostic tokens `default` / `inherit`.

**5. Every `references/*.md` must be reachable from `SKILL.md`**, directly or
transitively. An unreferenced file is dead context that ships and is never read.

**6. No external provider may substitute for built-in stage doctrine.**
`pipeline.example.json`'s `skills[]` may not name one for the stages whose doctrine
ships here (2, 3-spec, 4, 5, 6, 10). The optional tools — `context7`, `figma`,
`graphify`, `wiki-query` / `wiki-update` — and the UI-required `super-ux:*` track are
the enumerated exceptions, named deliberately.

**7. Stage 0 is mandatory and manual; stage 10 is manual and demands evidence; the
stage-4 gate is a set comparison.** These three are the spine, asserted in the
shipped config.

**8. `SKILL.md` frontmatter stays under 1024 characters, and the description says
WHAT before WHEN.** Anthropic's authoring guidance requires both halves — a
capability statement in third person, then the `Use when …` trigger — and Russian
trigger aliases ride beside the English ones. *(Before v1.8.0 this invariant demanded
the description **open** with `Use when`, which enforced the trigger half and left
the capability optional. The validator now rejects that shape.)*

**9. Relative links resolve.** Every relative markdown link in every file outside a
fenced code block must point at a path that exists.

**10. A seeded template must keep the seeded gate green — in both register shapes.**
`templates/docgate.sh` is run by `npm test` over two scratch projects: one seeded
from `docmap.md` / `decisions.md` / `open-questions.md` / `retro.md`, and one built
from `adr.md`'s own fenced example. Each must exit `0`, **report the shape it
found**, and run a minimum of live checks — because every section can go `dormant`,
and a gate blind to a shape passes exactly like one that reads it. Change a template
→ run `npm test`, not just your eyes.

**The same law now covers `templates/hygiene.sh`.** It is run over a clean scratch
project, must exit `0`, and must report all six of its check counts — exit `0` alone
proves nothing, because every check can go `dormant` and dormant is green. Both gate
scripts are validated by one iterated block, not two copies, and both must keep a
`# ---------- VERDICT` marker with nothing after it.
*(guard: `the VERDICT block must be last and must `)*

**Stages 3 and 4 must keep reading their rules back.** `spec.md`'s self-review asks
whether every check it names is real, reads back the brief's decisions and stage 2's
rejected options, and prints the cost; `planning.md` asks whether every command a DoD
names resolves; `learned.md` binds rule 14 at both stages. Both files carry a
committed `## Self-review` section of computed numbers rather than ticks.
*(guard: `the self-review no longer asks `)*

**11. Every reference over 100 lines carries a `## Contents` list**, and the list is
compared against that file's own `##` headings. The guidance asks for it because a
long file gets previewed with a partial read; the comparison is because a hand-kept
list is a second source that goes stale on the next heading.

**12. A section-qualified citation must name a section that exists.**
A citation of the form `file.md → *Section*` is checked against the target's headings. The
link checker proves the file resolves; only this proves the pointer is not false.

**13. Numbers stated in living documents are computed, not restated.** The guard
count in `README.md`, `SKILL-CARD.md` and `evals/RESULTS.md` is compared against the
negative self-tests the workflow defines. CHANGELOG entries are exempt — they record
what a past release shipped.

**14. Every relative link in `README.md` resolves inside the published package.**
`package.json` → `files[]` must ship whatever the README points at, or the link
dangles for every npm consumer.

**15. `SKILL-CARD.md` answers every risk indicator** and carries the current
version. It is the registry entry a consumer reviews before deploying, and an
omitted row reads as "does not apply".

**16. The evaluation suite covers all five dimensions** and `evals/run.py` accepts
it. Running it is a human step; the suite existing is not.

**17. Both adoption walkthroughs ship, with the ratchet-baseline step.** Greenfield
is the easy half and the one that gets written; brownfield is where a repository
actually is. *(guard: `adoption without it is a tutorial for the repository nobody has`)*

**18. The description states its exclusions, and the opt-out is exercised by an eval.**
Default-on without a release valve is a trap, and an escape hatch nobody tests is not
one. *(guard: `no eval exercises the opt-out phrase`)*

**19. The stage/artifact relation is mapped in both directions.** What each stage
writes, and what it reads and from where. *(guard: `must be mapped in BOTH directions`)*

**20. Every workflow decision has a home inside the bundle.** The manifest in
`references/portability.md` names it, and no row may point outside.
*(guard: `manifest names`)*

**21. The routing default ships as a file.** It is a workflow decision, so it travels
with the bundle instead of being hand-installed into an operator's config.
*(guard: `must ship as a file rather than be hand-installed`)*

**22. Every reference reaches the README map and the manifest.** Reachability from
`SKILL.md` proves an agent can *find* a file, not that a reader was *told* about it.
*(guard: `is named nowhere in README.md`)*

**23. A seeded template over 100 lines carries its own Contents.** A host project
reads those files, and a partial read shows whichever sections come first.
*(guard: `needs the same partial-read protection references get`)*

**24. Run-wide pacing is config, and the example demonstrates its default.** The
`run` block in `pipeline.schema.json` carries the loop mode; the shipped example
sets `run.loop.mode` explicitly rather than omitting it, because the example is
what gets copied and an absent field reads as an oversight instead of a decision.
*(guard: `no explicit run.loop.mode`)*

**25. The run-wide mode is named by every stage that could be misled by it.**
`SKILL.md`, `references/grill.md`, `references/build.md`, `references/stages.md`
and `templates/brief.md` each name `continuity.md`. The continuous-execution rule
sat inside `build.md` for nine releases and did not work, because an agent running
one stage never re-reads the orchestrator to discover a run-wide rule exists.
*(guard: `a run-wide rule no stage has heard of`)*

**26. `references/continuity.md` keeps its two load-bearing clauses.** One forbids
announcing that context is nearly spent without a harness signal; the other names
the harness limit on the loop primitive. Both are one edit away from softening into
nothing. The guard normalises whitespace first — the clauses wrap at 80 columns,
and a line-oriented search would reject correctly formatted prose.
*(guard: `missing the contractual clause`)*

**27. A seeded template carries no relative markdown links.** A template is copied
somewhere else by definition, so a link that resolves from `templates/` is broken
everywhere the file is actually read. `carryover.md` shipped one for nine minor
releases and the link checker stayed green throughout, because it resolves from the
file's home. Name the file in a code span instead — the same rule the Cursor rule
follows, for the same reason. *(guard: `resolves only from`)*

**28. The False success class has one home, and the files that use it cite it.**
`references/gates.md` defines it — the law, the did-not-look test, and its two
rules; `audit.md` (the fifth axis), `build.md`, `review.md` and `continuity.md`
point at that section instead of restating it. Every incident this repository has
recorded of a mechanism reporting a win it never checked was fixed as its own
instance, because the class had no name to be swept by.
*(guard: `the False success class is gone`)*

**29. A side effect is confirmed by re-reading the state, never by the reply.**
`references/build.md` binds the implementer to a `verified-by:` line for every
step whose effect lives outside its own diff, and names the hygiene gate's blind
side; `references/review.md` rates an effect asserted without one as **Important**,
not Minor. A finding that never blocks is a finding the fix loop never sees.
*(guard: `the report no longer requires verified-by lines`)*

**30. The code graph's ledger row states a measured lag, never a build date.**
Stage 0 reads the graph first, so its freshness is the one claim a whole run rests
on — and `built 2026-08-05` is the graph's own reply about itself, true and silent
about whether it describes the tree the run is about to change. `stages.md`'s stage-0
section and the config's stage-0 gate must both require the measurement, exactly as
they do for the stage-9 refresh, and `references/knowledge-graph.md` must keep the
commands and all three signal states — with a state missing, a graph that could not
be measured prints like a fresh one.
*(guard: `never requires it — a run passes intake quoting a`)*

**31. A CI run's verdict is read, never assumed — and every stage that pushes says so.**
`references/conventions.md` → *The CI verdict* keeps the commands, the unauthenticated
fallback and all three states; stages 7, 8 and 9 cite it rather than carrying a second
copy. A workflow run that nobody reads is the fail-open hook with extra steps: this
repo's own `validate` was red on a push to `main` and on a release tag, the guard that
failed was correct, and nothing obliged anyone to look.
*(guard: `never names it — the run it triggers is closed on an unread verdict`)*

**32. The negatives floor equals the workflow's count.**
`MIN_EXPECTED` is a number in a living document (rule 8). Below the count it cannot
notice losing the difference — it lagged at 20 against 34 once, and at 104 against 108
in v1.15.0.
*(guard: `a floor below the count is a floor that cannot`)*

**33. The evidence-docs navigator indexes the canons and never copies them.**
`skills/evidence-docs/SKILL.md` is a second skill in the same plugin: the ten canons as
a one-line index, a pointer to their one home, and a table of where to go next. The
guard holds the index to the doctrine's own list, requires the pointer, and resolves
every relative link **from the navigator's directory** — it sits one level over from
everything it names, which is canon 4 in the file that publishes canon 4.
*(guard: `index that has drifted from its doctrine`)*

**34. Every invariant above names the guard that enforces it, and that guard exists.**This list claims to be *what the validator enforces*; it was eight guards behind when
an audit measured it. A claim of enforcement is now checked like any other claim.
*(guard: `whose message does not appear in`)* — and a cited literal must lie inside
a **single** string in `test/validate.py`: the check reads that file as text, so a
quote straddling a line-continuation is a citation nothing can find.

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

**Before the tag, walk `docs/DOCMAP.md`'s propagation matrix — starting at its first
row.** The guards cover most of it; the one cell that is `review` is
`cursor/rules/task-pipeline.mdc`, because no check can decide whether a change alters
how an agent behaves in a *foreign* project. That cell was skipped for two releases
and the rule shipped two versions stale. If the change would make an agent act
differently somewhere else, the Cursor rule is part of the change.


1. Bump the version in **all four** places (see invariant 1) and write the
   `CHANGELOG.md` section — what changed and *why it mattered*, not a diff summary.
2. `npm test` green, commit, push.
3. Tag `vX.Y.Z` and push the tag. With the repo variable `RELEASE_ENABLED=true`,
   [`.github/workflows/release.yml`](.github/workflows/release.yml) re-runs the
   validator, checks the tag against the manifests, cuts a GitHub release from that
   CHANGELOG section, and smoke-tests `npx` from a clean checkout.
4. **`npm publish` runs in the same workflow**, in a second job armed by the repo
   variable `PUBLISH_NPMJS=true` — it was the one human step in every release, and
   the registry drifted behind the tags because of it. Auth is either the
   `NPM_TOKEN` secret (a **granular automation** token; a classic one is still
   refused by 2FA) or npm trusted publishing via OIDC, which needs no long-lived
   credential. With `PUBLISH_NPMJS` unset or false it stays manual, and 2FA makes
   that a human step.
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
