# Deploy targets — the runbook, and the verbs when the runbook is thin

**Load this when:** stage 7 is about to deploy or stage 8 is about to verify, and
the project's own runbook either does not exist yet or does not say enough to
act on.

The project's `docs/DEPLOYMENT.md` outranks everything here. This file exists for
the two moments it cannot help: when there is no runbook to read, and when the
runbook names a platform whose verbs you have to recall. `conventions.md` says
where to look; this says what to run once you know.

## Contents

- If there is no runbook, write one first
- Runbook template
- Heroku
- DigitalOcean App Platform
- Droplet / bare server over SSH
- Deploy that happens in CI
- Other platforms, quick verbs
- The verification trio

---

## If there is no runbook, write one first

A deploy performed from an agent's inference about the project is a deploy
nobody can repeat or roll back. Stage 7's authorization floor assumes a
documented procedure; absent one, **the runbook is the first deliverable of the
stage**, gathered from the operator and committed before anything ships.

Ask for what the template below leaves blank — the target, the trigger, the
gate commands, where secrets live, the migration step, the health check, the
rollback — and write the answers down. The questions take two minutes at the
gate where the operator is already present. Reconstructing them during an
incident does not.

## Runbook template

Scaffold `docs/DEPLOYMENT.md` with this. Fill every placeholder, delete what does
not apply, keep it short — it is the source of truth stage 7 follows, and a long
one goes stale.

```markdown
# Deployment

## Overview
- Project: <name>
- Environments: <production | staging | ...>
- Deploy branch: <main>
- Deploy trigger: <CLI push | container registry | CI on push>

## Platforms / targets
| Env | Platform | App / service | Region | Notes |
|-----|----------|---------------|--------|-------|
| production | <Heroku / DO App Platform / Droplet / Fly / Vercel / AWS / SSH> | <app-name or id> | <region> | <notes> |

## Pre-deploy gate
Commands that must pass before deploying:
- Lint: `<command>`
- Type check: `<command>`
- Tests: `<command>`
- Build: `<command>`

## Deploy steps
1. <exact commands, in order>
2. <release / migration commands>

## Environment variables / secrets
- Stored in: <Heroku config vars | DO app-level secrets | .env on server | GitHub secrets>
- Required keys (NAMES ONLY, never values): <KEY_A, KEY_B, ...>

## Migrations / release-phase commands
- <e.g. release phase in Procfile, or `heroku run <migrate> -a <app>`>

## Post-deploy verification
- Health check URL: <https://.../health> → expected `<200 / payload>`
- Logs: <exact command per platform>
- CI build (if any): <workflow name / link>

## Rollback
- <exact procedure — the one thing nobody writes down and everybody needs>

## Contacts / ownership
- Owner: <who>
- Escalation: <who / where>
```

**Never write secret values into the runbook.** Names only. A runbook is
committed; a secret in it is a secret in git history.

---

## Heroku

Check you are authenticated before relying on any of it: `heroku auth:whoami`.

```bash
# git-based deploy (build runs on Heroku)
git push heroku <local-branch>:main

# container-based deploy
heroku container:push web -a <app>
heroku container:release web -a <app>

# migrations / release-phase, when not automated in the Procfile
heroku run "<migrate command>" -a <app>
```

Verify:

```bash
heroku ps -a <app>            # dyno state — this is where a crash loop shows
heroku logs --tail -a <app>   # boot and runtime errors
heroku releases -a <app>      # confirm the new release landed; `heroku rollback` reverts
```

## DigitalOcean App Platform

`doctl account get` first.

```bash
# an app connected to a branch deploys on the push from stage 7; to force one:
doctl apps create-deployment <app-id> --wait
```

Verify:

```bash
doctl apps get <app-id>                 # active deployment and its phase
doctl apps logs <app-id> --follow       # runtime
doctl apps logs <app-id> --type build   # build — a different stream, and usually the answer
```

## Droplet / bare server over SSH

Shape only — the runbook's exact steps win, because this is the target where
"typical" is least likely to be true.

```bash
ssh <user>@<host> '
  cd <app-dir> &&
  git pull &&
  <build command> &&
  <restart command>          # systemctl restart <service> | docker compose up -d
'
ssh <user>@<host> 'systemctl status <service> --no-pager'
ssh <user>@<host> 'journalctl -u <service> -n 100 --no-pager'
```

## Deploy that happens in CI

When the push itself is the deploy, stage 8 verifies the run, not the host:

```bash
gh run list --branch <branch> --limit 5
gh run watch <run-id>
gh run view <run-id>
gh run view <run-id> --log-failed     # only the failed step's log
```

**Confirm the deploy job, not just the build job.** A green build with a skipped
or failed deploy is the most common way a run reports success while nothing
shipped — and it is exactly what the stage-8 gate is for.

## Other platforms, quick verbs

| Platform | Deploy | Verify |
|---|---|---|
| Fly.io | `fly deploy` | `fly status`, `fly logs` |
| Vercel | `vercel --prod`, or CI on push | `vercel ls`, the deployment URL |
| Cloudflare Workers/Pages | `wrangler deploy` | `wrangler tail` |

## The verification trio

Whatever the platform, stage 8's gate needs the same three, and all three:

1. **Process/deployment state** — is the new version the running version
2. **Runtime logs** — clean boot, no error spike
3. **A health-check request** — from outside, against the live URL

One or two of the three is where "deployed successfully" gets said about a
service that is crash-looping. If any of the three cannot be obtained, that is
the honest degradation report the gate asks for — not a reason to call it green.
