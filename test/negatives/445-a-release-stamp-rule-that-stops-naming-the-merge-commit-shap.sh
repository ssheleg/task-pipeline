#!/usr/bin/env bash
# name: Negative self-test (a release-stamp rule that stops naming the merge-commit shape)
set -eu
rm -rf /tmp/rm3 && cp -R . /tmp/rm3
python3 test/plant_stamp_needle.py /tmp/rm3 'merge commit'
if python3 /tmp/rm3/test/validate.py 2>&1 | grep -q "release-stamp rule no longer names"; then
  echo "OK: validator FAILs — the default — a SHA has to exist before a file names it"
else
  echo "ERROR: the rule stopped naming the merge-commit shape and nothing objected"; exit 1
fi
