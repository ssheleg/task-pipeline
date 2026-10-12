#!/usr/bin/env bash
# name: Negative self-test (a real broken link still fails past the fence stripper)
set -eu
rm -rf /tmp/link-copy && cp -R . /tmp/link-copy
printf '\n[gone](./does-not-exist.md)\n' >> /tmp/link-copy/README.md
if python3 /tmp/link-copy/test/validate.py; then
  echo "ERROR: validator missed a broken relative link outside a code fence"
  exit 1
else
  echo "OK: validator still catches broken links outside fences"
fi
