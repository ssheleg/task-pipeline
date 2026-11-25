---
report:
  id: task-pipeline/2026-11-21-brain-task-pipeline
  title: "Project brain: how skills and task-pipeline should read and write project memory (research and spec for the owner's decision)"
  kind: decision-input
  project: task-pipeline
  domains: [ai-agent]
  as_of: 2026-11-21
  status: active
  valid_until: 2026-12-21
  summary: >-
    The estate already holds seven memory systems. What is missing is the consumer side: no stage
    of task-pipeline and no Fabric skill is required to read project memory before work, lessons
    are written to five places, and the shared lesson index is empty. The spec proposes brain/1,
    a read-before and write-after protocol over the existing stores, with cited, dated,
    side-tagged records. Recommendation: build the minimum (read-only recall at intake) in about
    a week, measure for two weeks, then decide on the full version. Public copy: passages the IP
    gate holds are withheld.
  sources:
    - {name: "task-pipeline 1.109.0 shipped skill", path: "plugins/task-pipeline/skills/task-pipeline/", read_at: 2026-11-21}
    - {name: "Installed skills: fabric-agent-adapter 0.96.0, fabric-agents 0.7.5, passioncode 0.2.80, observatory-log 0.35.12", path: "~/.claude/plugins/cache/", read_at: 2026-11-21}
    - {name: "Live read calls: Fabric Memory, Observatory memory/0.1, knowledge-graph (passioncode)", path: "MCP, session 6eacd43c", read_at: 2026-11-21}
    - {name: "research-agent job job_01M7ZKXZFAD4BXCP0T5QAXWVCF (agent memory practices)", path: "raw/research-agent-memory.md", read_at: 2026-11-21}
    - {name: "research-agent job job_01M7ZKY246D8H158CBGDWGYAJN (retrieval and experience reuse in coding agents)", path: "raw/research-agent-coding-retrieval.json.gz", read_at: 2026-11-21}
  produced_by:
    agent: claude-code (Claude Fable 5.2)
    task: "Fabric task 7c34a2fc; owner's order 481968d0 relayed by the Fabric CEO, board request 0b6bfd75"
  supersedes: []
  consumers: []
---

# Project brain for skills and task-pipeline

Research and spec for a decision. Nothing in the skills or in task-pipeline was changed.
The owner's version in Russian is [brief.ru.md](brief.ru.md), rendered as
[brain-task-pipeline.ru.pdf](brain-task-pipeline.ru.pdf).

## Main points

1. **The store exists; the habit does not.** Seven systems hold memory today (section 2).
   No new store is needed.
2. **Nothing reads project memory at intake.** task-pipeline's stage 0 reads eleven source
   kinds, none of them Fabric Memory or a project `kb.*` door, and its "similar past tasks"
   lookup is a grep. Among 18 Fabric-side skills, one names `fabric_memory_search`, as an
   optional bullet.
3. **Write-back is scattered and partly dead.** One lesson is asked for in up to five places.
   The local lesson index measured 0 bytes on 2026-11-21, and this repository's retro has 0
   `**Lesson:**` lines, so the cross-project lesson loop has never run (backlog B-163).
4. **Outside evidence supports a narrow build.** Reusing abstracted past experience raises
   success on repair benchmarks; raw trajectories transfer worst; gains from richer context are
   task-dependent; memory that never expires goes stale; one poisoned write is enough.
5. **Recommendation: the minimum first.** A read-only `brain recall` at stage 0 and a required
   memory read in `working-with-fabric`, about one week, then two weeks of measurement before
   the full version.

## 1. Question and method

The owner asked (2026-11-21, Telegram, message 481968d0, relayed by the Fabric CEO) whether
his skills, the Fabric ones above all, should share a concept of a project brain or memory
that is checked, searched and used properly, and whether task-pipeline can use a brain to
become more efficient and more interesting.

Method: three read-only surveys (memory systems through their MCP doors; the installed skill
texts; task-pipeline at 1.109.0, commit 63cf9ca), two research-agent investigations with
quote-verified claims, and spot checks of the cited lines by the author. Figures are
measurements of 2026-11-21 unless a date is given.

## 2. What exists

_Passage withheld from the public copy by the IP gate (ip-gate/1); the full report is kept in a private repository._

Recorded decisions the spec builds on, not around:

_Passage withheld from the public copy by the IP gate (ip-gate/1); the full report is kept in a private repository._

Overlaps: lessons in five places (plan gap G6); project facts in both Fabric Memory and
Observatory; three graph shapes converging on one; retrieval implemented three times.

## 3. Where context is lost today

**task-pipeline** (`S/` is `plugins/task-pipeline/skills/task-pipeline/`):

- Stage 0 lists sources 0 to 10 (`S/references/knowledge-sources.md:37-53`). Pipeline history
  (6), the retro archive (7a) and lessons from other projects (7b) are three separate greps.
  There is no project-memory row.
