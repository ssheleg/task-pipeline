# Spec: the modes of /task-pipeline (waves, iteration, setup, checkup) and the continuation rules

Components (under `plugins/task-pipeline/skills/task-pipeline/references/`): `waves.md`,
`iteration.md`, `setup.md`, `exposure.md` (the checkup mode's real home), `continuity.md`,
`progress.md`, plus `commands/task-pipeline.md`. Checklist: [`../README.md`](../README.md).
Read at 1.104.3.

## Shared findings

- **P-01**: no mode states "Done when" near its top; the finish lines are scattered
  (`waves.md:176-195`, `setup.md:101-106`, `iteration.md:252-255`) or absent (checkup).
- **P-04**: none of the four unwanted stops is named in any mode. `continuity.md:99`
  names the wanted stops ("It stops for exactly four things") but the unwanted ones are
  only "should I continue?" (`:72`); `waves.md:186` "does not ask whether to continue".
- **P-05**: no cap on automatic continuations anywhere. Caps exist for fix rounds
  (`waves.md:216`), integration passes (`iteration.md:122`) and corrective releases
  (`iteration.md:237`), not for continuing without a passed gate.
- **P-13**: the hand-back fence lists DECISIONS WAITING after TASK, PROGRESS, DONE,
  SURFACED, SCOPE, NOT VERIFIED and FINISH (`progress.md:158-178`); what the person must
  do is read last.
- **P-07**: parallel agents are named (`waves.md:201`, `iteration.md:207-218`) without
  "check each returned evidence before accepting it" or a damping line.
- **P-10**: dated decisions and version notes in every mode (`waves.md:13,63`,
  `iteration.md:12,87-92,298-314`, `setup.md:5-6`, `progress.md:136-148,206,361,372`).

## Per mode

### waves
Current: stages 0-4 once, 5-8 per wave, 9-10 once; one planning gate; continues without
asking. Change: a header block (Done when: the board is empty or every remaining node is
parked with its reason; Stop only when: see `continuity.md` → the stop contract; Task
list: `inventory.json` and `graph.json`; Close with: the `progress.md` hand-back); an
evidence-check and damping line beside `:201`; history at `:13` and `:63` removed.
Deferred (row): moving the `waves.py`/`graph.py` mechanics at `:104-121` to the scripts'
documentation.

### iteration
Current: a 13-step cycle with a done-when column per step. Change: the same header block
(Done when: the release shipped, its post-release check read, the next pool handed back;
the next iteration starts on the operator's go unless a standing instruction arms the
loop); dated narratives removed. Deferred (row): moving the `lessons.py` internals
(`:264-517`, about 250 lines) to their own reference.

### setup
Current: seven passes, findings as file:line plus fix plus seam, a plan file. Change:
header block (Done when: `<artifacts>/plans/YYYY-MM-DD-doc-audit.md` written and its
findings filed); the contradiction fixed (`:29` says stages 3-5 "produce findings and
fixes", `:110` says "Nothing is fixed during the audit": the table is corrected to
findings and a fix plan); the capitalised "STOP AND ASK" inside a fence (`:48-49`)
becomes a plain sentence with its reason; the wanted stops ("Offer, never write") are
lifted into "Stop only when".

### checkup
Current: the command points the mode at `references/verification.md`, which never
mentions it; the spec is `references/exposure.md:75-95`. Change: the command's pointer
fixed; a header in `exposure.md` § checkup (Done when: every section printed, zeros
included, nothing written; first section: what waits on the person, the
`needs-operator` rows and abandoned runs; last: what could not be read).

## Continuation rules (one home: continuity.md)

A new paragraph in `continuity.md` Part 1, never inside the paragraphs tests read:

> **What is not a stop.** A turn that ends in text with work still owed is a report, not
> completion. Four such endings are not stops: a summary that announces the next step
> instead of taking it; an offer to continue; a list of decisions that block nothing;
> treating a passed gate, a certified node or a landed wave as a place to report. Put
> status notes in the same message as the next action. After three automatic
> continuations on one node without a gate passing, park the node with its open items
> named and move to the next.

The modes cite this paragraph instead of restating it.

## Hand-back order (progress.md)

DECISIONS WAITING moves to the top of the fence, before TASK; the rows tests check by
presence stay (SCOPE, NOT VERIFIED with "none within the stated scope", `FINISH  finish:
done | budget | blocked`, the SURFACED residual). The tests check presence, not order
(`validate.py:7055-7066`).

## Must not change (consumers)

- `test/continuity_doc_test.py:94-118`: the "Sign-ins, consents" paragraphs in `waves.md`
  and `iteration.md` (no "unless", no "standing authorization"), "In a round, the
  orchestrator", the exit-6 sentence; continuity.md headings, "loop: armed by", "Silence
  still arms nothing", the "What arming does NOT change" and "A block or an ambiguity
  stops" paragraphs.
- `validate.py:8302` (the four-stops sentence), `:5210-5215`, `:6541-6583`,
  `:8203-8213` ("It has five entries:"), `:2219-2221` (setup needles), `:2088-2097`
  (exposure "checkup", "no percentage", "never checked").
- `test/waves_test.py:561-562`; the hand-back rows above.

## Risks

- A new paragraph placed inside a tested paragraph changes what the test reads: inserted
  as its own paragraph.
- Reordering the hand-back fence could break an order-sensitive reader elsewhere:
  `grep -rn "DECISIONS WAITING"` across the repository before moving it.

## Verification

`npm test`, `python3 test/continuity_doc_test.py`, `python3 test/waves_test.py`,
`npm run test:negatives` for the continuity and progress negatives, prompt lint rebaseline.
