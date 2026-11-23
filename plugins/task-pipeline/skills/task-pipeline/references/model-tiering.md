# Model policy

## Contents

- The default
- Never hardcode a model id
- The operator's explicit choice is inherited, verbatim
- Roles and money
- Mechanic — confirm at preflight, then stop asking
- The plan-then-execute profile
- Subagents
- Degradation
- A harness clause encodes a model's weakness — stress-test it per generation

**One model, recorded once, before the run starts.** Not a per-stage tier list,
not a hardcoded vendor id: the model already running, kept and recorded at preflight
unless the operator switches it.

## The default

> **Use the most capable reasoning model the environment offers** — at the time of
> writing that is the **latest Opus generation**, but read that as *"the top tier
> of whatever you're on"*, not as a specific string.

Every stage runs on that model by default; *Roles and money* says which calls
go to tokens.

## Never hardcode a model id

Model ids go stale, and the operator may be on another provider. So:

- **Resolve at runtime.** Pick the top reasoning tier the environment offers
  (`/model`, the harness's model list).
- **Treat any id in this repo as an example**, including in `pipeline.example.json`.
  Stage configs use provider-agnostic tokens:
  - `default` — the model confirmed for this run (the recommendation above)
  - `inherit` — whatever the operator is currently on; no recommendation
- **Another provider is fine:** the best available tier; say which.

## The operator's explicit choice is inherited, verbatim

**Advice and choice are different things, and the second wins.** The
recommendation above is advice, printed once at preflight. A model or effort
the operator set explicitly (`/model`, `/fast`, a config entry, an answer
at preflight) is the CHOICE, and the plan, every stage and every subagent
inherit it unchanged. **Task size is not a basis for switching**: a large task
does not upgrade the model, a mechanical stage does not downgrade it; only an override
the operator RECORDED, with its basis, in the per-stage map changes it mid-run. A switch nobody recorded is a defect, whatever it saved.

**An unsupported capability is its own line, never a silent swap.** When the
confirmed model cannot do what a stage needs (vision, a context window, a tool), the
run states that limitation by NAME, records it in the brief, and asks or proceeds with the gap
named. Substituting another model without the operator's say-so is the same defect as
the silent downgrade.

## Roles and money

The owner, 2026-11-23: tokens buy only the thinking that decides.

| Role | Route |
|---|---|
| Thinker: decisions, a spec's meanings (`meanings.py write`) | tokens, the strongest model |
| Writer of the spec's text (`meanings.py writer-task`); main work; specialists; scouts | subscription |
| Validators | tokens, one call each, never retried |
| The council's verdict ([`consilium.md`](consilium.md)) | tokens, the strongest model |

`scripts/spend.py` books every token call (route, model, cost, task; an unknown
cost is never zero) and sums the day and month beside the estate's month from
Observatory; at 80 % of USD 5,000 `spend.py ceiling` exits 3 with the owner's
question.

## Mechanic — confirm at preflight, then stop asking

Once, as one line of the preflight notice (before stage 0, on the full flow):

> 🧠 **Model:** `<current>`, kept. Recommended for this run: **`<top tier
> available>`**. A switch is the operator's `/model` at any time; the brief records
> it.

The line is a **notice, not a question**.
Record the current model in the stage-0 brief (`Model` row of the autonomy sweep),
and a per-stage override map only when the operator states one. After that:

- **Do not prompt at any stage boundary**: the decision is recorded.
- **Print the line again only** when the operator recorded a *per-stage override
  map* and the next stage's entry differs from the current model, scoped to that stage.
- A skill **cannot change the main-loop model**; only the operator can (`/model`,
  `/fast`). So the default is the model already running.

## The plan-then-execute profile

The per-stage override is usually declined, and one tier for the whole run is right
when one tier is what the environment has. Where two are available, one override has a
basis worth writing down, so it ships as a named profile:

> **plan-then-execute** — the most capable reasoning tier for stages 0–4 (intake,
> docs, brainstorm, spec, plan) and stage 10 (acceptance); the strongest *working*
> tier for stages 5–9 (build, tests, deploy, post-deploy, docs).

**Its basis:** stages 0–4 produce *judgment that the later stages consume*: a brief,
contracts and a plan a stranger can follow. A weak plan is not recovered by a strong
build; a strong plan executed by a working tier is ordinary delivery. Acceptance is a
judgment too, so stage 10 returns to the planning tier.

It is still an override the operator states and the brief records. Task size still switches nothing.

`scripts/plan_audit.py --models <map.json>` checks the recorded map at stage 4: a stage
number this pipeline does not have, or an entry with no model behind it, fails there.

## Subagents

Stage 5 spawns subagents; the orchestrator pins them to the **run's confirmed
model** via the `Agent` / `Workflow` model override. No silent downgrade to a cheaper tier.

## Degradation

The recommendation is a **reminder, not a block**. If the recommended tier isn't
available, keep the current model, say which, and run.

## A harness clause encodes a model's weakness — stress-test it per generation

Every fixed control here (a cap, a checkpoint, a fix-loop ceiling) encodes what the
confirmed model cannot yet do, and that expires (*Harness design for long-running
agents*, anthropic.com/engineering, read 2026-08-30). When the tier moves a
generation, re-test those clauses.
