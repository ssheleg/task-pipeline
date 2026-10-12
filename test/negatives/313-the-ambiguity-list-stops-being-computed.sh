#!/usr/bin/env bash
# name: Negative self-test (the ambiguity list stops being computed)
set -eu
rm -rf /tmp/hb03-copy && cp -R . /tmp/hb03-copy
python3 - <<'EOF'
p = "/tmp/hb03-copy/plugins/task-pipeline/skills/task-pipeline/references/progress.md"
t = open(p, encoding="utf-8").read()
i = t.index("### AMBIGUITIES are computed")
j = t.index("\n## ", i)
assert "none found" in t[i:j], "PLANT DID NOT LAND: hb03"
# The shape it degrades into on its own: judgement with no register behind it.
open(p, "w", encoding="utf-8").write(
    t[:i] + "### AMBIGUITIES\n\nList anything that still looks unclear to you.\n" + t[j:])
EOF
if python3 /tmp/hb03-copy/test/validate.py 2>&1 | grep -q 'no longer names these computed sources'; then
  echo "OK: validator FAILs — an unbounded 'is anything unclear?' is a ritual sentence within three runs"
else
  echo "ERROR: the ambiguity list became judgement and nothing objected"
  exit 1
fi
