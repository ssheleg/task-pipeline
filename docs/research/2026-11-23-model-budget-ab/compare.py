#!/usr/bin/env python3
"""compare.py: build the blind options file and the judging brief for one spec pair.

    compare.py DIR --x before|after [OUTNAME] [AFTERFILE]

Writes DIR/compare/options.md (Option X and Option Y, no author, no model, no cost) and DIR/compare/brief.md
(the original brief plus the criteria). The arm behind each letter is recorded in DIR/compare/key.json, which
the council never reads. The two specs alternate letters across pairs against position bias.
"""
import json, pathlib, re, sys
d = pathlib.Path(sys.argv[1]); x = sys.argv[3] if len(sys.argv) > 3 else "before"
y = "after" if x == "before" else "before"
out = d / (sys.argv[4] if len(sys.argv) > 4 else "compare"); out.mkdir(exist_ok=True)
files = {"before": "before-spec.md", "after": sys.argv[5] if len(sys.argv) > 5 else "after-spec.md"}
def clean(t):
    # Strip lines that would unblind the arm: the Meanings and Author headers, a Thinker line.
    return "\n".join(l for l in t.splitlines() if not re.match(r"^\s*(Meanings|Author|Thinker|Writer)\s*:", l))
opts = (f"# Two candidate specs for the same brief\n\n## Option X\n\n{clean((d / files[x]).read_text())}\n\n"
        f"## Option Y\n\n{clean((d / files[y]).read_text())}\n")
(out / "options.md").write_text(opts)
brief = (d / "brief.md").read_text() + """

## How to judge the two candidates (Option X and Option Y)

Both were written for this brief. Pick the spec a zero-context implementer would build the RIGHT thing from with
the fewest questions and the least rework. Criteria, in order: (1) correct and complete against the brief and its
facts (nothing the owner asked is missing or contradicted); (2) buildable: exact contracts, verifiable
requirements, edge cases; (3) decisions made with reasons, no tactical question pushed to the owner; (4) no
invention beyond the brief that the facts do not support; (5) concise for what it must carry. Length is not a merit.
In `score` give each option 0-10.
"""
(out / "brief.md").write_text(brief)
(out / "key.json").write_text(json.dumps({"X": x, "Y": y, "files": {"X": files[x], "Y": files[y]}}))
print(out)
