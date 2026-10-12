#!/usr/bin/env bash
# name: Negative self-test (coverage stops refusing a requirement nothing serves)
set -eu
rm -rf /tmp/cov1-copy && cp -R . /tmp/cov1-copy
python3 - <<'EOF'
p = "/tmp/cov1-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
# Anchor INSIDE cmd_coverage: `return 1 if bad else 0` stopped being unique the
# day cmd_close landed, and a first-occurrence replace then disarmed cmd_validate
# instead — a plant pinned to a literal rots when the literal stays and multiplies.
start = t.index("def cmd_coverage(")
end = t.index("\ndef ", start)
body = t[start:end]
needle = "    return 1 if bad else 0"
assert needle in body, "PLANT DID NOT LAND: cov1 — coverage's verdict line moved"
open(p, "w", encoding="utf-8").write(
    t[:start] + body.replace(needle, "    return 0", 1) + t[end:])
EOF
if python3 /tmp/cov1-copy/test/validate.py; then
  echo "ERROR: a coverage report that cannot fail was accepted — B-085, and a
         report that never refuses counted every gap as covered"; exit 1
else
  echo "OK: coverage is run against both a covered and an uncovered graph"
fi