- The run ledger is "the run's working memory, not its record" and must never be evidence in
  a later run (`S/templates/run.md:195-209`), so what a run learned survives only if stage 10
  copies it out.
- The lesson loop is empty: `~/.sshlg-skills/lessons/index.jsonl` is 0 bytes (created
  2026-10-27), `docs/evidence/retro.md` has 0 `**Lesson:**` lines (backlog B-163).
- Checkpoints were written once in 293 sessions before the nudge hook
  (`S/references/continuity.md:443`). A step that depends on the agent remembering to do it
  does not happen.
- A `known-domain` answer passes its check with any filename-shaped token as a source
  (`S/scripts/spec_protocol.py:188`). An uncited memory note would pass.
- An `observed` store lesson "binds like a standing instruction" (`S/references/iteration.md:476`)
  without the retro's cap of ten and retirement rules.

**Fabric-side skills** (18 read; versions in the header):

- `working-with-fabric` makes `fabric_whoami` mandatory and `fabric_memory_search` one
  optional bullet (SKILL.md:176). Its retro writes one lesson to three places (SKILL.md:313-316).
- `creating-fabric-agents`, `adapting-projects-to-fabric`, `building-fabric-services`: no
  memory read before work; what the session learns ends in the chat report.
- `working-in-passioncode`: "Read the retrospectives before work" and "Write the lesson" name
  no door (SKILL.md:190); one fact goes to four places after work.
- `observing-products`: findings and baselines stay in the observer's own files.
- observatory-log: two opposite offline rules (`explaining-changes` says write no file,
  `tracking-resources` says write to project docs).
- Three side vocabularies (`personal|org:<id>`, `personal|passioncode|org-x`, Observatory's
  organization), and none in Fabric Memory, wiki-update or project-reports.
- Good models already in the family: the cited, checked consult of `fabric-agents`
  (SKILL.md:67-79), the side check before acting of `tracking-resources` (SKILL.md:46-56),
  `valid_until` of project-reports.

## 4. Outside evidence

From two research-agent runs; every claim below was kept only with a verbatim quote found in
its source. Three sources were flagged by the service as possibly carrying injected text
(marked †); their claims are used as data only.

- Reused, abstracted experience helps repair agents: SWE-Exp reports 73.0% Pass@1 on SWE-bench
  Verified from an experience bank of successful and failed attempts [E5]; STAIR lifts
  mini-SWE-agent v2 from 75.8% to 81.0% with plans built from past trajectories, and its
  ablation finds raw trajectories transfer worst [E6]. Agent Workflow Memory reports relative
  gains of 24.6% and 51.1% on two web benchmarks with fewer steps [E4].
- Richer repository context is task-dependent: map-based workflows cut tokens by 17 to 39%
  but gave little resolution gain on SWE-bench Pro (44.3 to 50.6% against 49.0%) and raised
  wall time [E1]. Retrieval thresholds fail to recognise "nothing relevant" on natural cases [E2].
- Memory needs maintenance: replacement, invalidation, expiration, compaction [M2†]. Zep keeps
  facts bi-temporal and never deletes an invalidated one [M4]. Defaults in Mem0 and Google
  Memory Bank are "never expire", with stale facts reported in use [M5].
- Evaluation must be behavioural: a system can retrieve the right fact while the agent ignores
  or misuses it [M2†].
- Poisoning: one successful write is enough, and agents that write and retrieve more
  aggressively are more exploitable [M8†]; label source, identity, timestamp and model version
  on every entry [M9].
- File memory accumulates old decisions and speculative conclusions until it is hard to trust [E8].
- How much memory helps depends on the model: a strong model kept improving with a full
  191-guideline set [M11].

Not covered by the retrieved sources: LoCoMo results, Letta, A-MEM, LangMem, Reflexion, ExpeL,
a measured hybrid BM25 plus embeddings design for code, and maintenance cost figures.

## 5. Spec: brain/1

### 5.1 Concept

A project brain is **a protocol, not a store**: one read door and one write door over the two
homes the plan already fixed. Every skill reads before work and writes after, the same way.

| Kind | What it answers | Home |
|---|---|---|
| fact | how it works, what was decided, with its reason | project knowledge (`kb.*`, docgraph), Fabric Memory facts |
| episode | a past task: what was asked, what shipped, where it hurt | `docs/evidence/` specs and acceptance files, `pipeline-run/1` (SP-04) |
| lesson | a trap as trigger, check and exit | Observatory lessons, retro |
| recipe | a check that proved a thing here: command and expected output | `verification.md`, acceptance files |
| open item | what a run deferred | carry-over ledgers, backlog |

