# Stage 3 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 3 — Spec — with UX track for user-facing tasks
- **The mechanical gate:** `spec_protocol.py check <spec>` passes (the template
  [`spec-template.md`](spec-template.md), its sections, a check per fact, the classed
  ledger, no open decision) and `spec_judge.py check --verify <dir>` exits 0 (a judge of
  another family passed this exact content; [`spec-protocol.md`](spec-protocol.md) section 5).
  Until then `build-gate.sh` refuses product edits.
- Who does what ([`spec-protocol.md`](spec-protocol.md) → *The loop*): the author defines
  the spec and plans the research; other agents research; the author and validators
  of another family verify.
- **How it runs: [`spec.md`](spec.md)** — built into this skill: the UX-track order,
  what the spec must lock (types, schemas, signatures, file layout, the **Global
  Constraints** block stages 4–5 depend on), the self-review pass and the judged gate.
- **Where the actor branch is armed, the contract comes before the screens**
  ([`agent-surface.md`](agent-surface.md); [`spec.md`](spec.md) → *Order of
  operations*): `foundation → capabilities → contract source + agent scenarios →
  logic → human flows, screens and scenarios → COPY and VISUAL`. Dossier section 4
  (*Contracts in and out*) is owed by every capability or contract change, not only
  by a platform module; section 7 only where a human lane exists. The agent tester's
  **pass C** reads the contract source cold. **agent-stack** (`agent-interop`) is the
  companion while a product's agent surface is designed: the contract source and
  snapshot, the gate protocol (`AN-7`) and a safe surface (`AN-8`); recommended,
  never a gate ([`companion-skills.md`](companion-skills.md)).
- **UX track (runs FIRST when stage 2 flagged UI; skip entirely otherwise).**
  Apply [the artifact-provider contract](companion-skills.md): super-ux is the
  preferred provider; equivalent artifacts or the inline fallback remain valid.
  Missing or invalid scenario artifacts stop the gate, regardless of provider.
  Record each unavailable check by name as NOT_RUN; do not claim a linter ran.
  The following chain describes the super-ux provider when available. Other
  providers owe the same scenario quality and traces, not these package commands.
  The chain, its order (destination, `/ux`, foundation, flows and screens,
  scenarios, `/ux-lint` green) and the Figma destination rule live in
  [`spec.md`](spec.md) → *UX track*; reuse and extend existing `docs/ux/` layers.
- **The COPY track and the VISUAL track, after UX, in parallel**: super-ux decides what the interface
  does, `copywriting` how it sounds, `sheleg-design` how it looks; where both ran, their
  convergence check is recorded. The VISUAL track leaves a trace: the director record
  `docs/design/<surface>/director-record.md` (`python3 scripts/visual_gate.py record <file>
  --class <c>`), or that file saying `Mode: declined` and why
  ([`spec.md`](spec.md) -> *The COPY and VISUAL tracks, and their convergence*).
- **Spec:** write the approved design to
  `docs/specs/YYYY-MM-DD-<topic>/spec.md` (`spec_judge.py init`) and commit it. Lock all
  shared contracts (types, schemas, signatures, file layout). For UI tasks the
  spec **embeds the UX layer**: links the validated scenario IDs, the flows and
  `SCR-` screens, the CJM stages the feature serves, and the UX
  patterns/principles from super-ux that apply (`best-practices.md`,
  `ux-design-principles.md`, `component-guidelines.md`).
