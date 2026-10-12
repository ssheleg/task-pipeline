#!/usr/bin/env bash
# name: Negative self-test (a mutating probe ships with no plant-landed assertion)
set -eu
rm -rf /tmp/ri13-copy && cp -R . /tmp/ri13-copy
python3 - <<'EOF'
import os, sys
sys.path.insert(0, "/tmp/ri13-copy/test")
import negatives
d = "/tmp/ri13-copy/test/negatives"
# A probe that reads a file and writes it back, with the phrase only in a
# COMMENT — all three of these shapes were watched passing a first version of
# the guard: the phrase in a comment, in a bash echo, and asserted about a
# different needle. Written as a check FILE, the shape the guard reads since v1.93.0.
name = "Negative self-test (planted, unasserted)"
body = (
    "set -eu\n"
    "rm -rf /tmp/zz9-copy && cp -R . /tmp/zz9-copy\n"
    "python3 - <<'XEOF'\n"
    "p = \"/tmp/zz9-copy/README.md\"\n"
    "t = open(p, encoding=\"utf-8\").read()\n"
    "# the plant would not land if the needle moved; checked by eye\n"
    "open(p, \"w\", encoding=\"utf-8\").write(t.replace(\"NEEDLE\", \"x\"))\n"
    "XEOF\n"
    "echo ok\n")
with open(os.path.join(d, "999-planted-unasserted.sh"), "w", encoding="utf-8") as fh:
    fh.write("#!/usr/bin/env bash\n# name: " + name + "\n" + body)
assert (name, body) in negatives.load_checks(d), "PLANT DID NOT LAND: ri13"
EOF
if python3 /tmp/ri13-copy/test/validate.py 2>&1 | grep -q "never assert the plant landed"; then
  echo "OK: validator FAILs — the phrase in a comment is not an assertion"
else
  echo "ERROR: a mutating probe shipped unasserted and the guard that exists for it stayed quiet"
  exit 1
fi
