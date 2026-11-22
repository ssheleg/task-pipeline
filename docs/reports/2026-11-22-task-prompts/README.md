---
report:
  id: task-pipeline/2026-11-22-task-prompts
  kind: audit
  status: active
  date: 2026-11-22
  valid_until: 2026-12-22
  owner: task-pipeline
  supersedes: none
---

# How tasks are written for executors: a check, a run over three days of tasks, and what is still missing

## Main points

1. The family had rules for a task's end result, its finish criterion and for not stopping
   between steps. It had no rule that a handed-over task ends with a pass looking for what
   was missed, and nothing read a task at the moment it was written (section 2).
2. `scripts/task_prompt.py` now reads a task and answers six questions; a plugin hook runs
   it on every subagent dispatch and adds a note, never a block (section 3).
3. Run over 2,410 tasks of three days from 41 projects on one machine: 51% pass. Of 1,058
   working tasks handed to subagents, 68 carried all four parts; a closing pass was asked
   for in 105. Stops for approval are rare: 3 tasks (section 4).
4. Assignments that reach a session from a person or a relay pass in 12% of cases; most
   name neither the end result nor a finish criterion (section 4).
5. Nine mechanics are missing between "the task is given" and "the task is done"; three
   ship in this change, six are board rows with dates and owners (section 5).

## 1. The order

The owner, 2026-11-22 02:54 UTC (Telegram, relayed by the CEO of Fabric, board request
bd16f215): «…верификацию промптов … что мы везде во всех проектах правильно пишем промпты
нашим агентам: всегда описываем конечный результат, к которому хотим прийти; всегда идем
волнами, находим то, что пропускали, и не раскладываем в гейты. И все такие вещи продумай:
каких еще механик нам не хватает, чтобы я отдавал задачу, шел заниматься своими делами,
возвращался и смотрел, как она уже выполнена и готова, причем за оптимальное время, в
оптимальном месте и в оптимальном порядке.»

## 2. What the family already said

Read at task-pipeline 478dce5 (paths under `plugins/task-pipeline/skills/task-pipeline/`).

| Subject | Where | Says |
|---|---|---|
| End result | `references/finish-line.md:23`, `templates/brief.md:119` | "Objective: one sentence: what is true when this iteration is done." |
| Finish criterion | `references/planning.md:197` | a task's definition of done is observable and verifiable |
| No stop between steps | `references/build.md:17`, `references/waves.md:185`, `references/continuity.md:102` | exactly four stops; "Should I continue?" is noise |
| What a dispatch carries | `references/build.md:208-215`, `references/planning.md:464-478` | five things in the prompt; nine in a packet's context closure |
| Rounds that look again | `references/finish-line.md:73-83`, `references/waves.md:208-231` | run by the orchestrator, after the executor returned |

Two gaps. No rule told the executor's own task to end with a pass for what was missed.
`test/prompt_lint.py` reads the skill's doctrine text; nothing read the prompts executors
receive. One line pulled the other way: the implementer contract said "Ask before
starting if anything in the brief is ambiguous" (`references/build.md:239` at 478dce5).

## 3. The check

`scripts/task_prompt.py check <file|->` reads a task, and the brief, plan or packet it
points to when that file can be read.

| Id | Question | Owed by |
|---|---|---|
| P1 | the end result is stated | every task |
| P2 | the finish criterion is named: a check, a command, a condition | work, verify |
| P3 | a closing pass looks for what was missed, or lists what was not examined | work |
| P4 | nothing stops for approval between steps | work |
| P5 | what comes back, and in which form | lookup, verify; a warning on work |
| P6 | where to look, what must not change | a warning |

A task is `work` when it changes something, `lookup` when it only finds or reads, `verify`
when it returns a verdict. The reading is by words, English and Russian: it proves a part
is present, never that the task is good. A brief that cannot be read leaves P1 to P3 open
and says so.

Where it is wired: the dispatch step (`references/build.md` 4.1), the implementer contract
(a closing pass before the report; an ambiguous brief returns `NEEDS_CONTEXT` and never
waits), the wave's close pass (`references/waves.md`), and the hook
`hooks/task-prompt-nudge.sh` before the subagent tool, in every project.

## 4. The run

Corpus: Claude Code transcripts of this machine's default home changed in the three days
to 2026-11-22: 1,968 prompts given to subagents and 442 messages of 200 characters or more
that reached a session from a person or a relay, from 41 project folders. The corpus and
the per-project table hold private text and stay outside this public repository.

