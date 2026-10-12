#!/usr/bin/env bash
# name: Negative self-test (the two artifact-root implementations must be compared, not merely run)
set -eu
rm -rf /tmp/ar-copy && cp -R . /tmp/ar-copy
python3 - <<'EOF'
# Reverse the precedence in ONE implementation. The table still describes the
# correct order, so a suite that only checked each side against the table
# would fail — but a suite that never compared them to each other would let
# the two drift apart on a case the table did not name. Anchored on the
# structural line, and it asserts it changed something: a plant that stops
# landing reports the guard it can no longer disarm as broken.
p = "/tmp/ar-copy/bin/lib/artifact-root.js"
t = open(p, encoding="utf-8").read()
old = "const KNOWN = ['docs/evidence', 'docs/superpowers'];"
assert old in t, "PLANT DID NOT LAND: the KNOWN order is not where it was"
t = t.replace(old, "const KNOWN = ['docs/superpowers', 'docs/evidence'];", 1)
open(p, "w", encoding="utf-8").write(t)
assert "const KNOWN = ['docs/superpowers'" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/ar-copy/test/artifact_root_test.py; then
  echo "ERROR: one implementation resolves a partial migration BACKWARDS and the suite passed"
  exit 1
else
  echo "OK: the suite refuses a disagreement between the two implementations"
fi
