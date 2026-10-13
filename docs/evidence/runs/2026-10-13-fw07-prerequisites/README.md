# FW07 prerequisite correction

Base: accepted `78c42124db910c56e74c8fbd524bdc9a4f8fb6c9`, plus the independently
accepted [source packet](../../plans/2026-10-13-fw07-ux-prerequisite-correction.md).
The coordinator advanced this isolated source work while the immutable 1.94.0
release gate runs elsewhere. No overlapping full suite or release action is taken.

## Corrected contract

Seven current shipped files/eight source locations retained package-install gates
contradicting accepted PR86's artifact-provider rule. The source now requires a
valid scenario artifact, names super-ux as preferred, and preserves equivalent
providers and inline fallback. Unavailable checks remain named NOT_RUN. No stage
id, gate type, authorization requirement or scenario-quality criterion changes.
Historical receipts are untouched; stages.md bytes are unchanged for later extraction.

## Actual verification and limits

The original regression passed seven cases despite every stale prerequisite.
After adding the bounded source guard, its real entry failed naming all seven
files: [red result](guard-red.log). Corrected doctrine passes nine cases, including
invalid-artifact refusal for every provider. New fw07_prerequisites.py runs the real
regression entry in an owned minimal source fixture: baseline, eight actual stale
rules, their whitespace variants, and harmless current reflow; 18 controls pass and
the fixture is removed. These are source and contract checks, not native-agent runs.

House audit: [19 PASS/0 GAP](house.log); body 4629/4750 working-limit tokens.
The first structural run failed on the planning report's generated JSON `version`
field, which the mutable version-surface guard classified as a new release home.
[Failure](structural-first-failure.log) is retained. The generator now labels that
frozen fact `source_release`. The original raw bytes are preserved as
[measurement-original.json.gz](../../../reports/2026-10-13-fw07-stage-reading-floor/raw/measurement-original.json.gz);
decoded equality proves only the schema key changed, no source measurement value.
No guard or version-sync requirement was waived, and no mutable version home was added.

Corrected `python3 -B test/validate.py` exits 0: [result](structural-corrected.log).
It passes after the source-release schema correction; the original failure remains.

Next: independent source/negative review, then the
accepted lossless stage extraction on this isolated line. Preserve complete gates,
exact entry/resume routes and custom-profile precedence. One composed full suite
follows peer acceptance; no model/native quality or billed-token claim is made here.

## Independent source review

The coordinator independently reviewed frozen [cfa5248](https://github.com/ssheleg/task-pipeline/commit/cfa5248240df71a55ca6c1742ab9a02ba7867949)
against the accepted artifact-provider contract and replayed the real regression
entry (9 controls) plus its public-entry mutation harness (18 controls), all passing.
The canonical default profile is
`plugins/task-pipeline/skills/task-pipeline/pipeline.example.json`; Git comparison
from the accepted base to that reviewed commit shows that profile and stages.md
unchanged. This accepts the bounded semantic correction, not native host behavior.
The following extraction is a separate source change with its own conservation proof.
