#!/usr/bin/env bash
# name: Negative self-test (a long reference's Contents must match its headings)
set -eu
rm -rf /tmp/toc-copy && cp -R . /tmp/toc-copy
python3 - <<'EOF'
p = "/tmp/toc-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
old = "## The program loop"
assert old in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(
    t.replace(old, "## A section nobody listed\n\nbody.\n\n" + old, 1))
EOF
if python3 /tmp/toc-copy/test/validate.py; then
  echo "ERROR: validator passed a Contents list that no longer matches the headings — a hand-maintained list is a second source, and a partial read trusts it"
  exit 1
else
  echo "OK: validator compares each long reference's Contents against its own headings"
fi
