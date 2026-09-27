#!/usr/bin/env python3
"""Raise the plugin's SessionEnd timeout past what a host gives, in a copy of the tree.

Codex 0.157 clamps a SessionEnd handler's timeout to 3 s and prints `clamping SessionEnd
hook timeout to 3s in …/hooks.json` at every session start. `hooks.json` declared 10 s
through v1.87.0. This puts that exact value back so CI can watch the validator refuse it.
It lives in a file rather than inline because `.github/workflows/validate.yml` sits at
GitHub's 512 000-byte workflow limit (see `plant_stamp_needle.py`).

Usage: plant_sessionend_timeout.py <copy-root>
"""
import json
import sys

REL = "plugins/task-pipeline/hooks/hooks.json"
PLANTED = 10


def main(argv):
    if len(argv) != 2:
        print("usage: plant_sessionend_timeout.py <copy-root>", file=sys.stderr)
        return 2
    path = f"{argv[1]}/{REL}"
    data = json.load(open(path, encoding="utf-8"))
    handlers = [h for g in data["hooks"].get("SessionEnd") or [] for h in g.get("hooks") or []]
    assert handlers, "PLANT DID NOT LAND: hooks.json declares no SessionEnd handler"
    for h in handlers:
        h["timeout"] = PLANTED
    json.dump(data, open(path, "w", encoding="utf-8"), indent=2)
    after = json.load(open(path, encoding="utf-8"))["hooks"]["SessionEnd"]
    assert all(h.get("timeout") == PLANTED for g in after for h in g["hooks"]), \
        "PLANT DID NOT LAND"
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
