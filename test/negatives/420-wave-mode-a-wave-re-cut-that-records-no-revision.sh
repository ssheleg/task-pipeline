#!/usr/bin/env bash
# name: Negative self-test (wave mode — a wave re-cut that records no revision)
set -eu
rm -rf /tmp/wave-rcut && cp -R . /tmp/wave-rcut
python3 test/plant_wave.py /tmp/wave-rcut recut
if python3 /tmp/wave-rcut/test/graph_test.py; then
  echo "ERROR: a wave re-cut that records no revision was accepted — an unrecorded re-cut is the dynamic graph planning.md refuses"; exit 1
else
  echo "OK: graph_test catches a wave re-cut that records no revision"
fi
