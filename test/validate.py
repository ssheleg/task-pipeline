#!/usr/bin/env python3
"""Structural validator for the task-pipeline skill repo. Exit 0 = pass."""
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "task-pipeline"
errors = []


LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^([ \t]*)(```+|~~~+).*?^\1\2[^\n]*$", re.M | re.S)


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
            # Anthropic's authoring guidance: the description "must include both what
            # the Skill does and when Claude should use it", written in third person,
            # and their own examples lead with the capability — "Extracts text and
            # tables from PDF files… Use when working with PDF files."
            #
            # This used to demand the string start with "Use when", which enforced the
            # WHEN half and let the WHAT half be optional. The rule now checks what the
            # guidance actually asks for: a capability statement, then the trigger.
            _uw = desc.find("Use when")
            if _uw < 0:
                fail("SKILL.md: description has no 'Use when …' clause — the trigger half "
                     "is what Claude matches a request against")
            elif _uw < 40:
                fail("SKILL.md: description opens with the trigger and never says what the "
                     "skill DOES — lead with the capability in third person, then 'Use when …' "
                     "(Anthropic skill-authoring guidance)")
            if len(desc) > 1024:
                fail(f"SKILL.md: description is {len(desc)} chars, the limit is 1024")
            if re.search(r"\b(I can|I'll|you can use this)\b", desc, re.I):
                fail("SKILL.md: description must be third person — it is injected into the "
                     "system prompt, and a first/second-person voice breaks discovery")
            if not re.search(r"[а-яё]", desc, re.I):
                fail("SKILL.md: description must carry Russian trigger aliases beside the English ones (canon)")
        # The PLATFORM limit is 1024 on `description` alone (checked above). This is
        # OURS, and it is a budget rather than a contract: the whole frontmatter is
        # preloaded into the system prompt for every session, so it stays bounded.
        # It used to be 1024 — the same number as the platform's — which silently
        # made the usable description ~975 and read as if it were the real rule.
        # Two different limits must not wear one number.
        if len(fm) > 1200:
            fail(f"SKILL.md: frontmatter is {len(fm)} chars, over this repo's budget "
                 "of 1200 (the platform's own limit is 1024 on `description` alone, "
                 "checked separately)")

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
    # README ships in the package, so every relative link in it must resolve INSIDE
    # the package too. It did not: SKILL-CARD.md and the whole evals/ directory were
    # excluded from files[] while the README pointed at both, and CONTRIBUTING /
    # SECURITY / CODE_OF_CONDUCT had been dangling for npm consumers for far longer.
    # references/learned.md rule 14 — a document may not send a reader to something
    # absent — applied to the artefact that is actually published.
    _rd_p = os.path.join(ROOT, "README.md")
    if os.path.isfile(_rd_p):
        _rd = FENCE_RE.sub("", open(_rd_p, encoding="utf-8").read())
        for _t in sorted({t for t in LINK_RE.findall(_rd)
                          if not t.startswith(("http://", "https://", "mailto:", "#"))}):
            _top = _t.split("/")[0].split("#")[0]
            if _top and _top not in files:
                fail(f"README.md links to {_t!r}, which package.json files[] does not "
                     f"ship ({_top!r} missing) — the link dangles for every npm install")
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
    # The documentation track (v1.7.0): docs are a deliverable with a gate, the
    # gate is an artefact somebody has to write, and a hook is the only mechanism
    # that can stop a bad edit before it lands. A stub here turns each of those
    # back into "the agent will remember", which is the state the track ends.
    "documentation.md", "gates.md", "hooks.md",
):
    rp = os.path.join(refdir, r)
    if not os.path.isfile(rp):
        fail(f"missing built-in stage doctrine: references/{r}")
    elif os.path.getsize(rp) < 1500:
        fail(f"references/{r}: too small to be the stage's doctrine (stub?)")

# Anthropic's Skill authoring guidance: "For reference files longer than 100 lines,
# include a table of contents at the top. This ensures Claude can see the full scope
# of available information even when previewing with partial reads." That preview is
# real — a long file gets `head -100`'d, and references/stages.md is 500 lines: an
# agent could read stages 0 and 1 and never learn stage 9 exists.
#
# The list is COMPARED against the headings, not merely required to be present. A
# contents list restated by hand is a second source that goes stale on the next
# heading — the failure references/documentation.md is written against.
for _fn in sorted(os.listdir(refdir)):
    if not _fn.endswith(".md"):
        continue
    _p = os.path.join(refdir, _fn)
    _txt = open(_p, encoding="utf-8").read()
    if _txt.count("\n") <= 100:
        continue
    _heads, _infence = [], False
    for _ln in _txt.split("\n"):
        if re.match(r"^\s*(```|~~~)", _ln):
            _infence = not _infence
            continue
        if not _infence and _ln.startswith("## "):
            _heads.append(_ln[3:].strip())
    if "Contents" not in _heads:
        fail(f"references/{_fn}: {_txt.count(chr(10))} lines and no '## Contents' — a "
             "reference over 100 lines needs one, or a partial read shows an agent "
             "only the sections that happen to come first")
        continue
    _m = re.search(r"^## Contents\s*\n\n((?:- .*\n)+)", _txt, re.M)
    _listed = [l[2:].strip() for l in _m.group(1).splitlines()] if _m else []
    _expected = [h for h in _heads if h != "Contents"]
    if _listed != _expected:
        _missing = [h for h in _expected if h not in _listed]
        _stale = [h for h in _listed if h not in _expected]
        fail(f"references/{_fn}: the Contents list disagrees with the headings — "
             f"missing {_missing or '[]'}, stale {_stale or '[]'}"
             + ("" if _missing or _stale else " (same items, wrong order)"))

# A section-qualified cross-reference — [`file.md`](file.md) → *Section* — must name
# a section that EXISTS in that file. The link checker proves the file resolves and
# stops there, which is exactly the hole references/learned.md keeps as a review
# question: "a stale reference was replaced with a FALSE one — the new target existed
# and said nothing about the subject."
#
# Found by sweeping: 15 broken pointers in one pass, including eleven that sent the
# reader to a section about something else entirely. Measured before being trusted
# (learned.md rule 10): whitespace is normalised first, because a citation wrapped
# across two lines is not a defect and reported six of them as one.
def _sections_of(path):
    out, infence = [], False
    for _ln in open(path, encoding="utf-8"):
        if re.match(r"^\s*(```|~~~)", _ln):
            infence = not infence
            continue
        if not infence and re.match(r"^#{2,4} ", _ln):
            out.append(re.sub(r"\s+", " ", re.sub(r"^#+\s*", "", _ln)).strip().lower())
    return out


_sec_cache, _bad_cites = {}, []
for _src in ["SKILL.md"] + [f"references/{f}" for f in sorted(os.listdir(refdir))
                            if f.endswith(".md")]:
    _sp = os.path.join(_skill_root := os.path.dirname(refdir), _src)
    if not os.path.isfile(_sp):
        continue
    _flat = re.sub(r"\s+", " ", open(_sp, encoding="utf-8").read())
    for _tgt, _sec in re.findall(
            r"\[`([a-z0-9-]+\.md)`\]\([^)]*\)\s*(?:→|->)\s*\*([^*]+)\*", _flat):
        _tp = os.path.join(refdir, _tgt)
        if not os.path.isfile(_tp):
            _bad_cites.append(f"{_src} cites {_tgt} → *{_sec.strip()}* — no such file")
            continue
        _sec_cache.setdefault(_tp, _sections_of(_tp))
        _s = re.sub(r"\s+", " ", _sec).strip().lower().rstrip(".,;")
        if not any(_s == _h or _s in _h or _h in _s for _h in _sec_cache[_tp]):
            _bad_cites.append(
                f"{_src} cites {_tgt} → *{_sec.strip()}*, which has no such section")
