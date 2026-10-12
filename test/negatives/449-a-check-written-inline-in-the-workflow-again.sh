#!/usr/bin/env bash
# name: Negative self-test (a check written inline in the workflow again)
set -eu
rm -rf /tmp/inl1-copy && cp -R . /tmp/inl1-copy
python3 - <<'EOF'
# Habit is the threat: until v1.93.0 a plant WAS a workflow step, and the next one
# written that way runs on CI only — outside test/negatives/, outside every count,
# invisible to the local runner, and back toward the 512,000-byte limit.
import re
p = "/tmp/inl1-copy/.github/workflows/validate.yml"
t = open(p, encoding="utf-8").read()
m = re.search(r"(?m)^  validate:\n(?:.*\n)*?    steps:\n", t)
assert m, "PLANT DID NOT LAND: no validate job to add a step to"
step = ("      - name: Negative self-test (written inline, the old way)\n"
        "        run: |\n"
        "          echo \"OK: proven nowhere but CI\"\n\n")
open(p, "w", encoding="utf-8").write(t[:m.end()] + step + t[m.end():])
assert re.search(r"(?m)^\s*- name:\s*Negative self-test \(written inline",
                 open(p, encoding="utf-8").read()), \
    "PLANT DID NOT LAND: no inline step where the guard reads"
EOF
if python3 /tmp/inl1-copy/test/validate.py 2>&1 | grep -q "is a check written inline"; then
  echo "OK: validator FAILs — a plant belongs in test/negatives/, never inline in the workflow"
else
  echo "ERROR: a check written inline in the workflow passed — it would run on CI only, outside every count"
  exit 1
fi
