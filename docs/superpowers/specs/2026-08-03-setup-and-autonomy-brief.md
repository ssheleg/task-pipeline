# Brief — the setup audit, self-currency, and a stated escalation boundary

**Run:** `setup-and-autonomy` · 2026-08-03 · stage-0 output, locked.
**Model:** the run's confirmed tier. **Single module** — no decomposition.

## Knowledge sources (phase-1 harvest, written before the first question)

| Source | What it says about this task | Fresh? | Authority |
|---|---|---|---|
| `references/audit.md` → *When this runs* | the ladder runs at stage 10, per module, or when the **whole task** is an audit — **never as an entry check on existing docs** | current | contract — this is gap A |
| `references/companion-skills.md`, `SKILL.md` | no comparison of installed vs released version anywhere | current | contract — gap B |
| `references/brainstorm.md` | 1 mention of edge cases, **0 of scenarios** — user paths are first thought about at stage 3, not in the design conversation | current | contract — gap E |
| `references/spec.md` | already locks *Error handling and degradation* per spec, and *Edge and failure cases* in a module dossier | current | contract — **the contract layer is not the thin one** |
| `references/adoption.md` | greenfield/brownfield walkthroughs exist; the audit that *finds what is broken* does not | current | contract |
| `docs/superpowers/retro.md` | R-001 doubt the probe · R-002 re-verify every edit in a failed batch — both bind | current | instruction |
| nicegram `AGENTS.md` §0.0/§7 | the version-floor ritual and the cost-of-being-wrong escalation rule, proven on a four-repo build | 2026-08 | prior art |
| `evals/RESULTS.md` | 0 of 3 models exercised — behavioural evidence still absent | current | ratchet |

**Reconcile (1c):** tree clean, `main` == `origin/main`, three repos in sync.

## Decisions locked

| # | Decision |
|---|---|
| D1 | The entry audit is a **mode inside task-pipeline** — `references/setup.md` + a `/task-pipeline setup` branch. One channel, one doctrine; no new family member competing for recall |
| D2 | It is **offered, not imposed**: stage 0 asks once when `docs/DOCMAP.md` is absent or stale. The answer — including a refusal — is recorded in the brief and never re-asked |
| D3 | Escalation uses **both**: the cost-of-being-wrong rule as the portable default, plus a sweep row for this project's exceptions |
| D4 | All five branches ship in one run — they interlock: an audit with no term index has less to check, and autonomy over unaudited docs runs on a rotten base |
| D5 | UX moves **earlier, not louder**: the thin layer is stage 2, so user paths, states and error paths become design outputs there and feed the stage-3 chain |

## Requirements (frozen)

| REQ | Requirement | How it's verified |
|---|---|---|
| REQ-001 | `references/setup.md` — the entry audit: when it runs, what it inspects, the finding shape (`file:line` + minimal fix), and that its output is a fix plan the pipeline can run | validator: file present, reachable, Contents matches; guard requires the inspect list and the finding shape |
| REQ-002 | Stage 0 offers it **once** when the doc map is absent or stale; the answer is recorded in the brief's sweep and never re-asked | `stages.md` stage-0 section + `templates/brief.md` sweep row; sweep-drift guard compares both tables |
| REQ-003 | `/task-pipeline setup` is a documented branch of the command | the command file names it; README names it |
| REQ-004 | Self-currency: preflight compares the installed version against the released one and recommends `npx sshlg-skills update`; staleness signals named (never-fired standing instructions, a stale doc map, a frozen ratchet) | guard requires the check in `companion-skills.md` and the launcher form, not the bare one |
| REQ-005 | The escalation boundary: cost-of-being-wrong as the default rule, plus a sweep row for exceptions | `grill.md` + `templates/brief.md`; guard requires both halves and the sweep parity holds |
| REQ-006 | Term index: every domain term used in the docs resolves to one definition; the doc map gains a *Terms* row; the seeded gate gains the section | `templates/docmap.md` + `templates/docgate.sh` section; both seeded shapes still exit 0 |
| REQ-007 | Stage 2 produces user paths, states and error paths as **design outputs**, feeding the stage-3 chain | `brainstorm.md` gains the section and its gate clause; guard requires it |
| REQ-008 | Every new invariant has a guard **and** a negative self-test watched failing | `npm run test:all` green with the floor raised |
| REQ-009 | Released, catalogue pinned, local installs refreshed through the launcher, this run recorded | `npm view`, `list`, no shadow copies |

## Users & UI verdict

No user-facing surface in this repository. **UI verdict: no.** (REQ-007 is about what
the pipeline *asks of a host project's* UI work, not about a UI here.)

## Autonomy (stages 1→10 read this instead of asking)

| Stage | Answer |
|---|---|
| run-wide | Autonomous to the end, including commit, push, tag and catalogue pin |
| run-wide · **escalation** | **Cost-of-being-wrong.** Decide alone while the cost stays inside these repositories and is reversible. Escalate: a price, a legal posture, a promise to a third party, anything spending money or reputation, and any irreversible outward act. Exceptions for this run: none |
| 0 Docs regime | This repo's decision home stays `CHANGELOG.md` + `docs/superpowers/specs/`; `docs/DOCMAP.md` exists and is current |
| 1 Docs | No new external libraries |
| 2 Decompose | Single module |
| 4–5 Dev | Doctrine edits land on `main`; no worktree |
| 6 Tests | `npm test`; full `npm run test:all` |
| 7 Deploy | **Standing go:** tag and publish task-pipeline, then pin the catalogue, once `npm run test:all` is green on the tagged commit |
| 9 Docs | README, CHANGELOG, SKILL-CARD, DOCMAP, CONTRIBUTING invariants |
| 10 | Operator signs off; deferrals to the ledger or `evals/RESULTS.md` |

## Done-criteria

`npm run test:all` green · both seeded gate shapes green · the setup mode runnable
end-to-end against a scratch project · every REQ closed with evidence · retro last.

## Open assumptions / risks

- **The setup audit can become the thing people skip.** It is offered once and its
  refusal is recorded, which makes skipping visible rather than silent — that is the
  mitigation, and it is a design choice, not a guarantee.
- **A term index has a false-positive budget.** Any "every capitalised word must be
  defined" heuristic will cry wolf; the check must be measured over a real corpus
  before it ships, or it becomes the gate people switch off.
- The behavioural evals remain unrun; nothing here changes that.
