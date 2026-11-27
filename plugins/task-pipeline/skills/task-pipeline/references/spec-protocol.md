# The spec protocol: stages 0 to 4 as checks

Stages 0 to 4 turn a request into a spec a builder starts from without a second
question; `scripts/spec_protocol.py` checks each step. The order: spec, board rows, build.

## Contents

- The loop
- 1. Size the spec
- 2. Grill with classes
- 3. Research with agents and other models
- 4. Check the spec, then the board, then the build
- 5. The clarity judge
- Rationalizations

## The loop

Five steps in this order; `spec_protocol.py loop` prints them.

| Step | Stage | Who | Takes | Leaves |
|---|---|---|---|---|
| 1. Analysis | 0 to 2 | the author | the request, the brief, the documents | the gaps, the size, the classed ledger |
| 2. Definition | 2 to 3 | the thinker by tokens (meanings, judged by the council from M), a writer on the subscription (text) | the brief, the size, the ledger | `meanings.md` that passes `meanings.py check`, the spec draft citing it |
| 3. Research planning | 3 | the author | the ledger's open rows, the size | the dossier skeleton, one question a scout |
| 4. Research | 3 | other agents on the subscription: scouts, specialists for code, mathematics, science | one question each | Findings, Options, sources read |
| 5. Verification | 3 to 4 | the author; validators of other families by tokens, one call each; the scripts | the dossier and the spec | Recommendation, verdicts, `check` and `gate` pass |

Who runs on tokens and who on the subscription: [`model-tiering.md`](model-tiering.md),
*Roles and money*. An M or L spec carries `Meanings: <file>`. Size S runs steps 1, 2, 5.

## 1. Size the spec

After the gap check (`grill.md`, phase 2), size the spec from the brief's facts:

```bash
python3 <skill>/scripts/spec_protocol.py size --reqs 5 --files 8 --contract
```

| Size | When | Sections it owes (legacy) | Research |
|---|---|---|---|
| S | a bounded change | Goal, Scope, Requirements, Design, Questions, Tests | none; a new domain owes one scout and three sources |
| M | a contract, several surfaces or unknowns | S plus Contracts, Edge cases, Decisions, Rollout | two scouts, six sources (one primary), one validator of another family, then the council ([consilium.md](consilium.md)) |
| L | hard to reverse, cross-project, large | M plus Architecture, Data, Non-functional, Alternatives, Risks | up to four scouts, twelve sources (two primary), two blind validators of two other families, then the council ([consilium.md](consilium.md)) |

The spec carries `Size: S|M|L`. Small is shorter, never incomplete: every owed
section is filled or says in one line why not. A run on the short path
(`stage-00-intake.md`, phase 1d) writes no spec.

## 2. Grill with classes

Every question the gap check leaves open goes into the spec's `## Questions`
ledger with a class:

| Class | Whose | What happens |
|---|---|---|
| `strategy` | the owner's | concept, vision, meaning: who it is for, what it promises, price, name. Asked, with a recommended default the work goes on with |
| `tactics` | the agent's | how to build it. Decided and recorded with its basis; never asked |
| `known-domain` | the agent's | established practice or a documented fact. Decided with a cited source; never asked |
| `unknown` | the owner's only after research | research could not answer it. Asked with the research linked and a default |

```
| id | question | class | answer | by | basis |
|---|---|---|---|---|---|
| Q1 | Which queue carries the jobs? | tactics | the stdlib queue | agent | no new dependency |
| Q2 | Teams or solo founders first? | strategy | solo founders | pending | the vision names founders |
```

`spec_protocol.py questions <spec>` prints the owner's batch (every `pending`
row, one message) and fails a tactical question left `pending`, strategy the
agent decided, an owner question without a default, an unknown not researched,
a known-domain answer without a source.

## 3. Research with agents and other models

Size M and L, or a new domain, owe a dossier. Write the skeleton first; a section
held only in context is lost with the session:

```bash
python3 <skill>/scripts/spec_protocol.py research init docs/research/<topic> \
  --tier M --question "<the question>" --author <family>/<tier>
python3 <skill>/scripts/spec_protocol.py research plan --tier M
```

Roles by model tier (`model-tiering.md`), at most five agents at once:

1. **Scouts** (working tier, web search): fill Findings, Options and
   `sources.json` (`id`, `kind`, `title`, `url`, `read`, `claim`); recommend
   nothing; an unopened page is `read: false`.
2. **Decider** (the author): rechecks numbers and citations, writes Recommendation,
   What would refute it and Rejected; a gap goes back to a scout, never filled
   from memory; every validator gap is answered, `agree` included.
3. **Validators** (top tier of another model family, blind to each other):
   `agree`, `partial` or `disagree` with evidence, by `research validate <dir>
   --model <id> --family <f> --endpoint <url> --key-env <VAR>` (any
   OpenAI-compatible route), recording nothing on a failed call. The author's
   family is recorded with a warning, never counted.
4. **Merge** (fast tier): on a `disagree`, `## Resolution` says whose evidence is
   stronger. No voting.

`research check <dir>` fails an unresolved citation, an unopened source or a
model's answer as evidence, too few sources or validators, a disagreement without
Resolution. Spend follows the host's per-run line.

## 4. Check the spec, then the board, then the build

```bash
python3 <skill>/scripts/spec_protocol.py check <spec>     # sections, ledger, research, no TBD
python3 <skill>/scripts/spec_protocol.py gate <spec> --board <backlog> --plan <plan>
```

`gate` opens stage 5 only when the spec passes and the board and the plan cite it.

## 5. The clarity judge

The owner, 2026-11-27: «на каждую спеку ещё нужен судья» (S0). `scripts/spec_judge.py`:

- `init <dir>`: `spec.md` from [the template](spec-template.md) and `spec.json`
  (`spec/1`, naming `author_family`) in `docs/specs/<date>-<slug>/`.
- `check <dir>`: ONE call to a judge of another family, never retried, with
  [the rubric](judge-rubric.md) and `--glossary`; the judge comes from a `judge-models/1`
  list (`--models`, `~/.config/task-pipeline/judge-models.json`; the shipped
  [list](judge-models.json) names roles, never called). The tool computes `pass`,
  `pass-with-fixes` or `fail` from what the judge listed and books the cost (`spend.py`).
  Round 2 adds the questions and the diff; a third round only for one open blocker; then
  the spec stays `draft` and `judge/escalation.json` holds the coordinator's task.
- `check --verify <dir>`: no call; 0 only when a pass carries the current hash (`spec.md`
  without `## Judge record`). One provider gives `judged-degraded`: S and M only, never
  under `require_cross_family: true`. M owes one validator of another family (`validate`)
  and a council ruling ([consilium.md](consilium.md), `--out <dir>/review/council`); L two
  validators of two families and the council.
- `gate`: CI over the `Spec: <id>@<commit>` trailer (`ci/spec-gate.yml`); `calibrate`: the
  ten seeds of `tests/judge-seeds/`, 9 caught, every Monday. Exits: 0 pass, 1 not, 2
  unreadable, 3 no judge. `build-gate.sh` denies product edits until `spec:` verifies.

## Rationalizations

| The excuse | Why it fails |
|---|---|
| "Ask the owner, to be safe." | A tactical question asked costs a human round for what the agent could decide. |
| "It is a one-line fix, no spec." | Inside a run no kind is exempt: an S spec is one page and one judge call. |
| "The model said so." | A model's answer is not a source; its claim needs a page that was read. |
