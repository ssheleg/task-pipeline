#!/usr/bin/env bash
# name: Negative self-test (an `npm` gloss that disagrees with package.json)
set -eu
rm -rf /tmp/gloss1-copy && cp -R . /tmp/gloss1-copy
python3 - <<'EOF'
# CLAUDE.md said `npm test` (= `python3 test/validate.py`), dropping graph_test.py
# and its 129 cases — the same suite-outside-the-run class the test:all reach check
# exists for, stated the other way round. Nothing compared a documented equation
# against package.json.
#
# Anchored on SHAPE, not on the equation's text (standing instruction #6). The
# first version named the two-suite equation verbatim and went silent the day a
# third suite joined it — reporting a guard that was fine as broken, which is the
# exact failure mode #6 exists for. The shape is the parenthesised `(= ...)`
# beside `npm test`; the plant truncates it to one suite however many it names.
import re
p = "/tmp/gloss1-copy/CLAUDE.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"\(= (`[^`]+`)\)", t)
assert m, "PLANT DID NOT LAND: no `(= ...)` equation beside npm test in CLAUDE.md"
assert "&&" in m.group(1), \
    "PLANT DID NOT LAND: the equation already names a single suite, nothing to truncate"
after = "(= `python3 test/validate.py`)"
t2 = t.replace(m.group(0), after, 1)
assert t2 != t and after in t2, "PLANT DID NOT LAND: the edit changed nothing"
open(p, "w", encoding="utf-8").write(t2)
EOF
if python3 /tmp/gloss1-copy/test/validate.py; then
  echo "ERROR: validator passed an npm gloss that names fewer suites than the script runs"
  exit 1
else
  echo "OK: validator correctly FAILs — a gloss is a claim about what the command does"
fi