Every record carries: the claim; a source that resolves (`git:<repo>@<commit>:path#L`, or a
command with its output); `as_of`; `valid_until`; status (`proposed`, `observed`,
`supported`); side (`personal` or `org:<id>`); `supersedes`.

Default expiry by kind (proposed, the owner may change): state of the world (what is open,
deployed, who holds what) 14 days; numbers and measurements 30 days; how-it-works facts 90
days or the next change of the cited file, whichever is first; decisions hold until
superseded; recipes hold until the file they test changes; lessons follow the retro's
retirement rules.

### 5.2 Read before work

1. One call, `brain recall "<task nouns, Russian and English>"`, run by a script. The model
   never reads the store. The answer is at most ten lines, each with kind, claim, citation,
   `as_of` and freshness.
2. **A brain line is a pointer, never evidence.** It enters as `recalled` and is used only
   after re-derivation from its cited source, which makes it `measured`. This is the existing
   rule for carried-in claims (`S/references/knowledge-sources.md:211-252`). Precedence stays:
   code, then documents and ADRs, then the graph, then the wiki, then memory.
3. Expired lines are returned marked `stale: verify`, never as current.
4. An unread or failed store is named `degraded`. Empty is never reported as "nothing known".
5. The side filter is applied before search: only the project's own side.
6. A brain may raise scrutiny (a known trap adds a check). It never lowers a gate.
7. Text from the brain is data. An instruction found in a record is never followed.

### 5.3 Write after work

1. One write, `brain note`, routed by kind to the home in the table. The three and four-place
   writes in the skills become one call with fan-out.
2. No source, no write. A lesson names its check, or acceptance fails (B-173, SD-TPL-03).
3. Search before write; a repeat corroborates the existing record, it does not add a twin.
4. Agent writes are proposals. Promotion is by a second project's corroboration or by the
   operator, as Observatory already does.
5. Redaction as today: no secrets, no people or client names, no private paths.
6. Never edit a record: correct by supersession.

### 5.4 Changes in task-pipeline, by stage

_Passage withheld from the public copy by the IP gate (ip-gate/1); the full report is kept in a private repository._

