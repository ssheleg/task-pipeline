report: model-budget-ab
date: 2026-11-23
project: task-pipeline
status: final

# Money by role: the review of the routes and the A/B test of quality and price

The owner's order of 2026-11-23 18:58 UTC (relayed by the Fabric CEO; host instructions, *Model and token budget by
role*): tokens buy only the thinking that decides, the spec's text is written on the subscription from the thinker's
meanings, validators answer by tokens one call each, every token route is tracked, and quality is not lost.

## 1. Review: where each step called which model, on which route

Read on 2026-11-23 from task-pipeline `26bb446` (v1.113.0), the host council file, the family's other members
(sshlg-skills checkout: no member besides task-pipeline calls a model; `agent-stack` only documents LLM billing) and
the one real council run so far (fabric-workspace, memory healing spec, branch `memory-healing-2026-11-23` at
`59f54b13`, `docs/plans/2026-11-23-memory-healing/`).

| Step | Model and route before | Model and route by the rule (1.114.0) | Spend measured |
|---|---|---|---|
| Spec analysis, gap check, sizing (stages 0 to 2) | the session's model, subscription | the same (routine); a deciding analysis goes into the thinker's call | 0 |
| Spec definition: meanings | not separate | Fable 5.2 by tokens, ONE call (`meanings.py write`) | A/B: USD 0.39 and 0.47 a spec (section 2) |
| Spec definition: text | v1.110.0 rule: the session's model; memory healing in practice: Fable 5.2 by tokens wrote the whole text | Opus 5.5 writer on the subscription (`meanings.py writer-task`) | memory healing: USD 21.65 over 9 Fable calls, 6 of them cut by the length limit; by the rule: 0 |
| Research planning | the session's model | the same (`spec_protocol.py research plan` is mechanical) | 0 |
| Research scouts, code and mathematics specialists | "working tier", route unnamed | agents on the subscription | 0 |
| `research validate` | any model by tokens; usage kept, cost not booked | tokens, one call, never retried, booked (`research.validate`) | 2026-11-21 dossiers: USD 0.009 to 0.178 a call |
| Council panel | six vendors by tokens, Opus 5.5 among them | GLM 5.3, Kimi K3.1 Pro, Grok 4.7, Gemini 4 Argon, Astra (`openai/gpt-6.2-astra-pro`, BYOK) by tokens, one call each; Opus on the subscription by `--import` | memory healing round 2 panel: USD 1.30 booked, Opus 0.49 of it; Astra booked as 0 (see below) |
| Council judge | Fable 5.2 by tokens | the same | memory healing: USD 1.64 and 2.20 a round |
| Build, tests, deploy, verifiers, design and agent testers | `model: inherit` (the session, subscription) | the same | 0 |
| Learning: retro, lessons, doc-graph healing | scripts, no model | the same | 0 |
| fabric-workspace memory healing, the model step (`memory_heal_model.py`) | Kimi K3.1 Pro by tokens per chunk | not task-pipeline's; its spend is in its own output only: a finding for that project | not read here |

**Two accounting defects found and fixed.** (1) A call through our own OpenAI key (BYOK) answers `usage.cost = 0`
with the real price in `usage.cost_details.upstream_inference_cost` (measured 2026-11-23 with one call to
`openai/gpt-6.2-astra-pro`: cost 0, upstream USD 0.014168). The memory healing council booked Astra's 300,026 tokens
over two rounds as free. (2) `consilium.py review --judge-only` wrote the reused panel verdicts with cost 0, so round
1's ledger shows the panel as free.

## 2. A/B on two real specs

**Specs.** S1: this order itself (brief `s1-model-budget/brief.md`, inputs: the three doctrine files at `26bb446`).
S2: test-stand-agent's proposal for the design-tester's device configurations (board request 77741b8d;
`s2-design-tester-config/brief.md`). Both size M, no research dossier in either arm.

