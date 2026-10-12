#!/usr/bin/env bash
# name: Negative self-test (stage coverage must refuse when it cannot look)
set -eu
rm -rf /tmp/stagecov2 && mkdir -p /tmp/stagecov2/scripts
cp plugins/task-pipeline/skills/task-pipeline/templates/stage-coverage.sh /tmp/stagecov2/scripts/
cd /tmp/stagecov2
set +e
bash scripts/stage-coverage.sh >/dev/null 2>&1
code=$?
set -e
# 2, never 0: no config and no ledger is "could not look", and a check that
# cannot run must say so rather than agree (standing instruction #1).
if [ "$code" = "2" ]; then
  echo "OK: refuses with 2 when there is nothing to look at"
else
  echo "ERROR: expected exit 2 with no config and no ledger, got $code"
  exit 1
fi
