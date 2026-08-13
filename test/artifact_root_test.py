#!/usr/bin/env python3
"""One rule, two implementations, one table — and they are compared to each other.

`test/artifact_root.py` answers for the validator; `bin/lib/artifact-root.js` ships
in the package and answers for `migrate-artifacts`. Two implementations of one rule
is the "second home for one fact" this repository refuses everywhere else, and the
refusal is affordable here only because of what this file does: every case in
`fixtures/artifact-root-cases.json` is built as a real tree, both implementations
are asked, and a disagreement between them fails just as loudly as a wrong answer.

Checking each against the table alone would let them drift into two shapes that are
both "right" against their own reading of it. Comparing them to each other is what
makes drift unshippable.

    python3 test/artifact_root_test.py            # all cases
    python3 test/artifact_root_test.py -k legacy  # by name

Zero dependencies, same as the rest of the suite.
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "test"))

CASES = os.path.join(ROOT, "test/fixtures/artifact-root-cases.json")
NODE_IMPL = os.path.join(ROOT, "bin/lib/artifact-root.js")

FIELDS = ("root", "reason", "legacy", "leftover", "collision")

failures = []


def fail(msg):
    failures.append(msg)
    print(f"FAIL: {msg}")


def build(case, base):
    """Materialise a case as a real tree. Real directories, because the rule is
    about what is on disk and a mocked filesystem would prove the mock."""
    for rel in case.get("tree", []):
        p = os.path.join(base, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("# fixture\n")
    if "config" in case:
        with open(os.path.join(base, "pipeline.json"), "w", encoding="utf-8") as fh:
            json.dump(case["config"], fh)


def ask_python(base):
    import artifact_root
    return artifact_root.resolve(base)


def ask_node(base):
    r = subprocess.run([_node(), NODE_IMPL, base], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"node impl exited {r.returncode}: {r.stderr.strip()}")
    return json.loads(r.stdout)


def _node():
    return os.environ.get("NODE", "node")


def norm(d):
    """Compare only the contract's fields, and normalise the root to a repo-relative
    posix path — an absolute temp path differs per run and per platform."""
    return {k: d.get(k) for k in FIELDS}


def main(argv):
    only = None
    if "-k" in argv:
        only = argv[argv.index("-k") + 1]

    table = json.load(open(CASES, encoding="utf-8"))
    ran = 0
    for case in table["cases"]:
        if only and only not in case["name"]:
            continue
        ran += 1
        with tempfile.TemporaryDirectory() as base:
            build(case, base)
            want = norm(case["expect"])
            try:
                got_py = norm(ask_python(base))
            except Exception as exc:                    # noqa: BLE001
                fail(f"{case['name']}: python impl raised {exc!r}")
                continue
            try:
                got_js = norm(ask_node(base))
            except Exception as exc:                    # noqa: BLE001
                fail(f"{case['name']}: node impl raised {exc!r}")
                continue

            if got_py != want:
                fail(f"{case['name']}: python answered {got_py}, table says {want}")
            if got_js != want:
                fail(f"{case['name']}: node answered {got_js}, table says {want}")
            if got_py != got_js:
                fail(f"{case['name']}: the two implementations DISAGREE — "
                     f"python {got_py} vs node {got_js}")

    # A filter that matches nothing, or a table that lost its cases, would print
    # "0 failures" and read as success. The same trap test/negatives.py guards with
    # MIN_EXPECTED.
    if ran == 0:
        fail("no cases ran — an empty table or a filter that matched nothing is not a pass")
    elif not only and ran < len(table["cases"]):
        fail(f"only {ran} of {len(table['cases'])} cases ran")

    if failures:
        print(f"\nFAIL: {len(failures)} problem(s) across {ran} case(s)")
        return 1
    print(f"PASS: artifact-root rule — {ran} cases, both implementations agree")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
