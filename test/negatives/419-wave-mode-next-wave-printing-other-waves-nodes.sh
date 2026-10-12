#!/usr/bin/env bash
# name: Negative self-test (wave mode — next --wave printing other waves' nodes)
set -eu
rm -rf /tmp/wave-flt && cp -R . /tmp/wave-flt
python3 test/plant_wave.py /tmp/wave-flt filter
if python3 /tmp/wave-flt/test/graph_test.py; then
  echo "ERROR: next --wave printing other waves' nodes was accepted — the frontier of one wave is what the wave loop walks"; exit 1
else
  echo "OK: graph_test catches next --wave printing other waves' nodes"
fi
