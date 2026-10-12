#!/usr/bin/env bash
# name: Negative self-test (a trigger named on the page but not in the enumerating paragraph)
set -eu
rm -rf /tmp/tg4-copy && cp -R . /tmp/tg4-copy
python3 - <<'EOF'
import re
p = "/tmp/tg4-copy/plugins/task-pipeline/skills/task-pipeline/references/backlog.md"
t = open(p, encoding="utf-8").read()
parts = re.split(r"(\n\s*\n)", t)
hit = [i for i, x in enumerate(parts) if "three triggers" in x]
assert hit, "PLANT DID NOT LAND: the enumerating paragraph is not where the plant looks"
parts[hit[0]] = parts[hit[0]].replace("unresolved", "not-done")
t = "".join(parts).rstrip() + "\n\nA later note mentioning unresolved in passing.\n"
open(p, "w", encoding="utf-8").write(t)
seg = [x for x in re.split(r"\n\s*\n", t) if "three triggers" in x][0]
assert "unresolved" not in seg, "PLANT DID NOT LAND: the literal is still in the paragraph"
EOF
if python3 /tmp/tg4-copy/test/validate.py; then
  echo "ERROR: a trigger word floating elsewhere on the page satisfied the enumeration — the false-success class this guard closes"
  exit 1
else
  echo "OK: validator correctly FAILs — the check is scoped to the paragraph that enumerates"
fi
