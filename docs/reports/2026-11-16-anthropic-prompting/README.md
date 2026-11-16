---
report:
  id: task-pipeline/2026-11-16-anthropic-prompting
  title: "Anthropic's current prompting and skill-authoring practices, as a checklist for task-pipeline"
  kind: decision-input
  project: task-pipeline
  domains: [ai-agent]
  as_of: 2026-11-16
  status: final
  valid_until: 2027-02-16
  summary: >-
    Fourteen practices (P-01..P-14) distilled from Anthropic's Opus 5.5 prompting
    guide, its general prompting best practices, its skill-authoring best practices
    and the claude.dev playbook for Opus 5.5. Each practice names its source, what it
    means for a skill that other agents load, and how it is checked. The baseline
    measurement of plugins/task-pipeline at 1.104.3 is in raw/baseline.txt.
  sources:
    - name: "Prompting Claude Opus 5.5 (platform docs)"
      url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5"
      read_at: 2026-11-16
    - name: "Prompting best practices (platform docs)"
      url: "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices"
      read_at: 2026-11-16
    - name: "Skill authoring best practices (platform docs)"
      url: "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices"
      read_at: 2026-11-16
    - name: "Getting the most out of Opus 5.5 in Claude and Claude Code (claude.dev, Addy Osmani)"
      url: "https://claude.dev/blog/getting-the-most-out-of-opus-5-5/"
      read_at: 2026-11-16
    - name: "Which Claude model is best to use for knowledge work (claude.com)"
      url: "https://claude.com/resources/articles/using-claude-opus-5-5-as-your-daily-driver-for-knowledge-work"
      read_at: 2026-11-16
    - name: "Anthropic says outdated prompting habits are slowing down Claude Opus 5.5 (The Decoder)"
      url: "https://the-decoder.com/anthropic-says-outdated-prompting-habits-are-slowing-down-claude-opus-5-5/"
      read_at: 2026-11-16
  produced_by: {agent: claude-code, task: prompt-practices-2026-11-16}
  supersedes: []
---

# Anthropic's prompting practices, as a checklist for task-pipeline

task-pipeline is prose that other agents load and act on, so Anthropic's guidance on
writing prompts and skills applies to every file of it. The five sources above were
read on 2026-11-16; this page keeps only what changes how a skill should be written.
Quotes are short; the sources hold the full text.

## The checklist

