#!/usr/bin/env python3
"""docgraph.py, the documentation graph's starter pack: every verb against a planted repo.

Each case plants the defect it looks for, so a docgraph that stopped finding it fails
here (canon 5: a green nobody watched turn red is not evidence).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline/scripts/docgraph.py")
COPY = os.path.join(ROOT, "plugins/task-pipeline/skills/evidence-docs/scripts/docgraph.py")
CASES = []
FAILS = []


def case(fn):
    CASES.append(fn)
    return fn


def run(root, *args):
    r = subprocess.run([sys.executable, SCRIPT, *args, "--root", root], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def plant():
    root = tempfile.mkdtemp(prefix="docgraph-")
    write(root, "README.md", "# Demo project\n\nDemo turns recipes into shopping lists for families.\n\n"
          "See [the decisions](docs/decisions.md) and [the scenarios](docs/ux/scenarios.md).\n")
    write(root, "docs/decisions.md", "# Decisions\n\n| Id | Date | Decision |\n|---|---|---|\n"
          "| D-1 | 2026-11-01 | Lists are grouped by aisle |\n| D-2 | 2026-11-02 | Prices stay out of v1 |\n\n"
          "D-2 follows from D-1. Решение принято по замеру `docs/ux/scenarios.md:3`.\n")
    write(root, "docs/ux/scenarios.md", "# Scenarios\n\n### S-1 A parent plans the week\n\n"
          "The parent picks five recipes and gets one list (D-1).\n")
    write(root, "docs/guide.md", "# Guide\n\nRead [the runbook](runbook.md) and [decisions](decisions.md).\n")
    write(root, "docs/ops/runbook.md", "# Runbook\n\nRestart the worker with `make restart`.\n")
    write(root, "docs/old-plan.md", "---\nstatus: superseded\n---\n# Old plan\n\nReplaced by D-2.\n")
    write(root, "docs/pricing.md", "---\nvalid_until: 2020-01-01\n---\n# Pricing\n\nFree for everyone.\n")
    write(root, "docs/lonely.md", "# Lonely\n\nNobody links here.\n")
    write(root, "docs/index.md", "# Index\n\n[Old plan](old-plan.md), [pricing](pricing.md), [guide](guide.md).\n")
    write(root, "AGENTS.md", "# Agents\n\nStart at [the index](docs/index.md).\n")
    subprocess.run(["git", "init", "-q", root], check=True)
    subprocess.run(["git", "-C", root, "add", "-A"], check=True)
    subprocess.run(["git", "-C", root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed"],
                   check=True)
    return root


def digest(root, rels):
    h = hashlib.sha256()
    for rel in rels:
        with open(os.path.join(root, rel), "rb") as fh:
            h.update(rel.encode() + b"\0" + fh.read())
    return h.hexdigest()


def graph(root):
    with open(os.path.join(root, ".docgraph/graph.json"), encoding="utf-8") as fh:
        return json.load(fh)


def expect(cond, msg):
    if not cond:
        raise AssertionError(msg)


@case
def detect_before_and_after_init(root):
    code, out = run(root, "detect", "--json")
    d = json.loads(out)
    expect(code == 0 and not d["agent_ready"] and "graph" in d["missing"], f"detect before init: {out}")
    run(root, "init")
    d = json.loads(run(root, "detect", "--json")[1])
    expect(d["agent_ready"], f"detect after init: {d}")


@case
def init_is_idempotent_three_times(root):
    committed = ["docs/graph/docgraph.json", "docs/graph/README.md", "docs/graph/MAP.md",
                 "docs/refactor-backlog.md", ".gitignore"]
    run(root, "init")
    first = digest(root, committed)
    for _ in range(2):
        code, out = run(root, "init")
        expect(code == 0 and "nothing (already set up)" in out, f"re-init wrote something: {out}")
        expect(digest(root, committed) == first, "init changed committed bytes on a repeat")
    with open(os.path.join(root, ".gitignore")) as fh:
        expect(fh.read().count(".docgraph/") == 1, ".docgraph/ ignored more than once")


@case
def nodes_and_edges_carry_the_shared_format(root):
    run(root, "init")
    g = graph(root)
    expect(g["schema"] == "knowledge-graph/1" and g["profile"] == "starter", "schema/profile")
    ids = {n["id"]: n for n in g["nodes"]}
    for want in ("project:" + os.path.basename(root), "doc:docs/decisions.md", "id:D-1", "id:D-2", "id:S-1"):
        expect(want in ids, f"missing node {want}")
    expect(ids["id:D-1"]["kind"] == "decision" and ids["id:S-1"]["kind"] == "scenario", "id kinds")
    expect(ids["id:D-1"]["title"] == "Lists are grouped by aisle", f"title: {ids['id:D-1']['title']}")
    expect(ids["id:D-1"]["pointer"] == "docs/decisions.md#L5", f"pointer: {ids['id:D-1']['pointer']}")
    for n in g["nodes"]:
        expect(set(n) == {"id", "kind", "area", "title", "pointer", "status", "source_at"}, f"node keys {n}")
    for e in g["edges"]:
        expect(set(e) == {"src", "dst", "kind", "basis", "provenance"}, f"edge keys {e}")
    pairs = {(e["src"], e["dst"], e["kind"]) for e in g["edges"]}
    expect(("doc:README.md", "doc:docs/decisions.md", "cites") in pairs, "doc link edge")
    expect(("doc:docs/ux/scenarios.md", "id:D-1", "cites") in pairs, "id citation edge")
    expect(("id:D-1", "doc:docs/decisions.md", "part-of") in pairs, "definition edge")
    expect(ids["doc:docs/old-plan.md"]["status"] == "superseded", "superseded status")


@case
def check_fails_on_broken_link_and_expired_fact(root):
    run(root, "init")
    code, out = run(root, "check")
    expect(code == 1, f"check passed with a broken link and an expired fact: {out}")
    expect("broken-link" in out and "docs/guide.md#L3" in out, f"broken link not named: {out}")
    expect("stale-fact" in out and "valid_until 2020-01-01" in out, f"expired fact not named: {out}")
    expect("orphan" in out and "docs/lonely.md" in out, f"orphan not named: {out}")


@case
def a_broken_link_alone_fails_the_check(root):
    os.remove(os.path.join(root, "docs/pricing.md"))
    write(root, "docs/index.md", "# Index\n\n[Old plan](old-plan.md), [guide](guide.md), [lonely](lonely.md).\n")
    run(root, "init")
    code, out = run(root, "check")
    expect(code == 1 and "fail broken-link" in out, f"a lone broken link passed the check: {code} {out}")
    write(root, "docs/guide.md", "# Guide\n\nSee `docs/gone/away.md:4` for the numbers.\n")
    code, out = run(root, "check")
    expect(code == 0 and "warn broken-citation" in out, f"a lone missing citation must warn, not fail: {code} {out}")


@case
def no_false_alarm_on_line_suffixes_other_repos_and_dated_records(root):
    os.remove(os.path.join(root, "docs/pricing.md"))
    write(root, "docs/index.md", "# Index\n\n[Old plan](old-plan.md), [lonely](lonely.md), "
          "[guide at a line](guide.md:3), [sibling](../../elsewhere/x.md).\n")
    write(root, "docs/guide.md", "# Guide\n\nSee [runbook](ops/runbook.md) and `Hub/hub_brain.py:12`.\n")
    write(root, "docs/HANDOFF.md", "# Handoff\n\nThen it lived at [plan](plans/gone.md).\n")
    write(root, "AGENTS.md", "# Agents\n\nStart at [the index](docs/index.md) and [handoff](docs/HANDOFF.md).\n")
    run(root, "init")
    code, out = run(root, "check")
    expect(code == 0, f"false alarm failed the check: {out}")
    expect("guide.md:3" not in out and "elsewhere" not in out, f"line suffix or outside link flagged: {out}")
    expect("warn broken-citation" in out and "another repository" in out, f"foreign citation: {out}")
    expect("(dated record)" in out, f"a dated record's link is not marked: {out}")
    run(root, "heal", "--fix")
    with open(os.path.join(root, "docs/HANDOFF.md")) as fh:
        expect("](plans/gone.md)" in fh.read(), "heal rewrote a dated record")


@case
def heal_fix_rewrites_a_moved_file_link(root):
    run(root, "init")
    code, out = run(root, "heal")
    expect("dry run" in out, f"heal without --fix must not write: {out}")
    with open(os.path.join(root, "docs/guide.md")) as fh:
        expect("](runbook.md)" in fh.read(), "dry run wrote")
    code, out = run(root, "heal", "--fix")
    expect("fixed  broken-link" in out, f"heal --fix did not fix: {out}")
    with open(os.path.join(root, "docs/guide.md")) as fh:
        expect("](ops/runbook.md)" in fh.read(), "link not rewritten to the moved file")
    os.remove(os.path.join(root, "docs/pricing.md"))
    with open(os.path.join(root, "docs/index.md"), "w") as fh:
        fh.write("# Index\n\n[Old plan](old-plan.md), [guide](guide.md), [lonely](lonely.md).\n")
    code, out = run(root, "check")
    expect(code == 0, f"check still fails after the fix: {out}")


@case
def heal_fix_resolves_a_root_relative_link_with_a_line(root):
    write(root, "docs/ops/README.md", "# Ops\n")
    write(root, "docs/ux/notes.md", "# Notes\n\nSee [the runbook](docs/ops/runbook.md:2) and [ops](docs/ops/README.md).\n")
    write(root, "docs/index.md", "# Index\n\n[Old plan](old-plan.md), [guide](guide.md), [lonely](lonely.md), "
          "[notes](ux/notes.md).\n")
    run(root, "init")
    code, out = run(root, "heal", "--fix")
    with open(os.path.join(root, "docs/ux/notes.md")) as fh:
        body = fh.read()
    expect("](../ops/runbook.md#L2)" in body, f"root-relative link with a line not repaired: {body}")
    expect("](../ops/README.md)" in body, f"suffix match lost to two files named README.md: {body}")


@case
def heal_never_rewrites_a_citation_or_guesses_across_folders(root):
    write(root, "templates/x/code/workflow.py", "x = 1\n")
    write(root, "docs/guide.md", "# Guide\n\nThe engine's `store/workflow.py:3` and [a link](store/workflow.py).\n")
    run(root, "init")
    run(root, "heal", "--fix")
    with open(os.path.join(root, "docs/guide.md")) as fh:
        body = fh.read()
    expect("`store/workflow.py:3`" in body, f"a citation was rewritten: {body}")
    expect("](store/workflow.py)" in body, f"a link was guessed into another folder: {body}")


@case
def heal_leaves_what_it_cannot_decide(root):
    write(root, "docs/guide.md", "# Guide\n\n[Gone](nowhere-at-all.md)\n")
    run(root, "init")
    code, out = run(root, "heal", "--fix")
    expect("left   broken-link" in out and "nowhere-at-all.md" in out, f"undecidable link: {out}")


@case
def stale_as_of_warns_without_failing(root):
    os.remove(os.path.join(root, "docs/pricing.md"))
    write(root, "docs/index.md", "# Index\n\n[Old plan](old-plan.md), [guide](guide.md), [lonely](lonely.md).\n")
    write(root, "docs/guide.md", "---\nas_of: 2020-05-01\n---\n# Guide\n\n[runbook](ops/runbook.md)\n")
    run(root, "init")
    code, out = run(root, "check")
    expect(code == 0 and "warn stale-fact" in out and "as_of 2020-05-01" in out, f"as_of: {code} {out}")
    with open(os.path.join(root, "docs/graph/MAP.md")) as fh:
        expect("as_of 2020-05-01" in fh.read(), "the map's re-check list misses the stale fact")


@case
def search_finds_passages_with_lines_in_both_languages(root):
    run(root, "init")
    code, out = run(root, "search", "aisle grouping", "--json")
    hits = json.loads(out)
    expect(hits and hits[0]["path"] == "docs/decisions.md", f"english search: {out[:300]}")
    expect(hits[0]["pointer"].startswith("docs/decisions.md#L"), "pointer with lines")
    with open(os.path.join(root, "docs/decisions.md")) as fh:
        lines = fh.read().splitlines()
    a, b = hits[0]["a"], hits[0]["b"]
    expect(hits[0]["text"] == "\n".join(lines[a - 1:b]).strip(), "passage is not verbatim at its lines")
    hits = json.loads(run(root, "search", "решения", "--json")[1])
    expect(hits and hits[0]["path"] == "docs/decisions.md", "russian word form did not match")
    hits = json.loads(run(root, "search", "D-1", "--json")[1])
    expect(hits, "an id query finds nothing")


@case
def cite_accepts_verbatim_and_refuses_an_added_number(root):
    code, out = run(root, "cite", "Lists are grouped by aisle", "docs/decisions.md")
    expect(code == 0 and out.strip() == "docs/decisions.md#L5", f"verbatim quote: {code} {out}")
    code, out = run(root, "cite", "Lists are grouped by 3 aisles", "docs/decisions.md")
    expect(code == 1, f"a quote with a number it lacks was accepted: {out}")
    code, out = run(root, "cite", "short", "docs/decisions.md")
    expect(code == 1, "a quote under 12 characters was accepted")


@case
def neighbours_walk_both_ways(root):
    run(root, "init")
    out = json.loads(run(root, "neighbours", "D-1", "--json")[1])
    expect(out["known"], "D-1 unknown")
    kinds = {(e["src"], e["kind"]) for e in out["edges"]}
    expect(("doc:docs/ux/scenarios.md", "cites") in kinds and ("id:D-1", "part-of") in kinds, f"edges {kinds}")
    out = json.loads(run(root, "neighbours", "D-999", "--json")[1])
    expect(out["known"] is False, "an absent node must say known: false")


@case
def prune_moves_superseded_and_rewrites_links(root):
    run(root, "init")
    code, out = run(root, "prune")
    expect("would move docs/old-plan.md -> docs/archive/old-plan.md" in out, f"prune dry run: {out}")
    expect(os.path.exists(os.path.join(root, "docs/old-plan.md")), "dry run moved the file")
    code, out = run(root, "prune", "--apply")
    expect(os.path.exists(os.path.join(root, "docs/archive/old-plan.md")), "file not moved")
    with open(os.path.join(root, "docs/index.md")) as fh:
        expect("](archive/old-plan.md)" in fh.read(), "inbound link not rewritten")
    g = graph(root)
    expect(not any(f["kind"] == "broken-link" and "old-plan" in f["what"] for f in g["findings"]),
           "prune left a broken link")


@case
def refactor_note_appends_numbered_rows(root):
    run(root, "init")
    _, first = run(root, "refactor-note", "docs/ had no graph", "--did", "docgraph init", "--task", "T-1")
    _, second = run(root, "refactor-note", "README cites a removed file")
    expect(first.strip() == "R-001" and second.strip() == "R-002", f"ids {first} {second}")
    with open(os.path.join(root, "docs/refactor-backlog.md")) as fh:
        body = fh.read()
    expect("| R-001 |" in body and "| done |" in body and "| R-002 |" in body and "| open |" in body, body)


@case
def map_names_project_decisions_scenarios_without_em_dash(root):
    write(root, "docs/decisions.md", "# Decisions\n\n| Id | Date | Decision |\n|---|---|---|\n"
          "| D-1 | 2026-11-01 | Lists — grouped by aisle |\n")
    run(root, "init")
    with open(os.path.join(root, "docs/graph/MAP.md"), encoding="utf-8") as fh:
        body = fh.read()
    for want in ("Demo turns recipes into shopping lists", "## Decisions", "D-1", "## Scenarios", "S-1",
                 "## Documents by area"):
        expect(want in body, f"map lacks {want!r}")
    expect("—" not in body, "the generated map carries an em dash")


@case
def evidence_docs_copy_is_byte_identical(root):
    with open(SCRIPT, "rb") as a, open(COPY, "rb") as b:
        expect(a.read() == b.read(), "evidence-docs/scripts/docgraph.py differs from its source home; "
               "run python3 test/audit_regressions/fix-ed-01.01.py --sync")


def main():
    for fn in CASES:
        root = plant()
        try:
            fn(root)
            print(f"ok   {fn.__name__}")
        except AssertionError as exc:
            FAILS.append(fn.__name__)
            print(f"FAIL {fn.__name__}: {exc}")
        finally:
            shutil.rmtree(root, ignore_errors=True)
    if FAILS:
        print(f"FAIL: docgraph.py, {len(FAILS)} of {len(CASES)} cases")
        return 1
    print(f"PASS: docgraph.py, {len(CASES)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
