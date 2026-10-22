# Spec: the design-review gate, its browser discipline, and the iteration stop (1.100.0)

Operator, 2026-10-22: every task that changes an interface gets a mandatory design-review
agent, a tester of the interface and its business logic, run as a gate in every pipeline this
family ships (a single run, `waves`, `iteration`). It walks the interface through scenarios of
ten user portraits, checks the design in Figma before it is built and the build after, drives a
real browser the operator chose, watches the machine's load and closes what it opened. Agents
also move in measurable, bounded iterations that a tester agent and a person can both check.

## REQ

| id | Requirement | Check |
|---|---|---|
| DR-01 | A run whose brief names a `surface_class` other than `none` owes a design review; no UI change ships without one | stage 3 and stage 6 gates name `design_gate.py`; a fixture without the report fails |
| DR-02 | The review walks a **test panel** of ten personas, each with the features it uses, composite scenarios, an activation funnel and a retention loop; the panel is a hypothesis instrument, never evidence | `design_gate.py panel` validates `docs/ux/test-panel.md`; super-ux ships the template |
| DR-03 | Pass D (design): before build, every changed scenario step × the personas who use that feature is walked over Figma frames, or over the mockups when there is no Figma | report rows of `pass: design` carry `frame` = Figma node or mockup path |
| DR-04 | Pass B (build): after build, the same matrix is driven in a real browser, each step captured, compared against its Figma frame or mockup, with the action's business outcome read back | report rows of `pass: build` carry `capture`, `engine`, `outcome` |
| DR-05 | Each step is judged on a fixed checklist: the step's frame exists, the primary action is present and visible without hunting, every control the scenario needs is there, nothing on the screen competes with the step's goal, its states (empty, loading, error) exist, text fits, the outcome matches the scenario | `design_gate.py report` refuses a step missing a checklist item |
| DR-06 | The browser is the operator's choice, asked once per project and recorded (`pipeline.json` → `browser`); WebKit/Safari first per `browser.md`; a fallback chain is declared; a fallback is said, never silent | `pipeline.schema.json` validates `browser`; the report names the engine of every capture |
| DR-07 | A prepared, signed-in session is used so a login wall does not stop a pass; signing in is a human gate done once, the state file stays outside the repository | `browser.storageState` path outside the repo, refused when inside |
| DR-08 | The agent watches the machine: it checks load and memory before it starts, caps browsers, tabs and dev servers, records every process it starts, and closes all of them at the end | `resource_guard.py` (check / record / close / verify); the report carries its receipt; a receipt with a live process fails the gate |
| DR-09 | Every run, not only `waves`, ends on a computed finish verdict; past the budget nothing continues without the operator's go; the budget includes `maxAgents` (parallel sub-agents, default 2) | stage-10 gate runs `waves.py finish` on the run's ledger; `agents:` ledger lines over `maxAgents` fail it |
| DR-10 | The review's own work is bounded: one pass D and one pass B per surface per round, re-review only of the changed steps, at most `maxRounds` rounds; findings outside the scope become board rows | `design_gate.py report` counts passes per round |

## The test panel (super-ux owns its format)

`docs/ux/test-panel.md`, built by super-ux `ux-foundation` from the foundation's personas and
evidence where they exist, filled out to ten portraits for coverage, and confirmed by the
operator once. Each portrait: who and in what situation; goals (the jobs it hires the product
for); the features it uses; two to four **composite scenarios** (chains that cross features, by
`SCR-` id); its **activation funnel** (steps to first value, and where it is likely to drop);
its **retention loop** (trigger → action → reward → what brings it back); its device, engine,
locale and accessibility needs. Every portrait carries `basis: evidence RE-… | hypothesis`.
A portrait that is a hypothesis never decides what to build; it decides what to test.

## The agent: `design-tester`

A task-pipeline agent, blind to the builder, reading the scenarios, the panel, the Figma file
(through the Figma MCP when connected) or the mockups, and the running build. It writes
`docs/design/<surface>/design-review.json` (`design-review/1`): the panel revision, the rows
(scenario step × persona × pass), each with its frame or capture, engine, checklist verdicts
and findings typed `breaks` / `risk` / `nit`, and the resource receipt. It never edits the
product; findings go to the builder (pass D: the designer), and outside the scope to the board.

## Browser discipline (`references/browser.md` → *The tester's browser*)

1. **Ask once.** When `pipeline.json` has no `browser` block, stage 0 asks the operator which
   browser the tests use (Safari through `safaridriver`, Playwright WebKit, Chrome Dev,
   Playwright Chromium) and the fallback order, and records the answer.
2. **Prepared session.** Safari reuses the operator's signed-in Safari through
   `safaridriver`; Playwright reuses a `storageState` file kept outside the repository. A
   sign-in, a one-time code or a consent is a human gate: name it, run the scenarios that do
   not need it, return to it after.
3. **Fallback, said.** A driver that fails to start or attach twice yields to the next in the
   chain; the capture names the engine; "checked only in Chromium" is said as such.
4. **Load.** Before starting and between scenarios: load average against cores, memory
   pressure, free disk. Over the line: wait, then run with fewer pages. Caps: one browser per
   engine, four pages, one dev server per project.
5. **Close.** Every process the agent starts (browser, driver, dev server) is recorded with its
   pid; at the end each is closed and the record verified empty. The operator's own browser
   windows are never touched.

## The stop (`references/finish-line.md`)

The finish contract already exists (objective, exit checks, scope, budget, base) and
`waves.py finish` computes it from `round:` lines. This change makes it every run's stage-10
gate, adds `run.finish.maxAgents` (default 2) with `agents: <round> — <n>` ledger lines, and
prints the finish block a person can read in under a minute: rounds n/max, releases n/max,
exit checks k/m on which artefact, blocking open/fixed, deferred → board ids.

## Out of scope for 1.100.0

Visual-diff tooling beyond what `visual_gate.py` already does; a hosted browser farm; any
change to sheleg-design's director record.
