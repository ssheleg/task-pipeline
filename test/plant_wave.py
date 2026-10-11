#!/usr/bin/env python3
"""Disarm one of wave mode's three graph mechanics, in a copy of the tree.

A plant's body lives here rather than inline in `.github/workflows/validate.yml`, which
sits close to GitHub's 512 000-byte workflow limit (see `plant_stamp_needle.py`). Each
plant writes code that still RUNS and behaves like the defect, so the suite that catches
it is watched catching behaviour, not a file that fails to load.

Usage: plant_wave.py <copy-root> <order|filter|recut>

  order   `validate` stops refusing an edge from a later wave into an earlier one
  filter  `next --wave N` stops narrowing the frontier to wave N
  recut   `wave` stops recording its move in the revision log
"""
import sys

REL = "plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"

PLANTS = {
    "order": ("wave_of[src] > wave_of[dst]:", "wave_of[src] > wave_of[dst] and False:"),
    "filter": ("    ready = [n for n in frontier(graph) if n.get(\"id\") in in_scope]",
               "    ready = frontier(graph)"),
    "recut": ("    revise(graph, \"wave\", args.node, why)\n", ""),
}


def main(argv):
    if len(argv) != 3 or argv[2] not in PLANTS:
        print("usage: plant_wave.py <copy-root> <%s>" % "|".join(PLANTS), file=sys.stderr)
        return 2
    path = "%s/%s" % (argv[1], REL)
    old, new = PLANTS[argv[2]]
    text = open(path, encoding="utf-8").read()
    assert text.count(old) == 1, "PLANT DID NOT LAND: %s — the needle moved" % argv[2]
    open(path, "w", encoding="utf-8").write(text.replace(old, new, 1))
    assert open(path, encoding="utf-8").read() != text, "PLANT DID NOT LAND"
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
