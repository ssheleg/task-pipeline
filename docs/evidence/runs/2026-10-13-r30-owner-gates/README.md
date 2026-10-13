# R30 owner guards — tp-r30 candidate

Objective: close reproduced actual-validator escapes at source `3596355ae56bd067a243bd5d17a8d40aeec292a0`: strict board widths, escaped-pipe parsing and release guard, preserving existing priority, duplicate, source and board-home checks. [Baseline actual processes](baseline-process.json) record the unmodified validator accepting the planted defects. Metadata absence alone was not treated as failure.

## Contract

The release helper extracts the reviewed bounded family grammar from agent-stack `792e3f6cb2e46517f0187066db55edc63ae7d12c:test/member_gates.py`. It requires a live unconditional full-history checkout before a refusing ancestry guard. It rejects unsupported quoted/merged keys and weakened guard shapes. It is not a general YAML or shell interpreter. Workflow bytes are unchanged.

The 27 focused release controls execute the workflow's own annotation and ancestry shell in local Git fixtures. Annotated current/ancestor tags pass; missing/lightweight tags and an unmerged commit refuse. A real shallow clone establishes the shallow fixture and the structural guard rejects depth one. Only `gh api` default-branch lookup is a stand-in; this is not hosted publication evidence. Annotation removal is covered by the aggregate runtime regression, not by the structural helper alone.

The board helper comes from the same reviewed source with one explicit historical lowercase-suffix grammar extension. Immediate matching separator, exact per-table width and duplicate identifiers across declared tables are required; fenced examples and prose references are not declarations. The owner validator applies it to both the backlog and shipped template. Existing priority, source and board-home checks use the same escaped-pipe splitting rather than raw delimiters. The 25 focused board controls exercise this contract. Parent's independently reviewed ledger [original ledger 9caf406](https://github.com/ssheleg/task-pipeline/commit/9caf406ca78a6b2661419ee1331af8879a665fa6) is composed as `ebd79a5`; no ledger runtime change is claimed.

## Handoff

This candidate is source-only. Focused final-tree controls, independent review and one serial full owner gate are required before draft-to-ready normal PR admission. Evidence must identify its exact measured source. No package bump, released tag, installed state, model behavior or universal R30 closure is claimed. Next: finish final-tree process controls, freeze the source for peer review, then run the owner gate when the serial slot is available.

## Focused observation before freeze

The final-tree process suite passed 6 controls: [focused-process.json](focused-process.json). Exact implementation and test bytes are [source-hashes.json](source-hashes.json). The shared release suite passed 27 controls and board suite passed 25 controls. Independent source review and the full owner gate remain separate next steps.

## Provenance correction before the full gate

The first full run at `c229d7f` was deliberately stopped after independent review found the original ledger SHA was written as a bare nonancestor citation. Its partial output and stop reason are retained in `aborted-full.json` and `aborted-full.log.gz`; no full pass is claimed. The original source now has an immutable GitHub commit link while the local cherry-pick remains explicitly identified. Re-run the documentation gate and then the full suite on the corrected commit.

## Failed full gate and bounded correction

The full `npm run test:all` at `b86478c` exited 1 after 1472.93 seconds: [failed-full.json](failed-full.json), [compressed complete output](failed-full.log.gz). All 438 negative guards passed; one of 15 property cases failed. Property 170 inserted its historical DATED row between a Markdown header and its separator. The new strict table grammar correctly refused that malformed positive fixture. The fixture now anchors the complete header and separator before inserting the same historical row; validator behavior is unchanged. The focused replay passed: [property-170.json](property-170.json).

Independent coordinator review accepted the fixture correction and a transparent split verification: retain the completed unchanged components of the failed run, replay the corrected property, then execute the previously unreached suffix and final structural/documentation checks. This is not a single final-SHA full PASS, and the failed full result remains failed. Hosted exact-candidate checks remain required before integration. Next: run and record the remaining suffix when the serial slot is free.
