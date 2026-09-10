#!/usr/bin/env python3
"""FIX-UP-05.02 — the writer contract applied to the task-pipeline installer
(sherlock audit, UP-05 leaf 2).

The finding: the installer deleted the destination and THEN copied into it, so
a crash mid-copy left nothing (with --force) or a partial tree. The writer
contract (UP-05) says: stage on the same filesystem, verify, then switch — a
stage crash leaves the ACTIVE install untouched, and --force=false preserves
the user's bytes.

The fix under test, against bin/task-pipeline.js through node (and the
install.sh discipline is asserted textually).

Standard library only.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BIN = os.path.join(ROOT, "bin", "task-pipeline.js")
INSTALL_SH = os.path.join(ROOT, "install.sh")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def make_src():
    src = tempfile.mkdtemp()
    d = os.path.join(src, "skill")
    os.makedirs(os.path.join(d, "references"))
    with open(os.path.join(d, "SKILL.md"), "w") as fh:
        fh.write("# new skill\n")
    with open(os.path.join(d, "references", "r.md"), "w") as fh:
        fh.write("# new ref\n")
    return d


def node(body):
    r = subprocess.run(["node", "-e", "const m=require(process.argv[1]);" + body, BIN],
                       capture_output=True, text=True, timeout=60)
    return r


def t_clean_install_lands_the_new_tree():
    src = make_src()
    dest = os.path.join(tempfile.mkdtemp(), "task-pipeline")
    r = node(f"m.installOne('skill', {json.dumps(src)}, {json.dumps(dest)}, true, true);")
    assert r.returncode == 0, r.stderr[:200]
    assert open(os.path.join(dest, "SKILL.md")).read() == "# new skill\n"
    assert not [x for x in os.listdir(os.path.dirname(dest))
                if x.startswith("task-pipeline.staging-")], "staging leaked"


def t_force_false_preserves_user_bytes():
    src = make_src()
    root = tempfile.mkdtemp()
    dest = os.path.join(root, "task-pipeline")
    os.makedirs(dest)
    with open(os.path.join(dest, "SKILL.md"), "w") as fh:
        fh.write("# USER edited\n")
    r = node(f"m.installOne('skill', {json.dumps(src)}, {json.dumps(dest)}, true, false);")
    assert r.returncode == 0
    assert open(os.path.join(dest, "SKILL.md")).read() == "# USER edited\n", \
        "--force=false overwrote the user's bytes"
    assert "skip:" in r.stdout


def t_stage_crash_leaves_active_install_intact():
    src = make_src()
    root = tempfile.mkdtemp()
    dest = os.path.join(root, "task-pipeline")
    os.makedirs(dest)
    with open(os.path.join(dest, "SKILL.md"), "w") as fh:
        fh.write("# OLD complete\n")
    # inject an ENOSPC on the 2nd copy, during staging (mid-transaction)
    script = (
        "const fs=require('fs');let n=0;const real=fs.copyFileSync;"
        "fs.copyFileSync=(a,b)=>{if(++n===2){const e=new Error('ENOSPC');e.code='ENOSPC';throw e;}return real(a,b);};"
        "const m=require(process.argv[1]);"
        f"try{{m.installOne('skill',{json.dumps(src)},{json.dumps(dest)},true,true);"
        "console.log('NO_THROW');}catch(e){console.log('ABORTED:'+e.message);}")
    r = subprocess.run(["node", "-e", script, BIN], capture_output=True, text=True, timeout=60)
    assert "ABORTED" in r.stdout, f"a stage crash did not abort: {r.stdout} {r.stderr[:200]}"
    assert open(os.path.join(dest, "SKILL.md")).read() == "# OLD complete\n", \
        "the old install was damaged by a stage crash — the finding itself"
    assert not [x for x in os.listdir(root) if ".staging-" in x], "staging leaked after abort"


def t_install_sh_stages_before_swapping():
    sh = open(INSTALL_SH, encoding="utf-8").read()
    assert "STAGING=" in sh and 'mv "$STAGING" "$DEST"' in sh, \
        "install.sh does not stage the skill before the swap"
    assert 'rm -rf "$DEST"\n  cp -R' not in sh, \
        "install.sh still deletes the destination before copying"
    assert 'mv "$CMD_STAGING" "$CMD_DEST"' in sh, \
        "install.sh does not atomically rename the command into place"


def main():
    case("a clean install lands the new tree", t_clean_install_lands_the_new_tree)
    case("--force=false preserves user bytes", t_force_false_preserves_user_bytes)
    case("a stage crash leaves the active install intact",
         t_stage_crash_leaves_active_install_intact)
    case("install.sh stages before swapping", t_install_sh_stages_before_swapping)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
