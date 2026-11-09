# The agent surface: how the pipeline applies the AI-native canon

Load this when stage 0's actor branch forecasts a **capability change** or a
**contract change**, when a work-graph node carries `agent_surface`, or when
`docs/ux/capabilities.md` exists in the project. It says how this pipeline applies
the canon, stage by stage, in what order and with which checks. It does not state
the canon: every rule (`AN-1` to `AN-10`) has one home in its owner's file, and this
file cites the id and the home.

The stage numbers do not change. What changes is an **order inside** stages 2 to 4
and short additions to the gates of stages 0, 2, 3, 6, 7, 8 and 10.

## Contents

- The canon, and where each rule lives
- When it is armed
- What stage 0 records
- Stage by stage
- Risk follows the contract
- The skeleton, split out
- The `agent` tier
- The agent tester
- When it runs, under a nightly CI policy
- The `library` profile
- Degradation
- Rationalizations

## The canon, and where each rule lives

| Id | Short name | Home |
|---|---|---|
| `AN-1` | Parity by story | super-ux `scenario-format.md`, section *Contract v5: agents and capabilities* |
| `AN-2` | Design order | super-ux `system-map.md` |
| `AN-3` | One contract, many clients | agent-stack `agent-interop/references/agent-surface.md` |
| `AN-4` | Why a person, two scales (gate, serving reason) | super-ux `scenario-format.md`, same section |
| `AN-5` | The attention budget | super-ux `ux-design-principles.md` |
| `AN-6` | Automation by default | super-ux `system-map.md` |
| `AN-7` | The gate protocol | agent-stack `agent-interop/references/agent-surface.md` |
| `AN-8` | A safe surface | agent-stack `agent-interop/references/agent-surface.md` |
| `AN-9` | Discoverable and proven | mechanics: agent-stack `agent-evals/references/operability.md`; in this pipeline: this file (stage 6, the `agent` tier) |
| `AN-10` | Telemetry knows the actor | the analytics agent's event-catalogue guidance |

The short name is a label, not the rule. When a rule decides something, read its
home. Each home also resolves by raw URL, so a run without the companion installed
can still read it:

- `https://raw.githubusercontent.com/ssheleg/super-ux/main/plugins/super-ux/skills/references/scenario-format.md`
- `https://raw.githubusercontent.com/ssheleg/super-ux/main/plugins/super-ux/skills/references/system-map.md`
- `https://raw.githubusercontent.com/ssheleg/super-ux/main/plugins/super-ux/skills/references/ux-design-principles.md`
- `https://raw.githubusercontent.com/ssheleg/agent-stack/main/plugins/agent-stack/skills/agent-interop/references/agent-surface.md`
- `https://raw.githubusercontent.com/ssheleg/agent-stack/main/plugins/agent-stack/skills/agent-evals/references/operability.md`

The agent-stack `agent-surface.md` carries the canon index with every home. A home
that cannot be read is a named NOT_RUN for the check that needed it, never a rule
recalled from memory.

## When it is armed

**By a capability change or a contract change, and by nothing else.** A capability
change adds or removes a capability, or changes its behaviour, its actors or its
gate. A contract change touches what an agent reads: a schema, an error code, an
effect, a tool description, an error body, or a data migration that changes what a
read returns.

**Not armed:** a visual or human-copy change, a refactor whose snapshot diff is
empty, infrastructure. Over-application is the failure on this side: a canon that
fires on every task is one every task learns to report around.

**Stage 0 answers with a forecast; stage 7 re-decides it.** At stage 7 the contract
snapshot (MCP `tools/list`, an OpenAPI document, `--help --json`) is diffed against
the base. A non-empty diff on a task forecast `no` fails stage 7 and re-classifies
the task: it goes back to stage 2 for the capability map. An empty diff on a task
forecast `yes` is recorded, not punished.

**The pipeline branches on a file, never on a version number.** It reads the
presence of `docs/ux/capabilities.md` (super-ux contract v5), never the contract
marker's digit: a v4 project migrates on its first capability task, and the
super-ux doctor names the step.

**In wave mode the answer is derived per row** from the row's text and the files it
touches, and asked only where it cannot be read ([`waves.md`](waves.md) runs stage
0 once over the board). A grill question per row is the interruption the wave
exists to avoid.

