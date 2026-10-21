#!/usr/bin/env bash
# name: Negative self-test (a lesson rebuild keeping a v1.95.0 origin as a second project)
set -eu
rm -rf /tmp/r13-rekey-rebuild-copy && cp -R . /tmp/r13-rekey-rebuild-copy
python3 - <<'EOF'
# Round 13, K: a rebuild re-keys a provenance-less origin its repository re-derives. Skip the re-key.
p = "/tmp/r13-rekey-rebuild-copy/plugins/task-pipeline/skills/task-pipeline/scripts/lessons.py"
t = open(p, encoding="utf-8").read()
needle = '        rekeyed = _rekey_legacy(old, entries, set(run["project"].values()) | _known_projects(old))\n'
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, '        rekeyed = []\n', 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
# The plant must fail with ITS defect, not any non-zero exit (round 16).
expect='K: a v1.95.0 origin of the same repository is re-keyed, its id kept, one project'
out=$(python3 /tmp/r13-rekey-rebuild-copy/test/lessons_test.py 2>&1) && rc=0 || rc=$?
rm -rf /tmp/r13-rekey-rebuild-copy
if [ "$rc" -eq 0 ]; then
  echo "ERROR: lessons_test passed an upgraded index counting its own repository twice"
  exit 1
elif printf '%s\n' "$out" | grep -qF "FAIL: $expect"; then
  echo "OK: lessons_test correctly FAILs — an origin v1.95.0 wrote is re-keyed, not a second project"
else
  echo "ERROR: lessons_test failed, but not with: FAIL: $expect"
  printf '%s\n' "$out" | tail -3
  exit 1
fi
