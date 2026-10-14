#!/usr/bin/env bash
# name: Negative self-test (a lesson re-keyed without its commit resolving)
set -eu
rm -rf /tmp/r13-rekey-resolve-copy && cp -R . /tmp/r13-rekey-resolve-copy
python3 - <<'EOF'
# Round 13, K: the re-key needs the origin's own commit to resolve in the re-derived checkout. Drop that evidence.
p = "/tmp/r13-rekey-resolve-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '            and any(_resolves_strict(c, o["commit"]) for c in n["checkouts"])]\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, ']\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/r13-rekey-resolve-copy/test/lessons_test.py; then
  rm -rf /tmp/r13-rekey-resolve-copy
  echo "ERROR: lessons_test passed a re-key on a retro anchor alone"
  exit 1
else
  rm -rf /tmp/r13-rekey-resolve-copy
  echo "OK: lessons_test correctly FAILs — the re-key needs positive evidence"
fi
