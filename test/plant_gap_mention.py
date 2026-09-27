#!/usr/bin/env python3
"""Turn the release-gap section's declarations into mere MENTIONS, in a copy of the tree.

Moved out of `.github/workflows/validate.yml` verbatim, because the workflow sits at
GitHub's 512 000-byte limit (see `plant_stamp_needle.py`) and this was its largest inline
plant, at 7.9 kB.

Usage: plant_gap_mention.py <copy-root>
Exit 9 means no `v*` tags are visible in the copy, so the guard cannot be probed; the
step treats that as a skip, as it did inline.
"""
# The hole this closes, measured 2026-08-24: the check read every `vX.Y.Z` token in
# the gap section, so one sentence mentioning a tag in passing declared it unstamped
# and exempted it. Here the trailing releases stay in the section, in the same
# words, with only their BOLD removed -- mentions instead of declarations. A guard
# that cannot tell the two apart accepts this, which is what it did.
#
# THE PLANT CREATES ITS OWN PRECONDITION, learned 2026-08-30 on the v1.79.0
# release: the guard checks only releases AFTER the newest run stamp, so the first
# release that actually carried a stamp emptied the trailing set and this plant's
# mutation became invisible -- a probe that no longer probed, reported green
# locally and caught only by the release job, whose tree is the first place the
# new tag and the new stamp coexist. So the plant now un-stamps every release
# newer than the newest DECLARED tag (removing those stamp rows from the copy),
# writes each such tag into the section's prose UNBOLDED, and then un-bolds every
# declaration. A guard that reads bold only must fail; one that reads mentions is
# satisfied -- exactly the defect this plant exists to keep dead.
import glob, re, subprocess, sys
base = sys.argv[1]
p = base + "/docs/evidence/retro.md"
tags = subprocess.run(["git", "tag", "-l", "v*", "--sort=v:refname"],
                      cwd=base, capture_output=True, text=True).stdout.split()
if not tags:
    print("SKIP: no v* tags visible in the copy, so the release-gap check cannot "
          "look and cannot be probed (submodule checkout)")
    sys.exit(9)
files = [p] + sorted(glob.glob(base + "/docs/evidence/retro/*.md"))
texts = {f: open(f, encoding="utf-8").read() for f in files}
GAP = "## Releases that carry no stamp"
STAMP_ROW = r"^\s*\|\s*\d{4}-\d\d-\d\d\s*\|[^|]*\|\s*`([0-9a-f]{7,40})`"

# THE PLANT MANUFACTURES THE GUARD'S OWN REFUSAL STATE, not a proxy for it.
# Draft two derived "the releases to un-stamp" from "the newest tag named in a
# bold span" -- and died one tree later, when the dead-tag declaration for
# v1.79.0 truthfully said, inside its bold span, that v1.79.1 carries the
# stamp: "named in bold" is not what the guard means by declared. So the
# trailing set is computed exactly the way the guard computes it -- walking
# tag ranges against the stamp-row commits -- and when it is empty, the
# newest stamped release is un-stamped to re-create it.
def stamp_shas():
    return [(f, s) for f, body in texts.items()
            for s in re.findall(STAMP_ROW, body, re.M)]

def walk(shas):
    """(trailing tags, shas that covered the newest stamped tag)."""
    prev, trailing, last_cover = None, [], set()
    short = {s[:7] for _, s in shas}
    for tg in tags:
        rng = "%s..%s" % (prev, tg) if prev else tg
        shipped = {c[:7] for c in subprocess.run(
            ["git", "rev-list", rng], cwd=base,
            capture_output=True, text=True).stdout.split()}
        cover = short & shipped
        if cover:
            trailing, last_cover = [], cover
        else:
            trailing.append(tg)
        prev = tg
    return trailing, last_cover

trailing, last_cover = walk(stamp_shas())
if not trailing:
    # the healthy state: the newest release is stamped. Un-stamp it, so the
    # guard has something it must refuse.
    assert last_cover, "PLANT DID NOT LAND: no stamps at all, yet nothing trails"
    for f, s in stamp_shas():
        if s[:7] in last_cover:
            # the STAMP row shape, never "any line naming the sha": the
            # standing instructions stamp the same commit in their `Fired at`
            # cell, and a first-line removal deleted one of those instead.
            row = re.search(STAMP_ROW.replace("([0-9a-f]{7,40})", s) + r".*$\n?",
                            texts[f], re.M)
            assert row, "PLANT DID NOT LAND: stamp row for %s not found" % s
            texts[f] = texts[f][:row.start()] + texts[f][row.end():]
    trailing, _ = walk(stamp_shas())
    assert trailing, "PLANT DID NOT LAND: un-stamping freed no release"
t = texts[p]
i = t.index(GAP)
e = t.find("\n## ", i + 5)
sec = t[i:e] if e > 0 else t[i:]
# every trailing release must be MENTIONED -- that is the state under test:
# named in the section, not bold-declared. Ranges in prose count as names.
known = set(re.findall(r"v\d+\.\d+\.\d+", sec))
for a, b in re.findall(r"`?(v\d+\.\d+\.\d+)`?\s*(?:through|to|–|-|\.\.)\s*`?(v\d+\.\d+\.\d+)`?", sec):
    if a in tags and b in tags and tags.index(a) <= tags.index(b):
        known |= set(tags[tags.index(a):tags.index(b) + 1])
absent = [g for g in trailing if g not in known]
if absent:
    sec = sec.rstrip("\n") + ("\n\nProbe prose, not a declaration: the figures "
          "were already stale at the %s tag.\n"
          % " and ".join("`%s`" % g for g in absent))
# un-bold every span that names a version: same words, same place, no longer a
# declaration.
def unbold(m):
    return m.group(1) if re.search(r"v\d+\.\d+\.\d+", m.group(1)) else m.group(0)
out = re.sub(r"\*\*(.+?)\*\*", unbold, sec, flags=re.S)
assert out != sec or absent, \
    "PLANT DID NOT LAND: nothing was unbolded and nothing needed mentioning"
assert re.search(r"v\d+\.\d+\.\d+", out), "PLANT DID NOT LAND: the versions vanished too"
texts[p] = t[:i] + out + (t[e:] if e > 0 else "")
for f, body in texts.items():
    open(f, "w", encoding="utf-8").write(body)
