#!/usr/bin/env python3
"""`migrate-artifacts`, proven at the layer that repeats.

Standing instruction #2 in this repository's retro: *prove idempotence at the layer
that repeats, not the layer that is easy to test.* A pure planner with passing
round-trip fixtures once sat under a command whose second run destroyed the file, so
these cases run the REAL command as a subprocess, three times, against a real
directory tree, and compare hashes.

    python3 test/migrate_artifacts_test.py
    python3 test/migrate_artifacts_test.py -k collision

Zero dependencies, same as the rest of the suite.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(ROOT, "bin", "task-pipeline.js")

failures = []


def fail(case, msg):
    failures.append(f"{case}: {msg}")
    print(f"FAIL: {case}: {msg}")


def tree_hash(base):
    """Every path and every byte under `base`, order-independent."""
    h = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames.sort()
        for fn in sorted(filenames):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, base).replace(os.sep, "/")
            h.update(rel.encode())
            with open(full, "rb") as fh:
                h.update(fh.read())
    return h.hexdigest()


def seed(base, files, config=None):
    for rel, body in files.items():
        p = os.path.join(base, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(body)
    if config is not None:
        with open(os.path.join(base, "pipeline.json"), "w", encoding="utf-8") as fh:
            json.dump(config, fh)


def run(base, *args):
    return subprocess.run([os.environ.get("NODE", "node"), CLI, "migrate-artifacts",
                           *args], cwd=base, capture_output=True, text=True)


# --- the cases ---------------------------------------------------------------

def case_three_runs_are_idempotent(base):
    seed(base, {
        "docs/superpowers/retro.md": "# retro\n",
        "docs/superpowers/backlog.md": "| B-001 | x |\n",
        "docs/superpowers/specs/2026-01-01-a-brief.md": "# brief\n",
    })
    r1 = run(base)
    if r1.returncode != 0:
        return fail("three-runs", f"first run exited {r1.returncode}: {r1.stderr}")
    if os.path.isdir(os.path.join(base, "docs/superpowers")):
        return fail("three-runs", "docs/superpowers/ survived a complete move")
    if not os.path.isfile(os.path.join(base, "docs/evidence/retro.md")):
        return fail("three-runs", "retro.md did not arrive")

    h1 = tree_hash(base)
    r2 = run(base)
    h2 = tree_hash(base)
    r3 = run(base)
    h3 = tree_hash(base)
    if r2.returncode != 0 or r3.returncode != 0:
        return fail("three-runs", f"a repeat run failed: {r2.stderr} {r3.stderr}")
    if not (h1 == h2 == h3):
        return fail("three-runs",
                    f"not idempotent: {h1[:12]} -> {h2[:12]} -> {h3[:12]}")
    if "nothing to do" not in r2.stdout:
        return fail("three-runs", "a repeat run did not say it had nothing to do")
    print("  ok  three runs, identical trees, second and third are no-ops")


def case_dry_run_writes_nothing(base):
    seed(base, {"docs/superpowers/retro.md": "# retro\n"})
    before = tree_hash(base)
    r = run(base, "--dry-run")
    after = tree_hash(base)
    if r.returncode != 0:
        return fail("dry-run", f"exited {r.returncode}: {r.stderr}")
    if before != after:
        return fail("dry-run", "the tree changed under --dry-run")
    if "nothing was written" not in r.stdout:
        return fail("dry-run", "--dry-run did not say it wrote nothing")
    print("  ok  --dry-run left the tree byte-identical")


def case_preview_shows_removals(base):
    seed(base, {"docs/superpowers/retro.md": "# retro\n"})
    r = run(base, "--dry-run")
    # A preview that shows only what arrives hides the half that loses data. This
    # repository shipped exactly that defect once: +361/-1 against a run that removed
    # 82 lines.
    if "- docs/superpowers/retro.md" not in r.stdout:
        return fail("preview", "the preview does not show what LEAVES")
    if "+ docs/evidence/retro.md" not in r.stdout:
        return fail("preview", "the preview does not show what arrives")
    print("  ok  the preview shows removals as well as additions")


def case_collision_is_never_overwritten(base):
    seed(base, {
        "docs/superpowers/retro.md": "LEGACY BODY\n",
        "docs/evidence/retro.md": "NEW BODY\n",
        "docs/superpowers/backlog.md": "| B-001 | x |\n",
    })
    r = run(base)
    if r.returncode != 0:
        return fail("collision", f"exited {r.returncode}: {r.stderr}")
    kept = open(os.path.join(base, "docs/evidence/retro.md"), encoding="utf-8").read()
    if kept != "NEW BODY\n":
        return fail("collision", "the existing file was overwritten")
    legacy = os.path.join(base, "docs/superpowers/retro.md")
    if not os.path.isfile(legacy):
        return fail("collision", "the colliding legacy file was deleted rather than kept")
    if not os.path.isfile(os.path.join(base, "docs/evidence/backlog.md")):
        return fail("collision", "a non-colliding file was not moved")
    h1 = tree_hash(base)
    run(base)
    if tree_hash(base) != h1:
        return fail("collision", "a second run changed a tree that still collides")
    print("  ok  collisions kept, non-collisions moved, and it repeats cleanly")


def case_configured_root_is_refused(base):
    seed(base, {"docs/superpowers/retro.md": "# retro\n"},
         config={"version": 1,
                 "stages": [{"id": 0, "state": "intake", "name": "Intake",
                             "gate": {"type": "manual", "check": "x"}}],
                 "paths": {"artifacts": "docs/runs"}})
    before = tree_hash(base)
    r = run(base)
    if r.returncode != 3:
        return fail("configured", f"expected exit 3, got {r.returncode}")
    if tree_hash(base) != before:
        return fail("configured", "a refused migration still changed the tree")
    if "refused" not in r.stdout:
        return fail("configured", "the refusal was not printed")
    print("  ok  a configured root is refused, not overridden")


def case_backup_is_taken(base):
    seed(base, {"docs/superpowers/retro.md": "# retro\n"})
    r = run(base)
    if r.returncode != 0:
        return fail("backup", f"exited {r.returncode}: {r.stderr}")
    bdir = os.path.join(base, ".task-pipeline", "backups")
    copies = os.listdir(bdir) if os.path.isdir(bdir) else []
    if not copies:
        return fail("backup", "no backup was taken before the move")
    body = open(os.path.join(bdir, copies[0], "retro.md"), encoding="utf-8").read()
    if body != "# retro\n":
        return fail("backup", "the backup does not hold the original content")
    print("  ok  the move is preceded by a readable copy")


def case_mentions_are_listed_never_edited(base):
    seed(base, {
        "docs/superpowers/retro.md": "# retro\n",
        "CLAUDE.md": "see `docs/superpowers/retro.md` for standing instructions\n",
    })
    claude_before = open(os.path.join(base, "CLAUDE.md"), encoding="utf-8").read()
    r = run(base)
    claude_after = open(os.path.join(base, "CLAUDE.md"), encoding="utf-8").read()
    if claude_before != claude_after:
        return fail("mentions", "a file outside the artifact root was EDITED")
    if "CLAUDE.md" not in r.stdout:
        return fail("mentions", "the surviving mention was not reported")
    if "none edited" not in r.stdout and "NOT EDITED" not in r.stdout:
        return fail("mentions", "the report does not say the files were left alone")
    print("  ok  mentions elsewhere are listed and left untouched")


CASES = [
    case_three_runs_are_idempotent,
    case_dry_run_writes_nothing,
    case_preview_shows_removals,
    case_collision_is_never_overwritten,
    case_configured_root_is_refused,
    case_backup_is_taken,
    case_mentions_are_listed_never_edited,
]


def main(argv):
    only = argv[argv.index("-k") + 1] if "-k" in argv else None
    ran = 0
    for c in CASES:
        if only and only not in c.__name__:
            continue
        ran += 1
        with tempfile.TemporaryDirectory() as base:
            try:
                c(base)
            except Exception as exc:                     # noqa: BLE001
                fail(c.__name__, f"raised {exc!r}")
    if ran == 0:
        fail("harness", "no cases ran — a filter that matched nothing is not a pass")
    if failures:
        print(f"\nFAIL: {len(failures)} problem(s) across {ran} case(s)")
        return 1
    print(f"PASS: migrate-artifacts — {ran} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