| Class | Tasks | Pass | P1 fails / owed | P2 | P3 | P4 |
|---|---|---|---|---|---|---|
| Subagent prompts | 1,968 | 59% | 247 / 1,644 | 374 / 1,622 | 472 / 577 | 0 / 1,058 |
| Assignments to a session | 442 | 12% | 316 / 402 | 108 / 115 | 102 / 133 | 2 / 149 |
| All | 2,410 | 51% | 563 / 2,046 | 482 / 1,737 | 574 / 710 | 2 / 1,207 |

"Owed" is smaller than the class when a task points to a brief that could no longer be
read: 716 tasks (650 subagent prompts), most of them in worktrees removed since. A brief
was read with its task in 164 cases.

Of the 1,058 working subagent tasks: a finish criterion in 766, a return form in 1,031, a
pointer to files in 1,055, a closing pass in 105, all of P1 to P4 in 68.

Shapes of the failures, with the project named by a letter:

- **No end result (P1), project A, 190 words.** "You implement task T-… of the app. Read and
  follow the brief: …. Run the tests, the device build, both lints. Commit and push after
  every green step. Answer briefly: head SHA, checks, files, anything blocked." The task
  names the work and the checks, not what is true afterwards.
- **No finish criterion (P2), project B, 300 words.** "Review round 1 of PR …. Classify P0,
  P1, P2 with file:line and fix; say clean if no P0 or P1." A fix is ordered with no check
  that says the fix holds.
- **No closing pass (P3), nearly every working task.** The task ends at "report the
  commits and the tests"; what the executor did not look at is not asked for.
- **A stop for approval (P4), 3 tasks.** "…wait for approval", «Дождись подтверждения»,
  «дождаться ответа».

Limits of the measurement. The patterns were tuned on samples of this corpus: two false
readings were removed (a wave named as a label, sound waves) and one added (a brief on
disk). No precision figure was measured on a held-out sample, so the shares are an upper
bound on what is missing by name, not a count of bad tasks. The "assignment" class also
holds questions and pasted logs, which fail P1 without being tasks. Isolated account
homes were not read.

## 5. Mechanics missing between "given" and "done"

| # | Mechanic | State | Owner |
|---|---|---|---|
| 1 | The executor's task ends with a pass for what was missed | shipped here (contract, check) | task-pipeline |
| 2 | A task is read when it is written, not in a reference | shipped here (hook, advisory) | task-pipeline |
| 3 | An ambiguous brief returns a question instead of a wait | shipped here (contract) | task-pipeline |
| 4 | An assignment relayed to a session carries its end result and finish criterion; the board checks a request before it is sent | asked of Fabric on the board | fabric-workspace |
| 5 | A run that died is offered at the next session start (loss audit H-03: 64 of 70 ledgers never reached acceptance) | B-179 | task-pipeline |
| 6 | An abandoned ledger does not hold a release (H-04) | B-180 | task-pipeline |
| 7 | The checkpoint at a stage change is written by a hook, not remembered (M-1 R3) | B-181 | task-pipeline |
| 8 | The returned result is read against the task's own finish criterion; the advisory hook is measured for a week, then raised or kept | B-182 | task-pipeline |
| 9 | A brief travels with its task by digest, so a resumed or audited task can still be read (716 of 2,410 could not) | B-183 | task-pipeline |

Time, place and order. Order exists: `graph.py` ranks by what a node unblocks. Place is
half there: B-172 (the build stage asks the machine governor) is open. Time has no
mechanic: a task carries no budget and nobody is told when a run is late; that is part of
B-182 (the task names its budget; the check warns when it does not) and of the Fabric wait
watcher in the loss audit (H-01, owner fabric-agent-adapter).

## 6. Sources

- Family rules: the files and lines in section 2, at task-pipeline 478dce5.
- Hook contract: Claude Code hooks reference, PreToolUse `additionalContext` "added to
  Claude's context alongside the tool result" (code.claude.com/docs/en/hooks, read
  2026-11-22 through a summarising fetch, not byte-checked).
- Loss audit: fabric-workspace `docs/plans/2026-11-22-harness-loss-fixes/specs/skills-and-harness.md`
  at 0079de42 (board request 83d5b776), requirements R3 and R4.
- Corpus and per-project table: the operator's machine, `task-pipeline-data/prompt-audit-2026-11-22/`.
