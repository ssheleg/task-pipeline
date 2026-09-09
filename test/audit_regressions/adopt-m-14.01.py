#!/usr/bin/env python3
"""ADOPT-M-14.01 — the UI handoff annex in packet doctrine (sherlock audit,
adoption from the external method set).

The contract under test: the planning doctrine adds a UI annex that lets an
executor build a screen fixture without re-deriving the visual spec — state
IDs, component reuse/props, tokens, content, accessibility, asset versions;
it ADDS to task context and never replaces the scheduler claim/fence; a
stale visual spec triggers a packet revision; and the annex is a DOMAIN
annex, optional for non-UI tasks.

Documented in planning.md, and the annex-required/optional and staleness
rules are run as behaviour.

Standard library only.
"""
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DOC = os.path.join(ROOT, "plugins", "task-pipeline", "skills", "task-pipeline",
                   "references", "planning.md")

failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def t_doctrine_states_the_annex():
    flat = " ".join(open(DOC, encoding="utf-8").read().split())
    for needle in ("The UI handoff annex — a packet an executor can build without "
                   "re-deriving",
                   "the state IDs it touches, the components it reuses and the props",
                   "the tokens and content strings, the accessibility requirements, "
                   "and the exact asset versions",
                   "It never replaces the scheduler's claim or fence".replace(
                       "It never", "it never"),
                   "a stale visual spec",
                   "triggers a packet REVISION",
                   "optional by domain"):
        assert needle in flat, f"the doctrine no longer states {needle!r}"
    # the Contents list carries the new heading (the validator also checks this)
    assert "- The UI handoff annex" in open(DOC, encoding="utf-8").read(), \
        "the Contents list is missing the annex heading"


# ---------------- the annex rules, executed


ANNEX_FIELDS = ("state_ids", "components", "tokens", "content",
                "accessibility", "asset_versions")


def annex_required(domain):
    return domain == "ui"


def annex_complete(annex):
    return all(annex.get(f) for f in ANNEX_FIELDS)


def dispatch_ready(packet):
    """A packet dispatches when its context is fresh; a UI packet ALSO needs a
    complete annex, and a stale visual spec blocks with a revision, never a
    silent dispatch."""
    problems = []
    if annex_required(packet["domain"]):
        a = packet.get("annex")
        if not a or not annex_complete(a):
            problems.append("ui packet: incomplete UI annex — executor would "
                            "re-derive the visual spec")
        elif a.get("asset_version_on_disk") != a.get("asset_versions_pinned"):
            problems.append("ui packet: stale visual spec — asset version moved; "
                            "revise the packet, do not dispatch against old pixels")
    # the annex never stands in for coordination
    if packet.get("claim") is None and packet.get("edits"):
        problems.append("packet with edits has no scheduler claim — the annex "
                        "does not replace the fence")
    return problems


def good_ui_annex():
    return {f: [f] for f in ANNEX_FIELDS} | {
        "asset_versions_pinned": "v3", "asset_version_on_disk": "v3"}


def t_ui_packet_needs_a_complete_annex():
    p = {"domain": "ui", "claim": "T-1", "edits": ["screen.tsx"],
         "annex": good_ui_annex()}
    assert dispatch_ready(p) == [], f"a complete UI packet was blocked: {dispatch_ready(p)}"
    p2 = dict(p, annex={"state_ids": ["S1"]})  # incomplete
    assert any("re-derive" in x for x in dispatch_ready(p2)), \
        "an incomplete annex dispatched — the executor would re-derive"


def t_stale_visual_spec_triggers_revision():
    a = good_ui_annex()
    a["asset_version_on_disk"] = "v4"          # moved under the plan
    p = {"domain": "ui", "claim": "T-1", "edits": ["screen.tsx"], "annex": a}
    assert any("stale visual spec" in x for x in dispatch_ready(p)), \
        "a moved asset version dispatched against old pixels"


def t_non_ui_needs_no_annex():
    p = {"domain": "migration", "claim": "T-1", "edits": ["001_add.sql"]}
    assert dispatch_ready(p) == [], \
        "a migration packet was forced to carry a UI annex"
    p2 = {"domain": "cli", "claim": "T-2", "edits": ["main.py"]}
    assert dispatch_ready(p2) == []


def t_annex_never_replaces_the_claim():
    p = {"domain": "ui", "claim": None, "edits": ["screen.tsx"],
         "annex": good_ui_annex()}
    assert any("does not replace the fence" in x for x in dispatch_ready(p)), \
        "a UI packet with a complete annex but no claim dispatched — the annex "\
        "stood in for coordination"


def main():
    case("the doctrine states the UI annex", t_doctrine_states_the_annex)
    case("a UI packet needs a complete annex", t_ui_packet_needs_a_complete_annex)
    case("a stale visual spec triggers a revision", t_stale_visual_spec_triggers_revision)
    case("a non-UI task needs no annex", t_non_ui_needs_no_annex)
    case("the annex never replaces the scheduler claim", t_annex_never_replaces_the_claim)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
