#!/usr/bin/env bash
# name: Negative self-test (a test file creates temp state and never cleans it up)
set -eu
rm -rf /tmp/tmpst-copy && cp -R . /tmp/tmpst-copy
python3 - <<'EOF'
# R07: 15,146 trees from one validator helper in one machine's TMPDIR. The call is
# built at run time — spelled out here, it would make this very file trip the guard.
import re
call = "mkd" + "temp("
p = "/tmp/tmpst-copy/test/zz_leaky.py"
open(p, "w", encoding="utf-8").write(
    "import tempfile\n\nd = tempfile." + call + ")\nprint(d)\n")
t = open(p, encoding="utf-8").read()
bare = call in t and not re.search(r"rmtree|unlink|\bremove\(|residue|_TMP_TREES", t)
assert bare, "PLANT DID NOT LAND: the planted test is not a bare temp-state creator"
EOF
if python3 /tmp/tmpst-copy/test/validate.py 2>&1 | grep -q "creates temp state"; then
  echo "OK: validator FAILs — a test that makes temp state also removes it"
else
  echo "ERROR: a test file leaking a temp tree per run passed the gate"
  exit 1
fi
