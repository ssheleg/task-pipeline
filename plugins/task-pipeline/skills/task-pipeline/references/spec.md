# Spec — stage 3, built in

Writing the approved design down so a zero-context implementer — human or subagent
— can build from it without asking. Built into this skill; nothing to install.

> The spec write-up and its self-review pass are ported
> from the tail of the `brainstorming` skill in
> [obra/superpowers](https://github.com/obra/superpowers) (MIT — see `LICENSE` →
> *Third-party*), extended here with the UX track and the Global Constraints block
> that stages 4–5 depend on.

## Contents

- Order of operations
- UX track (user-facing tasks only)
- The COPY and VISUAL tracks, and their convergence
- Write the spec
- Module dossier — when the run is one brick of a platform
- Self-review — before showing it
- Locked contracts are decisions — the register, not only the spec
- GATE (auto)

## Order of operations

For a **user-facing task** (stage-2 UI verdict = yes) the UX chain runs **first** —
scenarios before interface, always. For everything else, go straight to *Write the
spec*.

**Where stage 0's actor branch is armed** ([`agent-surface.md`](agent-surface.md)),
the order inside this stage is the design order of `AN-2`:

```
foundation → capabilities → contract source + agent scenarios → logic
  → { human flows, screens, scenarios → COPY ∥ VISUAL }
```

The **contract source** is schema-first and committed here: tool definitions with
their input and output schemas and annotations, an OpenAPI file, or a CLI spec, which
the code validates against or is generated from. Agent scenarios are written beside it
because they are its acceptance tests. The UX track below then designs the human lanes
only, each screen a client of the contract. **Dossier section 4, *Contracts in and
out*, is owed by every capability or contract change**, platform module or not;
section 7 only where a human lane exists.

## UX track (user-facing tasks only)

Apply [the artifact-provider contract](companion-skills.md): super-ux is the
preferred provider; equivalent artifacts or the inline fallback remain valid.
Missing or invalid scenario artifacts stop the gate, regardless of provider.
Record each unavailable check by name as NOT_RUN; do not claim a linter ran.
The following chain describes the super-ux provider when available. Other
providers owe the same scenario quality and traces, not these package commands.

0. **The design destination is already decided — read it, don't re-open it.** When
   Figma is on, the stage-0 brief names the team/org and the files — one per surface
   (App, Web, ASO) — ([`grill.md`](grill.md) → *The design destination*), and
   `docs/ux/foundation.md` → *Design tooling* is the canonical record. Confirm each
   recorded file **resolves** before any drawing. **Never create a file when a
   recorded one resolves; if it doesn't resolve, hold the visual track and ask once (an access
   problem; the rest of the run goes on), and never create a
   replacement.** A creation happens at most once per project, in the team the
   brief names, and its URL goes into the canonical record before the first frame.
1. `/ux` — the single super-ux entry: reports which `docs/ux/` layers exist,
   repairs the skeleton, records the Figma on/off choice, recommends the next
   action. Never make the operator pick skills.
2. `ux-foundation` → `docs/ux/foundation.md` — the **WHY**: personas, Jobs to Be
   Done, customer journey maps, user stories (Given/When/Then).
3. `ux-flows` → `docs/ux/flows.md` + `docs/ux/screens.md` — the **HOW + UI map**:
   task analysis, user-flow diagrams (branches, error paths), every screen and
   state with a wireframe and, when Figma is on, a frame link.
4. `ux-scenarios` → `docs/ux/scenarios.md` — the **WHAT**, the source of truth for
   user-facing behavior: scenarios validated against super-ux's format contract —
   IDs, statuses, `Traces:` to stories / journey stages / flows, edge and error
   states enumerated.
5. **Run the linter** (`/ux-lint`, i.e. `python3 docs/ux/lint.py`). It must pass:
   no drift, no orphans, no broken traces, no stale Figma links.

**The screen's source of truth is recorded here, not assumed.** Figma on → the frame
supplies composition, layout and tokens, and `sheleg-design` supplies only what the
frame is silent about. Figma off, or no frame for this screen → the style pack is the
source and the spec says so, screen by screen. A screen whose values were taken from a
screenshot is named as such: *sighted* and *read from the file* are different claims
([`build.md`](build.md) → *A screen is the frame, implemented*).