## What stage 0 records

The actor branch of the grill replaces the old single question about a user-facing
surface. It asks, and the brief records:

- `capability_change: yes | no` and `contract_change: yes | no`, each a forecast;
- on either `yes`, `agent_surface: public | internal | library | none`, where
  `none` is allowed only when the product has no capability an agent could use, and
  says why;
- the actors (people and agents) the change serves;
- the human surfaces, each with its serving reason (`AN-4`), and the
  `surface_class` of each human-surface node. A class is recorded per node, so one
  task can carry a `flagship` paywall and an `internal` admin view.

A work-graph node copies `agent_surface` as `public`, `internal` or `library`. The
node field has no `none`: a node that builds no agent surface omits the field, and
an absent field owes nothing. Old graphs validate unchanged.

## Stage by stage

| Stage | What the pipeline adds when armed |
|---|---|
| 0 Intake | the actor branch above; short-path answer 3 reads "a user or an agent observes" (`scripts/short_path.py --agent-facing`) |
| 1 Docs study | the protocol revision the surface speaks, fetched (the MCP versioning page; the OpenAPI version), never recalled |
| 2 Brainstorm | **the capability map first**: REQ, then stories, then `CAP-` rows (actors, roles, gate, emits, automation, human surface or none); agent paths as call sequences with their states (pending, partial, denied, async job) and typed errors |
| 3 Spec | the order `foundation → capabilities → contract source + agent scenarios → logic → human flows, screens and scenarios → COPY and VISUAL`; dossier section 4 *Contracts in and out* owed by every capability or contract change, section 7 only where a human lane exists; agent-tester **pass C** reads the contract source cold |
| 4 Plan | contract and logic nodes first; a UI node is `blocked_by` the contract node it consumes and the edge names the contract version it carries; packets carry `CAP-` traces |
| 5 Dev | TDD starts at the contract: a failing contract test per `CAP` (schema, typed errors, idempotent retry, scope refusal), then the code; the UI is built as one client of that contract |
| 6 Tests | the **proving call** through a real client (local stdio, or the dev deployment) and the contract tests, an `auto` gate; parity (the super-ux v5 lint, `/ux-audit` with the `AN-3` proxy); agent-tester **pass B**, a `judgment` gate where owed (below) |
| 7 Lint + deploy | the snapshot diff re-decides the forecast; schema lint; tool-description lint; for a CLI: `--json`, stable exit codes, non-interactive flags |
| 8 Post-deploy | **called, not curled**: against the deployed target, discovery (`server/discover` or the OpenAPI document), the tool list equal to the snapshot, one read-only call, one typed-error probe |
| 9 Docs + wiki | the capability list in `AGENTS.md` **generated** from `capabilities.md` and the snapshot; the event catalogue only when events changed |
| 10 Acceptance | a `C→B` row (contract to behaviour) in the ladder walk, and the parity matrix: every touched `CAP` is `exposed`, or `Agent excluded` with its evidence or its board row |

The stage 3 order is the design order of `AN-2`. Agent scenarios are written beside
the contract because they are the contract's acceptance tests. A capability found
while designing a later layer flows back into `capabilities.md` in the same change.

## Risk follows the contract

- **R3** when the contract **breaks** (a removal, a rename, a narrowed input, a
  widened effect) or when the auth or effect ceiling changes.
- **R2** for an **additive** change within one contract version.
- The skeleton (below) is **R3**.

Publicity alone does not raise the class. A `public` surface owes the adversarial
persona of the agent tester instead, because a wider audience widens the attack
surface rather than the blast radius of one change.

## The skeleton, split out

A product with no agent surface yet cannot carry one capability on nothing. The
**skeleton** (auth, the refusal vocabulary, the audit row, health, the snapshot) is
split out as its own R3 item and ranked first ([`intake-split.md`](intake-split.md)
§5). The feature's capability rides on it in the same run when the brief's budget
allows; otherwise it ships as `Agent excluded: debt (<board id>)`, with the skeleton
row on top of the board.

The inventory of the rest of the product is a `project-audit` run that proposes
board rows. It is never this task's work: a task that starts by exposing the whole
product has stopped being the task.

## The `agent` tier

