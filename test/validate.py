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
for r in ("brainstorm.md", "spec.md", "planning.md", "build.md", "review.md", "tdd.md"):
    rp = os.path.join(refdir, r)
    if not os.path.isfile(rp):
        fail(f"missing built-in stage doctrine: references/{r}")
    elif os.path.getsize(rp) < 1500:
        fail(f"references/{r}: too small to be the stage's doctrine (stub?)")

for r in ("README.md", "LICENSE"):
    if not os.path.isfile(os.path.join(ROOT, r)):
        fail(f"missing root file: {r}")

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
elif [t for t in ("brief.md", "context.md", "adr.md") if not os.path.isfile(os.path.join(tpl_dir, t))]:
    for t in ("brief.md", "context.md", "adr.md"):
        if not os.path.isfile(os.path.join(tpl_dir, t)):
            fail(f"missing template: plugins/task-pipeline/skills/task-pipeline/templates/{t}")
else:
    # The brief carries the stage-0 autonomy sweep — stages 1-9 read it instead of
    # asking. Without that section the grill has no place to record the answers and
    # the autonomy promise silently degrades into mid-flight questions.
    brief = open(os.path.join(tpl_dir, "brief.md"), encoding="utf-8").read()
    if not re.search(r"^##\s+Autonomy\b", brief, re.M):
        fail("templates/brief.md: missing the '## Autonomy' section (the stage-0 autonomy sweep)")

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
        if s0_gate.get("type") != "manual":
            fail(f"{EXAMPLE_REL} stage[1]: the intake grill gate must be 'manual' (the operator confirms the brief)")
        if "mandatory" not in str(s0_gate.get("check", "")).lower():
            fail(f"{EXAMPLE_REL} stage[1]: gate.check must state that the intake grill is MANDATORY (never skipped)")

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

if errors:
    print("FAIL: task-pipeline structure invalid")
    for e in errors:
        print(" - " + e)
    sys.exit(1)
print("PASS: task-pipeline structure valid")
