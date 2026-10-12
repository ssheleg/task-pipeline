#!/usr/bin/env bash
# name: Negative self-test (canon 9a — a count printed with no unmeasured case)
set -eu
rm -rf /tmp/c9a-copy && cp -R . /tmp/c9a-copy
python3 - <<'EOF'
p = "/tmp/c9a-copy/plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
t = open(p, encoding="utf-8").read()
verb = ('def cmd_tally(graph, args):\n'
        '    """A count-printing verb written without the rule."""\n'
        '    print(f"tally: {len(graph.get(chr(34)nodes(chr(34)) or [])} nodes")\n'
        '    return 0\n\n\n')
verb = verb.replace('chr(34)', '"')
assert "VERBS = {" in t, "PLANT DID NOT LAND: c9a — the verb table moved"
t = t.replace("VERBS = {", verb + "VERBS = {", 1)
t = t.replace('    "goal": (cmd_goal,',
              '    "tally": (cmd_tally, "count the nodes"),\n    "goal": (cmd_goal,', 1)
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/c9a-copy/test/validate.py; then
  echo "ERROR: a new count-printing verb with no unmeasured case was accepted — canon
         9a: a measured zero and an unmeasured quantity may not print the same,
         because 0 is the most reassuring answer available and it comes from an
         instrument nobody switched on"; exit 1
else
  echo "OK: the rule is checked over the shape, so the fourth site is caught too"
fi
