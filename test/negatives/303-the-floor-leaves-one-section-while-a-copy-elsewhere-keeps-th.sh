#!/usr/bin/env bash
# name: Negative self-test (the floor leaves one section while a copy elsewhere keeps the guard green)
set -eu
rm -rf /tmp/lp13-copy && cp -R . /tmp/lp13-copy
python3 - <<'EOF'
p = "/tmp/lp13-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md"
t = open(p, encoding="utf-8").read()
# No regex: an escaped pattern in a YAML heredoc searched for a literal
# backslash and the plant never landed. Plain indexing instead.
head = "## Part 1a"
i = t.index(head)
j = t.index("\n## ", i + len(head))
sec = t[i:j]
n = "*a generic flag is not a specific authorization*, and arming a"
assert n in sec, "PLANT DID NOT LAND: lp13 — Part 1a no longer states the floor"
# Only Part 1a's copy: the file-wide test this guard replaced stayed green here,
# answered by the bullet in "The limit" and a Rationalizations row.
sec2 = sec.replace(n, "arming a", 1)
open(p, "w", encoding="utf-8").write(t[:i] + sec2 + t[j:])
EOF
if python3 /tmp/lp13-copy/test/validate.py 2>&1 | grep -q "Part 1a.: the sentence that keeps arming"; then
  echo "OK: validator FAILs — a copy elsewhere in the file is not the copy this section's reader meets"
else
  echo "ERROR: the floor left Part 1a and a Rationalizations row kept the guard green"
  exit 1
fi
