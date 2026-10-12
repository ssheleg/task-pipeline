#!/usr/bin/env bash
# name: Negative self-test (cold trigger — the canonical row, where bold interrupts the phrase)
set -eu
rm -rf /tmp/cold2-copy && cp -R . /tmp/cold2-copy
python3 - <<'EOF'
p = "/tmp/cold2-copy/plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
t = open(p, encoding="utf-8").read()
# The canonical row moved when the retrospective gained rule CLASSES: a cold
# rule is now marked review-needed rather than deleted, and the trigger reads
# exposure opportunities. The guard's subject is unchanged — emphasis must be
# normalised before matching, or bolding defeats it — so the plant follows the
# row to its current wording.
needle = "**five exposure opportunities** — or no exposure occurred in **sixty days**"
assert needle in t, "PLANT DID NOT LAND: canonical row absent before edit"
t = t.replace(needle, "**five exposure opportunities**", 1)
open(p, "w", encoding="utf-8").write(t)
s = open(p, encoding="utf-8").read()
assert "**five exposure opportunities** — or no" not in s, "PLANT DID NOT LAND"
assert "**five exposure opportunities**" in s, "PLANT WRONG: the bold phrase must survive"
EOF
if python3 /tmp/cold2-copy/test/validate.py; then
  echo "ERROR: the guard skipped the file that DEFINES the trigger — markdown emphasis defeated it"
  exit 1
else
  echo "OK: validator correctly FAILs — emphasis is normalised before matching"
fi
