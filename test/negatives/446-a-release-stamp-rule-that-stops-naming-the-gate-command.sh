#!/usr/bin/env bash
# name: Negative self-test (a release-stamp rule that stops naming the gate command)
set -eu
rm -rf /tmp/rm4 && cp -R . /tmp/rm4
python3 test/plant_stamp_needle.py /tmp/rm4 'git merge-base --is-ancestor'
if python3 /tmp/rm4/test/validate.py 2>&1 | grep -q "release-stamp rule no longer names"; then
  echo "OK: validator FAILs — the question the release gate asks, so a run can ask it first"
else
  echo "ERROR: the rule stopped naming the gate command and nothing objected"; exit 1
fi
