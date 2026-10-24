# Release impact: who a release touches, how it is watched, and the way back

Load this at stage 7, before any outward act of a release (a tag, a publish, a deploy), and at
stage 8, while the release is watched. Its gate is `scripts/release_impact.py`; its card is
`templates/release-impact.md`. The rule is the operator's (2026-10-24): whenever a release is
decided in a project that has users, the release first makes sure the current users are not
harmed and says how they are affected; and there is always tracking that shows it goes as it
should, an alert when it does not, and a plan to roll back or ship an urgent fix.

## Contents

- Who has users
- When the card is owed
- The card
- What the checker refuses
- Stage 8: the watch and the decision
- Worked example: a skill or package release
- Worked example: a web or mobile product
- Companions and single homes
- Rationalizations

## Who has users

`pipeline.json` → `release.users` says it, once per project:

| Value | Means | The card |
|---|---|---|
| `external` | people or systems outside the team install, call or open what ships | owed |
| `internal` | only the team or the operator's own agents use it | owed (the segments are small, the sections are the same) |
| `none` | nothing ships to anyone: a scratch repository, a spike, an archive | not owed; the run writes `users: none` beside the stage 7 verdict |
| absent | **unknown**, treated as `external` for safety | owed, and the run says the value was unknown, asks the operator once and records the answer |

An answer is a property of the project, not of one release. A release that ships nothing to
anyone in a project with users (a docs-only commit that is never tagged) is not a release here.

## When the card is owed

Stage 7, before the first outward act, whenever `release.users` is not `none`. The card lives
beside the run's other records: `<artifacts>/specs/YYYY-MM-DD-<topic>-release-impact.md`, seeded
from `templates/release-impact.md`, one per release (a release iteration writes one for the
release it cuts, not one per wave). The stage 7 gate is:

```bash
python3 scripts/release_impact.py check <card.md> --pipeline pipeline.json
```

Exit 0 is PASS, 1 FAIL, 2 usage or an unreadable input, 3 NOT_RUN (no card where one is owed).
NOT_RUN stops the release exactly as FAIL does: it is never green.

## The card

Schema `release-impact/1`. A header (`schema`, `release`, `users`) and four sections, each
**answered** or `n/a: <reason>`. Every line the template marks `TODO` is replaced.

1. **Who is affected and how.** The user segments and a rough count of each; what changes for
   them (behaviour, data, API or file format compatibility, migrations); whether anything breaks
   for an existing user, and for whom; the rollout shape (all at once, a staged percentage, a
   canary, a feature flag); the timing (when, and why then).
2. **Tracking.** The signals that show the release is going well (metrics, dashboards, logs,
   error rates, install counts); their current **baseline**, so a change can be read as one;
   where each is read (a URL, a command, a query); and the **watch window**, how long after the
   release the signals are watched.
3. **Alerting.** What fires when it goes wrong (the threshold or condition), who receives it and
   where; and whether that alert has **ever been seen firing**. An alert nobody has seen fire is
   written as `never`: it is a hypothesis about an alert, and the card says so rather than
   letting it read as a tested one.
4. **Rollback or hotfix.** The exact rollback procedure and how long it takes; whether data
   changes are reversible (a backup, a down migration) or not, said plainly; any kill switch or
   flag; the hotfix path; and the **decision trigger**: `roll back if <signal crosses X> within
   <Y>`. The project's runbook owns the procedure itself
   ([`deploy-targets.md`](deploy-targets.md) → *Runbook template*, its `Rollback` section):
   the card links it and adds what is specific to this release, never a second copy.

## What the checker refuses

- No card where one is owed: NOT_RUN. A card for `users: none` is checked if it exists.
- A header without `schema: release-impact/1`, or a `users:` value outside the three, or a card
  whose `users:` disagrees with `pipeline.json` (or `--users`).
- A missing section, a section that appears twice, or an empty one (an HTML comment is empty).
- `n/a` with no reason, in a section or on any field line: `n/a: <reason>` or nothing.
- A `TODO` left anywhere in the card.
- Section 2 without a `Watch window:` value. Tracking cannot be `n/a` on a release with users.
- Section 3 without a `Seen firing:` line, or answered `n/a`: something must say it went wrong.
- Section 4 without a `Decision trigger:` that states its condition (`if` or `when`), or
  answered `n/a`: there is always a way back, even when the way back is a hotfix.
