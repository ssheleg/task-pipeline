---
report:
  id: task-pipeline/2026-10-13-fw07-stage-reading-floor
  title: "Stage reading-floor split: source feasibility and acceptance"
  kind: decision-input
  project: task-pipeline
  domains: [ai-agent]
  as_of: 2026-10-13
  status: draft
  valid_until: 2026-10-27
  summary: >-
    At accepted 1.94.0 source, stages.md contains 17616 cl100k tokens across
    967 lines. A conservative gate-spine model can reduce the stage-0 component
    of the reading floor, but 108 files cite the old address and many guards
    parse its sections. This is a source-only implementation proposal, not
    evidence of lower billed tokens or unchanged native-agent quality.
  sources:
    - name: "Frozen accepted source"
      url: "https://github.com/ssheleg/task-pipeline/tree/4d750573ce53ea4c7ffa2bde192ee35b59acefa7"
      read_at: 2026-10-13
    - name: "Measured source and literal consumers"
      path: "raw/measurement.json"
      read_at: 2026-10-13
  produced_by: {agent: codex, task: FW07-STAGE-READING-FLOOR}
  supersedes: []
  consumers: [task-pipeline]
---

<sub>ssheleg skills — task-pipeline · evidence-docs · agent-sync · make-skill · project-reports</sub>

# Stage reading-floor split: source feasibility and acceptance

Source: `4d750573ce53ea4c7ffa2bde192ee35b59acefa7`, package 1.94.0. This is a
planning artifact. No shipped skill, reference, test, hook or workflow changes
are made here. The release owner's exact-source gate remains separate.

## Decision proposed

Proceed with B-043 as a lossless relocation of stage detail, retaining
`references/stages.md` as the default-profile gate spine. Preserve every complete
gate, its stage id/name/type and freedom level, the run checklist, and every
run-wide section. Give each stage one explicitly named local detail reference and
require reading that reference on entry or resume **before stage work**. A custom
profile still owns its own stage ids and doctrine; do not map its ids onto the
example's 0–10 flow. An unreadable required detail is a named unavailable input,
not permission to advance or silently substitute the checklist's short form.

This addresses the user's request for cheaper loading while preserving obligations.
It does not change when a skill is selected, remove catalogue descriptions, modify
host visibility, or establish that a model obeyed the reading instruction.

## Measurements and method

Run `python3 -B docs/reports/2026-10-13-fw07-stage-reading-floor/measure.py` from a
checkout containing the frozen commit. It reads Git blobs only, uses installed
`tiktoken` with `cl100k_base`, and produces [measurement.json](raw/measurement.json)
and [the complete literal-address census](raw/consumers.json). No provider or model
was called. Catalogue lookup selected make-skill for authoring guidance; the reports
catalogue contained no prior task-pipeline report at this cut.

| Measurement | Frozen observation |
|---|---:|
| Entire stages.md | 17,616 tokens; 967 lines |
| SKILL.md body, excluding front matter | 4,638 tokens; 263 lines |
| Reference files directly in the skill | 41 |
| Literal stages.md occurrences across tracked text | 327 lines in 108 files |
| Shipped-surface occurrences | 36 lines |
| Tests / negative-test occurrences | 78 / 41 lines |
| Documentation / historical-evidence occurrences | 57 / 115 lines |

The historical B-043 row's 13,161 tokens is an old observation. The prior 160-line
reconnaissance used selected directories; the 327-line census above includes all
tracked text at the frozen source. It is a literal-address census, **not proof that
all indirect consumers were discovered**. Recursive installers, reference discovery
and hook globs also matter, as discussed below. Historical evidence is retained as
historical; it is not bulk rewritten to advertise the new layout.

A deliberately conservative syntactic model retains the complete suffix beginning
at each `GATE` bullet, stage headings/freedom lines, and all non-stage sections.
It measures **8,386 tokens before adding routes**. Adding the existing stage-0 detail
prefix gives **11,258 tokens**, versus 17,616 for the original stages component:
6,358 fewer tokens before final routing overhead. Stage-0 heading/freedom content
is conservatively counted twice in this model. This is feasibility evidence, not a
finished target file or a claimed realized saving. Other mandatory references are
unchanged. Total full-run reads may grow by routing overhead; cache pricing, input
billing, compaction, repeat reads and host behavior have not been measured.

The source has working body headroom after the prior L3 relocation. This task does
not claim to create that headroom, close unrelated deferred family packets or owner B-135/B-106, or silently change
their decisions. Final body/description measurements must remain within the existing
house budgets without trimming unrelated obligations to make this split fit.

## Source slices

Exact line intervals and section/gate SHA-256 digests are in measurement.json.
The proposed [conservation partition](raw/conservation-plan.json) assigns every one
of 967 source lines exactly once across 35 chunks. Reconstructing those chunks in
source order is byte-identical to the frozen file; this verifies bookkeeping only,
not equivalence after implementation or agent comprehension.
Gate suffixes are kept whole in the conservative model, including material after
the first gate sentence; shortening them to one bullet line would lose obligations.

