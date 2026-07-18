#!/usr/bin/env python3
"""Structural validator for the task-pipeline skill repo. Exit 0 = pass."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "task-pipeline"
errors = []


def fail(m):
    errors.append(m)


def load_json(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.isfile(p):
        fail(f"missing file: {rel}")
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        fail(f"invalid JSON in {rel}: {e}")
        return None


mkt = load_json(".claude-plugin/marketplace.json")
plg = load_json("plugins/task-pipeline/.claude-plugin/plugin.json")

mkt_name = None
if mkt:
    plugins = mkt.get("plugins") or []
    if not plugins:
        fail("marketplace.json: plugins[] empty")
    else:
        p0 = plugins[0]
        mkt_name = p0.get("name")
        src = p0.get("source", "")
        srcdir = os.path.normpath(os.path.join(ROOT, src))
        if not os.path.isfile(os.path.join(srcdir, ".claude-plugin", "plugin.json")):
            fail(f"marketplace source {src!r} has no .claude-plugin/plugin.json")

plg_name = plg.get("name") if plg else None

skill_path = os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline/SKILL.md")
fm_name = None
if not os.path.isfile(skill_path):
    fail("missing SKILL.md")
else:
    txt = open(skill_path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        fail("SKILL.md: no frontmatter")
    else:
        fm = m.group(1)
        nm = re.search(r"^name:\s*(.+)$", fm, re.M)
        dm = re.search(r"^description:\s*(.+)$", fm, re.M)
        fm_name = nm.group(1).strip().strip('"').strip("'") if nm else None
        if not fm_name:
            fail("SKILL.md: empty/missing name")
        if not dm or not dm.group(1).strip():
            fail("SKILL.md: empty/missing description")

for label, val in {"marketplace": mkt_name, "plugin.json": plg_name, "frontmatter": fm_name}.items():
    if val != NAME:
        fail(f"name mismatch: {label}={val!r} expected {NAME!r}")

# version must be in sync across marketplace entry and plugin.json
mkt_ver = None
if mkt and (mkt.get("plugins") or []):
    mkt_ver = mkt["plugins"][0].get("version")
plg_ver = plg.get("version") if plg else None
if not plg_ver:
    fail("plugin.json: missing version")
if not mkt_ver:
    fail("marketplace.json: plugin entry missing version")
if mkt_ver and plg_ver and mkt_ver != plg_ver:
    fail(f"version mismatch: marketplace={mkt_ver!r} plugin.json={plg_ver!r}")

# slash command must exist so /task-pipeline resolves
cmd_path = os.path.join(ROOT, "plugins/task-pipeline/commands/task-pipeline.md")
if not os.path.isfile(cmd_path):
    fail("missing command: plugins/task-pipeline/commands/task-pipeline.md")

refdir = os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline/references")
for r in ("stages.md", "model-tiering.md", "conventions.md"):
    if not os.path.isfile(os.path.join(refdir, r)):
        fail(f"missing reference: references/{r}")

for r in ("README.md", "LICENSE"):
    if not os.path.isfile(os.path.join(ROOT, r)):
        fail(f"missing root file: {r}")

if errors:
    print("FAIL: task-pipeline structure invalid")
    for e in errors:
        print(" - " + e)
    sys.exit(1)
print("PASS: task-pipeline structure valid")
