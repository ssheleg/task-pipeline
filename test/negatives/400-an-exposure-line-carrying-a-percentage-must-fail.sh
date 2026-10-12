#!/usr/bin/env bash
# name: Negative self-test (an exposure line carrying a percentage must fail)
set -eu
# The doctrine's own refusal: "no percentage, ever". A single score invites a
# threshold, and a threshold here is a target on `never`.
rm -rf /tmp/exp3-copy && cp -R . /tmp/exp3-copy
s=/tmp/exp3-copy/plugins/task-pipeline/skills/task-pipeline/templates/exposure.sh
grep -q '^LINE=' "$s" || { echo "PLANT DID NOT LAND: no LINE= assignment"; exit 1; }
sed 's|^LINE=.*|LINE="exposure: 12% likely broken"|' "$s" > /tmp/exp3-copy/g.sh
mkdir -p /tmp/exp3-copy/probe/docs/evidence
printf '| REQ | What | Run | Shipped in | Auto | Human | Note |\n|---|---|---|---|---|---|---|\n| R-1 | x | r | v1.0.0 | pass | never | - |\n' \
  > /tmp/exp3-copy/probe/docs/evidence/verification.md
if (cd /tmp/exp3-copy/probe && bash ../g.sh); then
  echo "ERROR: a percentage went out on the exposure line"
  exit 1
fi
echo "OK: refused, as the doctrine requires"
