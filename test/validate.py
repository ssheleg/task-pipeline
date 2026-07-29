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
        else:
            desc = dm.group(1).strip().strip('"').strip("'")
            if not desc.startswith("Use when"):
                fail("SKILL.md: description must start with 'Use when …' (canon)")
            if not re.search(r"[а-яё]", desc, re.I):
                fail("SKILL.md: description must carry Russian trigger aliases beside the English ones (canon)")
        if len(fm) > 1024:
            fail(f"SKILL.md: frontmatter is {len(fm)} chars, must be under 1024")

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

# npm package: version in sync, bin entry exists and points at a real file
pkg = load_json("package.json")
if pkg:
    pkg_ver = pkg.get("version")
    if not pkg_ver:
        fail("package.json: missing version")
    elif plg_ver and pkg_ver != plg_ver:
        fail(f"version mismatch: package.json={pkg_ver!r} plugin.json={plg_ver!r}")
    bin_map = pkg.get("bin") or {}
    if not bin_map:
        fail("package.json: missing bin entry")
    for bin_name, bin_rel in bin_map.items():
        if not os.path.isfile(os.path.join(ROOT, bin_rel)):
            fail(f"package.json bin {bin_name!r} -> missing file {bin_rel!r}")
    files = pkg.get("files") or []
    if "plugins" not in files or "bin" not in files:
        fail("package.json: files[] must whitelist 'bin' and 'plugins' (skill sources ship in the package)")
    # One documented way to run the checks. A contributor who has to reverse-engineer
    # the test command from CI is a contributor who opens the PR without running it.
    if "validate.py" not in str((pkg.get("scripts") or {}).get("test", "")):
        fail("package.json: scripts.test must run test/validate.py (npm test is the documented check)")

# slash command must exist so /task-pipeline resolves, with proper frontmatter
cmd_path = os.path.join(ROOT, "plugins/task-pipeline/commands/task-pipeline.md")
if not os.path.isfile(cmd_path):
    fail("missing command: plugins/task-pipeline/commands/task-pipeline.md")
else:
    ctxt = open(cmd_path, encoding="utf-8").read()
    cm = re.match(r"^---\n(.*?)\n---\n", ctxt, re.S)
    if not cm:
        fail("command: no frontmatter")
    else:
        cfm = cm.group(1)
        if not re.search(r"^description:\s*\S", cfm, re.M):
            fail("command: empty/missing description in frontmatter")
        if not re.search(r"^argument-hint:\s*\S", cfm, re.M):
            fail("command: empty/missing argument-hint in frontmatter")

# top CHANGELOG entry must carry the same version as the manifests
chg_path = os.path.join(ROOT, "CHANGELOG.md")
if not os.path.isfile(chg_path):
    fail("missing root file: CHANGELOG.md")
else:
    chg = open(chg_path, encoding="utf-8").read()
    vm = re.search(r"^##\s*v(\d+\.\d+\.\d+)", chg, re.M)
    if not vm:
        fail("CHANGELOG.md: no '## vX.Y.Z' entry found")
    elif plg_ver and vm.group(1) != plg_ver:
        fail(f"version mismatch: CHANGELOG top entry=v{vm.group(1)} plugin.json={plg_ver!r}")

