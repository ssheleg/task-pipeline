#!/usr/bin/env bash
# name: Negative self-test (the retro's archive pointer naming a root this project does not use)
set -eu
rm -rf /tmp/gap2-copy && cp -R . /tmp/gap2-copy
python3 - <<'EOF'
# Live stage-0 doctrine named `docs/superpowers/retro/YYYY-QN.md` — the
# pre-v1.53.0 root — so the one line a run reads to find the archive pointed at a
# directory that has not existed since.
p = "/tmp/gap2-copy/docs/evidence/retro.md"
t = open(p, encoding="utf-8").read()
needle = "`docs/evidence/retro/YYYY-QN.md`"
assert needle in t, "PLANT DID NOT LAND: anchor absent before edit"
open(p, "w", encoding="utf-8").write(
    t.replace(needle, "`docs/superpowers/retro/YYYY-QN.md`", 1))
assert "docs/superpowers/retro/YYYY-QN.md" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
if python3 /tmp/gap2-copy/test/validate.py; then
  echo "ERROR: validator passed an archive pointer at a root this project does not use"
  exit 1
else
  echo "OK: validator correctly FAILs — the archive pointer is compared against the resolved root"
fi