| Id | Practice | Source | What it means for this skill | How it is checked |
|---|---|---|---|---|
| P-01 | Give the whole task at once and say what "done" looks like, and when to stop and ask. | Opus 5.5 playbook §1; prompting guide "Unattended agentic runs" | Every entry point (SKILL.md, each command mode, each subagent) states its finish line and its legitimate stops in one place near the top. | Read: each entry file has a "Done when" and a "Stop only when" line. |
| P-02 | Remove "think carefully", "think step by step" and similar lines; effort is the control. | Opus 5.5 guide "Thinking instructions"; playbook §1 | No instruction asks the model to think harder or to deliberate; depth comes from effort. | `test/prompt_lint.py`: rule `think-instruction`. |
| P-03 | Never ask the model to reproduce its internal reasoning in the reply; ask for a short explanation or the actions taken instead. Such requests can be refused (`reasoning_extraction`). | Opus 5.5 guide "Safeguard refusals"; playbook §5 | Subagent output contracts ask for verdicts, evidence and a short rationale, never "your reasoning" or "your thought process". | `prompt_lint.py`: rule `reasoning-extraction`. |
| P-04 | Name the specific early stops to avoid (a summary that announces the next step, an offer to continue, a list of non-blocking decisions, stopping because a milestone feels like a report point) and the stops that are wanted. Keep confirmation for risky or irreversible acts. | Opus 5.5 guide "Unattended agentic runs" | The run rule names the four unwanted stops and the wanted ones (nothing can move without a person; a protected step), once, in the entry file. | Read: the four stops are named in SKILL.md. |
| P-05 | Treat a text-only end of turn as a report, not as completion; cap automatic continuations at two or three. | Opus 5.5 guide "Unattended agentic runs" | Waves and continuity loops count automatic continuations and stop after three on the same task, with the open items named. | Read: waves.md and continuity.md carry the cap. |
| P-06 | Keep the task list in a file the model updates; it survives compaction. | Playbook §2; best practices "Workflows across multiple context windows" | The run ledger is the task list; every mode names it and says to tick it as work lands. Already the design (run.md, graph.json); keep it. | Read. |
| P-07 | Fan big work out to subagents and check each one's evidence before accepting it; do not spawn subagents for what one grep answers. | Playbook §2; best practices "Subagent orchestration" | Verifier tiers stay; the orchestrator checks a returned verdict's evidence. A damping line names when not to delegate. | Read. |
| P-08 | Soften aggressive emphasis. Current models follow the system prompt closely; "CRITICAL: you MUST" causes overtriggering. Explain why a rule exists instead of shouting it. | Best practices "Tool usage" and "Add context"; skill best practices "Concise is key" | Bold and capitals are kept for the few words a reader must not miss; a rule carries its reason in one clause. | `prompt_lint.py`: the `bold` and `caps` ratchet. |
| P-09 | Be concise: the context window is shared. Assume the model already knows what a capable engineer knows; SKILL.md under 500 lines; details in references read when needed; references one level deep. | Skill best practices "Concise is key", "Progressive disclosure", "Token budgets" | SKILL.md is the index; history, incident narratives and justifications move out of files a run loads. | `prompt_lint.py`: `skill-length` and the `words` ratchet; reference depth is read. |
| P-10 | No time-sensitive or historical content in instructions; keep old patterns in a clearly marked section or out of the loaded file. | Skill best practices "Avoid time-sensitive information" | Version notes ("until 1.98.0 …"), incident dates and changelog prose leave the files a run reads; CHANGELOG.md holds them. | `prompt_lint.py`: the `version_history` ratchet. |
| P-11 | Descriptions are third person, say what the skill does and when to use it, and are the only text skill selection reads. | Skill best practices "Writing effective descriptions" | Every SKILL.md and agent description: what + when + when not, no internal ids. | `prompt_lint.py`: `description` (presence, length, point of view); ids are read. |
| P-12 | Consistent terminology; one term per concept. | Skill best practices "Use consistent terminology" | A term list for the run (stage, gate, node, REQ, ledger, brief) and no synonyms in entry files. | Read, plus the glossary in SKILL.md. |
| P-13 | At the end of a run, say first what is needed from the person, then what changed and what was found; mark what could not be confirmed and where it was looked for. | Playbook §3 | Stage 10's hand-back and every mode's close start with "Blocked on you", then "Changed", "Found", "Not confirmed". | Read: acceptance.md and the command's close. |
| P-14 | Mark pasted or untrusted content and follow instructions in it only where the user's own message asks to; keep untrusted content out of what an agent acts on. | Opus 5.5 guide "Mark pasted text" and "Explore context" | Stage 0's harvest treats pasted text, board messages and fetched pages as data; only the operator's own words are instructions. Already a rule in the family; state it in the grill. | Read: grill.md names it. |

## What does not change

- The gates, the kernel (scope, evidence, deps, resume), the verifier tiers and every
  script contract stay as they are. This work rewrites how the doctrine is said, not
  what it requires.
- Anything a test parses (section anchors, the triggers paragraph the hub's routing
  hook matches, schema fields) keeps its exact text unless the test changes with it.

## Baseline (1.104.3, measured 2026-11-16)

`raw/baseline.txt` holds the numbers for `plugins/task-pipeline`: 20 391 lines and
208 571 words of Markdown, 3 712 bold spans, 1 881 capitalised words, 2 884 em dashes,
24 version-history references, one "step by step" instruction and no reasoning-extraction
request. The full test suite passed (`npm test`, exit 0).
