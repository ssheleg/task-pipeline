#!/usr/bin/env bash
# name: Property check (the anchor census prints its disclosure beside the verdict)
set -eu
# A measurement nobody surfaces is the same silence as no measurement — the
# loudest canon in this repository, and the reason the never-count prints. The
# census is a disclosure with no floor and no target: how many plants there
# are, how many pin a value, how many declare, how many can decline to run.
# `|| true` because the disclosures print BESIDE the verdict, and the verdict
# block exits before them on a red tree: without it this check would report a
# missing disclosure whenever some unrelated guard is failing.
_out=$(python3 test/validate.py || true)
if printf '%s' "$_out" | grep -q "negative-test anchors: [0-9]* plants" \
   && printf '%s' "$_out" | grep -q "can decline to run"; then
  echo "OK: the anchor census prints its four numbers on every run"
else
  echo "ERROR: the census printed no disclosure — either it was dropped, or the"
  echo "       tree is red and the verdict block exited before the disclosures"
  exit 1
fi
