#!/usr/bin/env bash
# name: Property check (the shipped graph schema keeps its conditionals behind a `$ref`)
# Block scalar on purpose: negatives.py reads steps by `run: |`.
python3 test/property_graph_conditionals.py
