#!/usr/bin/env bash
# name: Negative self-test (a release-stamp rule that stops naming the tag shape)
set -eu
rm -rf /tmp/rm2 && cp -R . /tmp/rm2
python3 test/plant_stamp_needle.py /tmp/rm2 'cite the release tag'
if python3 /tmp/rm2/test/validate.py 2>&1 | grep -q "release-stamp rule no longer names"; then
  echo "OK: validator FAILs — the only shape available BEFORE the merge exists"
else
  echo "ERROR: the rule stopped naming the tag shape and nothing objected"; exit 1
fi