for _b in sorted(set(_bad_cites)):
    fail(_b + " — a citation whose file resolves and whose section does not is the "
               "one a link checker cannot catch and a reader believes")

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

# Compute, never restate (references/learned.md rule 8) — applied to this repo's own
# prose. The guard count is stated in living documents, and two of them silently
# claimed 46 after the suite reached 50: a number written by hand is a number that
# goes stale on the next commit. CHANGELOG entries are exempt on purpose — they are
# records of what a past release shipped, not claims about now.
_neg_wf = os.path.join(ROOT, ".github/workflows/validate.yml")
if os.path.isfile(_neg_wf):
    _neg_n = len(re.findall(r"^\s*- name:\s*Negative self-test",
                            open(_neg_wf, encoding="utf-8").read(), re.M))
    for _living in ("README.md", "SKILL-CARD.md", "evals/RESULTS.md"):
        _lp = os.path.join(ROOT, _living)
        if not os.path.isfile(_lp):
            continue
        for _m in re.finditer(r"\b(\d+)\+?\s+(?:of\s+\d+\s+)?(?:structural\s+)?guards\b",
                              open(_lp, encoding="utf-8").read()):
            if int(_m.group(1)) != _neg_n:
                fail(f"{_living}: states {_m.group(0)!r} but the workflow defines "
                     f"{_neg_n} negative self-tests — derive the number or delete it")

# references/artifacts.md maps stage -> what it WRITES. The reverse direction — what
# each stage READS and from where — is the one an agent actually needs at runtime,
# and it was absent for nine releases: learned.md rule 2 (compute the mapping in both
# directions) unapplied to this file itself. A stage whose inputs are unnamed reads
# whatever the context happens to hold.
_art = os.path.join(refdir, "artifacts.md")
if os.path.isfile(_art):
    _at = open(_art, encoding="utf-8").read()
    for _needle, _what in (("Stage → input map", "the stage → input map"),
                           ("Project-saved rules", "the project-saved-rules map"),
                           ("Stage → artifact map", "the stage → artifact map")):
        if _needle not in _at:
            fail(f"references/artifacts.md: no {_what} — the stage/artifact relation "
                 "must be mapped in BOTH directions, or one of them is assumed")

# CONTRIBUTING.md claims to be "what the validator enforces". It was eight guards
# behind when an audit measured it — the same class as the Cursor rule, on the
# contributor-facing surface, and the previous fix (references -> README + manifest)
# was scoped to its instance rather than the class. So the claim is now checked like
# any other claim: an invariant that names a guard literal must name one this file
# actually prints.
_contrib = os.path.join(ROOT, "CONTRIBUTING.md")
if os.path.isfile(_contrib):
    _ct = open(_contrib, encoding="utf-8").read()
    _self = open(os.path.abspath(__file__), encoding="utf-8").read()
    _cited = re.findall(r"\*\(guard: `([^`]+)`\)\*", _ct)
    if len(_cited) < 8:
        fail("CONTRIBUTING.md: only %d invariant(s) name the guard that enforces them "
             "— a list that claims to be 'what the validator enforces' and cites "
             "nothing drifts silently" % len(_cited))
    for _lit in _cited:
        if _lit not in _self:
            fail("CONTRIBUTING.md names a guard whose message does not appear in "
                 "test/validate.py: %r — the invariant claims an enforcement that "
                 "does not exist" % _lit)

# A new reference has to REACH the surfaces a human and a foreign agent read. Three
# instances in two releases: adoption.md, setup.md and portability.md landed and the
# README's map and the portability manifest never heard of two of them. Reachability
# from SKILL.md was green throughout — that check proves an agent can find the file,
# not that anybody was told it exists. Absence has one side, so it needs its own check.
_readme_p = os.path.join(ROOT, "README.md")
_port_p = os.path.join(refdir, "portability.md")
if os.path.isfile(_readme_p) and os.path.isfile(_port_p):
    _rd_txt = open(_readme_p, encoding="utf-8").read()
    _pt_txt = open(_port_p, encoding="utf-8").read()
    for _ref in sorted(f for f in os.listdir(refdir) if f.endswith(".md")):
        if _ref not in _pt_txt:
            fail("references/%s is not in references/portability.md's manifest — a "
                 "workflow decision with no manifest row is one nobody can check "
                 "travels with the bundle" % _ref)
        if _ref not in _rd_txt:
            fail("references/%s is named nowhere in README.md — it ships and no "
                 "reader is told it exists" % _ref)

# The portability manifest is the outward half of the check in
# references/portability.md: every WORKFLOW decision must have a home inside the
# bundle. A row naming a path that does not resolve here is a decision that was made
# and then left somewhere that does not travel — the fork that file exists to catch.
_port = os.path.join(refdir, "portability.md")
if not os.path.isfile(_port):
    fail("missing built-in doctrine: references/portability.md — without the manifest "
         "nothing checks that workflow decisions live inside the bundle")
else:
    _pt = open(_port, encoding="utf-8").read()
    _skill_root2 = os.path.dirname(refdir)
    _man = re.search(r"^## The manifest.*?\n(.*?)(?=^## )", _pt, re.M | re.S)
    if not _man:
        fail("references/portability.md: no manifest section")
    else:
        _rows = [l for l in _man.group(1).splitlines() if l.startswith("|") and "`" in l]
        if len(_rows) < 10:
            fail("references/portability.md: manifest has %d row(s) — it enumerates "
                 "every workflow decision, not a sample" % len(_rows))
        for _row in _rows:
            for _path in re.findall(r"`([a-zA-Z0-9_./-]+\.(?:md|json|sh))`", _row):
                if not os.path.isfile(os.path.join(_skill_root2, _path)):
                    fail("references/portability.md: manifest names %r, which does not "
                         "resolve inside the bundle — a workflow decision whose home is "
                         "outside the bundle does not travel with it" % _path)

for _f, _needles in (
    ("setup.md", ("What it inspects", "The finding shape", "inward check",
                  "Offer, never write")),
    ("companion-skills.md", ("Is this skill itself current", "sshlg-skills@latest update")),
    ("brainstorm.md", ("User paths are a design output", "error paths")),
):
    _p2 = os.path.join(refdir, _f)
    if not os.path.isfile(_p2):
        fail("missing reference: references/" + _f)
        continue
    _b = open(_p2, encoding="utf-8").read()
    for _n in _needles:
        if _n not in _b:
            fail("references/%s: missing %r — declared in the brief and absent from "
                 "the file that has to carry it" % (_f, _n))
if not os.path.isfile(os.path.join(os.path.dirname(refdir), "templates", "routing-rule.md")):
    fail("missing template: templates/routing-rule.md — the routing default is a "
         "workflow decision, so it must ship as a file rather than be hand-installed")

# The adoption doctrine has to carry BOTH entry conditions. Greenfield is the easy
# half and the one that gets written; brownfield is where a repository actually is,
# and its third step — baselining the ratchets at today — is the whole reason the
# gate survives adoption day. A file that documents only the easy half reads as
# complete and helps nobody with a real repo.
_adopt = os.path.join(refdir, "adoption.md")
if os.path.isfile(_adopt):
    _a = open(_adopt, encoding="utf-8").read().lower()
    for _needle, _what in (("a new project", "the greenfield walkthrough"),
                           ("an existing project", "the brownfield walkthrough"),
                           ("baseline the ratchets", "the ratchet-baseline step"),
                           ("not back-filled", "the do-not-back-fill rule")):
        if _needle not in _a:
            fail(f"references/adoption.md: no {_what} (looked for {_needle!r}) — "
                 "adoption without it is a tutorial for the repository nobody has")

