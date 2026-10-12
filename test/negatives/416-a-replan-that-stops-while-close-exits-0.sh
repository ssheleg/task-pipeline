#!/usr/bin/env bash
# name: Negative self-test (a replan that stops while close exits 0)
set -eu
rm -rf /tmp/cls1-copy && cp -R . /tmp/cls1-copy
python3 - <<'EOF'
p = "/tmp/cls1-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
needle = "        return 1\n    return 0\n\n\nVERBS"
assert needle in t, "PLANT DID NOT LAND: cls1 — close's stop branch moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "        return 0\n    return 0\n\n\nVERBS", 1))
EOF
if python3 /tmp/cls1-copy/test/graph_test.py; then
  echo "ERROR: a verdict saying the run cannot continue exited 0 — the loop would
         carry on past a stop, which is the one thing replan.possible false is
         for"; exit 1
else
  echo "OK: close's stop branch is fixtured on both sides"
fi
