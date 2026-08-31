#!/usr/bin/env python3
r"""anchors_test.py — the anchor census, watched failing before it is trusted.

`test/anchors.py` refuses a negative self-test whose needle pins a value a release
can move (board row **B-113**). A detector nobody has watched fire is exactly the
thing this repository refuses to ship — and the first draft of that detector
produced four false positives that only a fixture could show: a regex quantifier
read as a year, a `→` escape read as one, a payload built out of local strings,
and a `validate.py | grep 'message'` read as a needle instead of as assertion 3.

Each case below is a whole miniature workflow. They are fixtures rather than prose
because the module reads YAML step bodies, and a rule stated in a comment is a rule
nobody runs — `references/probing.md` in this bundle, and three of `project-audit`'s
own traps, were written the same way for the same reason.
"""
from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anchors                                                       # noqa: E402

CASES: list[tuple[str, str, bool]] = []


def case(name: str, body: str, must_fail: bool, step: str = "a plant") -> None:
    """`must_fail` — does the census have to report this workflow?"""
    indented = "\n".join("          " + l if l.strip() else "" for l in body.splitlines())
    CASES.append((name, f"""jobs:
  validate:
    steps:
      - name: Negative self-test ({step})
        run: |
{indented}
""", must_fail))


# -- the class the row is about ------------------------------------------------
case("a needle pinning a two-digit count is refused", '''
set -eu
rm -rf /tmp/fx-copy && cp -R . /tmp/fx-copy
python3 - <<'EOF'
p = "/tmp/fx-copy/README.md"
t = open(p, encoding="utf-8").read()
n = "The suite carries 46 guards"
assert n in t, "PLANT DID NOT LAND"
open(p, "w", encoding="utf-8").write(t.replace(n, "changed", 1))
EOF
''', True)

case("a needle pinning a version tag is refused", '''
set -eu
python3 - <<'EOF'
t = open("/tmp/fx-copy/CHANGELOG.md", encoding="utf-8").read()
assert "released in v1.72.0" in t
EOF
''', True)

case("a needle pinning a bare number in a table cell is refused", '''
set -eu
python3 - <<'EOF'
t = open("/tmp/fx-copy/docs/evidence/backlog.md", encoding="utf-8").read()
assert "| 3 | open" in t
EOF
''', True)

case("a needle pinning a board id is refused", '''
set -eu
python3 - <<'EOF'
t = open("/tmp/fx-copy/docs/evidence/backlog.md", encoding="utf-8").read()
open("/tmp/fx-copy/docs/evidence/backlog.md", "w", encoding="utf-8").write(
    t.replace("| B-008 |", "| B-008 | broken |", 1))
EOF
''', True)

case("a grep over a FILE pinning a count is refused", '''
set -eu
grep -q "the 250 guards" /tmp/fx-copy/README.md
''', True)

# -- the four false positives the fixtures found -------------------------------
case("a regex quantifier is shape, not a year", '''
set -eu
python3 - <<'EOF'
import re
t = open("/tmp/fx-copy/docs/evidence/retro.md", encoding="utf-8").read()
m = re.search(r"`([0-9a-f]{7,40})`", t)
assert m, "PLANT DID NOT LAND"
EOF
''', False)

case("a \\uXXXX escape in a raw pattern is not a number", '''
set -eu
python3 - <<'EOF'
import re
t = open("/tmp/fx-copy/CHANGELOG.md", encoding="utf-8").read()
m = re.search(r"Guards:\\s*\\d+\\s*(?:\\u2192|->)\\s*\\d+", t)
assert m, "PLANT DID NOT LAND"
EOF
''', False)

case("a payload built out of local strings reads nothing off disk", '''
set -eu
python3 - <<'EOF'
verb = 'print(f"tally: {len(graph.get(chr(34)nodes(chr(34)) or [])}")'
verb = verb.replace('chr(34)', '"')
t = open("/tmp/fx-copy/scripts/graph.py", encoding="utf-8").read()
open("/tmp/fx-copy/scripts/graph.py", "w", encoding="utf-8").write(verb + t)
EOF
''', False)

case("a grep on the validator's own output is assertion 3, not a needle", '''
set -eu
if python3 /tmp/fx-copy/test/validate.py 2>&1 | grep -q 'locked by the 2026-08-03 design'; then
  echo "OK"
fi
''', False)

# -- the row's own question, answered per occurrence ---------------------------
case("a value the plant writes and reads back is its own", '''
set -eu
python3 - <<'EOF'
p = "/tmp/fx-copy/README.md"
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(t.replace("## Contributing",
    "The suite carries 46 guards.\\n\\n## Contributing", 1))
assert "46 guards" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
''', False)

