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
| **grill-me** / **grilling** | stage 0 intake grill | **The stage is required; this provider is not.** Stage 0 can never be skipped — but it runs either through this skill or through the orchestrator's own grill loop, both compliant with the grill contract | `/plugin marketplace add alirezarezvani/claude-skills` → `/plugin install engineering-advanced-skills@claude-code-skills`; upstream origin `npx skills add mattpocock/skills` |
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
  ✗ grill-me           — provider absent; stage 0 still runs (built-in grill loop,
                         same contract). To use it instead:
                           /plugin marketplace add alirezarezvani/claude-skills
                           /plugin install engineering-advanced-skills@claude-code-skills
  ✓ wiki-update        — ready

🧠 Model for this run: recommended <top tier available>. You're on <current>.
   /model <id> to switch, or "keep current", or name per-stage overrides.

Install the ✗ items you want, answer the model line, then say "continue".
```

Rules:
- Only flag **super-ux** as recommended when the task implies a UI (the stage-0
  grill decides this; when unsure, flag it — a false positive costs one install).
- **superpowers** missing → stop; it's required for the core stages.
- **grill-me missing never blocks** — stage 0 is mandatory, its *provider* is not.
  Say which provider will run and move on; don't present the built-in loop as a
  downgrade.
- Optional tools missing → state the fallback, don't block.
- Re-detect after the operator installs; don't assume.
- The model answer goes into the brief. Don't ask again per stage
  (`model-tiering.md` → *Mechanic*).

## Hand-off the other direction

super-ux's `/ux` menu can hand off *to* this pipeline (its "execute
autonomously" action). When entered that way the UX chain already exists — see
`stages.md` → 0 *Entry-from-super-ux short-circuit*: verify, don't rebuild.
