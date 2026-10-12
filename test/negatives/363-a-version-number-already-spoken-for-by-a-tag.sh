#!/usr/bin/env bash
# name: Negative self-test (a version number already spoken for by a tag)
set -eu
# dormant-when: the checkout is shallow, so ancestry is unknowable and a
#   second lineage cannot be staged for the version to collide with. Cost: on
#   a `fetch-depth: 1` runner the collision check is unprobed, and the plant
#   says so rather than letting an environment answer for the guard.
rm -rf /tmp/vt1-copy && cp -R . /tmp/vt1-copy
cd /tmp/vt1-copy
# A collision is DIVERGENCE. Every tag in this repo is an ancestor of main,
# and carrying a released version forward is legitimate — so a real collision
# has to be built: a commit with no parent, tagged, and then claimed.
# Identity inline: a CI runner has none configured and commit-tree exits 128.
# Green locally, red in CI — the environment dependence B-066 is about, mine.
SIDE=$(git -c user.email=t@t -c user.name=t commit-tree \
         "$(git hash-object -t tree /dev/null)" -m "another lineage")
# -f, because a copy of a git WORKTREE carries .git as a pointer and this
# tag lands in the real repository. Verified once, the hard way.
git tag -f v99.99.99 "$SIDE" >/dev/null
python3 - <<'EOF'
import json, re
for f, fn in (("package.json", lambda d: d.__setitem__("version", "99.99.99")),
              (".claude-plugin/marketplace.json", lambda d: d["plugins"][0].__setitem__("version", "99.99.99")),
              ("plugins/task-pipeline/.claude-plugin/plugin.json", lambda d: d.__setitem__("version", "99.99.99"))):
    d = json.load(open(f, encoding="utf-8")); fn(d)
    json.dump(d, open(f, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(f, "a", encoding="utf-8").write("\n")
for f, pat, rep in (("SKILL-CARD.md", r"(\| \*\*Version\*\* \| )[\d.]+", r"\g<1>99.99.99"),
                    ("CHANGELOG.md", r"^## v[\d.]+", "## v99.99.99")):
    t = open(f, encoding="utf-8").read()
    _p = re.sub(pat, rep, t, count=1, flags=re.M)
    assert _p != t, "PLANT DID NOT LAND: vt1 " + f
    open(f, "w", encoding="utf-8").write(_p)
EOF
cd - >/dev/null
_out=$(python3 /tmp/vt1-copy/test/validate.py 2>&1 || true)
if printf '%s' "$_out" | grep -q "is spoken"; then
  echo "OK: validator FAILs — the number is taken by another lineage, and the merge is not the place to find out"
elif printf '%s' "$_out" | grep -q "shallow clone, ancestry unknowable"; then
  echo "SKIP: shallow checkout — ancestry cannot be answered, so the collision cannot be staged"
else
  echo "ERROR: a branch may claim a version another lineage already ships under"
  exit 1
fi
