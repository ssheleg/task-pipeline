#!/usr/bin/env bash
# name: Negative self-test (a browser pointer that renders as nothing)
set -eu
rm -rf /tmp/br3-copy && cp -R . /tmp/br3-copy
python3 - <<'EOF'
p = "/tmp/br3-copy/plugins/task-pipeline/skills/task-pipeline/references/stages.md"
t = open(p, encoding="utf-8").read()
needle = "either one ([`browser.md`](browser.md)) — load the deployed URL"
assert needle in t, "PLANT DID NOT LAND: stage 8's browser pointer moved"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "either one <!-- browser.md --> — load the deployed URL", 1))
EOF
if python3 /tmp/br3-copy/test/validate.py; then
  echo "ERROR: an HTML comment is invisible once rendered and satisfied the pointer check"
  exit 1
else
  echo "OK: validator correctly FAILs — the pointer must be a link, not a substring"
fi