# Default-on routing is only safe with a stated boundary AND a working opt-out.
# Anthropic's enterprise guidance names the failure directly: a description that is
# too broad steals triggers from narrower skills. So the exclusion clause is required
# in the description, and the opt-out phrase must appear in the eval suite — an
# escape hatch nobody tests is a trap rather than a default.
if fm_name and 'desc' in dir():
    _d = desc if 'desc' in dir() else ""
    if "Not for:" not in _d:
        fail("SKILL.md: the description widens to repo-changing work but states no "
             "'Not for: …' exclusion clause — that is the 'too broad, steals "
             "triggers' failure the enterprise guidance names")
    for _phrase in ("без пайплайна", "quick"):
        if _phrase not in _d:
            fail(f"SKILL.md: the description does not name the opt-out phrase "
                 f"{_phrase!r} — default-on without a release valve is a trap")
    _sp = os.path.join(ROOT, "evals", "task-pipeline.evals.json")
    if os.path.isfile(_sp):
        _suite = json.load(open(_sp, encoding="utf-8"))
        if not any("без пайплайна" in (e.get("query") or "")
                   for e in _suite.get("evals", [])):
            fail("evals: no eval exercises the opt-out phrase — the description "
                 "promises an escape hatch that nothing checks")

# Behavioural evaluations. Anthropic's guidance: "Create evaluations BEFORE writing
# extensive documentation", "At least three evaluations created", and the enterprise
# page requires 3-5 queries per Skill covering should-trigger, should-not-trigger and
# ambiguous cases, tested across the models in use.
#
# This repo's 46 structural guards prove the skill is well-FORMED. Until this suite
# runs, nothing proves it BEHAVES — that it fires on the right request, stays quiet
# on a question, and actually performs the steps it documents. Shipping the suite is
# the part a check can enforce; running it is a human/agent step, and evals/run.py
# deliberately never reports a pass it did not observe.
_evals_dir = os.path.join(ROOT, "evals")
if not os.path.isdir(_evals_dir):
    fail("missing evals/ — a skill with no behavioural evaluations is a skill whose "
         "structure is proven and whose behaviour is assumed")
else:
    for _f in ("task-pipeline.evals.json", "run.py", "RESULTS.md"):
        if not os.path.isfile(os.path.join(_evals_dir, _f)):
            fail(f"missing evals/{_f}")
    _runner = os.path.join(_evals_dir, "run.py")
    if os.path.isfile(_runner):
        _r = subprocess.run([sys.executable, _runner, "--list"],
                            cwd=ROOT, capture_output=True, text=True)
        if _r.returncode != 0:
            fail("evals/run.py rejects the suite: "
                 + (_r.stdout + _r.stderr).strip()[-400:])

# The open-source surface. These are the files a stranger looks for before they
# trust, use or contribute to the repo; one of them silently disappearing in a
# refactor is invisible in review and expensive at the moment someone needs it.
for r in ("README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md",
          "CODE_OF_CONDUCT.md", "CLAUDE.md", "SKILL-CARD.md"):
    if not os.path.isfile(os.path.join(ROOT, r)):
        fail(f"missing root file: {r}")

# The registry entry Anthropic's enterprise guidance asks every organisation to keep
# (purpose, owner, version, dependencies, evaluation status), plus an honest pass
# over its risk-tier table. This skill scores three "High" indicators — shipped
# scripts, MCP references, tool invocations — and a reviewer who cannot see that
# stated has to reverse-engineer it from 23 files.
_card_p = os.path.join(ROOT, "SKILL-CARD.md")
if os.path.isfile(_card_p):
    _card = open(_card_p, encoding="utf-8").read()
    for _field in ("Purpose", "Owner", "Version", "Dependencies", "Evaluation status"):
        if f"**{_field}**" not in _card:
            fail(f"SKILL-CARD.md: no '{_field}' row — that is a registry field the "
                 "enterprise guidance requires")
    for _ind in ("Code execution", "MCP server references", "Tool invocations",
                 "Filesystem access scope", "Instruction manipulation",
                 "Network access patterns", "Hardcoded credentials"):
        if _ind not in _card:
            fail(f"SKILL-CARD.md: risk indicator {_ind!r} is unanswered — an omitted "
                 "row reads as 'does not apply', and here three of them do")
    # A card that claims a version the manifests do not carry is worse than none.
    if plg_ver and f"| **Version** | {plg_ver} |" not in _card:
        fail(f"SKILL-CARD.md: Version row does not read {plg_ver!r} — the card is a "
             "registry entry, and a stale one misroutes a rollback")

# The negative self-tests are the only proof the guards above are not decoration,
# so they must be runnable on a maintainer's machine and not just on CI. `sed -i`
# is the one thing that reliably breaks that: BSD sed needs an argument GNU sed
# refuses, and `0,/re/` does not exist on BSD at all — where it silently edits
# nothing and the test reads as a guard that failed to fire. Corrupt in python.
_wf = os.path.join(ROOT, ".github/workflows/validate.yml")
if not os.path.isfile(os.path.join(ROOT, "test/negatives.py")):
    fail("missing test/negatives.py — the local runner for the CI negative self-tests; "
         "without it a guard can only ever be proven on CI")
elif os.path.isfile(_wf):
    _wf_txt = open(_wf, encoding="utf-8").read()
    for _lineno, _line in enumerate(_wf_txt.splitlines(), start=1):
        if re.search(r"\bsed -i\b", _line):
            fail(f".github/workflows/validate.yml:{_lineno}: uses `sed -i`, which is not "
                 "portable (BSD sed needs an argument, and `0,/re/` does not exist there) — "
                 "corrupt the file in python so test/negatives.py runs the same script "
                 "locally and on CI")

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
elif [t for t in ("brief.md", "carryover.md", "context.md", "adr.md", "retro.md") if not os.path.isfile(os.path.join(tpl_dir, t))]:
    for t in ("brief.md", "carryover.md", "context.md", "adr.md", "retro.md"):
        if not os.path.isfile(os.path.join(tpl_dir, t)):
            fail(f"missing template: plugins/task-pipeline/skills/task-pipeline/templates/{t}")
