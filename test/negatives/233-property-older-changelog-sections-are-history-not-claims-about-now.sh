#!/usr/bin/env bash
# name: Property check (older CHANGELOG sections are history, not claims about now)
set -eu
rm -rf /tmp/cl3-copy && cp -R . /tmp/cl3-copy
python3 - <<'EOF'
import re
p = "/tmp/cl3-copy/CHANGELOG.md"
t = open(p, encoding="utf-8").read()
i = t.index("\n## v", t.index("\n## v") + 4)          # the SECOND version heading
seg = t[i:]
m = re.search(r"(Guards:\s*\d+\s*→\s*\*\*)(\d+)(\*\*)", seg)
assert m, "PLANT DID NOT LAND: no guard count in an older section"
open(p, "w", encoding="utf-8").write(
    t[:i] + seg[:m.start(2)] + "999" + seg[m.end(2):])
EOF
if python3 /tmp/cl3-copy/test/validate.py >/dev/null; then
  echo "OK: an older section states what was true on its own day and is left alone"
else
  echo "ERROR: the guard reached back into history, where every count would need rewriting"
  exit 1
fi
