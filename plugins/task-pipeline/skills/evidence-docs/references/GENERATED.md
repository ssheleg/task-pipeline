# Generated copies — do not edit here

The files in this directory (and `../templates/`) are GENERATED (a deterministic transform: in-set links stay relative, out-of-set links point at the source home’s canonical URL) from the
source home `skills/task-pipeline/references/` and `skills/task-pipeline/templates/`
so an isolated single-skill install of evidence-docs resolves every required
link without a neighbouring checkout (FIX-ED-01.01). Edit the source home and
re-run `python3 test/audit_regressions/fix-ed-01.01.py --sync`;
`test/validate.py`'s regression stage fails when a copy drifts.