- At stage 8 (`--outcome`): no `## Outcome` section, or a `Result:` that is not one of `held`,
  `rolled back`, `hotfixed`, `watching`.

## Stage 8: the watch and the decision

Stage 8 reads the card's signals for its watch window and records what it read in the card's
`## Outcome` section: the signals with their values against the baseline, whether any alert
fired, and a `Result:`. When the decision trigger fires, the run rolls back or ships the hotfix
**per the card**, without a new debate: the trigger was agreed before the release precisely so
that the moment it fires is not the moment it is argued about. A rollback is itself outward and
is verified like a deploy ([`deploy-targets.md`](deploy-targets.md) → *The verification trio*).

A watch window longer than the session is a wait: `Result: watching`, the window's end, and the
watcher that reads the signals then (a scheduled job, a monitor, a named person). With no watcher
available the card says so; it never claims a watch that nobody runs.
`python3 scripts/release_impact.py check <card.md> --outcome` gates the record.

## Worked example: a skill or package release

The users are installers. Section 1 names them (`npm` weekly downloads, plugin marketplace
installs, the operator's own machines) and what changes for them (a renamed command, a new
required field, a dropped Node version); the rollout is all at once on the tag. Section 2 tracks
the registry readback (`npm view <pkg> version` equals the tag), a clean-directory install, the
installed version read back on the operator's machine, and new issues; baseline: open issues
today; watch window: 72 h. Section 3: a failed install in the release workflow's smoke test and a
new issue on the repository, received by the maintainer by mail; seen firing: yes, the smoke test
failed a release once. Section 4: re-pin the previous version in every consumer, `npm deprecate
<pkg>@<bad>` with a message pointing at the fixed one, then a patch release; minutes; nothing to
reverse in data; decision trigger: roll back if an install fails or a breaking issue is filed
within 72 h.

## Worked example: a web or mobile product

Section 1: signed-in customers on the web app (about 12,000 weekly), checkout changes to a new
payment form; existing saved cards keep working, a stored draft order is migrated; rollout behind
a flag at 5%, then 50%, then 100% over three days, starting on a Tuesday morning. Section 2:
checkout conversion, payment error rate and p95 latency on the product dashboard, baselines from
the last 14 days; the error tracker's release view; watch window: 24 h per step. Section 3: the
error tracker alerts on a new issue class or an error rate over twice the baseline for 10
minutes, to the on-call channel; the payment error alert has fired before, the latency one never
has. Section 4: switch the flag off (seconds); the migration has a down step tested on a staging
copy; the hotfix path is a patch through the normal pipeline with the flag held at its last good
step; decision trigger: roll back if payment errors exceed 2% or conversion falls 10% below
baseline within any step's window. A mobile release adds the store's staged rollout percentage,
the halt button as the kill switch, and the fact that a shipped binary cannot be recalled: its
way back is a hotfix build, so its section 4 names the server-side flag that disables the
feature for builds already installed.

## Companions and single homes

- Wiring the alerts in section 3 for a service: sheleg-dev's `error-tracking` skill (releases
  tied to commits, the release view the watch reads). Recommended, never required; absent, the
  card names what fires on the project's own tooling.
- The rollback procedure: the project's runbook ([`deploy-targets.md`](deploy-targets.md) →
  *If there is no runbook, write one first*). No runbook means stage 7 writes one first, and the
  card points at its rollback.
- The release's authority and approval mode: [`deploy-targets.md`](deploy-targets.md) → *When
  the release waits for an approval*. The card does not authorise anything; it is owed before
  the act the authority allows.

## Rationalizations

| The excuse | Why it fails |
|---|---|
| "It is a small release, nobody is affected." | Then section 1 says so in one line, with the reason. The card is short when the release is; it is never absent. |
| "We will notice if it breaks." | Noticing is section 3. If nothing is named that fires, nobody notices until a user writes. |
| "Rollback is obvious." | Obvious to the person who shipped it, at the moment they shipped it. The trigger and the procedure are written before the release so the person at the incident does not reconstruct them. |
| "The alert exists, it just never fired." | Then `Seen firing: never`. An alert nobody has seen fire is untested, and the card says that instead of implying the opposite. |
| "We do not know if there are users." | Unknown is treated as `external`. Ask once and record the answer in `pipeline.json`. |
