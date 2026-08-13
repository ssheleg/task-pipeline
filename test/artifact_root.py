#!/usr/bin/env python3
"""Where this project's run artifacts live — the validator's answer.

The rule, in one ordered list. `bin/lib/artifact-root.js` implements the same one
for `migrate-artifacts`, and `test/artifact_root_test.py` runs both against
`fixtures/artifact-root-cases.json` and fails when they disagree.

    1. `paths.artifacts` in pipeline.json wins outright. Any relative path.
    2. otherwise the first KNOWN name that exists AND CARRIES A REGISTER.
       `docs/evidence/` before `docs/superpowers/` — the new name wins a partial
       migration, so moving one file at a time never leaves a project split.
    3. otherwise `docs/evidence/`, the default for a project that has none.

**Carrying a register is the whole difference between a root and a directory.** A
project may keep an unrelated `docs/evidence/`, and adopting it on bare existence
would write a run's paperwork into somebody else's folder. Standing instruction #1:
assert the input is what you think before deciding on it.

**The answer is a record, not a string.** A bare path cannot say *this is the legacy
name*, *records also sit over there*, or *the default landed on an occupied
directory* — and a caller that cannot know those things writes blind.

`docs/superpowers/` is the name this pipeline used until 2026-08-13, inherited from
an unrelated pack whose own tests walk the same path. It is supported, not
deprecated: a project already using it keeps it, forever, with no warning. A
warning on every run is why hooks get switched off.
"""
import json
import os

#: Ordered. The new name first, so a partial migration resolves forward.
KNOWN = ("docs/evidence", "docs/superpowers")

#: The legacy name, called out so callers do not re-spell it.
LEGACY = "docs/superpowers"

#: What makes a directory a root rather than a directory. Any ONE of these.
REGISTERS = ("retro.md", "backlog.md", "verification.md",
             "specs", "plans", "briefs", "retro")


def carries_register(path):
    """Does this directory hold any artifact this pipeline recognises?"""
    if not os.path.isdir(path):
        return False
    return any(os.path.exists(os.path.join(path, name)) for name in REGISTERS)


def configured(project):
    """`paths.artifacts` from pipeline.json, or None.

    An unreadable or malformed config yields None rather than an exception: the
    resolver's job is to answer, and a project with a broken config still has a
    directory layout. The config's own validity is the schema check's business.
    """
    try:
        with open(os.path.join(project, "pipeline.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
    except (OSError, ValueError):
        return None
    paths = cfg.get("paths") if isinstance(cfg, dict) else None
    value = paths.get("artifacts") if isinstance(paths, dict) else None
    if isinstance(value, str) and value.strip():
        return value.strip().rstrip("/")
    return None


def resolve(project):
    """`{root, reason, legacy, leftover, collision}` for a project directory.

    `root` is relative to `project`, posix-separated — the shape every caller
    stores and every document prints.
    """
    if not isinstance(project, str) or not project:
        # A resolver handed nothing must not answer as though it were handed a
        # project: standing instruction #1, in the one line where it is cheapest.
        raise ValueError("resolve() needs a project directory")

    root = configured(project)
    reason = "configured" if root else None

    if not root:
        for name in KNOWN:
            if carries_register(os.path.join(project, name)):
                root = name
                reason = "legacy" if name == LEGACY else "found"
                break

    if not root:
        root = KNOWN[0]
        reason = "default"

    # `leftover` answers "what else carries records here", which is a different
    # question from "which root won" — so it is computed the same way whatever
    # chose the root.
    leftover = next(
        (n for n in KNOWN
         if n != root and carries_register(os.path.join(project, n))),
        None,
    )

    # The default landing on a directory that exists but is not a root: answer,
    # and say so, so the caller asks instead of writing into it.
    collision = (
        reason == "default"
        and os.path.isdir(os.path.join(project, root))
        and not carries_register(os.path.join(project, root))
    )

    return {
        "root": root,
        "reason": reason,
        "legacy": reason == "legacy",
        "leftover": leftover,
        "collision": collision,
    }


if __name__ == "__main__":
    import sys
    print(json.dumps(resolve(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())))