else:
    # The Contents rule was scoped to references/ and the seeded doc map grew past 100
    # lines with eight sections and no list at all — a host project reads that file, and a
    # partial read of it shows whichever sections happen to come first.
    for _tf in sorted(os.listdir(tpl_dir)):
        if not _tf.endswith(".md"):
            continue
        _tp = os.path.join(tpl_dir, _tf)
        _tt = open(_tp, encoding="utf-8").read()
        if _tt.count("\n") > 100 and not re.search(r"^## Contents\b", _tt, re.M):
            fail("templates/%s: %d lines and no '## Contents' — a seeded file a host "
                 "project reads needs the same partial-read protection references get"
                 % (_tf, _tt.count("\n")))

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
    # The retro is the only artifact that outlives the run, so it is the only one
    # that can rot. Its whole value depends on being READ IN FULL at stage 0, which
    # a growing file quietly stops being — and a rule nobody reads to the end is
    # worse than no rule, because everyone believes it is covered. The prune is what
    # prevents that, and the prune is only mechanical if every instruction carries
    # the trigger that retires it and the run stamps that make "hasn't fired in five
    # runs" countable. A retro template without those two columns degrades into a
    # notes file within a few runs.
    retro = open(os.path.join(tpl_dir, "retro.md"), encoding="utf-8").read()
    if not re.search(r"^##\s+Standing instructions\b", retro, re.M):
        fail("templates/retro.md: missing the '## Standing instructions' section — "
             "the in-force list stage 0 reads in full (see references/retrospective.md)")
    if "Retire when" not in retro:
        fail("templates/retro.md: the standing-instruction table must carry a "
             "\"Retire when\" column — an instruction with no retirement trigger "
             "written at birth is one the prune can only argue about, and the list "
             "grows until nobody reads it")
    if not re.search(r"^##\s+Run stamps\b", retro, re.M):
        fail("templates/retro.md: missing the '## Run stamps' section — it is what "
             "makes the cold-retirement rule ('has not fired in five run stamps') "
             "countable instead of a guess")
    # A lesson with no commit is a lesson nobody can reopen. `file:line` evidence
    # rots at the next edit and then points at something that has moved; a SHA
    # carries the diff, the message and the parent forever, so `git show <sha>`
    # reconstructs the incident two months later when the class comes back.
    for _col in ("Commit", "Fired at"):
        if _col not in retro:
            fail(f"templates/retro.md: the standing-instruction table must carry a "
                 f"'{_col}' column — evidence that survives a rename is a commit, "
                 "not a line number")
    if not os.path.isfile(os.path.join(tpl_dir, "retro-archive.md")):
        fail("missing template: templates/retro-archive.md — retro.md is capped and "
             "read IN FULL every run, so its history needs a home that is queried "
             "instead of read; without one the prune loses the incident")
    # Same drift class as the autonomy sweep: retrospective.md is what the agent
    # READS about the retro's shape, templates/retro.md is what it WRITES. A column
    # in one and not the other is a field never asked for or never recorded.
    _retro_doc = os.path.join(refdir, "retrospective.md")
    if os.path.isfile(_retro_doc):
        _rd = open(_retro_doc, encoding="utf-8").read()
        for _col in ("Commit", "Fired at", "Retire when"):
            if (_col in _rd) != (_col in retro):
                fail(f"retro field {_col!r} appears in only one of "
                     "references/retrospective.md and templates/retro.md — one is "
                     "the doctrine, the other is the artifact, and they drift silently")

    # ---- the documentation track (v1.7.0) -------------------------------------
    # The doc map is the host project's own copy of the documentation contract:
    # where decisions live, each fact's single home, what a change obliges, and
    # what proves it. A seeded map missing the matrix seeds a project with a
    # register and no obligation — which is the state the register exists to end.
    docmap = os.path.join(tpl_dir, "docmap.md")
    if not os.path.isfile(docmap):
        fail("missing template: templates/docmap.md (the host project's doc map)")
    else:
        _dm = open(docmap, encoding="utf-8").read()
        for _h in ("Regime", "Registers", "Single source of truth",
                   "Propagation matrix", "Gates", "Ratchets", "Navigation"):
            if not re.search(r"^##\s+" + re.escape(_h) + r"\b", _dm, re.M):
                fail(f"templates/docmap.md: missing the '## {_h}' section — the doc "
                     "map answers four questions and this is one of them")
    # The most frequent change in a documented project is ADDING a document, and it
    # is the row nobody writes — so the matrix cannot catch the class it meets most.
    # Measured here: nine findings across five audits were that one missing row, with
    # every check green throughout, because a check only walks the list it was given.
    if "new document" not in _dm.lower():
        fail("templates/docmap.md: the propagation matrix has no row for adding a new "
             "document or rule — the change type a project makes most often, and the "
             "one a matrix without it can never catch")

        if "Checked by" not in _dm:
            fail("templates/docmap.md: the propagation matrix must carry a "
                 "'Checked by' column — a row nothing enforces is a wish, and the "
                 "column is where the word 'review' has to be written out loud")

    # Two permitted shapes of ONE decision home. If they disagree on fields, a
    # project that picks the other shape silently loses a rule.
    _dec = os.path.join(tpl_dir, "decisions.md")
    _adr = os.path.join(tpl_dir, "adr.md")
    if not os.path.isfile(_dec):
        fail("missing template: templates/decisions.md (the decision register)")
    elif os.path.isfile(_adr):
        _d = open(_dec, encoding="utf-8").read()
        _a = open(_adr, encoding="utf-8").read()
        for _field in ("Status", "Consequences / affects", "Source",
                       "Refines", "Contradicts", "Supersedes"):
            if (_field in _d) != (_field in _a):
                fail(f"templates: {_field!r} is in only one of decisions.md and "
                     "adr.md — the register and the ADR set are two spellings of one "
                     "contract, so a field in one and not the other is a fork")
    if not os.path.isfile(os.path.join(tpl_dir, "open-questions.md")):
        fail("missing template: templates/open-questions.md")
    if not os.path.isfile(os.path.join(tpl_dir, "hooks.example.json")):
        fail("missing template: templates/hooks.example.json (references/hooks.md "
             "points at it as the one worked example)")
    else:
        try:
            json.load(open(os.path.join(tpl_dir, "hooks.example.json"), encoding="utf-8"))
        except Exception as e:
            fail(f"templates/hooks.example.json: invalid JSON ({e}) — it is copied "
                 "verbatim into a settings file, so a broken one breaks the project")

    # The seeded gate travels to macOS (bash 3.2) and to whatever CI the host runs.
    # These three constructs fail SILENTLY rather than loudly: BSD `sed -i` needs an
    # argument GNU refuses and `0,/re/` does not exist there at all.
    # ITERATED, NOT COPIED. A second seeded gate arrived (hygiene.sh) and copying
    # this block for it would have created two guards to keep in step — which is the
    # drift this repository writes retro entries about. Adding a third gate means
    # adding its name here and nothing else.
    GATE_SCRIPTS = (
        ("docgate.sh", "the seeded documentation gate"),
        ("hygiene.sh", "the seeded artifact-hygiene gate"),
    )
    for _gname, _gwhat in GATE_SCRIPTS:
      _gpath = os.path.join(tpl_dir, _gname)
      if not os.path.isfile(_gpath):
        fail(f"missing template: templates/{_gname} ({_gwhat})")
      else:
        _g = open(_gpath, encoding="utf-8").read()
        # Scan CODE, not comments. The gate's own header names these three
        # constructs in order to forbid them; a detector that reads its own
        # prohibition as a violation is the false-positive class of learned rule 10,
      # and a gate that cries wolf is switched off by the third person who hits it.
        _g_code = "\n".join(l for l in _g.splitlines() if not l.lstrip().startswith("#"))
        for _bad, _why in ((r"grep\s+-[a-zA-Z]*P\b", "grep -P is not on macOS"),
                           (r"\bsed\s+-i\b", "sed -i is not portable"),
                           (r"\breadarray\b|\bmapfile\b", "readarray/mapfile is bash 4+")):
            if re.search(_bad, _g_code):
                fail(f"templates/{_gname}: non-portable construct ({_why}) — the "
                     "gate ships to macOS bash 3.2 and must behave identically there")
        if "SCOPE:" not in _g:
            fail(f"templates/{_gname}: no 'SCOPE:' header — a gate quoted as "
                 "evidence must state what it does NOT cover, or its green is read "
                 "as proof of a surface nobody walked")
        # Split on the SECTION MARKER, not on the word. Splitting on "VERDICT"
        # matched the header sentence that forbids appending after it, so the
        # "tail" was most of the script and the guard passed on anything. Found by
        # writing the first probe for it — the guard had been decorative since it
        # shipped, on both gate scripts.
        _vmark = [l for l in _g.splitlines() if l.startswith("# ---------- VERDICT")]
        if not _vmark:
            fail(f"templates/{_gname}: no '# ---------- VERDICT' section marker — "
                 "the block that decides the exit code has to be findable, or "
                 "'nothing runs after it' is unenforceable")
        else:
            _after_verdict = _g.split(_vmark[-1])[-1]
            if "exit 0" not in _after_verdict or "exit 1" not in _after_verdict:
                fail(f"templates/{_gname}: the VERDICT block must be last and must "
                     "exit — a gate has shipped that appended a check after its "
                     "verdict, printed FAIL and returned 0, with CI green over it")

    # A generator seeds green (references/learned.md rule 9). A scaffold whose own
    # gate rejects its own templates teaches every new project that the gate is
    # noise. This is the one guard in this repo that EXECUTES what it checks.
    #
    # BOTH register shapes are exercised. references/documentation.md permits two
    # decision homes and says they owe the same six things; the gate read only one
    # of them, so an ADR project got eight green "dormant" lines over a fully
    # populated register and a planted propagation violation went uncaught. A
    # promise kept for one shape is a promise, not a contract — so the contract is
    # what runs here.
    # The hygiene gate is EXECUTED, not merely read — same law as the doc gate below
    # it, and for the same reason: a seeded gate that is red on the seeds teaches a
    # new project on day one that the gate is noise. Run it over a scratch project
    # holding one clean file and require exit 0 with all six checks reported live.
    _hyg = os.path.join(tpl_dir, "hygiene.sh")
    if os.path.isfile(_hyg) and shutil.which("bash"):
        _hs = tempfile.mkdtemp(prefix="tp-hyg-")
        try:
            with open(os.path.join(_hs, "README.md"), "w", encoding="utf-8") as _fh:
                _fh.write("# Scratch\n\nOne clean sentence, no defects of any kind.\n")
            with open(os.path.join(_hs, "check-hygiene.sh"), "w", encoding="utf-8") as _fh:
                _fh.write(open(_hyg, encoding="utf-8").read())
            _r = subprocess.run(["bash", "check-hygiene.sh"], cwd=_hs,
                                capture_output=True, text=True)
            _out = _r.stdout + _r.stderr
            if _r.returncode != 0:
                fail(f"templates/hygiene.sh seeds RED on a clean scratch project "
                     f"(exit {_r.returncode}) — a gate that rejects a file with "
                     "nothing wrong in it gets switched off. Output: "
                     + _out.strip()[-500:])
            else:
                # Exit 0 alone proves nothing: every check could have gone dormant,
                # and dormant is green by design. Require the verdict to report all
                # six counts, which is the smallest evidence that it looked.
                _missing = [_k for _k in ("conflict", "placeholder", "fence",
                                          "truncation", "duplicate", "empty-section")
                            if _k not in _out]
                if _missing:
                    fail("templates/hygiene.sh exited 0 without reporting "
                         f"{_missing} — a verdict that omits a check is "
                         "indistinguishable from a check that never ran")
        finally:
            shutil.rmtree(_hs, ignore_errors=True)

    # Bound explicitly: this block runs the DOCUMENTATION gate. It used to inherit
    # `gate` from the check above, which silently became the last-iterated script the
    # moment that check grew a second one.
    gate = os.path.join(tpl_dir, "docgate.sh")
    if os.path.isfile(gate) and shutil.which("bash"):

        def _run_seed(label, shape, build, min_ok):
            _seed = tempfile.mkdtemp(prefix="tp-seed-")
            try:
                os.makedirs(os.path.join(_seed, "scripts"))
                with open(os.path.join(_seed, "scripts/check-docs.sh"), "w",
                          encoding="utf-8") as _fh:
                    _fh.write(open(gate, encoding="utf-8").read())
                build(_seed)
                _r = subprocess.run(["bash", "scripts/check-docs.sh"], cwd=_seed,
                                    capture_output=True, text=True)
                _out = _r.stdout + _r.stderr
                if _r.returncode != 0:
                    fail(f"templates/docgate.sh seeds RED on a {label} project "
                         f"(exit {_r.returncode}) — a project that starts red learns "
                         "on day one that the gate is noise. Output: "
                         + _out.strip()[-500:])
                    return
                # Exit 0 alone proves nothing here: every section can go `dormant`,
                # dormant is green by design, and a gate blind to this shape would
                # pass exactly like a gate that read it. So make the run report
                # something verifiable — which shape it found, and how much of it it
                # actually looked at.
                if f"shape {shape}" not in _out:
                    fail(f"templates/docgate.sh did not report 'shape {shape}' on a "
                         f"{label} project — it exited 0 without recognising the "
                         "register, which is indistinguishable from reading it")
                _n_ok = len([l for l in _out.splitlines() if l.startswith("ok:")])
                if _n_ok < min_ok:
                    fail(f"templates/docgate.sh ran only {_n_ok} live check(s) on a "
                         f"{label} project (expected at least {min_ok}) — the rest "
                         "went dormant, and dormant is green: that is how a fully "
                         "populated register sits behind a passing gate")
            finally:
                shutil.rmtree(_seed, ignore_errors=True)

        def _copy(seed, src, dst):
            _p = os.path.join(tpl_dir, src)
            if not os.path.isfile(_p):
                return
            _t = os.path.join(seed, dst)
            os.makedirs(os.path.dirname(_t), exist_ok=True)
            with open(_t, "w", encoding="utf-8") as _fh:
                _fh.write(open(_p, encoding="utf-8").read())

        def _build_register(seed):
            for _src, _dst in (("docmap.md", "docs/DOCMAP.md"),
                               ("decisions.md", "docs/DECISIONS.md"),
                               ("open-questions.md", "docs/OPEN_QUESTIONS.md"),
                               ("retro.md", "docs/superpowers/retro.md")):
                _copy(seed, _src, _dst)

        def _build_adr(seed):
            # The fixture is DERIVED from templates/adr.md's own fenced example, so
            # it cannot drift from the format the skill documents. A hand-written
            # copy here would be a second statement of the ADR contract.
            _adr_src = os.path.join(tpl_dir, "adr.md")
            if not os.path.isfile(_adr_src):
                return
            _txt = open(_adr_src, encoding="utf-8").read()
            if "## When this directory IS the register" not in _txt:
                fail("templates/adr.md: no 'When this directory IS the register' "
                     "section — the seeded gate's ADR fixture is derived from its "
                     "fenced example, and without it the ADR shape ships untested")
                return
            _blk = _txt.split("## When this directory IS the register")[1]
            _blk = _blk.split("```md")[1].split("```")[0]
            _blk = _blk.replace("- **Supersedes:** ADR-0004", "")
            os.makedirs(os.path.join(seed, "docs/adr"), exist_ok=True)
            with open(os.path.join(seed, "docs/adr/0001-seed.md"), "w",
                      encoding="utf-8") as _fh:
                _fh.write(_blk)
            for _doc in re.findall(r"`([^`]+\.md)`", _blk):
                _t = os.path.join(seed, _doc)
                os.makedirs(os.path.dirname(_t), exist_ok=True)
                with open(_t, "w", encoding="utf-8") as _fh:
                    _fh.write("# %s\n\nGoverned by ADR-0001.\n" % os.path.basename(_doc))
            with open(os.path.join(seed, "docs/DOCMAP.md"), "w", encoding="utf-8") as _fh:
                _fh.write("# Doc map\n\n## Registers\n\n| Register | File | ID |\n"
                          "|---|---|---|\n| Decisions | `docs/adr/` | `ADR-NNNN` |\n"
                          "\n## Propagation matrix\n\n| Change | Update | Checked by |\n"
                          "|---|---|---|\n| a decision | its consequences | gate section 5 |\n")

        _run_seed("register-shape", "register", _build_register, 8)
        _run_seed("ADR-shape", "adr", _build_adr, 7)

    # A template that ships and is not listed is a template nobody knows to seed.
    _tpl_readme = os.path.join(tpl_dir, "README.md")
    if not os.path.isfile(_tpl_readme):
        fail("missing templates/README.md")
    else:
        _tr = open(_tpl_readme, encoding="utf-8").read()
        for _t in sorted(os.listdir(tpl_dir)):
            if _t == "README.md" or _t.startswith("."):
                continue
            if _t not in _tr:
                fail(f"templates/README.md does not list {_t!r} — an unlisted "
                     "template is one nobody knows to seed")

    # The autonomy sweep lives twice: grill.md's table is what the agent READS while
    # interviewing, brief.md's is what it WRITES. They drift silently — a row added
    # to one is simply never asked, or never recorded, and the autonomy promise
    # degrades into a mid-flight question with nothing to show it was ever dropped.
    # Compare the stage numbers each table covers, not the wording.
    # Compared per stage as a KEYWORD SET, not as a set of stage numbers. The
    # number-only version passed while grill.md was missing the documentation-regime
    # row that templates/brief.md had a field for — a question never asked with an
    # answer nowhere to write, which is the exact defect this check exists to catch,
    # walking through it because both files still "covered stage 0".
    # Measured before being trusted (learned.md rule 10): zero false positives on
    # the real content, including the legitimate case where the brief splits
    # grill's "7 Lint+deploy" into separate "7 Lint" and "7 Deploy" rows — the union
    # of words per stage is identical either way.
    def _sweep_stages(text):
        m = re.search(r"^\|\s*(?:Stage|run-wide)\b.*?\n(?:\|[-: |]+\|\n)?((?:\|.*\n)+)",
                      text, re.M)
        if not m:
            return None
        covered = {}
        for row in m.group(1).splitlines():
            cell = row.split("|")[1] if row.count("|") > 1 else ""
            key = tuple(re.findall(r"\d+", cell))
            covered.setdefault(key, set()).update(
                w.lower() for w in re.findall(r"[A-Za-z]{3,}", cell))
        return covered

    _grill_p = os.path.join(refdir, "grill.md")
    if os.path.isfile(_grill_p):
        _g = _sweep_stages(open(_grill_p, encoding="utf-8").read().split("## The autonomy sweep")[-1])
        _b = _sweep_stages(brief.split("## Autonomy")[-1])
        if _g is None or _b is None:
            fail("autonomy sweep: could not find the table in references/grill.md "
                 "and/or templates/brief.md — the sweep must be a table in both")
        elif _g != _b:
            _only_g = {k: sorted(_g[k] - _b.get(k, set())) for k in _g if _g[k] - _b.get(k, set())}
            _only_b = {k: sorted(_b[k] - _g.get(k, set())) for k in _b if _b[k] - _g.get(k, set())}
            fail("autonomy sweep drift — one file is what the grill ASKS, the other "
                 "is what the brief RECORDS, so a topic in only one is a question "
                 "never asked or an answer with nowhere to go. "
                 f"only in references/grill.md: {_only_g or '{}'} · "
                 f"only in templates/brief.md: {_only_b or '{}'}")

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
        # Creating a design file is outward and duplicates are silent: a second file
        # is internally consistent, its frames are named correctly and the UX linter
        # is green, so nothing downstream notices that half the work now lives where
        # nobody looks. The only place that can prevent it is intake, by naming the
        # team and the file before anything is drawn.
        if not re.search(r"design destination", s0_check):
            fail(f"{EXAMPLE_REL} stage[1]: gate.check must settle the DESIGN DESTINATION for "
                 "Figma work (which team/org, which file, and never create while a recorded "
                 "one resolves) — a destination decided at drawing time is how a project ends "
                 "up with several design files (see references/grill.md)")
        # Stage 9 is the other half of that loop.
        s9 = next((s for s in stages if isinstance(s, dict) and s.get("state") == "docs-wiki"), None)
        if s9 is not None and "ledger" not in str((s9.get("gate") or {}).get("check", "")).lower():
            fail(f"{EXAMPLE_REL} stage 'docs-wiki': gate.check must name the stage-0 source ledger as its "
                 "work list — a source read at stage 0 and left wrong is the next run's false premise")

    # A 'task-pipeline:<name>' entry in skills[] is not an installable skill — the
    # config's own note defines it as this skill's doctrine file, references/<name>.md.
    # So an entry that resolves to nothing is a stage pointed at doctrine that does
    # not exist: it reads as covered, ships as covered, and the agent following it
    # finds nothing. Three of them survived every review until a mechanical check
    # asked. (Host projects are free to name anything in THEIR pipeline.json; this
    # is the example we ship, and it is what people copy.)
    if isinstance(stages, list):
        for i, st in enumerate(stages, start=1):
            if not isinstance(st, dict):
                continue
            for s in st.get("skills") or []:
                if isinstance(s, str) and s.strip().startswith("task-pipeline:"):
                    _doc = s.strip().split(":", 1)[1] + ".md"
                    if not os.path.isfile(os.path.join(refdir, _doc)):
                        fail(f"{EXAMPLE_REL} stage[{i}]: skills[] names {s!r}, but "
                             f"references/{_doc} does not exist — a 'task-pipeline:<name>' "
                             "entry IS the built-in doctrine file, so a dangling one is a "
                             "stage pointing at doctrine nobody wrote")

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

    # The stage-10 close-out has now failed to reach every surface TWICE (v0.17.1
    # fixed it for the third review verdict; v1.3.1 added the parent-repository rule
    # to SKILL.md, build.md and conventions.md while acceptance.md, stages.md and the
    # config — the three places that actually define the gate — never heard of it).
    # A gate's own doctrine claiming "now requires X" while the gate says nothing
    # about X is invisible in review and inert at runtime. Twice is a category, so
    # it is a check: whatever close-out concept SKILL.md names, the surfaces that
    # enforce stage 10 must name too.
    _sk_low = _sk_txt.lower()
    for _anchor, _what in (
        ("submodule", "the parent-repository close-out"),
        ("ladder", "the ladder walk"),
        ("retro", "the retrospective (prune, stamp, entry)"),
        # Stage 10 must PROVE the documentation gate, not merely inherit its green.
        # acceptance.md — the file an agent actually opens at stage 10 — shipped
        # without a word about it while SKILL.md's row and the config both demanded
        # it: the same inert-gate shape the three anchors above already guard.
        ("documentation gate", "the documentation gate as a stage-10 proof obligation"),
    ):
        if _anchor not in _sk_low:
            continue
        for _rel, _txt in (
            (f"{SKILL_DIR}/references/acceptance.md",
             open(os.path.join(refdir, "acceptance.md"), encoding="utf-8").read()
             if os.path.isfile(os.path.join(refdir, "acceptance.md")) else ""),
            (f"{SKILL_DIR}/references/stages.md", _st_txt),
            (EXAMPLE_REL, json.dumps(_pipe_stages or [], ensure_ascii=False)),
        ):
            if _anchor not in _txt.lower():
                fail(f"{_rel}: SKILL.md describes {_what} as part of the stage-10 close-out, "
                     f"but this surface never mentions {_anchor!r} — a gate that is only "
                     "declared where it is not enforced is inert")

    # Same inert-gate class, for the documentation track: SKILL.md promises the
    # stage-0 inventory and the stage-9 propagation sweep, so the surfaces that
    # actually ENFORCE those stages must name them too. A track declared only where
    # it is not enforced is a track no run performs.
    _doc_ref = os.path.join(refdir, "documentation.md")
    _doc_txt = open(_doc_ref, encoding="utf-8").read() if os.path.isfile(_doc_ref) else ""
    for _anchor, _what in (
        ("propagation", "the stage-9 propagation sweep"),
        ("docmap", "the stage-0 documentation inventory"),
    ):
        if _anchor not in _sk_low:
            continue
        for _rel, _txt in (
            (f"{SKILL_DIR}/references/documentation.md", _doc_txt),
            (f"{SKILL_DIR}/references/stages.md", _st_txt),
            (EXAMPLE_REL, json.dumps(_pipe_stages or [], ensure_ascii=False)),
        ):
            if _anchor not in _txt.lower():
                fail(f"{_rel}: SKILL.md describes {_what}, but this surface never "
                     f"mentions {_anchor!r} — declared where it is not enforced is inert")

    # The Doc Loop is declared CROSS-CUTTING — "it fires at any stage" — in SKILL.md,
    # stages.md and documentation.md. It shipped that way while not one stage
    # doctrine file mentioned it, which means the flow as an agent EXECUTES it never
    # ran the loop: an agent opens the stage file, not the orchestrator's summary.
    # These five are the stages that settle decisions, so these five must say so.
    for _fn in ("brainstorm.md", "spec.md", "build.md", "review.md", "acceptance.md"):
        _p = os.path.join(refdir, _fn)
        if not os.path.isfile(_p):
            continue
        if "documentation.md" not in open(_p, encoding="utf-8").read():
            fail(f"references/{_fn}: the Doc Loop is declared cross-cutting but this "
                 "stage doctrine never names references/documentation.md — a stage "
                 "that settles decisions and does not know where they go is where "
                 "they are lost")

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

