# Generated copies: do not edit here

The files under this skill's `references/` and `templates/` are generated copies, so a
single-skill install of evidence-docs resolves every link without a neighbouring
checkout (FIX-ED-01.01). The one exception is `retrospective.md`, a hand-written
pointer to its single home.

- Source home: `skills/task-pipeline/references/` and `skills/task-pipeline/templates/`;
  `scripts/docgraph.py` is a byte copy of `skills/task-pipeline/scripts/docgraph.py`.
- Transform: deterministic. Links inside the copied set stay relative; links outside
  it point at the source home's canonical URL.
- Editing: edit the source home, never the copy, then re-run
  `python3 test/audit_regressions/fix-ed-01.01.py --sync`.
- Drift guard: `test/audit_regressions/fix-ed-01.01.py` fails when a copy differs
  from the source home, when a pointer grows back into a copy, or when an isolated copy
  of this directory breaks a link.
