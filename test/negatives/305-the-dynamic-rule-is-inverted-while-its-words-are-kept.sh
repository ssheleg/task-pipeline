#!/usr/bin/env bash
# name: Negative self-test (the dynamic rule is inverted while its words are kept)
set -eu
rm -rf /tmp/lp15-copy && cp -R . /tmp/lp15-copy
python3 - <<'EOF'
p = "/tmp/lp15-copy/plugins/task-pipeline/skills/task-pipeline/references/continuity.md"
t = open(p, encoding="utf-8").read()
n = "prints **the delay it chose and why**"
assert n in t, "PLANT DID NOT LAND: lp15"
# The noun pair survives; the obligation is reversed. The first predicate
# searched for the words and passed this.
t = t.replace(n, "keeps the delay it chose internal, because a pacing line every turn is noise", 1)
t = t.replace("A dynamic run that says nothing about its pacing is indistinguishable from a\nrun that quietly stopped.", "", 1)
open(p, "w", encoding="utf-8").write(t)
EOF
if python3 /tmp/lp15-copy/test/validate.py 2>&1 | grep -q 'never says a self-pacing run prints the delay'; then
  echo "OK: validator FAILs — the verb and the consequence are required, not the nouns"
else
  echo "ERROR: the rule was inverted with its words intact and the guard passed"
  exit 1
fi
