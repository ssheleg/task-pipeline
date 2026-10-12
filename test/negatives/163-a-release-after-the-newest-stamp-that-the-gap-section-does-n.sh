#!/usr/bin/env bash
# name: Negative self-test (a release after the newest stamp that the gap section does not name)
set -eu
rm -rf /tmp/gap1-copy && cp -R . /tmp/gap1-copy
# dormant-when: `git tag -l` returns nothing inside the copy, exactly as for
#   the sibling plant above and with the same measured correction: the local
#   runner repairs `.git` and CI fetches tags, so neither path reaches this
#   branch. Cost: the two go dormant together, so wherever it does fire the
#   whole release-gap check is unprobed rather than half of it.
set +e
python3 - <<'EOF'
# Fourteen consecutive releases carried no run stamp while the honest-gap section
# still named only v1.16.0-v1.23.0, and the cold-retirement trigger — which reads
# the last five stamps — had nothing to read across the whole stretch. Nothing
# failed, because nothing compared the tag list against the stamps. Narrowing the
# declared range must reopen the finding.
# The range moves on EVERY release that ships without a run stamp, so the plant
# reads its shape rather than its value. Pinned to the literal
# "`v1.60.1` through `v1.72.0`" it stopped landing the moment v1.73.0 extended the
# stretch — and a plant that does not land is a check nobody ran, reported green.
import re
p = "/tmp/gap1-copy/docs/evidence/retro.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"`(v[0-9.]+)` through `(v[0-9.]+)`", t)
assert m, "PLANT DID NOT LAND: no declared gap range of the form `vA` through `vB`"
hi = m.group(2)
# narrow the declared range: the releases above the new upper bound become
# unstamped AND unnamed, which is the finding this guard exists for.
# Narrow to a single release: every release after the lower bound is then
# unstamped AND unnamed, which is unambiguously the finding. Computing a
# "middle" version was arithmetic on a string and produced a version nobody
# ever tagged, which the guard had no reason to complain about.
t = t.replace(hi, m.group(1))
# AND remove the newest run stamp, because the guard reads releases AFTER it.
# Narrowing the range alone stopped exercising anything the moment a release
# shipped with a stamp of its own: v1.74.0 was both the newest release and the
# newest stamp, so nothing was "after" it and the plant landed while proving
# nothing. A plant has to create its own precondition, not inherit one from
# whatever the tree happens to look like on the day it runs.
import re as _re
import subprocess as _sp0
rows = [mm for mm in _re.finditer(r"(?m)^\|\s*\d{4}-\d{2}-\d{2}\s*\|.*$", t)]
assert rows, "PLANT DID NOT LAND: no run stamp rows to remove"
# Remove newest rows until one of them covered the newest tag — removing
# exactly one stopped constructing the refusal state the day TWO stamps
# sat above the newest tag's range (the 2026-08-31 stamp cites the
# main-tip commit, which no tag contains, so deleting it alone left the
# previous stamp still covering v-newest and nothing trailed).
_tags0 = _sp0.run(["git", "tag", "-l", "v*", "--sort=v:refname"],
                  cwd="/tmp/gap1-copy", capture_output=True, text=True).stdout.split()
_cover = set()
if len(_tags0) >= 2:
    _cover = {c[:7] for c in _sp0.run(
        ["git", "rev-list", f"{_tags0[-2]}..{_tags0[-1]}"],
        cwd="/tmp/gap1-copy", capture_output=True, text=True).stdout.split()}
newest = rows[0]
removed_any = False
for mm in rows:
    _sha = _re.search(r"`([0-9a-f]{7,40})`", mm.group(0))
    # keep removing while the newest tag's range still holds a live stamp:
    # stopping after the FIRST covering row left a second one (two stamps sat
    # inside v-newest's range on 2026-08-31) and nothing trailed.
    _rest_covered = any(
        (_s := _re.search(r"`([0-9a-f]{7,40})`", m2.group(0))) and _s.group(1)[:7] in _cover
        for m2 in rows if m2.group(0) != mm.group(0) and m2.group(0) in t)
    t = t.replace(mm.group(0) + "\n", "", 1)
    removed_any = True
    if not _rest_covered:
        break
assert removed_any and not any(
    (_s := _re.search(r"`([0-9a-f]{7,40})`", m2.group(0))) and _s.group(1)[:7] in _cover
    for m2 in rows if m2.group(0) in t), \
    "PLANT DID NOT LAND: a live stamp still covers the newest tag"
# AND strip every mention of a trailing tag from the gap section itself.
# Narrowing a range and dropping a stamp was not enough: the guard counts ANY
# `vX.Y.Z` token in that section as a declaration, so one sentence mentioning a
# tag in passing silenced the check for that release and the plant read as
# accepted. A plant creates its own precondition -- here, a section that names
# none of the releases the guard is about to ask about.
import subprocess as _sp, sys as _sys
_tags = _sp.run(["git", "tag", "-l", "v*", "--sort=v:refname"],
                cwd="/tmp/gap1-copy", capture_output=True, text=True).stdout.split()
if not _tags:
    # No tags are visible in the copy, which happens in a SUBMODULE checkout:
    # `.git` is a file holding a relative gitdir pointer and breaks under /tmp.
    # The guard itself declines to look in that state and says so via `unlooked`
    # -- so there is nothing here to probe, and reporting the guard as broken
    # would be this plant asserting about a check that never ran. CI clones
    # standalone and does exercise it.
    print("SKIP: no v* tags visible in the copy, so the release-gap check "
          "cannot look and cannot be probed (submodule checkout)")
    _sys.exit(9)
_GAP = "## Releases that carry no stamp"
_i = t.index(_GAP)
_e = t.find("\n## ", _i + 5)
_sec = t[_i:_e] if _e > 0 else t[_i:]
_stripped = _sec
for _tg in _tags[-6:]:                      # the only ones that can be trailing
    _stripped = _stripped.replace("`%s`" % _tg, "`vREDACTED`").replace(_tg, "vREDACTED")
assert _stripped != _sec, "PLANT DID NOT LAND: the gap section named no recent tag"
t = t[:_i] + _stripped + (t[_e:] if _e > 0 else "")
open(p, "w", encoding="utf-8").write(t)
after = open(p, encoding="utf-8").read()
assert hi not in after, "PLANT DID NOT LAND: the range did not narrow"
assert newest.group(0) not in after, "PLANT DID NOT LAND: the newest stamp is still there"
EOF
EOF_RC=$?
if [ "$EOF_RC" = "9" ]; then
  exit 0
elif [ "$EOF_RC" != "0" ]; then
  echo "PLANT FAILED TO RUN (exit $EOF_RC)"; exit 1
fi
if python3 /tmp/gap1-copy/test/validate.py; then
  echo "ERROR: validator passed unstamped releases named nowhere in the gap section"
  exit 1
else
  echo "OK: validator correctly FAILs — a release either carries a stamp or is recorded as a gap"
fi