These skills are **idempotent**: extend the `docs/ux/` layers, never rebuild them; a
validated chain is verified and embedded, and only what is missing is built.

## The COPY and VISUAL tracks, and their convergence

Three tracks, three questions, and they do not substitute for each other:
super-ux decides what the interface must **do**; `copywriting` how it
**sounds**; `sheleg-design` how it **looks**.

- **COPY track — how it sounds.** Every string a product's user will read is written
  through super-ux's `copywriting`, against the brand pack (`docs/brand/voice.md`,
  `terminology.md`, `facts.md`). No pack ⇒ `/brand-init` **before** the first string,
  not after: a voice reverse-engineered from copy already written is a description of
  what happened, not a decision. In scope: interface strings, errors, empty states,
  the landing, pricing, the user-facing changelog. **Out of scope, and saying so is
  what keeps the track honest:** commit messages, PR descriptions, code comments, a
  developer README, internal docs. Running a brand pack over a line in a contributors'
  changelog is the fastest way to teach an agent to route around the track.
- **VISUAL track — how it looks.** Where the task has a visual surface, the visual
  layer goes through `sheleg-design` ([`companion-skills.md`](companion-skills.md)):
  tokens and themes, typography and rhythm, motion and how it degrades to rest, the
  boundary with Figma (tokens as variables, never raw values carried across). Not
  through it: a purely structural change — what sits where is the UX track's — text,
  a backend, an internal script.
- **The VISUAL track leaves a trace, and the gate reads the trace.** "The track ran" is
  not checkable; a record is. The track writes a **director record** in the product's
  repository, beside `docs/ux/`: `docs/design/<surface>/director-record.md`, a header
  line `surface_class: <class>` and one `## <Field>` heading per field. Which fields are
  owed is the brief's `surface_class` ([`stage-00-intake.md`](stage-00-intake.md) → *0 — Intake grill — MANDATORY*, the surface-class bullet):

  | Class | Fields the record owes |
  |---|---|
  | `flagship` | Brief, Mode, Taste, References, Cast, Fork, Rubric, Critique, Markers, Alignment, Quality, Signature, Surfaces, Haptics, ADA, Open |
  | `product` | Brief, Mode, References, Markers, Open |
  | `ad` | Brief, Mode, References, Markers, ADA (the ad rubric profile and safe zones), Open |
  | `internal` | none — the project linter is the floor |

  What each field must say is sheleg-design's contract, and its validator checks it:
  `npx sheleg-design-skill --check-record <file>`. The pipeline's gate is `python3
  scripts/visual_gate.py record <file> --class <surface_class>`: it checks the headings
  itself — present, and not a placeholder — and runs that validator where sheleg-design
  is installed and new enough. Where it is not, the validator reads **NOT_RUN**, never
  PASS, and the gate stands on the heading floor with that said. **The refusal is the
  same file**: `## Mode` saying `declined` and why — *«без дизайна»*, *as is* — passes,
  and a bare `declined` with no reason does not. The Rubric is written **before** any
  direction is rendered; a rubric written after the render grades the render it already
  liked.
- **Each track's refusal is a sentence, never a silence.** *"Без дизайна" / "as is"*
  ends the visual track; *"без бренда" / "draft"* ends the copy track. Either one is
  the operator's to make and costs nothing — but it is **recorded in the brief and
  said out loud in the close-out**, because a track skipped silently and a track that
  ran are the same thing in a transcript. This is the rail's `⊘` rule one layer up: a
  skip nobody can see is indistinguishable from work that happened.
- **Two of the three are a parallel layer, and the third is their only real dependency.**
  COPY and VISUAL both consume the UX track's scenarios; **neither consumes the other**.
  Copy is written against the brand pack and the scenarios, not against tokens; the visual
  is built from the frame and the style pack, not from strings. Writing them in a line —
  which this doctrine did until 2026-08-15 — teaches a run to wait for a result that never
  arrives. The order is `UX → { COPY ∥ VISUAL }`, and the only thing crossing each of
  those two arrows is **the scenario set**.
