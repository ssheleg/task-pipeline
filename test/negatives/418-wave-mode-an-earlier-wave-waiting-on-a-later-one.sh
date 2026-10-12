#!/usr/bin/env bash
# name: Negative self-test (wave mode — an earlier wave waiting on a later one)
set -eu
rm -rf /tmp/wave-ord && cp -R . /tmp/wave-ord
python3 test/plant_wave.py /tmp/wave-ord order
if python3 /tmp/wave-ord/test/graph_test.py; then
  echo "ERROR: an earlier wave waiting on a later one was accepted — a wave holds only what closes in its own pass"; exit 1
else
  echo "OK: graph_test catches an earlier wave waiting on a later one"
fi