# The code graph is the third close-out artifact (references/knowledge-graph.md):
# stage 0 queries it, stage 9 refreshes it and checks it against the docs. Shipping
# that doctrine while the surfaces that ENFORCE stage 9 say nothing about it is the
# same inert-gate failure the stage-10 close-out hit twice — the file reads as law
# and the run never does it. So if the doctrine ships, stage 9 must name it in both
# places: the config gate (what the orchestrator verifies) and stages.md's stage-9
# section (what an agent reads).
if os.path.isfile(os.path.join(refdir, "knowledge-graph.md")):
    _s9_cfg = next(
        (s for s in (_pipe_stages or []) if isinstance(s, dict) and s.get("state") == "docs-wiki"),
        None,
    )
    if _s9_cfg is not None and "graph" not in str((_s9_cfg.get("gate") or {}).get("check", "")).lower():
        fail(f"{EXAMPLE_REL} stage 'docs-wiki': references/knowledge-graph.md ships the code-graph "
             "doctrine but the stage-9 gate.check never mentions the graph — the refresh is "
             "declared where it is not enforced, so a run closes with a stale graph the NEXT "
             "run's harvest will read as truth")
    _s9_doc = re.search(r"^## 9 — .*?(?=^## |\Z)", _st_txt, re.M | re.S)
    if _s9_doc and "graph" not in _s9_doc.group(0).lower():
        fail("references/stages.md stage 9: references/knowledge-graph.md ships the code-graph "
             "doctrine but the stage-9 section never mentions the graph — an agent reading the "
             "stage detail is never told to refresh it")

