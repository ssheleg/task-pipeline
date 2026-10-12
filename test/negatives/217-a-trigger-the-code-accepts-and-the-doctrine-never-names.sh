#!/usr/bin/env bash
# name: Negative self-test (a trigger the code accepts and the doctrine never names)
set -eu
rm -rf /tmp/tg1-copy && cp -R . /tmp/tg1-copy
python3 - <<'EOF'
p = "/tmp/tg1-copy/test/validate.py"
t = open(p, encoding="utf-8").read()
needle = 'r"^(?:open|unresolved|backlog)\\b"'
assert needle in t, "PLANT DID NOT LAND: the trigger regex is not where the guard reads it"
open(p, "w", encoding="utf-8").write(t.replace(needle, 'r"^(?:open|unresolved|backlog|parked)\\b"', 1))
EOF
if python3 /tmp/tg1-copy/test/validate.py; then
  echo "ERROR: the code grew a trigger the doctrine never names — that shipped three times in one module"
  exit 1
else
  echo "OK: validator correctly FAILs — the enumeration is computed from the regex, both directions"
fi
