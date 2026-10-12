#!/usr/bin/env bash
# name: Negative self-test (the cross-cutting rules stop naming the field every gate prints)
set -eu
rm -rf /tmp/res12-copy && cp -R . /tmp/res12-copy
python3 - <<'EOF'
p = "/tmp/res12-copy/plugins/task-pipeline/skills/task-pipeline/SKILL.md"
t = open(p, encoding="utf-8").read()
# Matched by regex, not by a literal with a line break in it: the phrase
# reflows whenever the paragraph is edited, and a plant that stops landing
# leaves its guard unproven while reading green (2026-08-16).
import re
_planted, _n = re.subn(r"every gate\s+prints `[^`]+`",
                       "every gate says nothing about what", t, count=1)
assert _n == 1, "PLANT DID NOT LAND: res12"
open(p, "w", encoding="utf-8").write(_planted)
EOF
if python3 /tmp/res12-copy/test/validate.py 2>&1 | grep -q 'no longer name the field'; then
  echo "OK: validator FAILs — a gate disclosure nobody is told to print does not exist"
else
  echo "ERROR: the obligation to print holds: vanished and only the doctrine file remembered it"
  exit 1
fi