A fifth reading, owed by a node whose `agent_surface` is `public` or `internal`
([`certification.md`](certification.md) → *The agent reading*). It **executes**: the
proving call and the contract tests against the node's build, and it reads the
agent tester's pass-B report where one is owed. It is not folded into the seam tier,
which reads static callers and runs nothing. `graph.py certify` refuses a round on
an owing node without it and names the tier; on any other node an `agent` report is
accepted when given. A `library` node owes none.

The agent is `agents/verifier-agent.md`; the portable procedure is
[`verifier-agent.md`](../assets/verifier-agent.md).

## The agent tester

`agents/agent-tester.md` walks the project's **agent panel**,
`docs/ux/agent-panel.md` (super-ux contract v5), through the agent-channel
scenarios of the changed `must` stories. The human `docs/ux/test-panel.md` and
`design_gate.py panel` stay as they are: the two panels are read by different
testers and drift independently.

- **The panel:** a full-grant agent, a narrowly delegated agent, an automation with
  no conversation, a cheap model, an adversarial agent fed injected content.
- **The checks, per step:** `discoverable`, `schema_valid`, `typed_error`,
  `idempotent_retry`, `auth_denied`, `gate_handoff`, `outcome_read_back`,
  `notified` (an `Emits` event arrived). Each is pass, fail, na or NOT_RUN with its
  reason.
- **The report:** `agent-review/1`, its shape in `agents/agent-tester.md`.
- **Pass C, stage 3, the contract source read cold:** does the description alone
  let a model choose the right tool and fill it?
- **Pass B, stage 6, executed:** a `judgment` gate owed on R3 nodes and on `public`
  surfaces. The full-grant persona runs on the verification model the operator's
  model map names (a tier, never an id), `pass^k` with k = 3, transcripts kept as
  fixtures, spend cited from the brief. The cheap-model persona is advisory; the
  adversarial persona is advisory, and owed on `public`.
- **Gated steps** are closed by sandbox fixtures (an approver that signs, a payment
  test mode, a magic-link sink), never by a person pressing a button mid-run.

Two levels, and they are not interchangeable: the proving call and the contract
tests are the **gate** (deterministic, byte-reproducible); the cold-agent run is
the **judgment** ([`gates.md`](gates.md) → *The judgment gate*). A judgment never
stands in for a failing gate.

## When it runs, under a nightly CI policy

Where the project runs its complete hosted checks nightly rather than per push:

- the proving call and the contract tests run locally in the stage 6 gate, and in
  the nightly run;
- the LLM pass B runs once per R3 or `public` node in the run, and nightly on the
  default branch, never per push.

The test-tenant credential comes from the project's credential door (a vault or
secret broker the run calls), never from a file in the repository.

## The `library` profile

A library with no server: its types, its docs and its doctests are the proof; an
`llms.txt` pointer belongs to seo-llmo. No `CAP` registry is required, stage 8 has
no call to make, and the node owes no `agent` tier.

## Degradation

- **No `docs/ux/capabilities.md`** (super-ux v5 absent or not adopted): the
  capability rows are written inline against the provider contract
  ([`companion-skills.md`](companion-skills.md)), and the parity lint is a named
  NOT_RUN.
- **No real client to make the proving call:** the call is NOT_RUN with its reason,
  never PASS, and the `agent` tier cannot pass on it.
- **No companion installed:** the homes are read by raw URL; an unreachable home is
  a NOT_RUN for the check that needed it.

## Rationalizations

| Temptation | Why it is wrong |
|---|---|
| «The screens already do it, agents can scrape them» | A function that exists only in a screen is the defect `AN-2` names; the agent path is the contract, not the pixels |
| «It is only a refactor» | Then the snapshot diff is empty and nothing is owed. A non-empty one is a contract change, whatever the commit message says |
| «The seam tier already reads the callers» | It reads them. The `agent` tier runs the call, and a contract that type-checks can still return a bare 500 |
| «Expose the whole product while we are here» | The inventory is a `project-audit` run proposing rows; this task ships its capability and the skeleton under it |
| «Run the cold agent on every push» | It is a judgment, costly and not byte-reproducible. The proving call and the contract tests are the gate; the LLM run is per R3 or `public` node and nightly |
