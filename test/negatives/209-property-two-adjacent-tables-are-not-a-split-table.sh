#!/usr/bin/env bash
# name: Property check (two adjacent tables are not a split table)
set -eu
rm -rf /tmp/adj-copy && cp -R . /tmp/adj-copy
python3 - <<'EOF'
p = "/tmp/adj-copy/README.md"
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(
    t + "\n| a | b |\n|---|---|\n| 1 | 2 |\n\n| c | d |\n|---|---|\n| 3 | 4 |\n")
EOF
if python3 /tmp/adj-copy/test/validate.py >/dev/null; then
  echo "OK: two independent tables one blank line apart are left alone — the shape the guard's comment claims"
else
  echo "ERROR: the split-table guard fires on a valid pattern; a checker with false positives is worse than none"
  exit 1
fi
