#!/usr/bin/env bash
# TP-OUT-006's command check: `waves.py validate` must REFUSE this fixture.
# The inventory holds three open items; the plan's only node closes two, so
# B-103 lands nowhere. Exit 0 means the refusal happened and named B-103;
# any other result — including the validator accepting the fixture, or the
# script not being found — is non-zero, so a missing tool can never pass.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
scripts="${TASK_PIPELINE_SCRIPTS:-$here/../../../plugins/task-pipeline/skills/task-pipeline/scripts}"
if [ ! -f "$scripts/waves.py" ]; then
  echo "expect-refusal: waves.py not found under $scripts (set TASK_PIPELINE_SCRIPTS)" >&2
  exit 2
fi
err="$(python3 "$scripts/waves.py" validate \
  --inventory "$here/inventory.json" \
  --modules "$here/modules.json" \
  --plan "$here/plan.json" 2>&1 >/dev/null)"
rc=$?
if [ "$rc" -ne 1 ]; then
  echo "expect-refusal: waves.py validate exited $rc, expected 1" >&2
  exit 1
fi
case "$err" in
  *B-103*) exit 0 ;;
  *) echo "expect-refusal: the refusal did not name B-103: $err" >&2; exit 1 ;;
esac
