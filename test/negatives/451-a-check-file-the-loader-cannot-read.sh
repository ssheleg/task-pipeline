#!/usr/bin/env bash
# name: Negative self-test (a check file the loader cannot read)
set -eu
rm -rf /tmp/fmt1-copy && cp -R . /tmp/fmt1-copy
python3 - <<'EOF'
# A file whose header the loader does not recognise is not a check that fails —
# it is a check that is never counted and never run, while the suite stays green.
import os, sys
sys.path.insert(0, "/tmp/fmt1-copy/test")
import negatives
d = "/tmp/fmt1-copy/test/negatives"
f = sorted(x for x in os.listdir(d) if x.endswith(".sh"))[0]
p = os.path.join(d, f)
lines = open(p, encoding="utf-8").read().split("\n")
assert lines[1].startswith(negatives.NAME_HEADER), "PLANT DID NOT LAND: no header to break"
lines[1] = "# title: " + lines[1][len(negatives.NAME_HEADER):]
open(p, "w", encoding="utf-8").write("\n".join(lines))
assert any(x.startswith(f + ":") for x in negatives.scan(d)[1]), \
    "PLANT DID NOT LAND: the loader still reads the file as a check"
EOF
if python3 /tmp/fmt1-copy/test/validate.py 2>&1 | grep -q "line 1 must be"; then
  echo "OK: validator FAILs — a file in test/negatives/ is a check the loader reads, or a refusal"
else
  echo "ERROR: a check the loader cannot read dropped out of the suite in silence"
  exit 1
fi
