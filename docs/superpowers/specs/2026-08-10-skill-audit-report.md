# Skill audit — where task-pipeline misleads, and why an agent running it can still talk nonsense

Measured 2026-08-10 at `ad351ea` (v1.37.0). This is an **audit**, not a pipeline run: it
measures and reports, it does not change behaviour. Every number below is a command's
output, not a recollection.

> **Scope, stated so a green here is not quoted past it.** This walks the *shipped
> surface* — `SKILL.md`, the 32 references, the 15 templates, the command, both
> manifests, the eval suite — and the agent behaviour this session produced first-hand.
> It does **not** run the skill on a fresh model, which is the one measurement that
> would settle the trigger questions (F-14).

---

## 1. What an agent pays before it does anything

```
SKILL.md                          ~ 7 953 tok    ← loaded on trigger
references/stages.md              ~13 161 tok    ← read in full at stage 0
references/grill.md               ~ 4 465 tok
references/knowledge-sources.md   ~ 4 769 tok
docs/superpowers/retro.md         ~14 896 tok    ← "read in full", a gate criterion
commands/task-pipeline.md         ~ 2 504 tok
                                  ───────────
stage-0 floor                     ~47 751 tok    before the first grill question
full bundle                      ~139 675 tok    (32 references + 15 templates + SKILL)
```

**This is the root of most of what follows.** Not because the doctrine is wrong — it is
unusually good — but because *volume is itself an instruction*, and the instruction it
gives is **skim**. Every finding in §4 is downstream of an agent that read 48 000 tokens
and retained the shape of them rather than the content.

---

## 2. The trigger surface — what is seen before anything runs

### F-01 · Two of the three modes are invisible in every browsable surface 🔴

`setup` and `checkup` exist only in the **body** of the command file. Measured:

| Surface | Names `setup` | Names `checkup` |
|---|---|---|
| `SKILL.md` frontmatter `description` (1015 chars) | no | no |
| `commands/task-pipeline.md` `description` | no | no |
| `.claude-plugin/marketplace.json` `description` | no | no |
| `plugins/task-pipeline/.claude-plugin/plugin.json` `description` | no | no |
| the command **body** | yes | yes |

The slash-command list, the plugin browser and the skill's own trigger text all describe
a single behaviour. `checkup` was built *specifically* to be run when nothing else is
running — and the only way to learn it exists is to read a file you open by running the
thing it is an alternative to.

### F-02 · The description is at 1015 / 1024 characters 🟠

Nine characters of headroom. This is not a style point: **it is a hard ceiling on every
future capability**, because the description is the only surface that decides whether the
skill fires at all. The last two programmes added four references, two templates and two
command modes, and **none of them could be mentioned**. The description still ends at the
v1.9-era feature set.

### F-03 · The description mixes three jobs and is measurably unbalanced 🟠

It carries the trigger vocabulary, the anti-trigger vocabulary, *and* four sentences of
mechanism (`the grill is mandatory…`, `documentation is a deliverable…`, `recommends
super-ux…`, `confirms one model up front…`). The mechanism sentences cannot affect
routing — a model choosing whether to fire never needs them — yet they occupy **~40%** of
a budget that is full.

### F-04 · The manifests describe a product that stopped existing at v1.30 🟠

Both say *"10 gated stages … a loop guard that breaks churn … an optional super-ux UX
track"*. Nothing about the board, the verification ledger, the exposure line, the progress
rail, the run ledger, the copy or visual tracks, or retro publishing. **Seven releases of
capability are absent from the only text a marketplace shows.**

---

## 3. The instruction surface — the wall

### F-05 · The command body is one 1281-word paragraph 🔴

```
paragraphs: 5
  para 1: 1281 words, ~25 sentences, 8112 chars   ← this is the launch instruction
  para 2:    2 words
  para 3:   60 words
  para 4:  125 words
  para 5:   61 words
longest line: 4115 chars
```

**This is the first text an agent reads when the skill fires**, and it is a single
unbroken block containing: the stage list, the harvest contract, the graph contract, the
grill contract, the autonomy sweep, the Figma destination rule, the REQ table, the board,
the verification ledger, decomposition, the loop guard, the ladder walk, the multi-repo
close-out, the retrospective's three acts, and the model confirmation.

Twenty-five obligations in one breath. An agent will comply with the ones it can still
see — and which those are is a function of position, not importance.

### F-06 · The command's own reference list names 13 of 32 files 🟠

```
references/{knowledge-sources,knowledge-graph,grill,brainstorm,decomposition,spec,
            planning,build,review,tdd,acceptance,retrospective,loop-guard}.md
```

Nineteen shipped references are never named there, including `gates.md`, `audit.md`,
`backlog.md`, `verification.md`, `exposure.md`, `progress.md`, `continuity.md`. The
sentence introducing the list reads *"Every stage's doctrine is built into the skill"* —
so the list reads as complete. It is the exact shape this repository has fixed four times
elsewhere and left standing in the file an agent reads first.