case("a post-write assertion confirms a landing, it does not pin an anchor", '''
set -eu
python3 - <<'EOF'
import re
p = "/tmp/fx-copy/docs/evidence/backlog.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"^\\| B-\\d+ \\|", t, re.M)
assert m, "PLANT DID NOT LAND"
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), "| B-777 |", 1))
assert "| B-777 |" in open(p, encoding="utf-8").read(), "PLANT DID NOT LAND"
EOF
''', False)

case("a needle pinning a cap is refused even where the plant writes that cap too", '''
set -eu
python3 - <<'EOF'
p = "/tmp/fx-copy/references/retrospective.md"
t = open(p, encoding="utf-8").read()
n = "**Standing** (max **10**) and **Stamps** (max **10**)"
assert n in t, "PLANT DID NOT LAND"
open(p, "w", encoding="utf-8").write(t.replace(n, "**Stamps** (max **10**)", 1))
EOF
''', True)

case("a derived needle passes", '''
set -eu
python3 - <<'EOF'
import re
p = "/tmp/fx-copy/references/learned.md"
t = open(p, encoding="utf-8").read()
m = re.search(r"\\*\\*Numbers issued so far: \\d+\\.\\*\\*", t)
assert m, "PLANT DID NOT LAND"
open(p, "w", encoding="utf-8").write(t.replace(m.group(0), "**A note.**", 1))
EOF
''', False)

# -- the escape hatch, and both ways it is refused -----------------------------
case("a declared anchor is accepted", '''
set -eu
python3 - <<'EOF'
# anchor: 2026-08-11 — the containers measurement is frozen and deriving the date
#   would make the plant agree with whatever the file says, which is the defect it
#   exists to catch. Falsified if the measurement is ever re-taken and re-dated.
t = open("/tmp/fx-copy/references/residue.md", encoding="utf-8").read()
assert "Measured 2026-08-11, enumerating" in t, "PLANT DID NOT LAND"
EOF
''', False)

case("a declaration naming nothing this plant looks for is refused", '''
set -eu
python3 - <<'EOF'
# anchor: 1999 — a value this plant never reads, so the declaration explains
#   nothing and silences a needle it does not name.
t = open("/tmp/fx-copy/references/residue.md", encoding="utf-8").read()
assert "Measured 2026-08-11, enumerating" in t, "PLANT DID NOT LAND"
EOF
''', True)

case("a declaration with no reason is refused", '''
set -eu
python3 - <<'EOF'
# anchor: 2026-08-11 — frozen
t = open("/tmp/fx-copy/references/residue.md", encoding="utf-8").read()
assert "Measured 2026-08-11, enumerating" in t, "PLANT DID NOT LAND"
EOF
''', True)


# -- the shapes the R-005 independent reader found the first draft blind to ------
# Each was a needle pinning a moving value that the census reported as clean, and two
# of them were shipping in this repository at the time: `wv1`/`wv2` pinned to `B-005`
# behind `enumerate()`, and `br2` behind `re.compile`.
case("provenance survives enumerate() — the blind spot two live plants sat behind", '''
set -eu
python3 - <<'EOF'
import re
lines = open("/tmp/fx-copy/templates/backlog.md", encoding="utf-8").read().split("\\n")
for n, ln in enumerate(lines):
    if re.match(r"^\\|\\s*B-005\\s*\\|", ln):
        lines[n] = "broken"
open("/tmp/fx-copy/templates/backlog.md", "w", encoding="utf-8").write("\\n".join(lines))
EOF
''', True)

case("provenance survives sorted() and list()", '''
set -eu
python3 - <<'EOF'
t = open("/tmp/fx-copy/README.md", encoding="utf-8").read()
for ln in sorted(list(t.splitlines())):
    if "the 250 guards" in ln:
        print(ln)
EOF
''', True)

case("pathlib.Path(p).read_text() is a file read", '''
set -eu
python3 - <<'EOF'
import pathlib
p = pathlib.Path("/tmp/fx-copy/hooks/release-gate.sh")
s = p.read_text()
needle = "released in v1.72.0"
assert needle in s, "PLANT NO-OP"
p.write_text(s.replace(needle, "x", 1))
EOF
''', True)

case("a with-statement handle is a file read", '''
set -eu
python3 - <<'EOF'
with open("/tmp/fx-copy/README.md", encoding="utf-8") as fh:
    t = fh.read()
assert "The suite carries 46 guards" in t, "PLANT NO-OP"
EOF
''', True)

case("a compiled pattern carries its needle", '''
set -eu
python3 - <<'EOF'
import re
rx = re.compile(r"^\\|\\s*12\\s*\\|")
t = open("/tmp/fx-copy/references/learned.md", encoding="utf-8").read()
assert rx.search(t), "PLANT NO-OP"
EOF
''', True)

