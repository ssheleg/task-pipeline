#!/usr/bin/env python3
"""Remove one named string from the release-stamp rule, in a copy of the tree.

Five near-identical CI steps carried this inline and pushed `.github/workflows/validate.yml`
from 508 189 to 518 928 bytes — **past GitHub's 512 000-byte workflow limit**, after which
the workflow is still reported `active` and simply never runs. `gh pr checks` says *no
checks reported*, which reads like a queue delay rather than a refusal, so the ceiling is
silent in both directions. The plant mechanism this repository relies on has a budget, and
inline plants spend it fastest.

Usage: plant_stamp_needle.py <copy-root> <needle>

Removes EVERY occurrence inside the section, never the first: a plant that leaves a second
copy behind reports its guard inert when it is not, which happened twice while these were
being written. Scoped to the section for the mirror reason — searching the whole file let
`git merge-base --is-ancestor` be answered by a different section entirely.
"""
import re
import sys

REL = "plugins/task-pipeline/skills/task-pipeline/references/retrospective.md"
SECTION = r"^## A release stamp names the TAG.*?(?=^## |\Z)"


def main(argv):
    if len(argv) != 3:
        print("usage: plant_stamp_needle.py <copy-root> <needle>", file=sys.stderr)
        return 2
    root, needle = argv[1], argv[2]
    path = f"{root}/{REL}"
    text = open(path, encoding="utf-8").read()
    match = re.search(SECTION, text, re.M | re.S)
    assert match, "PLANT DID NOT LAND: the release-stamp section is gone"
    assert needle in match.group(0), f"PLANT DID NOT LAND: the section does not name {needle!r}"
    open(path, "w", encoding="utf-8").write(
        text[: match.start()] + match.group(0).replace(needle, "XXX") + text[match.end():]
    )
    after = re.search(SECTION, open(path, encoding="utf-8").read(), re.M | re.S)
    assert after and needle not in after.group(0), "PLANT DID NOT LAND"
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
