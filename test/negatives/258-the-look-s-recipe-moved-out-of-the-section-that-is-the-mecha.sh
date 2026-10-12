#!/usr/bin/env bash
# name: Negative self-test (the look's recipe moved out of the section that is the mechanism)
set -eu
rm -rf /tmp/br4-copy && cp -R . /tmp/br4-copy
python3 - <<'EOF'
# DERIVED anchor (B-113): the example URL and its port are illustration,
# and the check is about WHERE the fence lives, not what it opens. Find
# the recipe by its shape so an edited example cannot silence the plant.
import re
p = "/tmp/br4-copy/plugins/task-pipeline/skills/task-pipeline/references/browser.md"
t = open(p, encoding="utf-8").read()
_m = re.search(r"(?m)^```bash\nplaywright-cli open \S+\n", t)
assert _m, "PLANT DID NOT LAND: the look's recipe moved"
i = _m.start()
j = t.index("```", i + 3) + 3
block = t[i:j]
open(p, "w", encoding="utf-8").write(
    t[:i] + "See the appendix.\n" + t[j:] + "\n\n## Appendix\n\n" + block + "\n")
EOF
if python3 /tmp/br4-copy/test/validate.py; then
  echo "ERROR: the four commands can leave the section the stages point at and nothing notices"
  exit 1
else
  echo "OK: validator correctly FAILs — the recipe lives in the section that is the mechanism"
fi