- **Their convergence needs a check, and it has a real contradiction to catch.** Both land
  on the same screen, so the failure is not that one is wrong: it is that each is right
  alone and they disagree together. Before the spec is committed, compare the two outputs
  and record the answer:
  1. **A string the layout has no room for** — a label, an error or an empty state longer
     than the frame's element, at the frame's own width.
  2. **A state one track has and the other does not** — copy for an empty state the design
     never drew, or a loading state drawn with no string.
  3. **Two names for one thing** — the design system's component name against the
     terminology file's noun, where a user reads both.
  4. **A tone the visual contradicts** — a calm, plain register on a screen whose motion
     and colour say urgency.
  `Tracks converge: clean` is the answer most runs write, and writing it is the point —
  a check whose silence is indistinguishable from not having run is not evidence. This is
  the same rule the harvest applies at stage 0 and the build applies to a fanned-out group
  at stage 5 ([`build.md`](build.md) §4.2a); one shape, three places.

## Write the spec

Path: `docs/specs/YYYY-MM-DD-<topic>/spec.md` with its `spec.json`, committed, the
brief's `<topic>` slug (`spec_judge.py init`; [`artifacts.md`](artifacts.md)). Runs
before 2026-11-28 keep `<artifacts>/specs/YYYY-MM-DD-<topic>-design.md`.

**Every section carries `covers: REQ-…`** — the brief's requirement ids it serves.
This is what makes the brief→spec seam checkable instead of a re-telling: at the
gate, every REQ must appear in at least one section, and a section that covers no
REQ is either scope creep or a missing REQ. Say which.

The spec **locks every shared contract**, because from here on people and subagents
work from it in parallel and can't renegotiate:

- **Types, schemas, signatures** — exact names, exact parameter and return types.
- **File layout** — which files exist, what each one owns.
- **Global Constraints** — the project-wide requirements every task inherits:
  version floors, dependency limits, naming and copy rules, platform requirements,
  exact values. Stage 4 copies this block verbatim into the plan and stage 5 hands
  it to every reviewer, so write it as literal values, never as prose.
- **Error handling and degradation** — what fails how, what the user sees, what
  gets logged.
- **Testing approach** — what proves this works.

For UI tasks the spec **embeds the UX layer**: the validated scenario IDs, the
flows and `SCR-` screens, the CJM stages the feature serves, and the applicable
super-ux patterns and principles. Every user-facing requirement traces to a
scenario ID.

## Module dossier — when the run is one brick of a platform

If stage 2 produced a module map ([`decomposition.md`](decomposition.md)), this
spec is that module's **dossier**, and it is the only document the module's build
gets. Cover all of it, in this order, each section carrying its `covers: REQ-…`:

1. **Purpose and boundary** — what this module delivers, and what it explicitly
   does not (naming the module that does).
2. **Architecture** — the module's internal shape: units, responsibilities, the
   flow of a request or event through it, and where it sits in the platform.
3. **Entities and data** — the entities this module **owns** (it is their source of
   truth), their fields and invariants, their lifecycle/state transitions, storage
   and migrations. Entities owned elsewhere are referenced by id, never copied into
   a second source of truth.
4. **Contracts — in and out.** For every inbound API/event this module serves and
   every outbound one it consumes: exact signature or schema, auth, idempotency,
   versioning, and **the behavior when the other side is unavailable or wrong**.
   These are the seams the map named; here they get their shapes. Outside a
   platform this section is still owed by every capability or contract change
   (*Order of operations*, above).
5. **Business logic and rules** — the rules in the domain's language, each with the
   condition that triggers it and the outcome. Rules that only exist as code are
   rules nobody can review.
6. **Edge and failure cases** — the boundaries (empty, first, last, maximum,
   concurrent), the failure modes (timeout, partial write, duplicate delivery,
   downstream down) and the honest degradation for each. This is the section that
   decides whether the module survives contact with production, so it is not a
   bullet list of "handle errors".
7. **UI / Figma** — for a module with a surface: the super-ux chain (foundation →
   flows → screens → scenarios), the `SCR-` screens and their Figma frame links,
   and the states each screen has (loading, empty, error, partial).
