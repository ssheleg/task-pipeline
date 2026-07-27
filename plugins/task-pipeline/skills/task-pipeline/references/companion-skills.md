# Companion skills — what powers each stage, how to install, what to run

task-pipeline is a thin orchestrator; the actual work is done by companion
skills. Preflight-detect each one; if a needed skill doesn't resolve, **give the
operator the install line immediately** and (for required ones) stop until it's
installed. Never silently degrade a required capability.

**Stage 0 is the exception: the grill is part of this skill**
(`references/grill.md`), so it has no companion, no install line and no failure
mode where it can't run.

## The matrix

| Skill / tool | Needed for | Required? | Install |
|---|---|---|---|
| **superpowers** (`brainstorming`, `writing-plans`, `subagent-driven-development`, `using-git-worktrees`, `test-driven-development`) | stages 2, 4, 5, 6 | **Required** (always) | `/plugin marketplace add obra/superpowers` → `/plugin install superpowers@superpowers` |
| **super-ux** (`ux-foundation`, `ux-flows`, `ux-scenarios`, `ux-audit`, `/ux`, `/ux-lint`) | stage 3 UX track | **Required for any user-facing task** | `/plugin marketplace add ssheleg/super-ux` → `/plugin install super-ux@super-ux` (or `npx skills add ssheleg/super-ux`) |
| ~~grill-me / grilling~~ | — | **Not a dependency.** The stage-0 grill is **built into this skill** (`references/grill.md`) — nothing to install, nothing to resolve, no fallback path | — |
| **context7** (MCP) | stage 1 docs study | Recommended (web-search fallback) | connect the context7 MCP server |
| **wiki-update** | stage 9 wiki sync | Optional (skip wiki if absent) | user's wiki skill set |

## Preflight (emit before stage 0)

At the very start, detect which of the above resolve and print ONE block —
companions **plus the model decision** (`model-tiering.md`), so the operator arms
the whole run in a single exchange. Example:

```
Pipeline companions:
  ✓ superpowers        — ready
  ✗ super-ux           — this task looks user-facing; recommended. Install:
                           /plugin marketplace add ssheleg/super-ux
                           /plugin install super-ux@super-ux
  ✓ context7           — ready
  ✓ wiki-update        — ready
  • intake grill       — built in, no install needed

🧠 Model for this run: recommended <top tier available>. You're on <current>.
   /model <id> to switch, or "keep current", or name per-stage overrides.

Install the ✗ items you want, answer the model line, then say "continue".
```

Rules:
- Only flag **super-ux** as recommended when the task implies a UI (the stage-0
  grill decides this; when unsure, flag it — a false positive costs one install).
- **superpowers** missing → stop; it's required for the core stages.
- **Never gate stage 0 on an install.** The grill ships with this skill; there is
  no external grill dependency to detect, recommend, or fall back from.
- Optional tools missing → state the fallback, don't block.
- Re-detect after the operator installs; don't assume.
- The model answer goes into the brief. Don't ask again per stage
  (`model-tiering.md` → *Mechanic*).

## Credit

The built-in grill is adapted from Matt Pocock's `grilling` / `grill-with-docs`
skills (MIT, https://github.com/mattpocock/skills) — see the repo `LICENSE` →
*Third-party*. It is **ported, not depended on**: no install, no resolution, no
version skew.

## Hand-off the other direction

super-ux's `/ux` menu can hand off *to* this pipeline (its "execute
autonomously" action). When entered that way the UX chain already exists — see
`stages.md` → 0 *Entry-from-super-ux short-circuit*: verify, don't rebuild.