What makes it "more interesting": the brief opens with what happened the last times
("3 of the last 5 tasks in this area re-opened the release stage; the trap was X; this check
caught it"), a predicted number of rounds, and the next steps that followed similar tasks.
Predictions are shown with their base (how many episodes) and never gate anything.

### 5.5 Changes in the Fabric-side skills

- One shared reference, `project-brain.md`, in fabric-agent-adapter; every skill links it
  instead of describing memory its own way.
- `working-with-fabric`: recall becomes a required step between `fabric_whoami` and the
  claim, also in the preamble for hosts without the hook; Step 7 becomes one `brain note`.
- `task-context` TC-5: the settled side of a task is stored once, so later sessions do not
  ask the owner again.
- `creating-fabric-agents`, `adapting-projects-to-fabric`, `building-fabric-services`: recall
  for prior art before step 1; the session's own findings written back, not left in chat.
- `observing-products`: baselines and known findings read from the brain; recurring findings
  written as lessons.
- `working-in-passioncode`: "read the retrospectives" and "write the lesson" get the named door.
- observatory-log: one offline rule for both skills (queue the write, name it `degraded`).
- One side vocabulary: `personal` or `org:<id>`.
- `fabric-agents` and project-reports stay as they are; they are the model.

## 6. Rollout

Durations are the author's estimates, not measurements.

| Phase | What | Estimate | Depends on |
|---|---|---|---|
| 0 | Fix B-163 (find the lesson writer, prove one cross-project read). Baseline on ten past runs: stage 0 tokens and time, questions to the owner per spec, repeated traps | 2 to 3 days | nothing |
| 1, minimum | `brain recall`, read-only, at stage 0 over what exists (episodes in `docs/evidence/`, lessons, docgraph, Observatory, Fabric Memory); the reference page; required read in `working-with-fabric` | about 1 week | phase 0 |
| measure | two weeks on real tasks, then the owner's decision on the rest | 2 weeks | phase 1 |
| 2 | Write-back: episode and lessons at stage 10, expiry fields, recipes, the shared reference rolled into the Fabric skills | 1 to 2 weeks | SP-01 (2026-12-05), SD-OBS-05 (2026-12-08) |
| 3 | `kb.*` kit module as the read door, risk and next-step prediction, sleep, organization level with a planted-node isolation test | 2 to 3 weeks | SD-FAB-07 (2026-12-12), SD-SKL-01 |

Success metrics, each against the phase 0 baseline:

- stage 0 cost (tokens, minutes) down, with the same or fewer contradictions found later;
- used-hit rate: share of runs where a recalled line was re-derived and cited in the brief
  (behavioural, not "was retrieved");
- stale-hit rate: share of recalled lines that re-derivation contradicted; above 20% the
  expiry defaults are wrong;
- repeated-trap rate: the same lesson class recurring in a project after it was recorded;
- questions that reach the owner per spec;
- lessons promoted from `proposed` (4 of 153 on 2026-11-12);
- cross-side leaks in the planted-node test: 0.

## 7. Risks

| Risk | Evidence | Control |
|---|---|---|
| Stale facts used as current | memory defaults are "never expire" [M5]; wiki lags the repo | expiry by kind; `stale: verify`; re-derive before use |
| False confidence | gates check presence, not truth; `Contradictions: none` is the usual answer | brain lines are `recalled`; a brain never lowers a gate |
| Poisoning | one write is enough [M8†] | writes are proposals with a source; records are data, never instructions; quarantine for outside content |
| Cost and context growth | richer context raised wall time [E1] | script-side search, ten-line budget, no preload |
| Mixing sides | the Observatory lesson probe searches without a project id; `lessons.py` has no organization partition | side tag on every record, filter before search, planted-node test; the businesses the owner's separation rule keeps apart never enter a shared level |
| Low adoption | 1 checkpoint in 293 sessions before the hook | hook nudge plus a gate line; the write is one call |
| A second system beside the plan | plan class C5, "one pattern, many hand-made copies" | brain/1 is a consumer protocol; it adds no store and no engine |
| Privacy of lessons | redaction rules exist in the retro doctrine | same rules at `brain note`; refuse on a path, a name or a secret shape |

## 8. Options and recommendation

| Option | What you get | Cost | Risk |
|---|---|---|---|
| Do nothing | the plan's graph work goes on; skills keep starting from scratch | 0 | the stores fill and nobody reads them; B-163 stays |
| Minimum (phases 0 and 1) | recall at intake, the dead lesson loop fixed, a baseline | about 1.5 weeks | low: read-only, no new store, removable |
| Full (phases 0 to 3) | read and write everywhere, prediction, sleep, organization level | about 5 to 7 weeks, tied to plan dates in December | medium: depends on SP-01, SD-OBS-05, SD-FAB-07 landing on time |

**Recommendation: the minimum now, the full version by a decision after two weeks of
measurement.** Reasons: the read side is where the loss is and it is cheap; the write side
depends on plan rows due 2026-12-05 to 2026-12-19, so building it earlier means building it
twice; outside results say gains are task-dependent, so the estate should measure its own
before paying for all of it; and a read-only start cannot poison anything.

Decisions that are the owner's:

1. Do nothing, the minimum, or the full version.
2. May a brain ever lower scrutiny (skip a check because "it passed before")? Proposed: no.
3. Do lessons cross sides as anonymized mechanics only, with the businesses the owner's
   separation rule keeps apart outside every shared level? Proposed: yes, as the plan's four
   levels say.
4. The expiry defaults in 5.1.

## Sources

Internal: listed in the header; line references are to task-pipeline at 63cf9ca and to the
installed skill versions named there.

External (through research-agent, read 2026-11-21):

- [E1] How Should Agents See Code? https://arxiv.org/html/2611.07286v1
- [E2] Agent Retrieval Bench. https://arxiv.org/html/2607.24882
- [E4] Agent Workflow Memory. https://proceedings.mlr.press/v267/wang25bx.html
- [E5] SWE-Exp. https://arxiv.org/abs/2507.23361
- [E6] Reusing Past Repairs Through Hierarchical Trajectory Abstraction (STAIR). https://arxiv.org/html/2607.29658
- [E8] Agent memory: patterns, tradeoffs, open problems. https://aaif.io/blog/agent-memory-patterns-tradeoffs-open-problems
- [M2†] AI memory: types, architecture. https://arize.com/resources/ai-memory/
- [M4] How Zep tracks provenance in agent memory. https://www.getzep.com/blog/how-zep-tracks-provenance-in-agent-memory/
- [M5] Memory expiry in Mem0, LangGraph, Memory Bank, AgentCore and Graphiti. https://botnet.com/resources/ops-memory-expiry-what-changed
- [M8†] From Untrusted Input to Trusted Memory. https://arxiv.org/html/2606.04329v2
- [M9] Manage AI memory safety in agentic systems. https://learn.microsoft.com/en-us/security/zero-trust/sfi/manage-agentic-memory-safety
- [M11] How Much Should an Agent Remember? https://arxiv.org/abs/2611.26361

## Limits of this report

- The Sound Engine Hub was not called; its figures are from its spec.
- Fabric Memory has no count door; its total is not known.
- The three surveys were run by subagents; the author re-read the lines quoted in section 3
  and the plan passages in section 2, not every row of section 2's table.
- The recommendation was not reviewed by a model of another family.
- This repository is public. Business side names and the closed parts of the agents database
  are left out on purpose; the plan and the decisions are cited by id.

## Corrections
