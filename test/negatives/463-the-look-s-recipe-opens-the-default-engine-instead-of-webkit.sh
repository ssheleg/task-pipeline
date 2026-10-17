#!/usr/bin/env bash
# name: Negative self-test (the look's recipe opens the default engine instead of WebKit)
set -eu
rm -rf /tmp/eng-webkit-copy && cp -R . /tmp/eng-webkit-copy
python3 - <<'PY'
# DERIVED anchor: find the recipe's `open` line by its shape, so a changed example
# URL cannot silence the plant, and strip only the engine flag from it.
import re
p = "/tmp/eng-webkit-copy/plugins/task-pipeline/skills/task-pipeline/references/browser.md"
t = open(p, encoding="utf-8").read()
_m = re.search(r"(?m)^playwright-cli open --browser[ =]webkit ", t)
assert _m, "PLANT DID NOT LAND: the recipe does not open WebKit to begin with"
t2 = t[:_m.start()] + "playwright-cli open " + t[_m.end():]
assert t2 != t, "PLANT DID NOT LAND"
open(p, "w", encoding="utf-8").write(t2)
PY
set +e
out=$(python3 /tmp/eng-webkit-copy/test/validate.py 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ] && echo "$out" | grep -qF 'the look'"'"'s recipe opens a page without'; then
  echo "OK: validator FAILs — the runnable recipe opens WebKit, the engine the doctrine ranks first"
else
  echo "$out" | tail -5
  echo "ERROR: the recipe went back to the default engine and nothing objected"
  exit 1
fi