| Stage | Current lines | Full section tokens | Gate suffix tokens |
|---|---|---:|---:|
| 0 | 74–265 | 3,689 | 817 |
| 1 | 266–275 | 162 | 34 |
| 2 | 276–335 | 1,123 | 187 |
| 3 | 336–428 | 1,773 | 577 |
| 4 | 429–457 | 527 | 383 |
| 5 | 458–520 | 1,249 | 195 |
| 6 | 521–586 | 1,325 | 1,178 |
| 7 | 587–634 | 956 | 704 |
| 8 | 635–671 | 686 | 203 |
| 9 | 672–728 | 1,064 | 269 |
| 10 | 729–865 | 2,700 | 949 |

Keep detail files one level deep beside existing references (e.g.
`references/stage-00-intake.md`), so their existing sibling reference links retain
meaning. The exact names are implementation-owned but must be frozen in one route
manifest/table before editing consumers. Small stages offer little local saving;
uniform explicit routes are proposed for deterministic selection, not because each
new file independently optimizes tokens.

## Consumers and migration seams

The raw census includes every exact `path:line:text` and a category. The following
are semantic groups, not a replacement hand-maintained full inventory:

- **Entry and profile contract:** SKILL.md lines 69, 156–182 and 196–219; the command,
  README, SKILL-CARD and Cursor rule; `pipeline.example.json` owns ids/gate types.
  Replace the existing navigation paragraph with precise on-entry/resume loading;
  do not add a second normative stage list. Preserve custom-profile precedence.
- **Reference navigator:** `references/doctrine-map.md`, `portability.md`,
  `artifacts.md`, `companion-skills.md`, `waves.md`, `iteration.md` and peer references
  distinguish default gates from stage detail. Link a surface-class or fan-out
  explanation to its actual new home, not merely to a still-existing spine heading.
  Existing stages.md heading anchors remain for gate consumers.
- **Validators and plants:** `test/validate.py:2393` compares the spine's stage sections
  with the example and entry table; its later stage-specific readers (e.g. 3589,
  4856, 5097, 5676 and 5792) inspect arming, source harvest, review caps and browser
  obligations. The 41 literal negative-test occurrences must be classified as
  spine mutations versus detail mutations. A plant must alter the actual consumed
  home and name the intended diagnostic; no-op plants stay BROKEN, not PASS.
- **Other tests/evals:** audit regression files, continuity/visual/checkpoint tests
  and browser claims may interpret section boundaries or expected source addresses.
  Move each reader with the fact it verifies. Do not restore a synthetic concatenated
  monolith solely to make old substring guards green: an omitted detail must still
  fail an actual installed-source check.
- **Discovery/installation:** `test/validate.py:235` onward discovers references,
  checks required doctrine and Contents for long files. Every new reference must be
  linked from the entry's deterministic route chain and included in each shipped
  payload. One-directory standalone skill installation must work without repository
  docs, source Git or a sibling plugin. Dynamic discovery counts must be recomputed.
- **Read accounting:** `scripts/graph.py:1580` enumerates top-level reference files and
  reports ledger reads as **unattested**; absent reads are **unmeasured**, not zero.
  The example Read hook is in `templates/hooks.example.json:26`, not the installed
  plugin's gate-observer hook. A route table and a positive counter are not evidence
  of host loading, source authenticity or model comprehension. Preserve those states.

## Existing tensions to preserve explicitly

SKILL.md's prerequisite paragraph says absent super-ux stops the stage-3 gate, while
its following artifact-based paragraph permits equivalent scenarios or an inline
fallback. doctrine-map.md repeats the older package exception. This pre-existing
inconsistency is not resolved by relocating text. The plan must identify these
sentences and obtain a source-owner interpretation before changing their meaning;
B-043 must not silently select one by dropping the other. Existing explicit user
instructions and the artifact contract continue to outrank a generic skill mandate.

The desired load rule is a **new explicit routing obligation**, whereas graph.py's
read ledger currently says there is no per-file floor. Reconcile that wording in
scope: route admission can require an available file and a declared read before
stage execution; an unattested ledger cannot mechanically prove comprehension.
Do not silently convert graph.py doctrine into a safety gate or mandatory preload
of every stage to resolve this distinction.

## Frozen acceptance and execution packet

The [bounded implementation packet](../../evidence/plans/2026-10-13-fw07-stage-reading-floor.md)
names requirements, counterexamples, owner boundaries and review sequence. It is
pending parent review. Implementation begins only after that review and closure of
the current release work. No model-quality or billed-token PASS is supported by this
report; native-host behavioral comparisons remain NOT_RUN.


---

**Made with [ssheleg skills](https://github.com/ssheleg/sshlg-skills)**

- [`task-pipeline`](https://github.com/ssheleg/task-pipeline) — source-owned feasibility and staged delivery
- [`evidence-docs`](https://github.com/ssheleg/task-pipeline) — commit-bound measurements and limits
- [`agent-sync`](https://github.com/ssheleg/agent-sync) — isolated planning lease
- [`make-skill`](https://github.com/ssheleg/make-skill) — portable lazy-reference contract
- `project-reports` — durable decision-input report — not a skill this family ships
