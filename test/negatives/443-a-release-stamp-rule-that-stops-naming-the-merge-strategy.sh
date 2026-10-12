#!/usr/bin/env bash
# name: Negative self-test (a release-stamp rule that stops naming the merge strategy)
set -eu
rm -rf /tmp/rm1 && cp -R . /tmp/rm1
python3 test/plant_stamp_needle.py /tmp/rm1 'rebase-merge'
if python3 /tmp/rm1/test/validate.py 2>&1 | grep -q "release-stamp rule no longer names"; then
  echo "OK: validator FAILs — without the strategy named, the rule reads as advice about tidiness"
else
  echo "ERROR: the rule stopped naming the merge strategy and nothing objected"; exit 1
fi