case("json.load(open(p)) carries the file into a structured look", '''
set -eu
python3 - <<'EOF'
import json
d = json.load(open("/tmp/fx-copy/pipeline.example.json"))
assert d.get("engines 18 and up") is None
EOF
''', True)

case("a grep needle without quotes is still a needle", '''
set -eu
grep -q the.250.guards /tmp/fx-copy/README.md
''', True)

case("a sed address is a needle", '''
set -eu
sed -n '/the 250 guards/p' /tmp/fx-copy/README.md
''', True)

case("a grep on a line naming validate.py AFTER it is still a needle", '''
set -eu
grep -q "the 250 guards" /tmp/fx-copy/README.md   # nothing to do with validate.py
''', True)

case("a subprocess grep is a needle", '''
set -eu
python3 - <<'EOF'
import subprocess
subprocess.run(["grep", "-c", "the 250 guards", "/tmp/fx-copy/README.md"])
EOF
''', True)

case("a write through a computed path still exempts its own read-back", '''
set -eu
python3 - <<'EOF'
d = "/tmp/fx-copy"
p = d + "/README.md"
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(t.replace("## Contributing",
    "The suite carries 46 guards.\\n\\n## Contributing", 1))
assert "46 guards" in open(p, encoding="utf-8").read(), "PLANT NO-OP"
EOF
''', False)

case("a Path().write_text() is a write, so its read-back is not an anchor", '''
set -eu
python3 - <<'EOF'
import pathlib
p = pathlib.Path("/tmp/fx-copy/README.md")
p.write_text(p.read_text() + "\\nThe suite carries 46 guards.\\n")
assert "46 guards" in p.read_text(), "PLANT NO-OP"
EOF
''', False)

case("a heredoc this census cannot recognise is counted, not read as clean", '''
set -eu
python3 <<'EOF'
t = open("/tmp/fx-copy/README.md", encoding="utf-8").read()
assert "The suite carries 46 guards" in t, "PLANT NO-OP"
EOF
''', True)

case("a heredoc quoted inside a PAYLOAD is not a heredoc this plant opens", '''
set -eu
python3 - <<'EOF'
step = (
    "        run: |\\n"
    "          python3 - <<'XEOF'\\n"
    "          print(1)\\n"
    "          XEOF\\n")
open("/tmp/fx-copy/.github/workflows/validate.yml", "a", encoding="utf-8").write(step)
EOF
''', False)

case("`SKIP:` inside a comment does not make a plant dormant-capable", '''
set -eu
# this plant prints no SKIP: of its own — the marker is discussed, not reachable
python3 - <<'EOF'
t = open("/tmp/fx-copy/README.md", encoding="utf-8").read()
assert "anything at all" in t, "PLANT NO-OP"
EOF
''', False)

case("a declaration whose reason wraps over continuation lines is accepted", '''
set -eu
python3 - <<'EOF'
# anchor: 2026-08-11
#   the containers measurement is frozen, and deriving the date would make this
#   plant agree with whatever the file happens to say, which is the defect it
#   exists to catch. Falsified if the measurement is re-taken and re-dated.
t = open("/tmp/fx-copy/references/residue.md", encoding="utf-8").read()
assert "Measured 2026-08-11, enumerating" in t, "PLANT NO-OP"
EOF
''', False)

case("a declaration padded to length with filler is refused", '''
set -eu
python3 - <<'EOF'
# anchor: 2026-08-11 — .....................................................................
t = open("/tmp/fx-copy/references/residue.md", encoding="utf-8").read()
assert "Measured 2026-08-11, enumerating" in t, "PLANT NO-OP"
EOF
''', True)


# -- round two of the same reader: four more blocking shapes ---------------------
case("json.dump(d, open(p, 'w')) is a write, so the read-back after it is not an anchor", '''
set -eu
python3 - <<'EOF'
import json
p = "/tmp/fx-copy/pipeline.example.json"
d = json.load(open(p))
d["stages"][0]["model"] = "some-vendor-model"
json.dump(d, open(p, "w"), indent=2)
assert json.load(open(p))["stages"][0].get("model") == "some-vendor-model 18"
EOF
''', False)

case("a comprehension variable's provenance dies with the comprehension", '''
set -eu
python3 - <<'EOF'
t = open("/tmp/fx-copy/README.md", encoding="utf-8").read()
rows = [ln for ln in t.splitlines() if ln.startswith("|")]
ln = "a local string that has nothing to do with the file"
assert "release 1.72.0" not in ln
EOF
''', False)

case("a name rebound to a local string loses its provenance", '''
set -eu
python3 - <<'EOF'
t = open("/tmp/fx-copy/README.md", encoding="utf-8").read()
for ln in t.splitlines():
    pass
ln = "a local string reassigned after the loop"
assert "release 1.72.0" not in ln
EOF
''', False)

