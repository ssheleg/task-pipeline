<!--
Thanks for the PR. Keep it to one idea — these files are read by agents under
load, and a PR that edits eight references for three reasons is unreviewable.
-->

## What changed

<!-- One or two sentences. If this changes doctrine, say which stage and why. -->

## Why

<!-- The failure this prevents, concretely. -->

## Surfaces updated

The stage list, gate types and the review-verdict count live on several surfaces
at once. Tick what this PR touched — or "n/a" if it touched none of them.

- [ ] `SKILL.md` (table + prose)
- [ ] `references/stages.md`
- [ ] the stage's own `references/*.md` doctrine file
- [ ] `pipeline.example.json` (and `pipeline.schema.json` if the contract changed)
- [ ] `commands/task-pipeline.md`
- [ ] `cursor/rules/task-pipeline.mdc` (self-contained — no relative links)
- [ ] the three JSON descriptions (`package.json`, `marketplace.json`, `plugin.json`)
- [ ] `README.md`
- [ ] `CHANGELOG.md`
- [ ] n/a — none of the above

## Checks

- [ ] `npm test` prints `PASS: task-pipeline structure valid`
- [ ] Version bumped in all four places, or no version bump needed
- [ ] No hardcoded vendor model id anywhere (name the tier, not the string)
- [ ] New validator guard → matching negative self-test in `validate.yml`, or n/a

```
$ npm test
<paste the output>
```
