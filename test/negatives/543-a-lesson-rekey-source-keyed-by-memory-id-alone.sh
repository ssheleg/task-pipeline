#!/usr/bin/env bash
# name: Negative self-test (a lesson re-key source keyed by memory id alone)
set -eu
rm -rf /tmp/r17-source-copy && cp -R . /tmp/r17-source-copy
python3 - <<'EOF'
# Round 17, F1: put back the re-key source looked up by memory id alone, whatever project holds it.
p = "/tmp/r17-source-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '                if (base, project) in source:\n                    mine[0]["rekeyedFrom"] = source[(base, project)]\n'
assert t.count(needle) == 1, "PLANT DID NOT LAND: anchor absent or not unique before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '                if any(b2 == base for b2, _ in source):\n                    mine[0]["rekeyedFrom"] = next(v for (b2, _), v in sorted(source.items()) if b2 == base)\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='r17 F1 rebuild: rekeyedFrom leaves with the id, and Z is given no source it never had'
out=$(python3 /tmp/r17-source-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r17-source-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed a project given a re-key source it never had"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs, the source follows (id, project)"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
