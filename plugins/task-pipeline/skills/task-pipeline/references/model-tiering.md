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

**Advice and choice differ, and the choice wins.** The recommendation is ADVICE,
printed once at preflight. A model or effort the operator set (`/model`, `/fast`, a
config entry, a preflight answer) is the CHOICE; the plan, every stage and every
subagent inherit it. **Task size switches nothing**; only an override the operator
RECORDED, with its basis, changes it mid-run. An unrecorded switch is a defect.

**An unsupported capability is named, never silently swapped.** When the model cannot
do what a stage needs (vision, a context window, a tool), the run names the limitation
in the brief and asks or proceeds with the gap named.

## Roles and money

The owner, 2026-11-23 (host instructions, *Model and token budget by role*):
tokens buy only the thinking that decides; the rest runs on the subscription.

| Role | Route | Model of the host's map |
|---|---|---|
| Thinker: decisions, a spec's meanings and key features, analysis and planning that decide | tokens, no stinting | the strongest (`meanings.py write`) |
| Writer: the spec's text from the meanings | subscription | the session's working tier (`meanings.py writer-task`) |
| Main work, routine hard thinking, code and mathematics specialists, scouts | subscription | the session's model |
| Validators of a decision | tokens, one call each, never retried | other vendors (the council's panel) |
| The council's final verdict | tokens | the strongest ([`consilium.md`](consilium.md)) |

Every token call goes into the spend ledger with its route, model, cost and task
(`scripts/spend.py`; consilium, meanings and research validation write it
themselves). `spend.py summary` gives the day and the month by route, model and
task, with the estate's month as Observatory measures it at the providers; an
unknown cost is counted apart, never as zero, and a call billed to the host's own
provider key is read from its upstream cost. At 80 % of the development-mode
ceiling (USD 5,000 a month) `spend.py ceiling` exits 3 with the one question the
owner gets, with its default.

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
- A skill **cannot change the main-loop model**; only the operator can.

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

It is still an override the operator states and the brief records.

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