8. **Non-functional** — limits, expected volumes, latency budget, security and
   privacy constraints that bind this module specifically.
9. **Open questions** — anything still undecided, with the latest moment it can be
   decided and who decides. An open question that reaches the plan becomes an
   implementer's guess.

A skipped section says why in one line (`no UI surface`); silence is not a skip. What
stage 1 could not ground (a private API) is **flagged as an assumption**.

## Self-review — before showing it

Read what you wrote with fresh eyes and fix inline. No subagent, no second pass:

1. **REQ coverage:** does every REQ in the brief appear in at least one section's
   `covers:` line, and does every section cover at least one REQ? A missing REQ is
   scope lost here; a section covering none is scope creep or a missing REQ.
2. **Placeholders, contradictions, two readings:** fix them now; the judge fails them.
3. **Internal consistency:** does the architecture match the locked signatures?
4. **Scope:** is this one implementable plan, or does it need decomposition?
5. **Ambiguity:** a requirement read two ways gets one reading, said.
6. **Traceability (UI):** does every user-facing requirement name its scenario ID?
7. **Every check this spec names resolves:** each verification claim names a check that
   exists today or that this plan builds; any other is marked `review`. A green from a
   check nobody watched fail is not evidence, and this stage is where checks are named.
8. **Read the decisions back:** the brief's `## Decisions locked` and stage 2's rejected
   options (`references/brainstorm.md`). A contradiction is resolved out loud: amend the
   spec, or reverse the decision and record it.
9. **Print the cost:** surfaces, guards and REQ rows now versus at stage 2; print all
   three and decide nothing (*never narrow the task silently*).
10. **Run the hygiene gate** over what this stage wrote and record its counts below.

### The `## Self-review` section — committed, not asserted

The checklist above leaves a **committed trace**, last section before the gate.
Every line carries a **computed number, not a tick**: a number nobody computed is
visible as such, and a checkbox never is. `planning.md` uses the identical shape, so
one habit covers both stages.

```markdown
## Self-review

- REQ coverage: <n> in brief, <n> covered, difference <set or ∅>
- Named checks: <n> named, <n> resolve, <n> marked `review`
- Decisions: checked against <the brief's D-table> and <stage 2's rejected options> — <verdict>
- Cost: <surfaces>/<guards>/<REQ> now, <…> at stage 2 — <proportionate | grown, and why>
- Hygiene: <n> checks, <n> findings, <n> open
- Placeholders: <n> · Ambiguity: <n> found, <n> resolved inline
```

## Locked contracts are decisions — the register, not only the spec

A schema, a signature, a status vocabulary or an error shape outlives the spec: run the
**Doc Loop** ([`documentation.md`](documentation.md)) for each that binds future work and
cite its id from the spec section.

**A spec states a contract; the register makes it addressable.** A spec is per-run
and the next one supersedes it; an id survives. If this stage settled something and
no entry names it, the run has agreed to decide it again later.

## GATE (auto)

The spec is judged, never reviewed by the operator instead: `spec_protocol.py check
<dir>/spec.md` and `spec_judge.py check --verify <dir>` both exit 0 (the template
[`spec-template.md`](spec-template.md); judge, rounds and design review in
[`spec-protocol.md`](spec-protocol.md) section 5). The run says "Spec committed to
`<path>`, judged `pass` by <model> (<family>), round <n>". Otherwise apply the fixes and
judge again; after three rounds the open questions go to the owning project's coordinator.

Also: **every section carries `covers: REQ-…` and every REQ appears in one.** UI tasks:
the chain designed, validated and approved, `/ux-lint` green, every user-facing
requirement traced to a scenario ID (or the operator's recorded waiver); **every string
through the COPY track and the visual layer through the VISUAL track, or the refusal
recorded**; where both ran, **their convergence check recorded** (findings with the ruling,
or `Tracks converge: clean`).

With Figma on, every frame link in `screens.md` carries a file key the canonical record
names (a string match, `visual_gate.py filekeys`; the audit's `F` rung, [`audit.md`](audit.md)).

No plan starts before this gate passes.
