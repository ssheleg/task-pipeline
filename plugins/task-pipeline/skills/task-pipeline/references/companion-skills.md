# Companion skills — what powers each stage, how to install, what to run

task-pipeline is a thin orchestrator; the actual work is done by companion
skills. Preflight-detect each one; if a needed skill doesn't resolve, **give the
operator the install line immediately** and (for required ones) stop until it's
installed. Never silently degrade a required capability.

## The matrix

| Skill / tool | Needed for | Required? | Install |
|---|---|---|---|
| **superpowers** (`brainstorming`, `writing-plans`, `subagent-driven-development`, `using-git-worktrees`, `test-driven-development`) | stages 2, 4, 5, 6 | **Required** (always) | `/plugin marketplace add obra/superpowers` → `/plugin install superpowers@superpowers` |
| **super-ux** (`ux-foundation`, `ux-flows`, `ux-scenarios`, `ux-audit`, `/ux`, `/ux-lint`) | stage 3 UX track | **Required for any user-facing task** | `/plugin marketplace add ssheleg/super-ux` → `/plugin install super-ux@super-ux` (or `npx skills add ssheleg/super-ux`) |
| **grill-me** / **grilling** | stage 0 intake grill | Optional (built-in grill loop is the fallback) | `npx skills add mattpocock/skills`, or the engineering-advanced-skills marketplace |
| **context7** (MCP) | stage 1 docs study | Recommended (web-search fallback) | connect the context7 MCP server |
| **wiki-update** | stage 9 wiki sync | Optional (skip wiki if absent) | user's wiki skill set |

## Preflight recommendation (emit before stage 0)

At the very start, detect which of the above resolve and print ONE recommendation
block so the operator can arm the full flow before work begins. Example:

```
Pipeline companions:
  ✓ superpowers        — ready
  ✗ super-ux           — this task looks user-facing; recommended. Install:
                           /plugin marketplace add ssheleg/super-ux
                           /plugin install super-ux@super-ux
  ✓ context7           — ready
  ✗ grill-me           — optional; falling back to the built-in grill loop
  ✓ wiki-update        — ready
Recommend installing the ✗ items marked recommended, then say "continue".
```

Rules:
- Only flag **super-ux** as recommended when the task implies a UI (the stage-0
  grill decides this; when unsure, flag it — a false positive costs one install).
- **superpowers** missing → stop; it's required for the core stages.
- Optional tools missing → state the fallback, don't block.
- Re-detect after the operator installs; don't assume.

## Hand-off the other direction

super-ux's `/ux` menu can hand off *to* this pipeline (its "execute
autonomously" action). When entered that way the UX chain already exists — see
`stages.md` → 0 *Entry-from-super-ux short-circuit*: verify, don't rebuild.