**Arms.** *Before*: Fable 5.2 by tokens writes the whole spec in one call (`before.py`, the practice of the memory
healing spec). *After*: Fable 5.2 by tokens writes the meanings in one call (`meanings.py write`), then an Opus 5.5
agent on the subscription writes the spec from them (`writer-task.md`, `meanings.py writer-task`). Same thinker, same
reasoning effort (medium), same inputs.

**Judging.** Blind: `compare.py` strips the lines that would name an arm and alternates the letters across the pairs
(`compare/key.json`); `consilium.py decide` with the host council (GLM, Kimi, Grok, Gemini, Astra by tokens, one call
each) and Fable 5.2 as the judge. The judge's family also thought both arms' meanings, so the panel's ranking is
reported beside the judge's pick.

## 3. Results

Every number below is read from the round ledgers and `results.json` (computed by the script in this commit's
history from `*/compare-v*/council/round-1/`). Panel: GLM 5.3, Kimi K3.1 Pro, Grok 4.7, Gemini 4 Argon, Astra; judge
Fable 5.2. Letters alternated across rounds (`compare-v*/key.json`).

| Pair and version of the "after" arm | Panel for "after" | Judge | Panel mean score after / before |
|---|---|---|---|
| S1 v1: the writer filed gaps as owner questions | 1 of 5 | before | 6.6 / 7.8 |
| S2 v1: the same | 1 of 5 | before | 6.6 / 7.8 |
| S1 v2: the writer decides tactics, checks prove truth, examples checked | 0 of 5 | before | 6.0 / 8.0 |
| S2 v2: the same | **5 of 5** | **after** | **8.3 / 6.2** |
| S1 v3: v2 plus the council on the meanings before the writer | **5 of 5** | **after** | **7.8 / 5.4** |

**What lost and why.** v1 lost both pairs for one reason the judges named in both: the writer's task told it to
file a gap as an `unknown` owner question, so dates and fifteen tactical questions went back to the owner. v2 fixed
the writer and won S2, but lost S1 on the meanings themselves: the thinker's short call bent the order (a retry where
the order says one request, size S exempted, a cost rule that could count twice), and the writer, who may not change
a meaning, carried it into the spec. The council on the meanings (one round, USD 1.21) caught exactly those as three
blockers; v3, written from the corrected meanings, won S1 unanimously. So the release ships v2's writer task and
v3's order: meanings, then the council on them from size M, then the writer.

**Price, the thinking that decides on tokens only.**

| | Before: the thinker writes the whole spec | After: meanings + council on them + writer on the subscription |
|---|---|---|
| S1 | USD 3.42 (a first call spent 32,000 tokens reasoning and returned no text, USD 1.33; the second 50,924 output tokens, USD 2.09) | USD 1.76 (meanings 0.55, council 1.21, writer 0) |
| S2 | USD 1.02 | USD 0.49 measured without the council on the meanings; with it, about USD 1.5 by S1's council cost (an estimate) |
| memory healing spec (fabric-workspace, before this rule) | USD 21.65 over 9 calls, 6 cut by the length limit | not rerun |

The writer's work moved to the subscription (the Opus agents used 159k to 322k subscription tokens a spec). The
council that judges the finished spec (stage 3, size M and L) runs in both arms and is not counted here. The whole
experiment cost USD 13.54 over 43 token calls (`spend.py summary --task model-budget-ab`), including the discarded v1
meanings (USD 0.86).

**Limits.** Two specs, one judge model of the same family as the thinker (the panel of five other vendors agreed with
it in every round); size M only; S2 v2 ran without the council on the meanings. One measurement is not a trend: every real spec
from now on books its calls (`spend.py`), so the next comparison reads the ledger instead of rerunning both arms.

**Files.** Briefs `*/brief.md`; inputs `*/input-*.txt` (copies at `26bb446`); the arms `*/before-spec.md.txt`,
`*/after-spec.md.txt`, `*/v1-*`, `s1-model-budget/v2-*`; the meanings `*/meanings*.md.txt` with their `.meta.json`;
the writer tasks; the rounds `*/compare-v*/` and `s1-model-budget/meanings-review/`. Raw model output is kept as
`.txt`, so its relative links are not read as this repository's links.
