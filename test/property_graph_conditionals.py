#!/usr/bin/env python3
"""The shipped graph schema keeps its conditionals behind a `$ref`.

The deref branch is only exercised while the shipped schema actually uses it. If
somebody inlines the rules again the guard goes back to being untested by anything
but a fixture, which is the state B-079 was found in.

The COUNT is DERIVED, not pinned. This lived inline in the workflow asserting
`len(refs) == 3` and went red the moment a fourth conditional was added — all four
correctly behind a `$ref`. A guard whose subject is "nothing is inlined" must not
fail a schema in which nothing is inlined. It moved out of the workflow when that
file reached GitHub's 512,000-byte limit, which is the remedy the size guard names.

Standard library only.
"""
import json
import os
import sys

sys.dont_write_bytecode = True

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                      "graph.schema.json")


def main():
    with open(SCHEMA, encoding="utf-8") as fh:
        allof = json.load(fh)["definitions"]["node"]["allOf"]
    refs = [x.get("$ref") for x in allof if isinstance(x, dict) and x.get("$ref")]
    inlined = [x for x in allof if not (isinstance(x, dict) and x.get("$ref"))]
    assert not inlined, f"a conditional is inlined rather than behind a $ref: {inlined}"
    assert refs and all(r.startswith("#/definitions/") for r in refs), \
        f"the node's conditionals are not behind #/definitions/ $refs: {refs}"
    assert len(refs) == len(allof), \
        f"{len(allof) - len(refs)} of {len(allof)} conditionals are not $refs"
    print(f"OK: {len(refs)} conditionals, all behind #/definitions/ — " + ", ".join(refs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
