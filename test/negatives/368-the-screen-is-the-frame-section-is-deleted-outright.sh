#!/usr/bin/env bash
# name: Negative self-test (the screen-is-the-frame section is deleted outright)
set -eu
rm -rf /tmp/fig5-copy && cp -R . /tmp/fig5-copy
python3 - <<'EOF'
import re
p = "/tmp/fig5-copy/plugins/task-pipeline/skills/task-pipeline/references/build.md"
t = open(p, encoding="utf-8").read()
# fig1-fig4 mutate a phrase inside the section, so none of them reaches the
# branch that fires when the heading itself is gone. A fail() path with no
# probe is a path nobody has watched.
m = re.search(r"^## 4a\. A screen is the frame, implemented.*?(?=^## )", t, re.S | re.M)
assert m, "PLANT DID NOT LAND: fig5"
_planted = t[:m.start()] + t[m.end():]
assert _planted != t, "PLANT DID NOT LAND: fig5"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/fig5-copy/test/validate.py 2>&1 | grep -q "no section making a screen"; then
  echo "OK: validator FAILs — without the section Figma is an address and a link, which is what it was"
else
  echo "ERROR: the whole rule was removed and only its citations objected"
  exit 1
fi