### F-07 · 92 hand-written counts in prose, 9 registered claim classes 🟠

```
hand-written count claims in prose: 92     (across SKILL.md + 32 references)
claim registry classes:              9     (6 of them dormant)
```

Most are currently true. **That is not the finding.** The finding is that a repository
whose loudest canon is *compute, never restate* ships 92 restatements with 83 of them
unguarded — and its own history records this class drifting silently five separate times.

### F-08 · Prohibition saturation: one "never" per 227 words 🟠

```
total words in the shipped bundle: 77 230
  never   340   (1 per   227 words)
  must     71   (1 per 1 087 words)
  always   21   (1 per 3 677 words)
```

When 340 rules are all absolute, an agent has no ranking function. It does not disobey the
important one deliberately — it cannot tell which one that is. **Emphasis that is
everywhere is emphasis nowhere**, and the observable consequence is selective compliance
that looks arbitrary from outside and feels principled from inside.

---

## 4. Why an agent running this pipeline can still generate nonsense or lie

Everything here is from **this session**, not theory. Seven distinct mechanisms.

### F-09 · The measurement instrument reports on itself 🔴

Three times today, in a repository whose central doctrine is *an actor's own reply is not
evidence about the world*:

| What happened | What it reported |
|---|---|
| `npm test \| head && git commit` | `head`'s exit code — a commit landed over a **red** validator |
| `gh pr edit --base main >/dev/null 2>&1` | success by silence — the API had refused every call |
| a guard scanning for `%` | matched **its own line**, the one line guaranteed to contain it |

**The general shape:** a check and the thing it checks share a channel. The pipe shares
`$?`; the suppression shares stdout; the self-matching regex shares the corpus. An agent
does not lie here — it reports the truth about the wrong object.

### F-10 · A probe written by the author of the check can only confirm the author 🔴

Three probes today were wrong *before* their guards were, all the same way — **planted
where convenient, not where the check reads**:

- removed 1 of 3 `touch:` lines → the shape stayed shown → the guard was correctly silent,
  and the silence was read as a broken guard;
- decremented a guard count in an **already-released** CHANGELOG section, because this
  release wrote the number in a slightly different form;
- deleted the SHOUTED spelling of a track and left the lowercase one.

R-001 exists for exactly this and it still fired three times in one day. **This is the
strongest single argument in the audit**: a green from a self-probed check is worth
approximately nothing, and the pipeline currently has no stage that dispatches anyone else.

### F-11 · The independent reader is a third party with no contract 🔴

R-005 requires an independent reader on any change that adds or widens a check. Four PRs
of exactly that work were opened today; the review app reported **`skipping`** on every
one. Twenty-two new guards merged with the author's own probes as their only reading.

**The instruction was followed to the letter and the reading never happened.** Nothing in
the pipeline reads the reviewer's *output* before treating the requirement as met — it
reads its own *dispatch*. That is F-09 one level up, and it is board row `B-003`.

### F-12 · The absence has no signal 🔴

`str.replace` that matches nothing returns the string unchanged. `Edit` on a shape the
file does not have errors — but a *python* substitution does not. Three times in the
previous programme and once today, an edit targeted a shape that was not there and
**nothing said so**. Recorded as `B-024b` and still open.

Generalised: **every silent no-op in the toolchain is a place an agent will later report
work it did not do**, in complete good faith, because its model of the file diverged from
the file at a moment nothing marked.

### F-13 · Volume produces confident summary 🟠

Stage 0 obliges ~48 000 tokens of reading, of which `retro.md` (~14 900) and `stages.md`
(~13 100) are required **in full**. An agent that has read 48 000 tokens has, in practice,
compressed them — and a compression is a summary written by the reader. Every
summary-drift failure this repository has recorded (*a summary that lists most of a list*,
*a corpus that is too small*, *a count restated in prose*) is this mechanism.

The pipeline's own answer to over-long documents is progressive disclosure. **It does not
apply that answer to itself**: `retro.md` is capped at ten standing instructions precisely
because it is read in full, and then the same gate also demands the run stamps and the
recent log, which are not capped by anything.

### F-14 · The trigger has never been tested on a model that did not write it 🔴

```
eval cases: 15   (TRIG 4 · NOTRIG 4 · AMB 2 · COEX 1 · INSTR 4)
dated runs recorded: 1, self-observed by the author
blind runs on any model: 0
```

And the suite's coverage is frozen: grepping it for the vocabulary of the last seven
releases returns **`harvest` 3, `gate` 3, `grill` 2, `retro` 1** and **zero** for
`backlog`, `verification`, `exposure`, `progress`, `checkup`, `setup`, `copywriting`,
`sheleg-design`.

