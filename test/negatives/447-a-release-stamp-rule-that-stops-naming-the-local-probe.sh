#!/usr/bin/env bash
# name: Negative self-test (a release-stamp rule that stops naming the local probe)
set -eu
rm -rf /tmp/rm5 && cp -R . /tmp/rm5
python3 test/plant_stamp_needle.py /tmp/rm5 'test:all'
if python3 /tmp/rm5/test/validate.py 2>&1 | grep -q "release-stamp rule no longer names"; then
  echo "OK: validator FAILs — the tag has its own tree; a green branch build is a promise about a different one"
else
  echo "ERROR: the rule stopped naming the local probe and nothing objected"; exit 1
fi
