# Model policy

**One model, confirmed once, before the run starts.** Not a per-stage tier list,
not a hardcoded vendor id — a single decision the operator makes at preflight and
the pipeline then honors without nagging.

## The default

> **Use the most capable reasoning model the environment offers** — at the time of
> writing that is the **latest Opus generation**, but read that as *"the top tier
> of whatever you're on"*, not as a specific string.

Every stage runs on that model by default. The pipeline is a full delivery cycle:
the grill has to hear what the operator didn't say, the spec has to lock contracts
a zero-context implementer will follow, and the build has to hold a plan in its
head. Downgrading any of those to save tokens costs more in rework than it saves.

## Never hardcode a model id

Model ids go stale — generations ship, tiers get renamed, and the operator may not
even be on the same provider. So:

- **Resolve at runtime.** Look at what the environment actually offers (`/model`,
  the harness's model list) and pick the top reasoning tier available there.
- **Treat any id in this repo as an example**, including in `pipeline.example.json`.
  Stage configs use provider-agnostic tokens:
  - `default` — the model confirmed for this run (the recommendation above)
  - `inherit` — whatever the operator is currently on; no recommendation
- **Another provider is fine.** "Top tier available" is the contract. If the
  environment has no Opus-class model, the best available one is the right answer —
  say which one you settled on and keep going.

## Mechanic — confirm at preflight, then stop asking

Once, as part of the preflight (before stage 0):

> 🧠 **Model for this run:** recommended **`<top tier available>`**. You're on
> `<current>`.
> Switch with `/model <id>`, or say "keep current" / name another. Per-stage
> overrides welcome (e.g. a cheaper model for mechanical stages) — say so now and
> I'll record the map.

Record the answer in the stage-0 brief (`Model` row of the autonomy sweep). After
that:

- **Do not re-prompt at every stage boundary.** The decision is made; nagging is
  the thing this replaces.
- **Re-prompt only** when the operator recorded a *per-stage override map* and the
  next stage's entry differs from the current model — then emit the same block
  scoped to that stage.
- A skill runs inside the current context and **cannot change the main-loop
  model**; only the operator can, via `/model` (or `/fast`). Preflight is
  interactive anyway, so this costs one exchange.

## Subagents

Stage 5 spawns subagents; the orchestrator pins them to the **run's confirmed
model** via the `Agent` / `Workflow` model override. No operator action needed —
and no silent downgrade to a cheaper tier.

## Degradation

The recommendation is a **reminder, not a block**. If the recommended tier isn't
available, keep the current model, state plainly which one is in use, and run. The
pipeline never stalls on a model it can't get.