# An unresolved merge leaves conflict markers in the file, and this repo is almost
# entirely prose — so a botched resolution ships as doctrine an agent will read and
# obey. Nothing here noticed: a CHANGELOG carrying three markers passed every other
# check, because they all look at structure and none at the text. (Only the two
# arrow markers are checked; a bare row of '=' is legal setext markdown.)
_OPEN, _CLOSE = "<" * 7 + " ", ">" * 7 + " "
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "graphify-out")]
    for fn in filenames:
        if not fn.endswith((".md", ".mdc", ".json", ".py", ".js", ".sh", ".yml", ".yaml")):
            continue
        fp = os.path.join(dirpath, fn)
        try:
            body = open(fp, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(body.splitlines(), start=1):
            if line.startswith(_OPEN) or line.startswith(_CLOSE):
                fail(f"{os.path.relpath(fp, ROOT)}:{lineno}: unresolved merge conflict marker — "
                     "a half-resolved merge ships as doctrine somebody reads and obeys")

# --- run continuity (v1.11.0) -------------------------------------------------
# G1. The run-wide pacing block. A config field that a project may set but the
# shipped example never shows is a field nobody discovers: the example is what
# gets copied. So the example must set run.loop.mode EXPLICITLY — demonstrating
# the default rather than relying on its absence, which reads as an oversight.
_sch = load_json("plugins/task-pipeline/skills/task-pipeline/pipeline.schema.json")
_exm = load_json("plugins/task-pipeline/skills/task-pipeline/pipeline.example.json")
if _sch and "run" not in _sch.get("definitions", {}):
    fail("pipeline.schema.json: no 'run' definition — run-wide pacing has no contract")
if _exm is not None:
    _mode = (_exm.get("run") or {}).get("loop", {}).get("mode")
    if _mode not in ("off", "interval"):
        fail("pipeline.example.json: no explicit run.loop.mode — the example must "
             "DEMONSTRATE the default, not rely on its absence")

# G2. The continuity reach guard. references/build.md carried the continuous-
# execution rule for nine releases and it did not work, because it lived inside one
# stage: an agent running stage 5 opens build.md and never re-reads SKILL.md to
# learn that a run-wide mode exists. Same class as the doc-loop reach guard above —
# declaring a thing run-wide does not distribute it.
_SKILLDIR = "plugins/task-pipeline/skills/task-pipeline"
for _rel in ("SKILL.md", "references/grill.md", "references/build.md",
             "references/stages.md", "templates/brief.md"):
    _p = os.path.join(ROOT, _SKILLDIR, _rel)
    if os.path.isfile(_p) and "continuity.md" not in open(_p, encoding="utf-8").read():
        fail(f"{_rel} does not name continuity.md — "
             "a run-wide rule no stage has heard of is a rule that does not run")

# G3. Two clauses in references/continuity.md are load-bearing and easy to soften
# into nothing during an edit: the one forbidding a context warning without
# evidence, and the one naming the harness limit. Whitespace is normalised first —
# the first clause is 74 characters and wraps at this repo's 80-column style, so a
# line-oriented search would reject correctly formatted prose. That false-positive
# class already cost this repository six bogus findings once (learned.md rule 10).
_cont = os.path.join(ROOT, _SKILLDIR, "references/continuity.md")
if os.path.isfile(_cont):
    _cn = re.sub(r"\s+", " ", open(_cont, encoding="utf-8").read())
    for _clause in ("never announce that the context is nearly spent without one "
                    "of those signals",
                    "Claude Code only"):
        if _clause not in _cn:
            fail(f"references/continuity.md: missing the contractual clause "
                 f"{_clause!r} — without it the rule degrades to a suggestion")

# G4. A template is COPIED somewhere else — that is what a template is. A relative
# link inside one resolves from templates/, where the file is stored, and from
# nowhere it is ever actually read: carryover.md shipped '../references/audit.md'
# for nine minor releases and broke the moment it was seeded to the path its own
# doctrine names. The repo's link checker stayed green throughout, because it
# resolves from the file's home. Same rule as the Cursor rule, same reason: a
# document that travels must be self-contained. Name the file in a code span.
_tpl = os.path.join(ROOT, _SKILLDIR, "templates")
if os.path.isdir(_tpl):
    for _fn in sorted(os.listdir(_tpl)):
        if not _fn.endswith(".md") or _fn == "README.md":
            continue  # README.md is the directory's own index and is never seeded
        _body = FENCE_RE.sub("", open(os.path.join(_tpl, _fn), encoding="utf-8").read())
        for _t in LINK_RE.findall(_body):
            if _t.startswith(("http://", "https://", "mailto:", "#")):
                continue
            fail(f"templates/{_fn}: relative link {_t!r} resolves only from "
                 "templates/, not from the destination it is seeded to — a seeded "
                 "template must be self-contained; name the file in a code span")

# Two negative self-tests that share a scratch directory can mask each other: the
# second copy lands in a populated tree, git's read-only pack files refuse to be
# overwritten, and on a good day it fails loudly. On a bad day it succeeds and the
# test passes against the FIRST test's corruption instead of its own. Found by a
# collision on /tmp/verdict-copy, in the release that ships a gate for exactly this
# class of accident.
_wf_p = os.path.join(ROOT, ".github/workflows/validate.yml")
if os.path.isfile(_wf_p):
    _wf_t = open(_wf_p, encoding="utf-8").read()
    # Strip heredoc bodies first. A step that PLANTS a duplicate as test data
    # contains the very string this scans for, and counting it made the guard fail
    # on its own negative self-test — the same class as the markdown fence strip
    # above, one file format over.
    _wf_scan, _inheredoc = [], False
    for _l in _wf_t.splitlines():
        if "<<'EOF'" in _l:
            _inheredoc = True
            continue
        if _inheredoc:
            if _l.strip() == "EOF":
                _inheredoc = False
            continue
        _wf_scan.append(_l)
    _dirs = re.findall(r"cp -R \. (/tmp/[A-Za-z0-9._-]+)", "\n".join(_wf_scan))
    _dupes = sorted({d for d in _dirs if _dirs.count(d) > 1})
    if _dupes:
        fail("`.github/workflows/validate.yml`: scratch directories reused across "
             f"negative self-tests: {_dupes} — a shared scratch dir lets one test "
             "corrupt another's copy, and a test that passes against the wrong "
             "corruption proves nothing")

# The read-back guards (v1.13.0). Four rules already lived in this bundle and were
# stranded in stages that never handed them to the stage which had to obey them; the
# fix is that stages 3 and 4 are told to go and read them. These three checks prove
# the doctrine FILES CARRY the items — nothing here can prove a run in someone
# else's repository performed a self-review, and saying so plainly is the point:
# a guard that claimed otherwise would be the exact defect this release fixes.
_rb = (
    (os.path.join(refdir, "spec.md"), "references/spec.md", (
        ("Every check this spec names resolves",
         "stage 3 names checks, and nothing asked whether a named one is real"),
        ("Read the decisions back",
         "brainstorm.md records rejected options and no stage-3 item ever opens them"),
        ("Print the cost",
         "nothing anywhere asks whether a change still costs what it was worth"),
    )),
    (os.path.join(refdir, "planning.md"), "references/planning.md", (
        ("Every command, path and file a DoD names resolves",
         "learned.md rule 14 fired only at stage 9, four stages after the target is written"),
    )),
)
for _p, _rel, _items in _rb:
    if not os.path.isfile(_p):
        continue
    _txt = open(_p, encoding="utf-8").read()
    for _needle, _why in _items:
        if _needle not in _txt:
            fail(f"{_rel}: the self-review no longer asks '{_needle}' — {_why}")
    if "## Self-review" not in _txt or "computed number, not a tick" not in _txt:
        fail(f"{_rel}: no committed '## Self-review' section shape — a checklist that "
             "leaves no trace is an assertion, and this repository already demands "
             "the set difference be PRINTED one stage over")

# Rule 14 binds the stages that WRITE a target, not only the one that trips over it.
_lp = os.path.join(refdir, "learned.md")
if os.path.isfile(_lp):
    _lt = open(_lp, encoding="utf-8").read()
    for _stage in ("| 3 Spec | 14", "| 4 Plan | 14"):
        if _stage not in _lt:
            fail(f"references/learned.md: the stage map does not bind rule 14 at "
                 f"'{_stage.strip('| ')}' — a rule mapped only to the stage that "
                 "notices the breakage is a rule nobody reads while causing it")

# The false-success guards (v1.14.0). Every incident this repository has recorded in
# which a mechanism reported a win it never checked -- the fail-open hook, the cancel
# that accepted an unscheduled id, the counter that asserted presence of the new
# instead of absence of the old, R-002's half-applied batch -- was one class with no
# name, so each was fixed as its own instance. These four checks hold the class in one
# home and hold the other files to citing it rather than restating it.
_fs = os.path.join(refdir, "gates.md")
if os.path.isfile(_fs):
    _ft = open(_fs, encoding="utf-8").read()
    if "## False success" not in _ft:
        fail("references/gates.md: the False success class is gone -- the one home for "
             "an actor's reply not being evidence about the world")
    for _needle, _why in (
        ("re-reading the state it changed",
         "the law itself, without which the section is a list of anecdotes"),
        ("what does it print when it did not look",
         "the test that separates a checked pass from a silent one"),
        ("Verify by re-reading, not by the reply",
         "rule 1, the one the other files cite"),
        ("Assert the absence of the old, not the presence of the new",
         "rule 2, the shape that stayed green for three releases"),
    ):
        if _needle not in _ft:
            fail(f"references/gates.md: the False success section no longer states "
                 f"'{_needle}' -- {_why}")

# The class is cited, never restated: four files must point at the one home.
for _rel, _why in (
    ("audit.md", "the fifth axis is what sweeps for the class; an axis that does not "
                 "name its definition drifts into a second definition"),
    ("build.md", "the implementer contract demands the read-back and must say under "
                 "which rule"),
    ("review.md", "the rubric raises an unverified effect to Important and must cite "
                  "the class that defines it"),
    ("continuity.md", "the cancel rule is one instance of the class and was the "
                      "incident that named it"),
):
    _p = os.path.join(refdir, _rel)
    if os.path.isfile(_p):
        _txt = open(_p, encoding="utf-8").read()
        if "*False success*" not in _txt:
            fail(f"references/{_rel}: no citation of the False success class -- {_why}")

# The implementer contract carries the read-back, and the hygiene gate names its blind side.
_bp = os.path.join(refdir, "build.md")
if os.path.isfile(_bp):
    _bt = open(_bp, encoding="utf-8").read()
    if "`verified-by:` line" not in _bt and "`verified-by:` lines" not in _bt:
        fail("references/build.md: the report no longer requires verified-by lines -- a "
             "side effect confirmed by the command that caused it is not confirmed")
    if "confirmed by re-reading the state it changed" not in _bt:
        fail("references/build.md: the implementer contract dropped the re-reading "
             "clause -- an implementer told to report success is not told to check it")
    if "cannot see what the task did" not in _bt:
        fail("references/build.md: the hygiene gate no longer states its blind side -- "
             "a gate over the diff reads what the task wrote, never what it did")

# The rubric item exists and is Important rather than Minor.
_rp = os.path.join(refdir, "review.md")
if os.path.isfile(_rp):
    _rt = open(_rp, encoding="utf-8").read()
    if "**Effect verification.**" not in _rt:
        fail("references/review.md: the rubric lost the Effect verification item -- the "
             "reviewer reads the diff and would never ask what happened outside it")
    if "unverified claim, and it is **Important**" not in _rt:
        fail("references/review.md: an unverified effect is no longer Important -- a "
             "finding that never blocks is a finding the fix loop never sees")

if errors:
    print("FAIL: task-pipeline structure invalid")
    for e in errors:
        print(" - " + e)
    sys.exit(1)
print("PASS: task-pipeline structure valid")
