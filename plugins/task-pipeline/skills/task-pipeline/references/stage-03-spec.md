# Stage 3 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 3 — Spec — with UX track for user-facing tasks
- **How it runs: [`spec.md`](spec.md)** — built into this skill: the UX-track order,
  what the spec must lock (types, schemas, signatures, file layout, the **Global
  Constraints** block stages 4–5 depend on), the self-review pass and the operator
  review gate.
- **UX track (runs FIRST when stage 2 flagged UI; skip entirely otherwise).**
  Requires the **super-ux** skills. If missing on a UI task → give the install
  line and stop (see SKILL.md *Prerequisites*: `/plugin marketplace add
  ssheleg/super-ux` → `/plugin install super-ux@super-ux`, or `npx skills add
  ssheleg/super-ux`). super-ux builds a traced chain — walk it top-down (see its
  `system-map.md`):
  0. **Destination first, when Figma is on.** The brief already names the team/org
     and the files — **one per surface** (App, Web, ASO: store screenshots, icon and
     logo), never one file for every frame; `docs/ux/foundation.md` → *Design tooling*
     is the canonical record. Confirm each **resolves** before drawing. **Never create a file while a
     recorded one resolves; if it doesn't resolve, stop and ask — never create a
     replacement** (that is the duplicate, and it hides a permissions problem).
     A creation happens at most once, in the named team, and its URL is written to
     the canonical record before the first frame.
  1. `/ux` (the only super-ux entry) — reports which `docs/ux/` layers exist,
     repairs the skeleton, records the Figma on/off choice, recommends the next
     action. Never make the operator pick skills.
  2. `ux-foundation` → `docs/ux/foundation.md` — the **WHY**: personas, Jobs to
     Be Done, **customer journey maps (CJM)**, user stories (Given/When/Then).
  3. `ux-flows` → `docs/ux/flows.md` + `docs/ux/screens.md` — the **HOW + UI
     map**: task analysis, user-flow diagrams (branches, error paths), every
     screen + state with wireframe and (Figma on) a Figma frame link.
  4. `ux-scenarios` → `docs/ux/scenarios.md` — the **WHAT** (source of truth for
     behavior): scenarios validated against the scenario-format contract super-ux
     itself ships (`scenario-format.md` — read its current version there, never
     pin one here) — IDs, statuses, `Traces:` to stories/journey stages/flows,
     edge/error states enumerated.
  5. **Run the super-ux linter** (`/ux-lint` or `python3 docs/ux/lint.py`) — it
     must pass: no drift, no orphans, no broken traces or stale Figma links.
  These skills are **idempotent** — reuse and extend existing `docs/ux/` layers,
  never rebuild from scratch. If the chain already exists and is validated (e.g.
  the task entered from super-ux), just verify (linter green) and embed it into
  the spec; only build the parts that are missing.
- **COPY track and VISUAL track — a parallel layer after UX, and their
  convergence.** Three tracks, three questions, none substituting for another:
  super-ux decides what the interface must **do**, `copywriting` how it
  **sounds** (every string a product's user will read, against the brand pack),
  `sheleg-design` how it **looks** (tokens, themes, typography, motion). COPY and
  VISUAL are **parallel** — both consume the UX track's scenarios, neither
  consumes the other — and where both ran, **their convergence check is run and
  recorded before the spec is committed**: each can be right alone and the two
  disagree together on one screen. The full doctrine — each track's scope and
  out-of-scope, the refusal sentences, the four contradictions the check
  catches — is [`spec.md`](spec.md) → *The COPY and VISUAL tracks, and their
  convergence*, its one home. **The VISUAL track leaves a trace, not a fact**: a
  director record at `docs/design/<surface>/director-record.md`, whose fields the gate
  reads by the brief's `surface_class` (`python3 scripts/visual_gate.py record <file>
  --class <c>`), and a refusal is that same file saying `Mode: declined` and why.
- **Spec:** write the approved design to
  `<artifacts>/specs/YYYY-MM-DD-<topic>-design.md` and commit it. Lock all
  shared contracts (types, schemas, signatures, file layout). For UI tasks the
  spec **embeds the UX layer**: links the validated scenario IDs, the flows and
  `SCR-` screens, the CJM stages the feature serves, and the UX
  patterns/principles from super-ux that apply (`best-practices.md`,
  `ux-design-principles.md`, `component-guidelines.md`).
