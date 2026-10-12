#!/usr/bin/env bash
# name: Negative self-test (an open board row citing a span and quoting nothing from it)
set -eu
rm -rf /tmp/bcite2-copy && cp -R . /tmp/bcite2-copy
python3 - <<'EOF'
# Without a quoted needle the address can only be checked against the file's
# LENGTH, which is how five stale citations read as sound.
p = "/tmp/bcite2-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
needle = "*«Scale the check to what breaking costs»* — "
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "", 1))
assert needle not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/bcite2-copy/test/validate.py; then
  echo "ERROR: validator passed an open row citing a span with no phrase to check it against"
  exit 1
else
  echo "OK: validator correctly FAILs — a range in an open row quotes what it points at"
fi
