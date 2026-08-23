---
description: Audit a whole project — discover what it is, probe it, read production evidence, and leave an HTML report plus a JSON sidecar. Read-only.
argument-hint: "[path] (default: the current project)"
---

Run the `project-audit` skill against $ARGUMENTS (default: this project).

Follow its six phases in order — discover, probe, prod, seams, report, propose —
and do not skip discovery: a fixed checklist returns the same findings on every
repository it is pointed at, which is a fact about the checklist.

Start with the mechanical half, then spend your reading where it could not look:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/project-audit/scripts/audit.py" --root .
```

It writes `docs/audit/<date>-audit.html` and `docs/audit/<date>-audit.json` and
opens the page. Read the sidecar's `probes` array before saying anything is
clean — every `blind` entry is a question this run did not answer, and its
reason is why.

Close on the skill's exit criterion. **Propose board rows; write nothing.**
