#!/usr/bin/env python3
"""CTX-02.03 — content-addressed export/import (sherlock audit, parent
CTX-02, third stage of the packet compiler).

The contract under test, as behaviour against scripts/context_packets.py:

* export → import on TWO different recipient roots materializes
  byte-identical trees, with no absolute path anywhere in the bundle;
* a corrupt blob and a missing blob each reject the WHOLE import by name —
  nothing is written (all or nothing);
* an absolute locator, an escaping `..` locator and a credential-looking
  input are refused at export;
* a source file that moved under the plan (digest mismatch) refuses to
  travel.

Standard library only.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                      "scripts", "context_packets.py")

_spec = importlib.util.spec_from_file_location("context_packets", SCRIPT)
M = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(M)

checks = 0
failures = []


def case(name, fn):
    global checks
    try:
        fn()
        checks += 1
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def make_source():
    src = tempfile.mkdtemp()
    files = {"docs/brief.md": b"# the brief\n", "context/decisions.json": b"{}\n"}
    for rel, data in files.items():
        os.makedirs(os.path.join(src, os.path.dirname(rel)), exist_ok=True)
        with open(os.path.join(src, rel), "wb") as fh:
            fh.write(data)
    inputs = [{"address": rel, "sha256": hashlib.sha256(data).hexdigest()}
              for rel, data in sorted(files.items())]
    leaf = {"schema_version": "execution-packet/1", "id": "L-1",
            "module": "m", "intent": "travel", "inputs": inputs}
    return src, leaf, files


def tree_bytes(root):
    out = {}
    for dirpath, _dirs, names in os.walk(root):
        for n in names:
            f = os.path.join(dirpath, n)
            out[os.path.relpath(f, root)] = open(f, "rb").read()
    return out


def t_two_roots_identical_bytes_no_absolute_paths():
    src, leaf, files = make_source()
    bundle = tempfile.mkdtemp()
    m, problems = M.export_bundle(leaf, src, bundle)
    assert problems == [], f"a clean export was refused: {problems[:2]}"
    r1, r2 = tempfile.mkdtemp(), tempfile.mkdtemp()
    for r in (r1, r2):
        _m, p2 = M.import_bundle(bundle, r)
        assert p2 == [], f"a clean import was refused: {p2[:2]}"
    assert tree_bytes(r1) == tree_bytes(r2), "two roots imported different bytes"
    assert tree_bytes(r1) == files, "the imported bytes differ from the source"
    manifest_bytes = open(os.path.join(bundle, "manifest.json")).read()
    for absroot in (src, r1, r2, os.path.expanduser("~")):
        assert absroot not in manifest_bytes, \
            f"the manifest leaks an absolute root: {absroot}"


def t_corrupt_blob_rejects_everything():
    src, leaf, _files = make_source()
    bundle = tempfile.mkdtemp()
    M.export_bundle(leaf, src, bundle)
    blobs = os.listdir(os.path.join(bundle, "blobs"))
    victim = os.path.join(bundle, "blobs", sorted(blobs)[0])
    open(victim, "ab").write(b"tampered")
    dest = tempfile.mkdtemp()
    m, problems = M.import_bundle(bundle, dest)
    assert m is None and any("CORRUPT" in p for p in problems), \
        f"a corrupt blob imported: {problems[:2]}"
    assert tree_bytes(dest) == {}, \
        "a rejected import still wrote files — all or nothing broke"


def t_missing_blob_rejects_by_name():
    src, leaf, _files = make_source()
    bundle = tempfile.mkdtemp()
    M.export_bundle(leaf, src, bundle)
    blobs = sorted(os.listdir(os.path.join(bundle, "blobs")))
    os.unlink(os.path.join(bundle, "blobs", blobs[0]))
    dest = tempfile.mkdtemp()
    m, problems = M.import_bundle(bundle, dest)
    assert m is None and any("MISSING" in p for p in problems)
    assert tree_bytes(dest) == {}


def t_absolute_escaping_and_credentials_refused_at_export():
    src, leaf, _files = make_source()
    for bad, needle in ((dict(address="/etc/passwd", sha256="0" * 64), "absolute"),
                        (dict(address="../outside.md", sha256="0" * 64), "escaping"),
                        (dict(address="conf/.env", sha256="0" * 64), "credential")):
        crooked = dict(leaf, inputs=leaf["inputs"] + [bad])
        m, problems = M.export_bundle(crooked, src, tempfile.mkdtemp())
        assert m is None and any(needle in p for p in problems), \
            f"{bad['address']}: exported despite being {needle}: {problems[:2]}"


def t_moved_source_refuses_to_travel():
    src, leaf, _files = make_source()
    with open(os.path.join(src, "docs", "brief.md"), "a") as fh:
        fh.write("drifted\n")
    m, problems = M.export_bundle(leaf, src, tempfile.mkdtemp())
    assert m is None and any("moved under the plan" in p for p in problems), \
        "a drifted source travelled under its stale digest"


def t_cli_round_trip():
    src, leaf, _files = make_source()
    d = tempfile.mkdtemp()
    lp = os.path.join(d, "leaf.json")
    json.dump(leaf, open(lp, "w"))
    bundle, dest = os.path.join(d, "bundle"), os.path.join(d, "dest")
    r = subprocess.run([sys.executable, SCRIPT, "export-bundle", lp, src, bundle],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[:200]
    v = subprocess.run([sys.executable, SCRIPT, "import-bundle", bundle, dest],
                       capture_output=True, text=True)
    assert v.returncode == 0 and "imported 2 file(s)" in v.stdout, v.stderr[:200]


def main():
    case("two roots import identical bytes; no absolute path in the bundle",
         t_two_roots_identical_bytes_no_absolute_paths)
    case("a corrupt blob rejects everything, nothing is written",
         t_corrupt_blob_rejects_everything)
    case("a missing blob rejects by name", t_missing_blob_rejects_by_name)
    case("absolute, escaping and credential locators are refused at export",
         t_absolute_escaping_and_credentials_refused_at_export)
    case("a source that moved under the plan refuses to travel",
         t_moved_source_refuses_to_travel)
    case("the CLI round-trips", t_cli_round_trip)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK ({checks} checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
