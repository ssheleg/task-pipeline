#!/usr/bin/env bash
# name: Negative self-test (a worked verdict on a surface no list named)
set -eu
rm -rf /tmp/discnew-copy && cp -R . /tmp/discnew-copy
python3 - <<'EOF'
p = "/tmp/discnew-copy/README.md"
t = open(p, encoding="utf-8").read()
needle = "  abstained: 1 (1 cannot-verify) · unlooked: 0\n"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(t.replace(needle, "", 1))
assert "abstained: 1 (1 cannot-verify)" not in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/discnew-copy/test/validate.py; then
  echo "ERROR: validator passed a worked verdict on a surface the hand-written list had missed"
  exit 1
else
  echo "OK: validator correctly FAILs — the disclosure corpus is discovered, not listed"
fi