case("a comprehension RESULT carries the file onward", '''
set -eu
python3 - <<'EOF'
files = ["/tmp/fx-copy/README.md"]
texts = {f: open(f, encoding="utf-8").read() for f in files}
for f, body in texts.items():
    assert "the 250 guards" in body, "PLANT NO-OP"
EOF
''', True)

case("a heredoc opened after an env assignment is counted", '''
set -eu
HOOK_INPUT=x python3 - <<EOF
t = open("/tmp/fx-copy/README.md", encoding="utf-8").read()
assert "the 250 guards" in t
EOF
''', True)

case("a heredoc opened after a pipe is counted", '''
set -eu
echo hi | python3 <<'EOF'
t = open("/tmp/fx-copy/README.md", encoding="utf-8").read()
assert "the 250 guards" in t
EOF
''', True)

case("a `|`-delimited sed address is a needle", '''
set -eu
sed -n '|the 250 guards|p' /tmp/fx-copy/README.md
''', True)

case("an unquoted grep takes the pattern, never the path", '''
set -eu
grep -q needle /tmp/fx-copy/docs/2026-08-08-audit-followup-carryover.md
''', False)

case("a one-line declaration is judged on its own length, not on twice it", '''
set -eu
python3 - <<'EOF'
# anchor: 2026-08-11 — frozen by design, and re-deriving it would be wrong here
t = open("/tmp/fx-copy/references/residue.md", encoding="utf-8").read()
assert "Measured 2026-08-11, enumerating" in t, "PLANT NO-OP"
EOF
''', True)


# -- round three: scoping a `for` target killed provenance Python itself keeps ----
case("a name assigned INSIDE a for-body keeps its provenance after the loop", '''
set -eu
python3 - <<'EOF'
import glob
t = ""
for f in glob.glob("/tmp/fx-copy/*.md"):
    t = open(f, encoding="utf-8").read()
assert "the 250 guards" in t, "PLANT NO-OP"
EOF
''', True)

case("a for target is still bound after the loop, as in real Python", '''
set -eu
python3 - <<'EOF'
t = open("/tmp/fx-copy/README.md", encoding="utf-8").read()
for l in t.splitlines():
    break
assert "the 250 guards" in l, "PLANT NO-OP"
EOF
''', True)

case("a heredoc named after another command on the line is not python3's own", '''
set -eu
if python3 /tmp/fx-copy/test/validate.py; then cat <<EOT > /tmp/out
nothing to see
EOT
fi
''', False)


def _run() -> int:
    bad = 0
    for name, doc, must_fail in CASES:
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False,
                                         encoding="utf-8") as fh:
            fh.write(doc)
            path = fh.name
        try:
            found = anchors.findings(path)
        finally:
            os.unlink(path)
        ok = bool(found) == must_fail
        print(f"  {'PASS' if ok else 'FAIL':<6}{name}")
        if not ok:
            bad += 1
            print(f"      wanted {'a finding' if must_fail else 'silence'}, got "
                  f"{len(found)} finding(s)")
            for f in found[:2]:
                print("      " + f[:150])

    # The empty corpus, which passes every rule above by having nothing to break.
    # `negatives.py` learned this at the suite level — *all 0 guards provably reject*
    # is a pass over an empty set — and a census with no plants must not read as one.
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False,
                                     encoding="utf-8") as fh:
        fh.write("jobs:\n  validate:\n    steps:\n      - name: Lint\n        run: |\n"
                 "          echo hi\n")
        path = fh.name
    try:
        empty = anchors.census(path)
    finally:
        os.unlink(path)
    ok = empty == []
    print(f"  {'PASS' if ok else 'FAIL':<6}an empty corpus yields an empty census, "
          "which the caller must refuse rather than read as clean")
    bad += 0 if ok else 1

    # And the caller does refuse it: the live wiring in `test/validate.py` fails when
    # the census is empty, so the two halves cannot drift apart silently.
    src = open(os.path.join(anchors.ROOT, "test", "validate.py"), encoding="utf-8").read()
    ok = "the anchor census found no negative self-tests" in src
    print(f"  {'PASS' if ok else 'FAIL':<6}the validator refuses an empty census by name")
    bad += 0 if ok else 1

    print()
    if bad:
        print(f"FAIL: {bad} of {len(CASES) + 2} anchor-census cases behaved wrongly")
        return 1
    print(f"PASS: anchors.py — {len(CASES) + 2} cases, "
          f"{sum(1 for _n, _d, m in CASES if m)} of them watched firing")
    return 0


if __name__ == "__main__":
    sys.exit(_run())