# every relative markdown link in repo docs must resolve. Links inside fenced code
# blocks are sample content (illustrative trees, template snippets), not links —
# strip the fences before scanning, or every example path becomes a false failure.
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^([ \t]*)(```+|~~~+).*?^\1\2[^\n]*$", re.M | re.S)
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
    for fn in filenames:
        if not fn.endswith(".md"):
            continue
        fp = os.path.join(dirpath, fn)
        body = FENCE_RE.sub("", open(fp, encoding="utf-8").read())
        for target in LINK_RE.findall(body):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            tpath = os.path.normpath(os.path.join(dirpath, target.split("#")[0]))
            if not os.path.exists(tpath):
                rel = os.path.relpath(fp, ROOT)
                fail(f"broken relative link in {rel}: {target}")

refdir = os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline/references")
for r in ("grill.md", "stages.md", "model-tiering.md", "conventions.md", "companion-skills.md", "artifacts.md"):
    if not os.path.isfile(os.path.join(refdir, r)):
        fail(f"missing reference: references/{r}")

# The pipeline is self-contained: every stage's doctrine ships inside the skill.
# These files ARE stages 2-6 — a missing or stub one silently turns a stage back
# into a dependency on someone else's plugin.
for r in (
    "brainstorm.md", "decomposition.md", "spec.md", "planning.md",
    "build.md", "review.md", "tdd.md", "acceptance.md", "loop-guard.md",
    "knowledge-sources.md", "audit.md",
):
    rp = os.path.join(refdir, r)
    if not os.path.isfile(rp):
        fail(f"missing built-in stage doctrine: references/{r}")
    elif os.path.getsize(rp) < 1500:
        fail(f"references/{r}: too small to be the stage's doctrine (stub?)")

# Progressive disclosure means an agent loads only what SKILL.md points it to,
# directly or transitively. A reference nothing links to is dead context: it
# ships, it passes every other check, and it is never read.
_skill_dir = os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline")
_seen, _frontier = set(), ["SKILL.md"]
while _frontier:
    _f = os.path.join(_skill_dir, _frontier.pop())
    if not os.path.isfile(_f):
        continue
    with open(_f, encoding="utf-8") as fh:
        for _m in re.finditer(r"references/([a-z0-9-]+\.md)", fh.read()):
            if _m.group(1) not in _seen:
                _seen.add(_m.group(1))
                _frontier.append(f"references/{_m.group(1)}")
for _orphan in sorted({f for f in os.listdir(refdir) if f.endswith(".md")} - _seen):
    fail(f"references/{_orphan}: unreachable from SKILL.md — dead context, wire it in or delete it")

# The open-source surface. These are the files a stranger looks for before they
# trust, use or contribute to the repo; one of them silently disappearing in a
# refactor is invisible in review and expensive at the moment someone needs it.
for r in ("README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md",
          "CODE_OF_CONDUCT.md", "CLAUDE.md"):
    if not os.path.isfile(os.path.join(ROOT, r)):
        fail(f"missing root file: {r}")

# The stage list is published on three surfaces an agent may read independently:
# SKILL.md's table (what it walks), references/stages.md (the per-stage detail and
# gate criteria) and pipeline.example.json (the machine-readable flow). Drift
# between them is invisible in review and lethal at runtime — a stage silently
# manual on one surface and auto on another, or a stage that exists in the config
# and has no doctrine. Compare ids, names and gate types across all three.
_sk_txt = open(skill_path, encoding="utf-8").read() if os.path.isfile(skill_path) else ""
_st_path = os.path.join(refdir, "stages.md")
_st_txt = open(_st_path, encoding="utf-8").read() if os.path.isfile(_st_path) else ""
_cfg_path = os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline/pipeline.example.json")
if os.path.isfile(_cfg_path) and _sk_txt and _st_txt:
    try:
        _stages_cfg = json.load(open(_cfg_path, encoding="utf-8")).get("stages") or []
    except Exception:
        _stages_cfg = []

    def _norm(name):
        return re.sub(r"[^a-z0-9+ ]", "", name.lower()).replace("  ", " ").strip()

    _cfg_rows = [(s.get("id"), _norm(str(s.get("name", ""))), (s.get("gate") or {}).get("type")) for s in _stages_cfg]
    _sk_rows = [
        (int(a), _norm(b), c)
        for a, b, c in re.findall(r"^\|\s*(\d+)\s*\|([^|]+)\|.*\|\s*(auto|manual)\s*\|\s*$", _sk_txt, re.M)
    ]
    _st_rows = []
    for _n, _title, _body in re.findall(r"^## (\d+) — (.*?)\n(.*?)(?=^## |\Z)", _st_txt, re.M | re.S):
        _g = re.findall(r"\*\*GATE \((auto|manual)\)", _body)
        _st_rows.append((int(_n), _norm(_title.split("—")[0]), _g[0] if _g else None))

    if [r[0] for r in _cfg_rows] != [r[0] for r in _sk_rows]:
        fail(f"stage ids differ: pipeline.example.json {[r[0] for r in _cfg_rows]} vs SKILL.md table {[r[0] for r in _sk_rows]}")
    if [r[0] for r in _cfg_rows] != [r[0] for r in _st_rows]:
        fail(f"stage ids differ: pipeline.example.json {[r[0] for r in _cfg_rows]} vs references/stages.md {[r[0] for r in _st_rows]}")
    for _c, _s in zip(_cfg_rows, _sk_rows):
        if _c[2] != _s[2]:
            fail(f"stage {_c[0]}: gate type differs — pipeline.example.json {_c[2]!r} vs SKILL.md {_s[2]!r}")
        if _c[1] not in _s[1] and _s[1] not in _c[1]:
            fail(f"stage {_c[0]}: name differs — pipeline.example.json {_c[1]!r} vs SKILL.md {_s[1]!r}")
    for _c, _t in zip(_cfg_rows, _st_rows):
        if _t[2] is None:
            fail(f"references/stages.md stage {_t[0]}: no '**GATE (auto|manual)**' line — every stage states its gate")
        elif _c[2] != _t[2]:
            fail(f"stage {_c[0]}: gate type differs — pipeline.example.json {_c[2]!r} vs references/stages.md {_t[2]!r}")
        if _c[1] not in _t[1] and _t[1] not in _c[1]:
            fail(f"stage {_c[0]}: name differs — pipeline.example.json {_c[1]!r} vs references/stages.md {_t[1]!r}")

# Cursor channel: every cursor/rules/*.mdc must carry `description` + `alwaysApply`
# frontmatter (Cursor copies these into foreign projects, so no relative links —
# not machine-checked here, but keep content self-contained).
cursor_dir = os.path.join(ROOT, "cursor", "rules")
mdcs = [f for f in os.listdir(cursor_dir) if f.endswith(".mdc")] if os.path.isdir(cursor_dir) else []
if not mdcs:
    fail("cursor/rules: no .mdc rules found")
for f in mdcs:
    mtxt = open(os.path.join(cursor_dir, f), encoding="utf-8").read()
    mm = re.match(r"^---\n(.*?)\n---\n", mtxt, re.S)
    if not mm:
        fail(f"cursor/rules/{f}: no frontmatter")
        continue
    mfm = mm.group(1)
    if not re.search(r"^description:\s*\S", mfm, re.M):
        fail(f"cursor/rules/{f}: empty/missing description")
    if not re.search(r"^alwaysApply:\s*(true|false)\s*$", mfm, re.M):
        fail(f"cursor/rules/{f}: alwaysApply must be true or false")

# templates/: skeletons this plugin seeds into a host project (the stage-0 brief).
tpl_dir = os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline/templates")
if not os.path.isdir(tpl_dir):
    fail("missing skill templates/ directory")
elif [t for t in ("brief.md", "carryover.md", "context.md", "adr.md") if not os.path.isfile(os.path.join(tpl_dir, t))]:
    for t in ("brief.md", "carryover.md", "context.md", "adr.md"):
        if not os.path.isfile(os.path.join(tpl_dir, t)):
            fail(f"missing template: plugins/task-pipeline/skills/task-pipeline/templates/{t}")
else:
    # The brief carries the stage-0 autonomy sweep — stages 1-10 read it instead of
    # asking. Without that section the grill has no place to record the answers and
    # the autonomy promise silently degrades into mid-flight questions.
    brief = open(os.path.join(tpl_dir, "brief.md"), encoding="utf-8").read()
    if not re.search(r"^##\s+Autonomy\b", brief, re.M):
        fail("templates/brief.md: missing the '## Autonomy' section (the stage-0 autonomy sweep)")
    # The REQ spine is what stages 3-5 trace to and what stage 10 accounts for.
    # Without it in the template the grill has nowhere to write requirements, the
    # stage-4 set-comparison has nothing to compare, and acceptance degrades into
    # recalling the task from memory — the exact failure the spine exists to stop.
    if not re.search(r"^##\s+Requirements\b", brief, re.M):
        fail("templates/brief.md: missing the '## Requirements' section (the REQ spine)")
    if "REQ-001" not in brief:
        fail("templates/brief.md: Requirements section has no REQ-NNN example row")
    if not re.search(r"How it's verified", brief):
        fail("templates/brief.md: the REQ table must carry a \"How it's verified\" column — "
             "a requirement with no named check is what makes acceptance green over a gap")
    # Stage 0 phase 1 writes the source ledger here, BEFORE the first question, and
    # stage 9 reads it back as its work list. Without the section the harvest has
    # nowhere to land: the grill degrades to asking from memory, and "docs updated"
    # silently narrows to whatever files the change happened to touch.
    if not re.search(r"^##\s+Knowledge sources\b", brief, re.M):
        fail("templates/brief.md: missing the '## Knowledge sources' section "
             "(the stage-0 harvest ledger that stage 9 updates)")
    # The autonomy sweep lives twice: grill.md's table is what the agent READS while
    # interviewing, brief.md's is what it WRITES. They drift silently — a row added
    # to one is simply never asked, or never recorded, and the autonomy promise
    # degrades into a mid-flight question with nothing to show it was ever dropped.
    # Compare the stage numbers each table covers, not the wording.
    def _sweep_stages(text):
        m = re.search(r"^\|\s*(?:Stage|run-wide)\b.*?\n(?:\|[-: |]+\|\n)?((?:\|.*\n)+)",
                      text, re.M)
        if not m:
            return None
        covered = set()
        for row in m.group(1).splitlines():
            cell = row.split("|")[1] if row.count("|") > 1 else ""
            covered.update(int(n) for n in re.findall(r"\d+", cell))
        return covered

    _grill_p = os.path.join(refdir, "grill.md")
    if os.path.isfile(_grill_p):
        _g = _sweep_stages(open(_grill_p, encoding="utf-8").read().split("## The autonomy sweep")[-1])
        _b = _sweep_stages(brief.split("## Autonomy")[-1])
        if _g is None or _b is None:
            fail("autonomy sweep: could not find the table in references/grill.md "
                 "and/or templates/brief.md — the sweep must be a table in both")
        elif _g != _b:
            fail(f"autonomy sweep drift: references/grill.md covers stages {sorted(_g)} "
                 f"but templates/brief.md covers {sorted(_b)} — one is what the grill "
                 "asks, the other is what the brief records; a row in only one is a "
                 "question never asked or an answer never written down")

# No hardcoded vendor model ids in anything we ship: model generations ship and get
# renamed, and the operator may be on another provider entirely. Stage configs use
# provider-agnostic tokens; prose names a TIER ("the most capable model available"),
# never a string. See references/model-tiering.md.
VENDOR_MODEL_RE = re.compile(r"\b(?:claude-[a-z]+-\d|gpt-\d|gemini-\d|grok-\d|llama-?\d)", re.I)
model_scan = [
    os.path.join(ROOT, "README.md"),
    os.path.join(ROOT, "plugins/task-pipeline/commands/task-pipeline.md"),
]
for base in (
    os.path.join(ROOT, "plugins/task-pipeline/skills/task-pipeline"),
    os.path.join(ROOT, "cursor", "rules"),
):
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        model_scan += [
            os.path.join(dirpath, fn)
            for fn in filenames
            if fn.endswith((".md", ".mdc", ".json"))
        ]
for fp in model_scan:
    if not os.path.isfile(fp):
        continue
    for lineno, line in enumerate(open(fp, encoding="utf-8"), start=1):
        hit = VENDOR_MODEL_RE.search(line)
        if hit:
            rel = os.path.relpath(fp, ROOT)
            fail(
                f"hardcoded model id {hit.group(0)!r} in {rel}:{lineno} — "
                "name the tier, not the id (see references/model-tiering.md)"
            )

# Pipeline config is generic: pipeline.schema.json is the universal contract,
# pipeline.example.json is a copy-and-rewrite example. The framework ships NO
# project-specific config, no fixed stage count, no opinion on which stages are
# manual vs auto — that is all the host project's config. We validate that the
# schema is well-formed and that the example conforms to it (dependency-free shape
# check below; plus a full jsonschema pass when the library is available).
SKILL_DIR = "plugins/task-pipeline/skills/task-pipeline"
SCHEMA_REL = f"{SKILL_DIR}/pipeline.schema.json"
EXAMPLE_REL = f"{SKILL_DIR}/pipeline.example.json"
GATE_TYPES = {"auto", "manual"}
# 'default' = the model confirmed for the run; 'inherit' = whatever the operator is on.
MODEL_TOKENS = {"default", "inherit"}

schema = load_json(SCHEMA_REL)
if schema is not None and schema.get("type") != "object":
    fail(f"{SCHEMA_REL}: not a JSON Schema (missing top-level type: object)")

pipe = load_json(EXAMPLE_REL)
if pipe is not None:
    stages = pipe.get("stages")
    if not isinstance(stages, list) or not stages:
        fail(f"{EXAMPLE_REL}: stages[] must be a non-empty list")
    else:
        seen_states = set()
        for i, st in enumerate(stages, start=1):
            where = f"{EXAMPLE_REL} stage[{i}]"
            if not isinstance(st, dict):
                fail(f"{where}: not an object")
                continue
            state = st.get("state")
            if not (isinstance(state, str) and state.strip()):
                fail(f"{where}: empty/missing state")
            elif state in seen_states:
                fail(f"{where}: duplicate state {state!r}")
            else:
                seen_states.add(state)
            skills = st.get("skills")
            if not (isinstance(skills, list) and skills and all(isinstance(s, str) and s.strip() for s in skills)):
                fail(f"{where}: skills[] must be a non-empty list of non-empty strings")
            # Models are provider-agnostic: a vendor id goes stale as generations
            # ship and may not exist on the operator's provider at all.
            model = st.get("model")
            if model is not None and model not in MODEL_TOKENS:
                fail(f"{where}: model must be a provider-agnostic token {sorted(MODEL_TOKENS)}, got {model!r}")
            gate = st.get("gate")
            if not isinstance(gate, dict):
                fail(f"{where}: gate missing or not an object")
            else:
                if gate.get("type") not in GATE_TYPES:
                    fail(f"{where}: gate.type must be one of {sorted(GATE_TYPES)}, got {gate.get('type')!r}")
                if not (isinstance(gate.get("check"), str) and gate.get("check").strip()):
                    fail(f"{where}: empty/missing gate.check")

    # Stage 0 is the mandatory intake grill: its gate must be manual (the operator
    # confirms the brief) and must state that the stage is mandatory, so the
    # config can't drift from the doctrine in references/stages.md.
    if isinstance(stages, list) and stages:
        s0 = stages[0] if isinstance(stages[0], dict) else {}
        s0_gate = s0.get("gate") if isinstance(s0.get("gate"), dict) else {}
        s0_check = str(s0_gate.get("check", "")).lower()
        if s0_gate.get("type") != "manual":
            fail(f"{EXAMPLE_REL} stage[1]: the intake grill gate must be 'manual' (the operator confirms the brief)")
        if "mandatory" not in s0_check:
            fail(f"{EXAMPLE_REL} stage[1]: gate.check must state that the intake grill is MANDATORY (never skipped)")
        # The interview is phase 2. Dropping phase 1 from the gate turns the grill
        # back into asking from memory: answers stop being checkable against
        # anything, and stage 9 loses the list of sources it is supposed to update.
        if "ledger" not in s0_check or not re.search(r"harvest|knowledge source", s0_check):
            fail(f"{EXAMPLE_REL} stage[1]: gate.check must require the phase-1 knowledge harvest and "
                 "its source ledger before the interview (see references/knowledge-sources.md)")
        # Stage 9 is the other half of that loop.
        s9 = next((s for s in stages if isinstance(s, dict) and s.get("state") == "docs-wiki"), None)
        if s9 is not None and "ledger" not in str((s9.get("gate") or {}).get("check", "")).lower():
            fail(f"{EXAMPLE_REL} stage 'docs-wiki': gate.check must name the stage-0 source ledger as its "
                 "work list — a source read at stage 0 and left wrong is the next run's false premise")

    # No required external skill provider may sit in the default flow: the example
    # config is what a host project copies, so a foreign `plugin:skill` entry there
    # reintroduces exactly the dependency this skill ported in-house. Substituting
    # one is the operator's call in THEIR pipeline.json (see companion-skills.md ->
    # Optional bridge), never the shipped default.
    FORBIDDEN_SKILL_PREFIXES = ("superpowers:", "grill-me", "grilling")
    if isinstance(stages, list):
        for i, st in enumerate(stages, start=1):
            if not isinstance(st, dict):
                continue
            for s in st.get("skills") or []:
                if isinstance(s, str) and s.strip().lower().startswith(FORBIDDEN_SKILL_PREFIXES):
                    fail(
                        f"{EXAMPLE_REL} stage[{i}]: skills[] names {s!r} — the default flow must run on "
                        "the built-in doctrine (references/*.md), not an external provider"
                    )

    # The shipped default flow must close the circle: the last stage is acceptance,
    # and it is manual. Every earlier gate asks "is this artifact good?"; only this
    # one asks "does this still contain everything that was asked for?" — and only
    # the person who asked can answer that, so an auto gate here would be a lie.
    # (Host projects are unconstrained: pipeline.schema.json fixes no stage count.
    # This checks the EXAMPLE we ship.)
    if isinstance(stages, list) and stages:
        last = stages[-1] if isinstance(stages[-1], dict) else {}
        last_gate = last.get("gate") if isinstance(last.get("gate"), dict) else {}
        if last.get("state") != "acceptance":
            fail(f"{EXAMPLE_REL}: the default flow's last stage must be 'acceptance' "
                 f"(the REQ close-out), got {last.get('state')!r}")
        elif last_gate.get("type") != "manual":
            fail(f"{EXAMPLE_REL}: the acceptance gate must be 'manual' — a green table "
                 "is not the operator confirming it is what they asked for")
        elif "evidence" not in str(last_gate.get("check", "")).lower():
            fail(f"{EXAMPLE_REL}: the acceptance gate.check must require EVIDENCE per "
                 "requirement — 'done' without evidence is the gap this stage exists to catch")
        # The REQ table compares two lists, so it can only find a requirement that was
        # NAMED and lost. A requirement nobody ever wrote appears on neither side —
        # an absence has one side, and no comparison finds it. The ladder walk
        # (references/audit.md) is the only pass in the flow that can, and it has to
        # run BEFORE the table or its findings arrive too late to become rows.
        _acc_chk = str(last_gate.get("check", "")).lower()
        if "ladder" not in _acc_chk or "absence" not in _acc_chk:
            fail(f"{EXAMPLE_REL}: the acceptance gate.check must require the LADDER WALK "
                 "(references/audit.md) before the coverage table, and must say that an "
                 "absence becomes a new REQ row — the table alone cannot find what was "
                 "never written")
        # The brief->plan seam is where scope leaks silently, so the plan gate must
        # state the mechanical set comparison, not a judgement call.
        plan = next((st for st in stages if isinstance(st, dict) and st.get("state") == "plan"), None)
        if plan is not None:
            pchk = str((plan.get("gate") or {}).get("check", "")).upper()
            if "SET EQUALITY" not in pchk or "REQ" not in pchk:
                fail(f"{EXAMPLE_REL} stage 'plan': gate.check must require SET EQUALITY between "
                     "the brief's REQ ids and the union of Implements: across tasks")

    # Release config is optional and individually toggleable. If present, shape-check it.
    rel = pipe.get("release")
    if rel is not None:
        if not isinstance(rel, dict):
            fail(f"{EXAMPLE_REL}: release must be an object")
        else:
            if not isinstance(rel.get("enabled"), bool):
                fail(f"{EXAMPLE_REL}: release.enabled must be a boolean (the on/off toggle)")
            if "trigger" in rel and rel["trigger"] not in {"tag", "manual", "push", "none"}:
                fail(f"{EXAMPLE_REL}: release.trigger must be one of ['manual','none','push','tag'], got {rel['trigger']!r}")
            for key in ("steps", "verify"):
                if key in rel:
                    v = rel[key]
                    if not (isinstance(v, list) and v and all(isinstance(s, str) and s.strip() for s in v)):
                        fail(f"{EXAMPLE_REL}: release.{key} must be a non-empty list of non-empty strings")
            # If this repo declares release automation ON, it must ship the workflow that implements it.
            if rel.get("enabled") is True and not os.path.isfile(os.path.join(ROOT, ".github/workflows/release.yml")):
                fail("release.enabled is true but .github/workflows/release.yml is missing")

    # Full schema validation when jsonschema is installed (optional — the shape
    # check above is the dependency-free guarantee, so CI stays green without it).
    if schema is not None:
        try:
            import jsonschema  # type: ignore
            try:
                jsonschema.validate(instance=pipe, schema=schema)
            except jsonschema.ValidationError as e:  # pragma: no cover - only with the lib
                fail(f"{EXAMPLE_REL}: does not conform to pipeline.schema.json: {e.message}")
        except ImportError:
            pass

# A stage added at the END of the flow is the one every human-written blurb forgets:
# the pipeline grows a tenth stage and six descriptions still enumerate nine, or list
# the new one before the stage it runs after. Those blurbs are the only thing a user
# reads on npm and in the marketplace, so drift there ships a wrong flow to every
# install. Derive the last stage from the config and hold every surface to it.
_pipe_stages = (pipe or {}).get("stages") if isinstance(pipe, dict) else None
if isinstance(_pipe_stages, list) and _pipe_stages and isinstance(_pipe_stages[-1], dict):
    _last = str(_pipe_stages[-1].get("state") or "")
    _prev = str(_pipe_stages[-2].get("state") or "") if len(_pipe_stages) > 1 else ""
    # (surface label, text) — every place the flow is enumerated for a human.
    _blurbs = []

    def _add_blurb(label, path, extract=None):
        p = os.path.join(ROOT, path)
        if not os.path.isfile(p):
            return
        raw = open(p, encoding="utf-8").read()
        _blurbs.append((label, extract(raw) if extract else raw))

    def _json_desc(key_path):
        def _x(raw):
            try:
                d = json.loads(raw)
            except Exception:
                return ""
            for k in key_path:
                d = (d or {})[k] if not isinstance(k, int) else (d or [])[k]
            return str(d or "")
        return _x

    def _frontmatter_desc(raw):
        m = re.match(r"^---\n(.*?)\n---\n", raw, re.S)
        if not m:
            return ""
        d = re.search(r"^description:\s*(.+)$", m.group(1), re.M)
        return d.group(1) if d else ""

    _add_blurb("package.json description", "package.json", _json_desc(["description"]))
    _add_blurb("marketplace.json plugin description", ".claude-plugin/marketplace.json",
               _json_desc(["plugins", 0, "description"]))
    _add_blurb("plugin.json description", "plugins/task-pipeline/.claude-plugin/plugin.json",
               _json_desc(["description"]))
    _add_blurb("SKILL.md description", f"{SKILL_DIR}/SKILL.md", _frontmatter_desc)
    _add_blurb("command description", "plugins/task-pipeline/commands/task-pipeline.md", _frontmatter_desc)
    _add_blurb("cursor rule description", "cursor/rules/task-pipeline.mdc", _frontmatter_desc)
    _add_blurb("README", "README.md")

    def _spellings(state):
        """A config state key ('docs-wiki') is written several ways in prose."""
        s = state.lower()
        return {s, s.replace("-", "/"), s.replace("-", " "), s.replace("-", " + "), s.replace("-", "")}

    def _first_index(text, state):
        """First mention — an enumeration names each stage once; a later incidental
        mention ("reads deploy/docs/wiki conventions") is not part of the list."""
        hits = [text.index(v) for v in _spellings(state) if v and v in text]
        return min(hits) if hits else None

    for _label, _text in _blurbs:
        low = _text.lower()
        _i_last = _first_index(low, _last) if _last else None
        if _last and _i_last is None:
            fail(f"{_label}: never names the flow's final stage {_last!r} — "
                 "a description that stops one stage short is what ships to npm and the marketplace")
        # …and it must come last: listing acceptance before docs/wiki inverts the flow.
        _i_prev = _first_index(low, _prev) if _prev else None
        if _i_last is not None and _i_prev is not None and _i_last < _i_prev:
            fail(f"{_label}: stage {_last!r} is listed before {_prev!r} — the enumeration "
                 "contradicts the order in pipeline.example.json")

    # The per-task review's verdict count lives in five files. When it changed from two
    # to three, three of them kept saying "both verdicts" — and the shipped reviewer
    # prompt is what actually decides how many come back.
    _dev = next((s for s in _pipe_stages if isinstance(s, dict) and s.get("state") == "dev"), None)
    if _dev and "three verdicts" in str((_dev.get("gate") or {}).get("check", "")).lower():
        for _rel in (f"{SKILL_DIR}/references/review.md", f"{SKILL_DIR}/references/build.md",
                     f"{SKILL_DIR}/references/planning.md", f"{SKILL_DIR}/references/stages.md",
                     "cursor/rules/task-pipeline.mdc"):
            _p = os.path.join(ROOT, _rel)
            if not os.path.isfile(_p):
                continue
            _body = open(_p, encoding="utf-8").read()
            for _lineno, _line in enumerate(_body.splitlines(), start=1):
                if re.search(r"(two|\*{0,2}both\*{0,2})\s+(review\s+)?verdicts", _line, re.I):
                    fail(f"{_rel}:{_lineno}: says two/both verdicts, but the dev gate declares three "
                         "(spec compliance, REQ satisfied, code quality)")

    # Each stage's doctrine file states its own GATE type. If it disagrees with the
    # config, an agent reading the doctrine gates differently than the flow says.
    for _fn, _sid in (("brainstorm.md", 2), ("spec.md", 3), ("planning.md", 4),
                      ("build.md", 5), ("tdd.md", 6), ("acceptance.md", 10)):
        _p = os.path.join(refdir, _fn)
        _cfg = next((s for s in _pipe_stages if isinstance(s, dict) and s.get("id") == _sid), None)
        if not os.path.isfile(_p) or _cfg is None:
            continue
        _m = re.search(r"GATE\s*\([^)]*?(auto|manual)", open(_p, encoding="utf-8").read())
        if not _m:
            fail(f"references/{_fn}: no 'GATE (auto|manual)' line — every stage doctrine states its gate")
        elif _m.group(1) != (_cfg.get("gate") or {}).get("type"):
            fail(f"references/{_fn}: gate type {_m.group(1)!r} contradicts stage {_sid} in "
                 f"{EXAMPLE_REL} ({(_cfg.get('gate') or {}).get('type')!r})")

if errors:
    print("FAIL: task-pipeline structure invalid")
    for e in errors:
        print(" - " + e)
    sys.exit(1)
print("PASS: task-pipeline structure valid")
