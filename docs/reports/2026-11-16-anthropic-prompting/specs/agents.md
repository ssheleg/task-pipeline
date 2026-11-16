# Spec: the eight subagent definitions

Component: `plugins/task-pipeline/agents/*.md` and the five tier copies in
`plugins/task-pipeline/skills/task-pipeline/assets/verifier-<tier>.md`.
Checklist: [`../README.md`](../README.md) (P-01..P-14). Read at 1.104.3.

## What changes, and why

A subagent definition is a system prompt read with a fresh context; its description
decides when it is spawned. Measured problems:

| Problem | Where (examples) | Practice |
|---|---|---|
| The role line is buried under a blockquote about other agents | `verifier.md:10-23` | P-01, P-09 |
| Stale counts: "three readings", "three-tier certification" while five tiers exist | `verifier.md:10`, `verifier-unit.md:10-11`, `verifier-seam.md:10`, `verifier-product.md:10`, `verifier-visual.md:11` | P-12 |
| History inside instructions ("until B-080 closed") | `verifier.md:85-86` | P-10 |
| Descriptions carry ids a selector cannot use (Tier 1, R3, pass D, "stage 0's actor branch", AN-5) and capitals (REACH, SEES) | all eight frontmatters | P-11, P-08 |
| "will never see your reasoning" placed next to the output contract | `design-tester.md:10-11`, `agent-tester.md:10-11` | P-03 |
| No "Done when" naming the command that accepts the report | all eight | P-01 |
| Contents lists and restated budgets in ~120-line prompts | `verifier-visual.md:33-38`, `verifier-agent.md:33-38` | P-09 |
| Tool fit: the testers write a report with no `Write` tool; design-tester is told to use Figma MCP tools its `tools:` line excludes | `design-tester.md:21-22`, frontmatter | correctness |
| A time-sensitive legal rule inside the prompt | `design-tester.md:61-62` | P-10 |

## How

1. One skeleton for all eight: role (one line), Done when (the accepting command:
   `graph.py certify`, `graph.py close --verdict`, `design_gate.py`), inputs, numbered
   procedure, severity line, output contract (unchanged JSON), "Ways this goes wrong"
   table, doctrine pointers. "You spawn no subagents." stated once (P-07).
2. Descriptions rewritten third person: what it reads, what it returns, Use when, Not
   for; tiers named by role ("unit tier"), never by number or count.
3. One blindness paragraph for every tier, with no count: "Other tiers read the same
   node at other distances; you never see their reports and they never see yours. Do
   not cite another tier's verdict."
4. "never see your reasoning" becomes "they read only your report".
5. design-tester: `Write` added to tools; the Figma step names the REST route through
   Bash or the mockup files (MCP tool names are not reachable from a subagent's tool
   list); the click-to-cancel rule moves to `references/design-review.md` with its source.
   agent-tester: `Write` added.
6. Terminology: "node" everywhere, "judgement" one spelling, tester walks named
   "design pass", "build pass", "contract pass" so "pass" the verdict stays unambiguous.

## Must not change (consumers)

- Five tier bodies equal their `assets/verifier-<tier>.md` copies byte for byte:
  `test/audit_regressions/host-portability.py:22-25`. Every body edit is made twice.
- `verifier.md`: "the node's `check`" and the exact `**Run the node's `check`.**`
  (`test/validate.py:3575-3590`, `test/negatives/438-*.sh:7`); allowed frontmatter keys
  (`test/graph_test.py:427-436`).
- Verdict keys and tier-report keys parsed by `graph.py` (`:522`, `:543-620`, `:741-835`);
  the `CROSS_TIER` blindness regex refuses a report that quotes another tier.
- `NOT_ASSESSED`, `uncertain`, `unresolved` (`visual_gate.py:77`).
- design-review/1 field names and enums (`design_gate.py:48-50, 150-232, 288`); the
  agent-review/1 JSON block is that contract's only specification
  (`references/agent-surface.md:174`).

## Risks

- A body edit that misses its asset copy fails host-portability: mitigated by editing
  through one script that writes both.
- A rewritten description triggers the agent less or more often: kept to the same
  what/when/not scope; descriptions are read by the orchestrator, which names agents
  explicitly in `references/certification.md`, so spawning is not description-driven.
- Adding `Write` widens two testers' tools: limited to report files they already
  produce through Bash heredocs today.

## Verification

`npm test` (includes host-portability, graph tests, design gate tests, prompt lint),
`bash test/negatives/438-*.sh`, and `python3 test/prompt_lint.py rebaseline`, which
refuses if any metric rose.
