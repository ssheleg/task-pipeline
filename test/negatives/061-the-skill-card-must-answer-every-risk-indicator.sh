#!/usr/bin/env bash
# name: Negative self-test (the skill card must answer every risk indicator)
set -eu
rm -rf /tmp/card-copy && cp -R . /tmp/card-copy
python3 - <<'EOF'
p = "/tmp/card-copy/SKILL-CARD.md"
t = open(p, encoding="utf-8").read()
assert "MCP server references" in t, "PLANT MISSED"
open(p, "w", encoding="utf-8").write(t.replace("MCP server references", "Other notes"))
EOF
if python3 /tmp/card-copy/test/validate.py; then
  echo "ERROR: validator passed a skill card with a risk indicator omitted — an omitted row reads as 'does not apply', and here three of them do"
  exit 1
else
  echo "OK: validator requires every risk indicator answered on the card"
fi