So the two claims that matter most — *does it fire when it should* and *does it stay quiet
when it should not* — rest on the author agreeing with himself once, about a version of
the skill that no longer exists.

### F-15 · The gates all measure the artifact, none measures the reading 🟠

Every gate asks *is this artifact good?* Not one asks *did the agent actually read the
thing it says it read?* The source ledger records which sources were **consulted** — a
claim the agent makes about itself, with no counter-evidence anywhere. F-09's shape, at
the level of the whole stage.

---

## 5. Smaller inaccuracies worth fixing while nearby

| # | Finding | Evidence |
|---|---|---|
| F-16 | `templates/` ships **15 files ≈ 21 400 tok** seeded into host projects, and `templates/README.md` is the only index — no gate checks a template against the doctrine that describes it, except the four the docgate executes | `ls templates/`, `references/` cross-refs |
| F-17 | `evals/RESULTS.md` is honest about having no blind run, which is correct — but nothing surfaces that fact at runtime. The preflight prints companion state and never *"this skill's behaviour is unverified"* | `evals/RESULTS.md`, `companion-skills.md` → *Preflight* |
| F-18 | The `retro.publish` redaction rules are enforced against the **doctrine's own example** and not against a real body — no check can see an issue that was opened. Stated in the guard's scope, worth repeating here | `test/validate.py` P4-G2 |
| F-19 | `graphify`'s semantic layer is **80 markdown files** behind while its structural layer is current, so `graphify query` answers about doctrine from the pre-v1.31 text — with a machine's authority | `B-007`, re-measured today |

---

## 6. The plan

Priorities use the board's own formula — `prio = sev × blast + age_bonus`, inputs stated
so the ranking can be checked rather than trusted.

### Tier 1 — the trigger and the wall (prio 6)

| Row | Work | Why first |
|---|---|---|
| **P-01** | **Split the command body into labelled sections.** One block per obligation with a heading; the stage list, the harvest, the grill, the close-out. No content change — structure only | F-05. It is the cheapest change in this document and it touches the text every run begins with |
| **P-02** | **Reclaim the description budget.** Cut the four mechanism sentences (~400 chars); spend the room on `setup`, `checkup` and the boundary. Then re-run the trigger evals | F-02·F-03·F-01 |
| **P-03** | **Give `setup` and `checkup` their own command files** so they appear in the slash list, and name all three modes in both manifests | F-01·F-04 |

### Tier 2 — make the green mean something (prio 6)

| Row | Work | Why |
|---|---|---|
| **P-04** | **A stage that dispatches the reader**, rather than a repository that happens to run a bot — and it reads the reviewer's *output*, recording `no reader` as a distinct state beside the verdict. This is R-005's own retirement condition | F-11·F-10. Closes `B-003` |
| **P-05** | **A probe harness that asserts the plant changed the text the check parses** — R-001's own retirement condition, written at birth in 2026-08-03 and never built. Three probe faults today argue it | F-10 |
| **P-06** | **Ban the silent no-op.** A helper that raises when a substitution matches nothing, and a doctrine line that says a command's output is never suppressed at a decision point | F-12·F-09. Closes `B-024b` |

### Tier 3 — the reading load (prio 4)

| Row | Work | Why |
|---|---|---|
| **P-07** | **Cut the stage-0 floor below ~25k tokens.** `stages.md` splits into a spine (gates + criteria) and per-stage detail loaded on entry; `retro.md`'s *read in full* narrows to the standing instructions, with stamps and the log queried | F-13. The biggest single lever on agent quality here |
| **P-08** | **Rank the prohibitions.** Reserve **NEVER** for acts that lose work or ship a false claim; demote the rest to plain statements. Then measure the ratio again | F-08 |
| **P-09** | **Widen the claim registry toward the 92.** Not all at once — add the classes whose drift has actually shipped, and delete the counts that cannot be computed | F-07 |

### Tier 4 — evidence about behaviour (prio 6, blocked on a human)

| Row | Work | Why |
|---|---|---|
| **P-10** | **Extend the eval suite to the last seven releases** — trigger cases for `checkup`/`setup`, instruction cases for the board, the ledger and the three tracks | F-14 |
| **P-11** | **Run the suite blind on three models**, one fresh session per query. This needs a person or a dispatch budget; it is the only item here that cannot be done by editing files | F-14. Closes `B-002` |
| **P-12** | **Surface unverified behaviour at preflight** — one line beside the companion block when `evals/RESULTS.md` records no blind run | F-17 |

### What this plan deliberately does not propose

- **Removing doctrine.** Nothing in §4 says the rules are wrong; they are unread, which is
  a different problem with a different fix. Deleting a correct rule to shorten a file is
  how a project loses the thing it learned.
- **A cap on `learned.md`.** Refused once already by measurement, for the reason that still
  holds: it is entered by citation, not read end to end.
- **Automating the redaction check against real issue bodies.** No static check can read
  what was sent; F-18 stays reported.
