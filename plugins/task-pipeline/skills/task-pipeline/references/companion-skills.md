# Companions — what's built in, what's optional, what to install

**The pipeline's doctrine is entirely built into this skill.** Stages 0, 2, 3, 4, 5,
6 and 10 run from `references/*.md` — no companion plugin, no resolution step, no
fallback path, no version skew, and no failure mode where a stage can't run because
something isn't installed.

What remains is a short list of **optional** companions that make individual stages
better, plus one that is required only for user-facing work.

## Built in — nothing to install

| Stage | Doctrine |
|---|---|
| 0 Knowledge harvest (pre-grill) | `references/knowledge-sources.md` |
| 0 Intake grill | `references/grill.md` |
| 2 Brainstorm | `references/brainstorm.md` |
| 2 Decompose (platforms only) | `references/decomposition.md` |
| 3 Spec | `references/spec.md` |
| 4 Plan | `references/planning.md` |
| 5 Build (isolation, subagents, fix loop) | `references/build.md` + `references/review.md` |
| 5–6 TDD + suite gate | `references/tdd.md` |
| 10 Acceptance (REQ close-out) | `references/acceptance.md` |
| 10 + any audit (finding what's missing) | `references/audit.md` |
| any repeating loop | `references/loop-guard.md` |

## The matrix

| Skill / tool | Needed for | Required? | Install |
|---|---|---|---|
| **super-ux** (`ux-foundation`, `ux-flows`, `ux-scenarios`, `ux-audit`, `/ux`, `/ux-lint`) | stage 3 UX track | **Required for any user-facing task** | `/plugin marketplace add ssheleg/super-ux` → `/plugin install super-ux@super-ux` (or `npx skills add ssheleg/super-ux`) |
| **context7** (MCP) | stage 1 docs study | Recommended (web-search fallback) | connect the context7 MCP server |
| **Figma** (MCP) | stage 3 UX track, when the project designs visually — super-ux mirrors each `SCR-` screen/state into a frame | Optional, **UI + Figma-on only**. Absent → super-ux degrades to text-only *by itself and never blocks*, so shipping a UI feature with no mockups becomes a silent scope call — which is why the stage-0 sweep decides it | connect the Figma MCP server (`/mcp`, or your claude.ai connectors) |
| **[obsidian-wiki](https://github.com/ar9av/obsidian-wiki)** (`wiki-query`, `wiki-update`) | **stage 0 harvest** (query what's already known) **+ stage 9 sync** | **Recommended** — never a gate; absent → harvest runs on repo docs alone | `pip install obsidian-wiki` → `obsidian-wiki setup --vault /path/to/your/vault` |
| ~~superpowers~~ | — | **Not a dependency.** Stages 2/4/5/6 run on the built-in doctrine above. See *Optional bridge* | — |
| ~~grill-me / grilling~~ | — | **Not a dependency.** The stage-0 grill is built in (`references/grill.md`) | — |

## Optional bridge — substituting an external skill set

An operator who already runs an equivalent skill set may map it onto stages 2/4/5/6
in their `pipeline.json` → `skills[]`, e.g. `superpowers:brainstorming`,
`superpowers:writing-plans`, `superpowers:using-git-worktrees`,
`superpowers:subagent-driven-development`, `superpowers:test-driven-development`.

Rules for that bridge:

- **It is a substitution, never a requirement.** Nothing detects it, nothing
  recommends it, nothing waits for it, and its absence is never an error.
- **The gates still govern.** Whatever runs a stage, `stages.md` decides when the
  stage is done.
- **Never mix providers inside one stage** — either the built-in doctrine runs it or
  the substitute does; interleaving two review loops produces neither.

## Preflight (emit before stage 0)

Detect the optional companions and print ONE block — companions **plus the model
decision** (`model-tiering.md`), so the operator arms the whole run in a single
exchange:

```
Pipeline companions (stage doctrine is built in — nothing to install for it):
  ✗ super-ux           — this task looks user-facing; required for the UX track:
                           /plugin marketplace add ssheleg/super-ux
                           /plugin install super-ux@super-ux
  ✓ context7           — ready
  ✗ Figma MCP          — this task is user-facing and the project designs in Figma
                         (docs/ux/foundation.md → Design tooling). Without it the
                         UX chain still runs, text-only — no mockups this run:
                           connect the Figma MCP via /mcp
                         (say "text-only is fine" and I'll record that instead)
  ✗ obsidian-wiki      — recommended: stage 0 queries it before grilling you,
                         stage 9 syncs back what this run learned:
                           pip install obsidian-wiki
                           obsidian-wiki setup --vault /path/to/your/vault
                         (running without it — the harvest uses repo docs only)

🧠 Model for this run: recommended <top tier available>. You're on <current>.
   /model <id> to switch, or "keep current", or name per-stage overrides.

Install the ✗ items you want, answer the model line, then say "continue".
```

Rules:

- Only flag **super-ux** when the task implies a UI (the stage-0 grill decides;
  when unsure, flag it — a false positive costs one install).
- **obsidian-wiki**: detect via `~/.obsidian-wiki/config` or a resolving
  `wiki-query`/`wiki-update`. Present → say `✓ ready` and use it in the harvest.
  Absent → print the two install lines **once** and continue; never ask twice in a
  run and never block a stage on it ([`knowledge-sources.md`](knowledge-sources.md)).
- **Figma MCP**: flag it only when the task is user-facing **and** the project
  designs visually — read `docs/ux/foundation.md` → *Design tooling* first; no
  record yet means the choice itself is a stage-0 question (super-ux's default is
  on). Detect the official Figma MCP tools; **how** frames get built, named and
  linted is entirely super-ux's — its own `figma-integration.md` and
  `figma-structure.md` own that — while this preflight only decides whether the run
  has the capability
  and, if not, what ships instead. That last part is the point: super-ux recommends
  the MCP and then *continues text-only on its own*, so without a recorded answer
  the run silently narrows from "designed" to "described". The sweep row is
  `3 Design surface` ([`grill.md`](grill.md) → *The autonomy sweep*).
- **Never gate any stage on an install** except the stage-3 UX track on a UI task.
- Optional tools missing → state the fallback, don't block.
- Re-detect after the operator installs; don't assume.
- The model answer goes into the brief. Don't ask again per stage
  (`model-tiering.md` → *Mechanic*).

## Credit

The built-in doctrine is **ported, not depended on**:

- The stage-0 grill is adapted from Matt Pocock's `grilling` / `grill-with-docs`
  skills (MIT, https://github.com/mattpocock/skills).
- Stages 2–6 are adapted from the `brainstorming`, `writing-plans`,
  `using-git-worktrees`, `subagent-driven-development`, `test-driven-development`
  and `requesting-code-review` skills in obra/superpowers (MIT,
  https://github.com/obra/superpowers).

Both notices live in the repo `LICENSE` → *Third-party*.

## Hand-off the other direction

super-ux's `/ux` menu can hand off *to* this pipeline (its "execute autonomously"
action). When entered that way the UX chain already exists — see `stages.md` → 0
*Entry-from-super-ux short-circuit*: verify, don't rebuild.
