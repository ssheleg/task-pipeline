#!/usr/bin/env bash
# name: Property check (a document may narrate the provenance claim it used to make)
set -eu
python3 - <<'EOF'
# Both surfaces cite «never agent-written» while marking it as what was wrong. A
# guard that cannot tell an assertion from its own obituary forces the history out
# of the document — and this one was watched doing exactly that, twice, first by
# flattening the emphasis away before looking for it and then by mispairing a
# single asterisk against an adjacent bold span.
import re
for p in ("plugins/task-pipeline/skills/task-pipeline/templates/run.md",
          "plugins/task-pipeline/skills/task-pipeline/references/progress.md"):
    t = open(p, encoding="utf-8").read()
    assert "agent-written" in t, f"{p}: the narration of the old claim is gone"
    assert "unattested" in t, f"{p}: the unattested mark is gone"
    print(f"OK: {p} narrates the claim and carries the mark")
EOF
