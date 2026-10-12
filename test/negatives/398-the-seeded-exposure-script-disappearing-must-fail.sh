#!/usr/bin/env bash
# name: Negative self-test (the seeded exposure script disappearing must fail)
set -eu
# B-43: this script was written, tested green, parked in a session scratchpad
# and lost when the scratchpad was cleaned. The board called it "built and
# parked" for two days while nothing on disk held it.
rm -rf /tmp/exp1-copy && cp -R . /tmp/exp1-copy
rm /tmp/exp1-copy/plugins/task-pipeline/skills/task-pipeline/templates/exposure.sh
if python3 /tmp/exp1-copy/test/validate.py 2>&1 | grep -q "missing template: templates/exposure.sh"; then
  echo "OK: validator FAILs — a template can no longer vanish silently"
else
  echo "ERROR: the seeded script can disappear and the gate stays green"
  exit 1
fi
