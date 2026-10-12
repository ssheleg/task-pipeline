#!/usr/bin/env bash
# name: Negative self-test (the workflow itself stops being valid YAML)
set -eu
# dormant-when: PyYAML is absent, so the guard under test cannot parse the
#   workflow at all and discloses that instead of passing. Cost: the parse
#   guard is unprobed on a bare interpreter, which is the machine most likely
#   to be missing it — the plant's ERROR branch would otherwise read as a
#   finding about the workflow rather than about the environment.
rm -rf /tmp/res8-copy && cp -R . /tmp/res8-copy
python3 - <<'EOF'
import re
p = "/tmp/res8-copy/.github/workflows/validate.yml"
t = open(p, encoding="utf-8").read()
# A colon-space inside an unquoted step name. The checks the validator reads
# with a regex cannot tell; only a parse can. The step this plant first broke
# left the workflow with every other plant in v1.93.0, so the target is the
# first plain step name with no colon of its own — derived, not named.
m = re.search(r"(?m)^(\s*- name: )([^:'\"\n]+)$", t)
assert m, "PLANT DID NOT LAND: res8 — no plain step name left to break"
_planted = t[:m.end(2)] + ": with a colon-space" + t[m.end(2):]
assert _planted != t, "PLANT DID NOT LAND: res8"
try:
    import yaml
except ImportError:
    yaml = None
if yaml is not None:
    # Asserted on the value the guard reads: the parse itself must now refuse.
    try:
        yaml.safe_load(_planted)
    except yaml.YAMLError:
        pass
    else:
        raise AssertionError("PLANT DID NOT LAND: res8 — the planted name still parses")
open(p, "w", encoding="utf-8").write(_planted)
EOF
_out=$(python3 /tmp/res8-copy/test/validate.py 2>&1 || true)
if printf '%s' "$_out" | grep -q "not valid YAML"; then
  echo "OK: validator FAILs — the workflow is parsed, not only pattern-matched"
elif printf '%s' "$_out" | grep -q "PyYAML not installed"; then
  echo "SKIP: PyYAML is absent, so the parse guard could not run — it said so"
  echo "      rather than passing quietly, which is the behaviour under test here"
else
  echo "ERROR: the workflow stopped being loadable, the parse guard neither fired"
  echo "       nor declared itself unable to look, and every regex count stayed happy"
  exit 1
fi
