#!/usr/bin/env python3
"""Neuter each rule of the certification gate and require its own fixture to notice.

`graph_test.py` proves the gate refuses what it should. This proves the fixtures are
not decorations: every rule in `cmd_certify` and `tier_violations` is disabled in a
copy of the tree, one at a time, and a mutant is **killed** only when a fixture whose
name begins `certify:` goes red. That last clause is the whole point and it was
learned the hard way — the first run of this pass reported 11 of 11 killed, and every
mutant had died of the same unrelated fixture, because the copy has no `.git` and one
pre-existing case checks the commit stamp.

Two disclosures make the result readable rather than reassuring:

  * **the control** runs unmutated first and requires exactly the expected number of
    `certify:` fixtures to have RUN and none to be red. A copy where they never
    execute reports every mutation as survived, which is the true answer to a
    question nobody asked. The same run also caught the fixtures sitting BELOW
    `graph_test.py`'s `sys.exit`, so any earlier failure skipped all twenty.
  * **`NOT PLANTED`** where a mutation's anchor is no longer in the source. A
    mutation pinned to a literal stops landing the moment the line is reworded, and
    a pass that silently skips it reports a rule as covered.

    python3 test/certify_mutations.py           # every rule
    python3 test/certify_mutations.py -k blind  # rules whose name matches

Exit 0 = every planted mutation was noticed by a `certify:` fixture.
Zero dependencies, same as the rest of the suite.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
GRAPH_REL = "plugins/task-pipeline/skills/task-pipeline/scripts/graph.py"
EXPECTED_FIXTURES = 23

# (name, the source to disable, what to replace it with). Each disables exactly one
# rule; the fixture that must notice is named in the output when it does.
MUTATIONS = [
    ("the rubber-stamp rule",
     'if not t["scope"]:', 'if False:'),
    ("pass-carrying-a-break",
     'if breaks:\n            out.append("tier report `%s` passes while',
     'if False:\n            out.append("tier report `%s` passes while'),
    ("fail-names-no-break",
     'if not breaks:\n            out.append("tier report `%s` fails and names',
     'if False:\n            out.append("tier report `%s` fails and names'),
    ("the blind rule",
     'if isinstance(e, str) and CROSS_TIER.search(e):', 'if False:'),
    ("the blind rule over findings",
     'if isinstance(v, str) and CROSS_TIER.search(v):', 'if False:'),
    ("break-needs-a-check",
     'if sev == "breaks" and not str(f.get("check", "")).strip():', 'if False:'),
    ("all-three-required", 'if missing:', 'if False:'),
    ("one-report-per-tier", 'if t["tier"] in reports:', 'if False:'),
    ("same-node", 'if t["node"] != nid:', 'if False:'),
    ("the round increments",
     'round_no = int(prior.get("round") or 0) + 1', 'round_no = 1'),
    ("the churn detector",
     'if len(history) >= 2 and all(h.get(x) == "fail" for h in history)', 'if False'),
    ("the pass writes a verdict", 'os.replace(tmp, out)', 'os.remove(tmp)'),
    ("empty-evidence on a pass", 'if not t["evidence"]:', 'if False:'),
    ("the eight required keys", 'if k not in t:', 'if False:'),
    ("the verdict enum", 'if t["verdict"] not in TIER_VERDICTS:', 'if False:'),
    ("terminal-node refusal",
     'if node.get("status") in TERMINAL:\n        die("%s is already %s — certifying',
     'if False:\n        die("%s is already %s — certifying'),
    ("open-blocker refusal",
     'if open_blockers:\n        die("%s waits on %s, which %s not closed — certifying',
     'if False:\n        die("%s waits on %s, which %s not closed — certifying'),
]


def run_suite(mutated_source=None):
    """Run graph_test.py in a fresh copy. Returns (red fixtures, how many ran)."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    tree = tmp / "repo"
    shutil.copytree(ROOT, tree,
                    ignore=shutil.ignore_patterns(".git", "node_modules", "__pycache__"))
    if mutated_source is not None:
        (tree / GRAPH_REL).write_text(mutated_source, encoding="utf-8")
    proc = subprocess.run([sys.executable, "test/graph_test.py"], cwd=tree,
                          capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    red = [l.strip() for l in out.splitlines()
           if l.strip().startswith(("FAIL", "CRASH")) and "certify:" in l]
    ran = sum(1 for l in out.splitlines() if "certify:" in l)
    shutil.rmtree(tmp, ignore_errors=True)
    return red, ran


def main():
    only = None
    if "-k" in sys.argv:
        only = sys.argv[sys.argv.index("-k") + 1]
    source = (ROOT / GRAPH_REL).read_text(encoding="utf-8")

    red, ran = run_suite()
    print("control: %d `certify:` fixture(s) ran, %d red" % (ran, len(red)))
    if ran != EXPECTED_FIXTURES or red:
        print("the control is not clean, so no mutation result below would mean "
              "anything: expected %d fixtures and 0 red." % EXPECTED_FIXTURES,
              file=sys.stderr)
        for r in red:
            print("  " + r, file=sys.stderr)
        return 2
    print()

    survived, planted = [], 0
    for name, old, new in MUTATIONS:
        if only and only not in name:
            continue
        if old not in source:
            print("  NOT PLANTED  %s — its anchor is gone from graph.py" % name)
            survived.append(name)
            continue
        planted += 1
        red, ran = run_suite(source.replace(old, new, 1))
        if red:
            noticed = red[0].split("certify:", 1)[1].strip()[:70]
            print("  noticed     %-26s by: %s" % (name, noticed))
        else:
            print("  SURVIVED    %-26s (%d fixtures ran)" % (name, ran))
            survived.append(name)

    print("\n%d of %d planted mutation(s) noticed by a `certify:` fixture"
          % (planted - len(survived), planted))
    if survived:
        print("SURVIVED or NOT PLANTED: " + ", ".join(survived), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
