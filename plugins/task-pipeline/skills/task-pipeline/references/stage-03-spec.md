# Stage 3 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 3 — Spec — with UX track for user-facing tasks
- **The mechanical gate:** `spec_protocol.py check <spec>` passes (sections owed by
  its size, the classed question ledger, the research, no open decision in prose):
  [`spec-protocol.md`](spec-protocol.md).
- Who does what ([`spec-protocol.md`](spec-protocol.md) → *The loop*): the author defines
  the spec and plans the research; other agents research; the author and validators
  of another family verify.
- **How it runs: [`spec.md`](spec.md)** — built into this skill: the UX-track order,
  what the spec must lock (types, schemas, signatures, file layout, the **Global
  Constraints** block stages 4–5 depend on), the self-review pass and the judge.
- The judge replaces operator review (S0): [`judge-rubric.md`](judge-rubric.md).
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
- **COPY track and VISUAL track, after UX, in parallel, and their convergence.**
  super-ux decides what the interface must **do**, `copywriting` how it
  **sounds**, `sheleg-design` how it **looks**; where both COPY and VISUAL ran,
  their convergence check is recorded before the spec is committed. The doctrine
  is [`spec.md`](spec.md) → *The COPY and VISUAL tracks, and their convergence*.
  **The VISUAL track leaves a trace, not a fact**: a director record at
  `docs/design/<surface>/director-record.md`, whose fields the gate reads by the
  brief's `surface_class` (`python3 scripts/visual_gate.py record <file> --class <c>`);
  a refusal is that same file saying `Mode: declined` and why.
- **Spec:** write the approved design to
  `<artifacts>/specs/YYYY-MM-DD-<topic>-design.md` and commit it. Lock all
  shared contracts (types, schemas, signatures, file layout). For UI tasks the
  spec **embeds the UX layer**: links the validated scenario IDs, the flows and
  `SCR-` screens, the CJM stages the feature serves, and the UX
  patterns/principles from super-ux that apply (`best-practices.md`,
  `ux-design-principles.md`, `component-guidelines.md`).
