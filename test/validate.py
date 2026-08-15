#!/usr/bin/env python3
"""Structural validator for the task-pipeline skill repo. Exit 0 = pass."""
import datetime, glob, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "task-pipeline"
errors = []

# Where THIS repository keeps its run paperwork, resolved rather than spelled.
#
# Every check below used to name `docs/superpowers/` literally, which made the
# validator agree with exactly one layout — its own. A host project that relocated
# the root (the thing references/artifacts.md has promised since v0.1.0) got a
# validator that failed on every artifact it could not find at the one address it
# knew. `artifact_root.resolve` answers for whatever layout is actually there:
# `paths.artifacts` if set, else docs/evidence/, else the legacy docs/superpowers/.
#
# `bin/lib/artifact-root.js` implements the same rule for the shipped side, and
# `test/artifact_root_test.py` fails when the two disagree — that comparison is why
# two implementations of one rule are affordable here.
import artifact_root                                        # noqa: E402

_ART_INFO = artifact_root.resolve(ROOT)
ART = _ART_INFO["root"]          # e.g. "docs/evidence", or "docs/superpowers" (legacy)
ARTP = os.path.join(ROOT, ART)   # the same, absolute


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
            r"\[`(?:[a-z0-9./-]*/)?([a-z0-9-]+\.md)`\]\([^)]*\)\s*(?:→|->)\s*\*([^*]+)\*", _flat):   # a path-prefixed label — [`references/gates.md`](...) — used to slip past this
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

# ============================================================================
# THE CLAIM REGISTRY — compute, never restate (references/learned.md rule 8)
# ============================================================================
# This began as ONE check, over ONE number: the guard count, because two living documents
# silently claimed 46 after the suite reached 50. It stayed one check while the same class
# went stale in five more places — `learned.md` described as "fifteen rules" against a table
# of twenty-one, `evals/RESULTS.md` ratcheting "Dated runs recorded 0" directly above a
# dated run and directly on top of a tool computing 1, `docs/DOCMAP.md` claiming two
# standing instructions against the retro's four, and the version-sync invariant NAMED
# "four-way" while the validator enforced five. Each was fixed as an instance. The class
# was never gated, which is `audit.md`'s own rule — a class seen twice belongs in a script —
# unapplied to the file that enforces it.
#
# So the check is now a REGISTRY: one row per claim class, each naming
#   · the pattern that recognises the claim in prose,
#   · the command that computes the truth,
#   · the incident that earned the row.
# Adding a class is a row, not a new block. That is the whole point: the next stale number
# costs one line here instead of one more bespoke check nobody generalises.
#
# SCOPE, stated rather than implied:
#   · It compares numbers that a command can produce. A count of an enumeration inside one
#     sentence ("lives on nine surfaces: A, B, C…") is NOT computable from outside that
#     sentence — those are DELETED rather than gated, and `CLAUDE.md` says so where it used
#     to carry one.
#   · CHANGELOG.md is exempt by design. It records what a past release shipped; a number
#     true on the day of the release is not a claim about now.
#   · A document that states no number is trivially green. The registry cannot make anyone
#     write the number down, and does not try to.
# Numbers appear in this corpus as DIGITS and as WORDS, and the incident that named this
# registry's second row was a word: README.md and SKILL.md said "fifteen rules", not "15".
# A registry that cannot see the form its own founding defect took is a check whose green is
# narrower than the sentence people read it as. Measured after adding this: four live
# word-form claims — "the ten canons", on four surfaces — that the digit-only patterns had
# been skipping in silence. All four are correct; none of them was being checked, and the
# release note for this very change claimed those classes were dormant because the numbers
# had been deleted. For one of them that was simply untrue.
_NUM_WORDS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen twenty".split())}
for _tens, _tv in (("twenty", 20), ("thirty", 30), ("forty", 40), ("fifty", 50),
                   ("sixty", 60), ("seventy", 70), ("eighty", 80), ("ninety", 90)):
    _NUM_WORDS[_tens] = _tv
    for _u, _uv in [(w, i) for i, w in enumerate(
            "zero one two three four five six seven eight nine".split()) if i]:
        _NUM_WORDS[f"{_tens}-{_u}"] = _tv + _uv
_NUM = r"(\d+|" + "|".join(sorted(_NUM_WORDS, key=len, reverse=True)) + r")"

_UNPARSED_WORDS = set()

def _as_int(tok):
    """None means 'this token is outside the map'. The map stops in the forties, and the
    guard count is already past a hundred — so a word form above the ceiling would be
    SKIPPED. Skipping is fine; skipping in silence is not (canon 9), so every unparseable
    token is collected and printed beside the verdict."""
    tok = tok.strip().lower()
    if tok.isdigit():
        return int(tok)
    val = _NUM_WORDS.get(tok)
    if val is None:
        _UNPARSED_WORDS.add(tok)
    return val

_neg_wf = os.path.join(ROOT, ".github/workflows/validate.yml")
_NEG_WF_TEXT = open(_neg_wf, encoding="utf-8").read() if os.path.isfile(_neg_wf) else ""
# Both counts, from ONE read, used by every check below that needs either. The workflow
# was being opened three times for two numbers.
_neg_n = len(re.findall(r"^\s*- name:\s*Negative self-test", _NEG_WF_TEXT, re.M))
_prop_n = len(re.findall(r"^\s*- name:\s*Property check", _NEG_WF_TEXT, re.M))

def _count_re(path, pattern, flags=re.M):
    p = os.path.join(ROOT, path)
    if not os.path.isfile(p):
        return None
    return len(re.findall(pattern, open(p, encoding="utf-8").read(), flags))

def _count_run_headings(path):
    """Dated run headings in evals/RESULTS.md, outside fenced blocks — the same unit
    evals/run.py counts, deliberately duplicated in shape so the two can be compared."""
    p = os.path.join(ROOT, path)
    if not os.path.isfile(p):
        return None
    infence, n = False, 0
    for ln in open(p, encoding="utf-8").read().split("\n"):
        if re.match(r"^\s*(```|~~~)", ln):
            infence = not infence
            continue
        if not infence and re.match(r"^## 20\d{2}-\d{2}-\d{2}\b", ln):
            n += 1
    return n

# (label, claim pattern, computing callable, incident)
_AX_STOP = {"the", "one", "a", "an"}


_AXIS_MEMO = {}


def _axis_keys():
    """Bold leads of the numbered axis list in audit.md -> match keys.

    Key = the first one or two non-stopword words of the lead, lowercased. Two words
    where the first alone would collide with ordinary prose: 'class' appears in "a
    class that repeats twice" on the same surfaces, and would report an axis named
    that nobody named.
    """
    if "r" in _AXIS_MEMO:
        return _AXIS_MEMO["r"]
    _p = os.path.join(refdir, "audit.md")
    if not os.path.isfile(_p):
        return None, None
    # Called once by the claim-registry lambda and once to build _AXIS_KEYS, both
    # BEFORE _LIVING_TEXT exists — so the file is memoised here rather than fetched
    # from a cache that is not built yet at the first call.
    _t = open(_p, encoding="utf-8").read()
    _AXIS_MEMO["t"] = _t
    _h = re.search(r"^###\s+\d+\.\s+Every pass changes the axis.*$", _t, re.M)
    if not _h:
        return None, None
    _seg = _t[_h.end():]
    _nx = re.search(r"^###\s", _seg, re.M)
    if _nx:
        _seg = _seg[:_nx.start()]
    _keys = []
    for _lead in re.findall(r"^\d+\.\s+\*\*(.+?)\*\*", _seg, re.M):
        _w = [_x for _x in re.findall(r"[A-Za-z][A-Za-z-]*", _lead.lower())
              if _x not in _AX_STOP]
        if not _w:
            continue
        _keys.append(" ".join(_w[:2]) if len(_w) > 1 else _w[0])
    _AXIS_MEMO["r"] = (_keys, _p)
    return _keys, _p


# One pattern, two readers. The registry counted rule rows and the shape disclosure
# counted them again with a byte-identical regex differing only in its capture group —
# rule 8's own class ("compute, never restate") living inside the file that enforces it.
_RULE_ROW = r"^\|\s*\d+\s*\|\s*\*\*"
_RULE_ROW_ID = r"^\|\s*(\d+)\s*\|\s*\*\*"

_CLAIM_REGISTRY = [
    ("negative self-tests",
     r"\b" + _NUM + r"\+?\s+(?:of\s+\d+\s+)?(?:structural\s+)?guards\b(?!\s+behind)",
     lambda: _neg_n,          # one source: computed once above, not a second identical regex
     "two living documents claimed 46 after the suite reached 50"),

    ("rules in learned.md",
     r"\b" + _NUM + r"\s+rules\s+earned\b",
     lambda: _count_re("plugins/task-pipeline/skills/task-pipeline/references/learned.md",
                       _RULE_ROW),
     "README.md and SKILL.md said 'fifteen rules' against a table of twenty-one"),

    ("dated eval runs",
     r"[Dd]ated\s+(?:eval\s+)?runs\s+recorded[^.\n]{0,20}?\*{0,2}" + _NUM + r"\*{0,2}",
     lambda: _count_run_headings("evals/RESULTS.md"),
     "RESULTS.md ratcheted 0 directly above a dated run, while run.py computed 1"),

    ("standing instructions",
     r"\b" + _NUM + r"\s+of\s+a\s+hard\s+cap\s+of\s+10\b",
     lambda: _count_re(f"{ART}/retro.md", r"^\|\s*R-\d+\s*\|"),
     "docs/DOCMAP.md claimed two while the retro held four"),

    ("evidence canons",
     r"\bthe\s+" + _NUM + r"\s+canons\b",
     lambda: _count_re("plugins/task-pipeline/skills/task-pipeline/references/documentation.md",
                       r"^\*\*\d+\.\s"),
     "the canons are cited by count from three surfaces and the list can grow"),

    ("rotation axes",
     r"\b" + _NUM + r"\s+(?:orthogonal|rotation)\s+axes\b",
     lambda: (lambda k: len(k) if k else None)(_axis_keys()[0]),
     "audit.md defined five while the Cursor rule summarised four and README three"),

    # "axes" is polysemous in this corpus: audit.md rotates between them, gates.md is
    # BUILT on three of its own. The qualifier is what separates the classes, and the
    # bare form below cannot match "six rotation axes" because the qualifier sits
    # between the number and the noun.
    ("gates.md's own axes",
     r"\b" + _NUM + r"\s+axes\b",
     lambda: _count_re("plugins/task-pipeline/skills/task-pipeline/references/gates.md",
                       r"^##\s+Axis\s"),
     "gates.md's title said 'the two axes' over a file with Axis A, B and C"),

    # The number moved the moment an exclusion was added, and prose in two documents
    # kept the old one. Registered so the corpus's own size cannot be restated stale.
    ("cold-trigger surfaces",
     r"\b" + _NUM + r"\s+(?:files|surfaces)\s+state\s+the\s+condition\b",
     lambda: len(_COLD_SURFACES) if "_COLD_SURFACES" in globals() and _COLD_SURFACES else None,
     "prose said fourteen after an exclusion took the corpus to thirteen"),

    ("reference files",
     r"\b" + _NUM + r"\s+files\s+under\s+`?references/`?",
     lambda: len([f for f in os.listdir(refdir) if f.endswith(".md")]) if os.path.isdir(refdir) else None,
     "SKILL-CARD.md said 26 against a directory holding 28"),
]

# Living documents: what a reader takes as true NOW. CHANGELOG is excluded above; run
# records under the artifact root's specs/ are frozen accounts of a past run, same reasoning.
_LIVING = ["README.md", "SKILL-CARD.md", "CONTRIBUTING.md", "CLAUDE.md",
           "docs/DOCMAP.md", "evals/RESULTS.md",
           "plugins/task-pipeline/skills/task-pipeline/SKILL.md",
           "plugins/task-pipeline/skills/evidence-docs/SKILL.md"]
for _root, _dirs, _fs in os.walk(refdir):
    _LIVING += [os.path.relpath(os.path.join(_root, _f), ROOT) for _f in _fs if _f.endswith(".md")]

def _is_quoted(text, match):
    """A number inside a double-quoted span is a CITATION of what a document said, not a
    claim about now — `evals/RESULTS.md` quotes its own stale "Dated runs recorded 0" while
    narrating the incident that put this registry here. Deterministic and vocabulary-free:
    no marker list to grow per incident, which is the drift class this file is about.

    Scoped to the PARAGRAPH, not the line. Its first version checked one line, and this
    repository wraps prose at ~80 characters — so a quotation split across a line break
    stopped being a quotation and the citation tripped the check. That is the third time a
    per-line predicate has failed on this wrapping corpus (v1.24.0's marker guard was the
    second), which is why the unit is written down here rather than discovered again.
    Cost, stated: a live claim someone chose to wrap in quotes is exempt."""
    ps = text.rfind("\n\n", 0, match.start())
    ps = 0 if ps < 0 else ps + 2
    pe = text.find("\n\n", match.end())
    pe = len(text) if pe < 0 else pe
    para, off = text[ps:pe], ps
    for _q in re.finditer(r'"[^"]*"', para, re.S):
        if _q.start() + off <= match.start() and match.end() <= _q.end() + off:
            return True
    return False

# Each living document is read ONCE, not once per class. Nested class-outer/doc-inner
# opened ~36 files six times over; the states logic below is unchanged.
def _paragraphs(text):
    """Split on blank lines. The unit matters and has bitten this file: scoped to the
    whole file, a guard measures a document's VOCABULARY; scoped to a paragraph, it
    measures what one passage claims. Third call site, so it is a function."""
    return re.split(r"\n\s*\n", text)


# One home for the carve-out vocabulary. It was written twice — once correctly and
# once with the escaping doubled, so the second site matched a literal backslash and
# every inversion walked past it. The copy that worked and the copy that did not were
# forty lines apart and looked identical in review.
_EXCEPTION_MARKER = r"\b(unless|except|other than|save where)\b"


def _carve_out(text, needle):
    """The exception marker inside the ITEM that carries `needle`, or None.

    Scope has been wrong in both directions here. Sentence-scoped, a carve-out one
    period away was invisible; paragraph-scoped, three independent bullets share one
    blank-line-delimited block in residue.md, so a legitimate exception on the third
    tripped the second's rule. An item is what a rule actually occupies: a bullet or
    a numbered entry plus its indented continuation."""
    _n = _flatten(needle, lower=True)
    for _para in re.split(r"\n\s*\n", text):
        if _n not in _flatten(_para, lower=True):
            continue
        # Narrowest chunk that still holds the whole rule: the paragraph, then the
        # bullet inside it. Splitting on items ALONE glued a rule that lives in a
        # paragraph to the bullet above it, and a legitimate `unless` two rules away
        # tripped it — the third scoping mistake this guard has made, in the third
        # direction.
        for _item in re.split(r"\n(?=\s*(?:[-*]|\d+\.)\s)", _para):
            if _n in _flatten(_item, lower=True):
                return re.search(_EXCEPTION_MARKER, _flatten(_item, lower=True))
        return re.search(_EXCEPTION_MARKER, _flatten(_para, lower=True))
    return None


def _row_cells(line, lower=True):
    """Pipe-split a markdown row into flattened cells. Third copy of this comprehension
    when it was extracted, and the drift it invites is not hypothetical: the Human-column
    index bug in this same module came from two lists split slightly differently."""
    return [_flatten(_x, lower=lower).strip() for _x in line.split("|")[1:-1]]


def _flatten(text, lower=False):
    """Collapse the corpus's own formatting before matching: ~80-column wrapping and
    emphasis INSIDE a phrase have now defeated three guards in this file, each of
    which hand-rolled its own version of this. The class repeated three times, so it
    became a mechanism — the same rule audit.md applies to findings."""
    _f = re.sub(r"\s+", " ", re.sub(r"[*_`]+", "", text))
    return _f.lower() if lower else _f


def _gate_bullet(section_body):
    """The `- **GATE` bullet of a stage section, bounded below.

    Two call sites extracted this byte for byte with different variable names. The
    bound below matters and was learned once already: the GATE is the last bullet, so
    a plain split hands it the rest of the section and a following paragraph answers
    for it. A fix to how the bullet is bounded should land in one place."""
    _b = next((_x for _x in re.split(r"\n(?=- )", section_body)
               if re.match(r"- \*\*GATE\b", _x.lstrip())), "")
    return re.split(r"\n(?=\S)", _b)[0]


# This file reads itself in three places; once is enough.
_OWN_SRC = open(os.path.join(ROOT, "test", "validate.py"), encoding="utf-8").read()

_LIVING_TEXT = {}
for _living in _LIVING:
    _lp = os.path.join(ROOT, _living)
    if os.path.isfile(_lp):
        _LIVING_TEXT[_living] = open(_lp, encoding="utf-8").read()
# The Cursor rule and the command are shipped doctrine and restate counts like any
# other surface, but neither was in this corpus — so the review that found the Cursor
# rule still claiming "two axes" found it by reading, not by a check. Added here
# rather than to _LIVING, which other guards use for a different question.
for _extra in ["cursor/rules/task-pipeline.mdc",
               "plugins/task-pipeline/commands/task-pipeline.md"]:
    _xp = os.path.join(ROOT, _extra)
    if os.path.isfile(_xp) and _extra not in _LIVING_TEXT:
        _LIVING_TEXT[_extra] = open(_xp, encoding="utf-8").read()

_UNLOOKED = []

# learned.md rule 16 — a rule that lands in the table and nowhere else is a rule the
# run never meets, because nothing at stage 0 or stage 10 sends anybody to it. The
# rule's own failure mode applied to itself: doctrine carried in one file reads like
# doctrine in force. Each consumer is named, so a file dropping its citation fails
# here rather than silently ending the coverage.
_learned = os.path.join(refdir, "learned.md")
if os.path.isfile(_learned):
    _lt = open(_learned, encoding="utf-8").read()
    if re.search(r"^\|\s*16\s*\|", _lt, re.M):
        if "Carried-in claims" not in _lt:
            fail("references/learned.md: rule 16 is in the table and its binding row "
                 "does not name knowledge-sources.md -> Carried-in claims")
        for _f, _needle in (
            ("knowledge-sources.md", "## Carried-in claims"),
            ("continuity.md", "Each iteration re-measures the work-list"),
            ("audit.md", "the work-list is re-measured"),
            ("grill.md", "0 Work-list"),
        ):
            _fp = os.path.join(refdir, _f)
            if not os.path.isfile(_fp) or _needle not in open(_fp, encoding="utf-8").read():
                fail(f"references/{_f}: learned.md rule 16 is in force and this file "
                     f"does not carry {_needle!r} — a state claim inherited across a "
                     "session boundary goes unmeasured wherever the citation is missing")

# learned.md rule 17 — the same shape as rule 16's guard, and for the same reason: a rule that
# lands in the table and nowhere else is a rule the run never meets. This one guards the check that
# would have caught the incident that produced it, so it is the one most likely to be quietly
# dropped when a consumer file is rewritten.
if os.path.isfile(_learned):
    _lt17 = open(_learned, encoding="utf-8").read()
    if re.search(r"^\|\s*17\s*\|", _lt17, re.M):
        for _f, _needle in (
            ("knowledge-sources.md", "## The source is not the copy you have"),
            ("grill.md", "0 Source"),
        ):
            _fp = os.path.join(refdir, _f)
            if not os.path.isfile(_fp) or _needle not in open(_fp, encoding="utf-8").read():
                fail(f"references/{_f}: learned.md rule 17 is in force and this file "
                     f"does not carry {_needle!r} — a run editing a stale checkout deletes "
                     "newer work by fast-forward wherever the citation is missing")

# learned.md rule 18 — same shape, same reason. This one guards the check that separates a green
# from a green obtained off residue, which is the class the retro has recorded more often than any
# other over the life of this skill.
if os.path.isfile(_learned):
    _lt18 = open(_learned, encoding="utf-8").read()
    if re.search(r"^\|\s*18\s*\|", _lt18, re.M):
        for _f, _needle in (
            ("tdd.md", "## The green from residue"),
            ("grill.md", "0 Fixtures"),
        ):
            _fp = os.path.join(refdir, _f)
            if not os.path.isfile(_fp) or _needle not in open(_fp, encoding="utf-8").read():
                fail(f"references/{_f}: learned.md rule 18 is in force and this file "
                     f"does not carry {_needle!r} — a suite green against accumulated local "
                     "state is a green whose premise is false on every runner")

# learned.md rule 19 — the other half of rule 11. A command that never ran exits 0 and prints
# nothing, and satisfies a run that checks neither, so the guard names both consumers.
if os.path.isfile(_learned):
    _lt19 = open(_learned, encoding="utf-8").read()
    if re.search(r"^\|\s*19\s*\|", _lt19, re.M):
        for _f, _needle in (
            ("audit.md", "## Silence is not a reading"),
            ("review.md", "An empty result is not a clean result"),
        ):
            _fp = os.path.join(refdir, _f)
            if not os.path.isfile(_fp) or _needle not in open(_fp, encoding="utf-8").read():
                fail(f"references/{_f}: learned.md rule 19 is in force and this file "
                     f"does not carry {_needle!r} — an instrument that failed and a subject "
                     "that is clean both produce an empty string")

# learned.md rule 20 — the rule about a thing existing twice, guarded in both files it exists in,
# which is the joke and also the point: the sweep lives in grill.md and templates/brief.md, and this
# skill has twice added a row to one of them and not the other.
if os.path.isfile(_learned):
    _lt20 = open(_learned, encoding="utf-8").read()
    if re.search(r"^\|\s*20\s*\|", _lt20, re.M):
        for _f, _needle in (
            ("audit.md", "## Two copies, and which one wins"),
            ("grill.md", "0 Duplicates"),
        ):
            _fp = os.path.join(refdir, _f)
            if not os.path.isfile(_fp) or _needle not in open(_fp, encoding="utf-8").read():
                fail(f"references/{_f}: learned.md rule 20 is in force and this file "
                     f"does not carry {_needle!r} — the copy that ships is often not the copy "
                     "anybody opens")

# learned.md rule 21 — the deadlock rule, guarded where it was found. The retro stage must not
# reintroduce "prune first": its cold trigger reads the stamp, so a prune ahead of the stamp is a
# check that has never run on real data.
if os.path.isfile(_learned):
    _lt21 = open(_learned, encoding="utf-8").read()
    if re.search(r"^\|\s*21\s*\|", _lt21, re.M):
        _rp = os.path.join(refdir, "retrospective.md")
        _rt = open(_rp, encoding="utf-8").read() if os.path.isfile(_rp) else ""
        if "## Stamp first, then prune, then write" not in _rt:
            fail("references/retrospective.md: learned.md rule 21 is in force and the stage does "
                 "not open with 'Stamp first, then prune, then write' — the cold trigger reads the "
                 "stamp, so a prune placed ahead of it can never run on real data")
        if re.search(r"runs BEFORE the new entry", _rt):
            fail("references/retrospective.md: the prune is still described as running BEFORE the "
                 "stamp — that ordering is the deadlock rule 21 records")
        if "Each trigger is a command, not a judgement" not in _rt:
            fail("references/retrospective.md: the three retirement triggers are not expressed as "
                 "commands — a retirement condition nobody can run is one nobody applies")

# learned.md rule 21, widened from one file to THE CLASS. v1.23.0 changed the retro's act order to
# stamp-first in references/retrospective.md and reached no other surface: SKILL.md — which an agent
# loads first — still enumerated "prune, stamp, entry" through v1.23.1, along with six more surfaces.
#
# The guard above proves a consumer still CITES retrospective.md. It cannot prove the consumer AGREES
# with it, because a contradicting consumer keeps its citation, its link resolves and its section
# exists. Every guard for rules 16-21 has that shape, which is why this one compares ORDER instead,
# and derives the expected order from retrospective.md at check time rather than hardcoding it — a
# guard written against a literal drifts from the doctrine it guards the moment the doctrine moves.
#
# SCOPE: ordered ENUMERATIONS of the two acts, in four deterministic shapes —
#   P1 "prune, stamp" / "prune → stamp" (adjacent, connector punctuation only)
#   P2 "prune first ... then stamp"     (the first...then construction, aside allowed between)
#   P4 "prune … then stamp"          (sequence marker without "first" — "prune before you add … then stamp")
#   P5 a bare "prune first" / "prune before" directive with NO second act nearby — the shape a
#      TABLE CELL takes ("| carry a lesson | retrospective.md | prune first, cap of ten |"), which
#      every pairwise shape misses by construction because there is no pair. It was live in the
#      shipped evidence-docs navigator and only a review found it.
#   P3 an ordered LIST whose items open with the acts ("1. Prune first." / "2. Stamp the run")
#      — the shape acceptance.md and stages.md used, which P1 and P2 both missed because a
#      numbered list needs no connector word at all. Found by probing the guard against the
#      corpus rather than by trusting its first green.
# Prose that merely mentions both acts in one paragraph ("the prune runs after the stamp") is NOT an
# enumeration and is deliberately OUT of scope. Measured before shipping (learned.md rule 10): the
# loose "both words in a paragraph" predicate returned 32 hits of which 22 were false, including
# retrospective.md's own correct sentences. This one returns 8, all true.
# HISTORY EXEMPTION: a paragraph carrying a past-tense marker is quoting the OLD order as the
# defect — learned.md's rule-21 narrative and retrospective.md's own rationale both do this. The
# markers are exact strings, not a heuristic; a new one has to be added deliberately. The marker may
# sit AFTER the enumeration ("The stage's own instruction was **prune first, then stamp**. So the
# trigger…"), so the paragraph is the unit and the exemption is computed once for every shape.
# Cost, stated: a paragraph that narrates the old order AND states a wrong one is exempt.
_ORDER_HISTORY = ("used to be", "instruction was", "order was", "it used to read",
                  "still said", "still taught", "still teach")
_P1 = re.compile(r"\b(prune|stamp)\b[\s,;:·]*(?:→|->|,|·)?\s*(?:then\s+)?(?:the\s+)?\b(stamp|prune)\b", re.I)
_P2 = re.compile(r"\b(prune|stamp)\b[^.!?]{0,60}?\bfirst\b.{0,400}?(?:\bthen\b|,)\s*(?:the\s+)?\b(stamp|prune)\b", re.I | re.S)
_P4 = re.compile(r"\b(prune|stamp)\b.{0,400}?\bthen\s+(?:the\s+)?\b(stamp|prune)\b", re.I | re.S)
_P5 = re.compile(r"\bprune\s+(?:first|before)\b", re.I)
_rp21 = os.path.join(refdir, "retrospective.md")
if os.path.isfile(_learned) and os.path.isfile(_rp21):
    _lt = open(_learned, encoding="utf-8").read()
    if re.search(r"^\|\s*21\s*\|", _lt, re.M):
        # Derive the expected order from the doctrine's own heading, do not restate it.
        _rt21 = open(_rp21, encoding="utf-8").read()
        _hm = re.search(r"^##\s+(Stamp|Prune)\s+first,\s+then\s+(prune|stamp)", _rt21, re.M | re.I)
        if not _hm:
            fail("references/retrospective.md: no '## <act> first, then <act>' heading — the order "
                 "guard derives the expected order from it and cannot run without it")
        else:
            _expect_first = _hm.group(1).lower()          # 'stamp'
            _scan = []
            for _root, _dirs, _fs in os.walk(os.path.join(ROOT, "plugins")):
                _scan += [os.path.join(_root, _f) for _f in _fs if _f.endswith(".md")]
            _scan += [os.path.join(ROOT, _f) for _f in
                      ("README.md", "CONTRIBUTING.md", "CLAUDE.md", "docs/DOCMAP.md",
                       "cursor/rules/task-pipeline.mdc", f"{ART}/retro.md")]
            for _f in sorted(set(_scan)):
                if not os.path.isfile(_f):
                    continue
                _raw = open(_f, encoding="utf-8").read()
                _prev = ""
                for _para in _paragraphs(_raw):
                    _flat = re.sub(r"\s+", " ", _para)
                    # The history exemption is computed ONCE per paragraph and applies to every
                    # shape, P3 included. Its first version exempted only the prose shapes, so a
                    # numbered list narrating the old order as the defect — the most natural way
                    # to write that narration, and one this repository already writes in prose —
                    # would have blocked a legitimate commit. Found in review, not by a green.
                    #
                    # The PRECEDING paragraph counts too: a list is introduced by its lead-in
                    # ("The stage's own instruction was, in this order:" followed by a blank line
                    # and the items), so a marker-only-in-this-paragraph rule still fired on the
                    # one narration shape a reader would actually write.
                    # Cost, stated: a paragraph immediately after a history narration is exempt
                    # even if it states a wrong order on its own account.
                    _hist = any(_h in (_flat + " " + _prev).lower() for _h in _ORDER_HISTORY)
                    _prev = _flat
                    if _hist:
                        continue
                    # P3 — ordered list items opening with an act, compared in list order.
                    # An item may open with a connector ("2. **Then prune.**"); matching only a
                    # bare act word made the guard blind to the wording this very release
                    # introduced. Scoped to ONE paragraph — a markdown ordered list is one block —
                    # because scanning the whole file let two unrelated lists read as one
                    # enumeration, and comparing only the first pair let a violation that follows
                    # a correct list through unseen. EVERY adjacent pair is checked, not the first.
                    _P3RE = r"^\s*\**\s*\d+\.\s+\**(?:then\s+|first,?\s+)?\**\s*(prune|stamp)\b"
                    _seq = [x.lower() for x in re.findall(_P3RE, _para, re.M | re.I)]
                    for _i in range(len(_seq) - 1):
                        _a, _b = _seq[_i], _seq[_i + 1]
                        if _a == _b or _a == _expect_first:
                            continue
                        _rel = os.path.relpath(_f, ROOT)
                        _ln = _raw[:_raw.find(_para)].count("\n") + 1
                        fail(f"{_rel}:{_ln}: an ordered list runs the retro's acts "
                             f"{_a!r} then {_b!r} — references/retrospective.md orders them "
                             f"{_expect_first!r} first (learned.md rule 21)")
                        break
                    # P5 — a lone directive, no pair to compare. Only fires when the expected
                    # first act is NOT "prune"; derived, not hardcoded.
                    if _expect_first != "prune":
                        for _m5 in _P5.finditer(_flat):
                            _rel = os.path.relpath(_f, ROOT)
                            _line = _raw[:_raw.find(_para)].count("\n") + 1
                            fail(f"{_rel}:{_line}: directs {_m5.group(0)!r} with no second act "
                                 f"to compare — references/retrospective.md puts {_expect_first!r} "
                                 f"first (learned.md rule 21). A table cell naming one act is the "
                                 f"shape every pairwise check misses.")
                            break
                    for _pat in (_P1, _P2, _P4):
                        for _m in _pat.finditer(_flat):
                            _a, _b = _m.group(1).lower(), _m.group(2).lower()
                            if _a == _b or _a == _expect_first:
                                continue
                            _rel = os.path.relpath(_f, ROOT)
                            _line = _raw[:_raw.find(_para)].count("\n") + 1
                            fail(f"{_rel}:{_line}: enumerates the retro's acts as "
                                 f"{_a!r} before {_b!r} — references/retrospective.md orders them "
                                 f"{_expect_first!r} first (learned.md rule 21: the cold trigger "
                                 f"reads the stamp, so a prune ahead of it never runs on real "
                                 f"data). Found: {_m.group(0).strip()!r}")

# The companion list exists TWICE in companion-skills.md — as the matrix a reader consults
# and as the preflight block the agent prints — and nothing compared them. That is
# learned.md rule 20's shape exactly (a thing that exists twice; the useful question is which
# one is used, and here BOTH are: the reader reads one, the operator is shown the other).
# A companion added to the matrix and missing from the preflight is a recommendation nobody
# is ever offered; the reverse is an install line for something the matrix does not explain.
# Found while adding chrome-devtools, which would have been the first to drift.
_cs = os.path.join(refdir, "companion-skills.md")
if os.path.isfile(_cs):
    _cst = open(_cs, encoding="utf-8").read()
    # matrix rows: bolded name in the first cell, minus the struck-through "not a dependency" rows
    _matrix = set()
    for _row in re.findall(r"^\|\s*\*\*([^*|]+)\*\*", _cst, re.M):
        _name = re.split(r"\s*\(", _row)[0].strip()
        _name = re.sub(r"^\[|\]$", "", _name)      # the matrix wraps some names in a markdown link
        _matrix.add(_name.lower())
    _pre = _cst.split("Preflight (emit before stage 0)")[-1]
    _block = re.search(r"```(.*?)```", _pre, re.S)
    if _matrix and _block:
        # The preflight names a companion then dashes into its explanation; take everything
        # before the dash, so "Figma MCP" arrives whole rather than truncated at the space.
        _offered = set()
        for _line in re.findall(r"^\s*[✓✗]\s+(.+?)\s+[—-]", _block.group(1), re.M):
            _offered.add(re.sub(r"\s*mcp$", "", _line.strip().lower()))

        def _same(_a, _b):
            return _a == _b or _a.startswith(_b) or _b.startswith(_a)

        # BOTH directions (learned.md rule 2). The first version checked matrix -> preflight
        # only, in a repository whose rule 2 is precisely "compute the mapping in both
        # directions" — and the reverse is a real failure with a different shape: an install
        # line for a companion the matrix never explains, which is what an operator would be
        # asked to run without being told why.
        for _m in sorted(_m for _m in _matrix if not any(_same(_m, _o) for _o in _offered)):
            fail("references/companion-skills.md: a companion is in the matrix and not in the "
                 f"preflight block — {_m!r}. A companion the operator is never offered is a "
                 "recommendation that exists only for the reader (learned.md rule 20: the list "
                 "exists twice and both copies are used)")
        for _o in sorted(_o for _o in _offered if not any(_same(_o, _m) for _m in _matrix)):
            fail("references/companion-skills.md: a companion is offered in the preflight and "
                 f"absent from the matrix — {_o!r}. The operator is asked to install something "
                 "the table never explains, which is the same drift read from the other side")

# The cold-retirement condition is stated on every surface in _COLD_SURFACES below (the list is
# the count — an earlier draft of this comment said 'seven' over a list of six). It gained a SECOND UNIT in
# v1.27.0: "five run stamps OR sixty days". The stamp counter is written only by a run of this
# pipeline, so where a project ships some of its work another way the counter stops while the
# work does not — measured here, ten consecutive releases (v1.16.0..v1.23.0) carry no stamp,
# and across that stretch the trigger was not strict or lenient but UNREADABLE. A list capped
# at ten with an unreadable retirement condition fills up and stops being pruned.
#
# A second unit on one surface and not the others is the class M8 shipped a guard for: the
# rule is corrected where somebody was looking and left everywhere else. So every surface that
# states the condition must state BOTH units. Rotation ("entries older than five stamps move
# to the archive") is a DIFFERENT mechanism and is deliberately out of scope — it is named in
# the scope line so the exclusion is a decision rather than an oversight.
# The corpus is DISCOVERED, not listed. A hand-listed one was seven files and missed
# README.md, which states the condition and had never been checked — found by reading,
# in the release after a review found the same shape in the claim registry's corpus.
# Nobody notices a corpus that is too small, because everything inside it passes. So
# any shipped surface that states the condition is a surface that must state both units.
#
# Excluded on purpose, and each for a reason that is not "it was inconvenient":
# CHANGELOG.md narrates the day the second unit was added, the artifact root's specs/ are
# point-in-time design records, and the retro archive is not read in full.
# Only load-bearing entries: the directory names below are pruned out of the walk
# itself, so listing them here again would state the intent twice and enforce it once.
# <artifacts>/{specs,plans,retro}/ are frozen point-in-time records; retro.md
# itself is live and stays in. plans/ was missing and a plan already carried the phrase
# — it escaped only because its wording did not match the stricter regex.
_COLD_SKIP = ("CHANGELOG.md", f"{ART}/specs/", f"{ART}/retro/", f"{ART}/plans/")
def _discover_md(skip, predicate):
    """Walk the repo for .md/.mdc surfaces a check applies to. Second caller, so it is
    a function: the shape (prune, filter, relpath, sort) was copy-pasted once and this
    file's own doctrine promotes a class at its second occurrence, not its third."""
    _out, _texts = [], {}
    for _r, _d, _f in os.walk(ROOT):
        _d[:] = [_x for _x in _d if _x not in (".git", "node_modules", "graphify-out")]
        for _n in _f:
            if not _n.endswith((".md", ".mdc")):
                continue
            _rl = os.path.relpath(os.path.join(_r, _n), ROOT)
            if any(_rl == _s or _rl.startswith(_s) for _s in skip):
                continue
            _c = _LIVING_TEXT.get(_rl) or open(os.path.join(_r, _n), encoding="utf-8").read()
            if predicate(_c):
                _out.append(_rl)
                _texts[_rl] = _c
    _out.sort()
    return _out, _texts


_COLD_SURFACES, _COLD_TEXT = _discover_md(
    _COLD_SKIP, lambda _c: "five run stamps" in _flatten(_c, lower=True))
# A NARRATION of what the rule said before the second unit existed is not a statement
# of the rule — learned.md's own rule-21 incident quotes the old wording, and rewriting
# it would falsify the incident. Same convention the claim registry uses: a
# double-quoted span is a citation. Italics are not, deliberately — a marker vocabulary
# that grows per incident is the drift this file exists to prevent.
_COLD_RE = re.compile(r"(?:has\s+not\s+)?fired\s+in\s+(?:the\s+last\s+)?five\s+run\s+stamps", re.I | re.S)
for _f in _COLD_SURFACES:
    _fp = os.path.join(ROOT, _f)
    if not os.path.isfile(_fp):
        continue
    _ft = _COLD_TEXT.get(_f) or open(_fp, encoding="utf-8").read()
    for _para in _paragraphs(_ft):
        # Normalise whitespace AND markdown emphasis. The canonical row in
        # retrospective.md reads "the last **five run stamps**", and a whitespace-only
        # normalisation left the asterisks sitting inside the phrase — so the guard
        # silently skipped the one file that DEFINES the trigger. Third time in this
        # programme that a predicate was defeated by this corpus's formatting rather
        # than by its content (twice by the ~80-column wrap, once by bold).
        _flat = _flatten(_para)
        _m = _COLD_RE.search(_flat)
        if not _m:
            continue
        if _is_quoted(_flat, _m):
            continue                    # a narration of the old wording, not a statement
        if not re.search(r"sixty\s+days|60\s+days", _flat, re.I):
            _line = _ft[:_ft.find(_para)].count("\n") + 1
            fail(f"{_f}:{_line}: states the cold-retirement condition as five run stamps and "
                 "omits the second unit — the stamp counter is written only by a run of this "
                 "pipeline and stops when the pipeline is not used, which is exactly when a "
                 "stale rule matters most. Both units, on every surface that states it.")

# Every worked GATE verdict in the doctrine must print BOTH disclosures. The formats live in
# four files, and this bundle's recurring defect is one statement updated on one surface — so
# the example verdicts are held together the way the stage list and the retro order are.
#
# Why disclosures and not a ratchet: a ratchet may only shrink, and an abstention count under
# that rule pressures exactly one thing — claiming more. A run reaching `abstained: 0` is not
# more careful, it stopped saying "I don't know". Refusals and wrong answers are communicating
# vessels. gates.md -> Disclosures states the rule; this guard only holds the print.
# Discovered, not listed — third corpus in this file to be widened by finding what a
# hand-written list had missed, and the last one that was still hand-written. The
# five-file version omitted README.md, which prints a worked GATE 10 verdict in its
# own doctrine section. A surface that shows a verdict teaches its format.
_DISCLOSURE_FILES, _ = _discover_md(
    # a changelog narrates old verdict formats; superpowers/ is a record of runs
    ("CHANGELOG.md", f"{ART}/"),
    lambda _c: any(re.search(r"^GATE\s+\d+", _b, re.M)
                   for _b in re.findall(r"```[^\n]*\n(.*?)```", _c, re.S)))
for _f in _DISCLOSURE_FILES:
    _fp = os.path.join(ROOT, _f)
    if not os.path.isfile(_fp):
        continue
    _ft = open(_fp, encoding="utf-8").read()
    for _blk in re.findall(r"```[^\n]*\n(.*?)```", _ft, re.S):
        if not re.search(r"^GATE\s+\d+", _blk, re.M):
            continue
        _flat = _flatten(_blk)
        _missing = [_d for _d in ("abstained", "unlooked") if _d not in _flat]
        if _missing:
            _line = _ft[:_ft.find(_blk)].count("\n") + 1
            fail(f"{_f}:{_line}: a worked GATE verdict omits {' and '.join(_missing)} — "
                 "a verdict that prints neither reads as 'verified' rather than as 'green, "
                 "and here is what nobody claimed and what nothing looked at' "
                 "(gates.md -> Disclosures)")

# Evaluated HERE, not where the registry is declared: one class counts a DISCOVERED
# corpus, which does not exist until the walks above have run. Declared early,
# computed late.
_CLAIM_STATES = []
for _label, _pat, _compute, _incident in _CLAIM_REGISTRY:
    _truth = _compute()
    if _truth is None:                      # the source of truth is absent — say so, do not guess
        _CLAIM_STATES.append(f"{_label}: skip — no source")
        continue
    _seen = 0
    for _living, _txt in _LIVING_TEXT.items():
        for _m in re.finditer(_pat, _txt, re.I):   # "## The ten canons" is a heading; case is not a claim
            if _is_quoted(_txt, _m):
                continue
            _stated = _as_int(_m.group(1))
            if _stated is None:            # a word outside the map — say nothing rather than guess
                continue
            _seen += 1
            if _stated != _truth:
                fail(f"{_living}: states {_m.group(0).strip()!r} but {_label} computes to "
                     f"{_truth} — derive the number or delete it. This class is registered "
                     f"because: {_incident}")
    # Progressive arming (gates.md): a class nobody states is DORMANT, not passing. Printed,
    # because a registry reporting green over six classes it never looked at is exactly the
    # false success it exists to catch. Most classes are dormant on purpose — the numbers
    # were deleted rather than corrected, and this is the ratchet against re-introducing them.
    # "ok 4 (truth 10)" reads as "claims 4, truth is 10" — the author of this line misread
    # his own output that way within a day of writing it. The count is of agreeing statements,
    # so it is written as a multiplier: a state line nobody can parse is not a disclosure.
    _CLAIM_STATES.append(
        f"{_label}: {'agrees x' + str(_seen) if _seen else 'dormant'} (truth {_truth})")

# The rotation axes are defined once, in audit.md, and summarised on surfaces that
# cannot link to it (the Cursor rule is self-contained by contract). Measured on
# 2026-08-09, before this guard existed: audit.md defined FIVE axes, the Cursor rule
# named FOUR and README named THREE — and each summary read as complete, because a
# list of three orthogonal things is a convincing list of three orthogonal things.
# Nothing compared them, so the drift was invisible from inside every file.
#
# Keys are derived from audit.md at check time, never hand-listed here: a hand-listed
# key set is the second source of truth this guard exists to forbid. A surface naming
# three or more axes is enumerating them, and must name all of them.
_AXIS_KEYS, _AXIS_SRC = _axis_keys()
if _AXIS_KEYS is None:
    fail("test/validate.py: cannot locate the rotation-axis list in references/audit.md "
         "— the axis-enumeration guard has no source of truth and is silently passing")
elif len(_AXIS_KEYS) < 2:
    fail(f"references/audit.md: the rotation-axis list parsed to {len(_AXIS_KEYS)} axes "
         "— either the list moved or the bold-lead shape changed; a guard reading one "
         "axis would pass every surface trivially")
else:
    _AXIS_SURFACES = ["README.md", "CONTRIBUTING.md", "CLAUDE.md",
                      "cursor/rules/task-pipeline.mdc",
                      "plugins/task-pipeline/commands/task-pipeline.md"] + [
        _l for _l in _LIVING if _l.startswith("plugins/")]
    for _f in dict.fromkeys(_AXIS_SURFACES):
        _fp = os.path.join(ROOT, _f)
        if not os.path.isfile(_fp) or os.path.relpath(_fp, ROOT) == os.path.relpath(_AXIS_SRC, ROOT):
            continue
        # Unit: the PARAGRAPH, not the file. Scoped to the file, this guard's first run
        # accused stages.md of enumerating three axes when its three hits were 595 lines
        # apart and meant different things — "decisions, seams, why", a stage-9 duty, and
        # a citation to gates.md. An enumeration is contiguous; a vocabulary is not.
        # Emphasis lives INSIDE these phrases ("invariants *across* deliverables") and
        # ~80-column wrapping splits them; both defeated earlier guards in this file.
        _raw = _LIVING_TEXT.get(_f) or open(_fp, encoding="utf-8").read()
        for _para in _paragraphs(_raw):
            _flat = _flatten(_para, lower=True)
            _named = [_k for _k in _AXIS_KEYS if _k in _flat]
            if len(_named) < 3:
                continue                 # not enumerating; a passing mention is not a list
            _missing = [_k for _k in _AXIS_KEYS if _k not in _named]
            if _missing:
                _line = _raw[:_raw.find(_para)].count("\n") + 1
                fail(f"{_f}:{_line}: enumerates the rotation axes but names "
                     f"{len(_named)} of {len(_AXIS_KEYS)} — missing "
                     f"{', '.join(repr(_m) for _m in _missing)}. Either name every axis "
                     "audit.md defines, or stop enumerating and point at audit.md; a "
                     "summary that lists most of a list reads as complete.")

# The re-derivation axis demands a PAIR printed rather than agreement asserted. A
# doctrine that only asserts that cannot teach it, so the axis carries a worked block
# and this guard holds the block to the axis's own contract: both numbers and the
# verdict, visible. The lead is located by name and its absence FAILS rather than
# skips — a guard whose subject was renamed away must say so.
_rd = os.path.join(refdir, "audit.md")
if os.path.isfile(_rd):
    _rdt = (_LIVING_TEXT.get("plugins/task-pipeline/skills/task-pipeline/references/audit.md")
            or _AXIS_MEMO.get("t") or open(_rd, encoding="utf-8").read())
    _m = re.search(r"^\d+\.\s+\*\*Re-derivation\*\*", _rdt, re.M)
    if not _m:
        fail("references/audit.md: the Re-derivation axis is gone or renamed — the guard "
             "holding its worked example to its own 'print the pair' contract has no "
             "subject, and a guard with no subject passes everything")
    else:
        _body = _rdt[_m.start():]
        _nxt = re.search(r"^(?:\d+\.\s+\*\*|\*\*The crossover)", _body[3:], re.M)
        if _nxt:
            _body = _body[:_nxt.start() + 3]
        _blocks = re.findall(r"```[^\n]*\n(.*?)```", _body, re.S)
        _ok = [_b for _b in _blocks
               if all(_lbl in _flatten(_b, lower=True)
                      for _lbl in ("claimed:", "re-derived:", "verdict:"))]
        if not _ok:
            fail("references/audit.md: the Re-derivation axis has no worked block printing "
                 "`claimed:`, `re-derived:` and `verdict:` — the one axis whose exit "
                 "criterion is a printed pair must show the pair, or it is teaching "
                 "'assert agreement', which is the failure it names")

# learned.md's shape, printed rather than capped. The retro caps its standing
# instructions because they are read IN FULL every run; this file is entered by
# citation and its index is what must be right. Measured before writing that down:
# rules 15 -> 18 -> 21 -> 21 across four releases while the file grew, and every word
# of the growth was in the binding map — a cap would have squeezed the axis that had
# not moved, and a word budget would have hit the incidents, which are the only record
# of those events anywhere here.
#
# So it is a DISCLOSURE (gates.md -> Disclosures): no floor, no direction, never a
# target. It exists so growth is visible rather than a surprise, and so no document
# has to restate a number about this file.
#
# A rule leaves on two triggers only, and a departure shows as a GAP in the numbering:
# numbers are never reused and never closed up. A gap the Retired log does not name is
# a rule that vanished silently, taking its incident with it.
_LSHAPE = ""
_lp = os.path.join(refdir, "learned.md")
if os.path.isfile(_lp):
    _lt = _LIVING_TEXT.get("plugins/task-pipeline/skills/task-pipeline/references/learned.md") \
        or open(_lp, encoding="utf-8").read()
    _nums = [int(_n) for _n in re.findall(_RULE_ROW_ID, _lt, re.M)]
    _inc = re.search(r"^## The incidents.*?(?=^## )", _lt, re.M | re.S)
    # "**4 and 5 · Probes.**" is one write-up covering two rules. A digits-then-dot
    # pattern drops it, and the disclosure then prints a number lower than the file —
    # a disclosure that is wrong is worse than none, because nothing cross-checks it.
    _incs = ([_d for _h in re.findall(r"^\*\*([\d,\s]+(?:and[\d,\s]+)*)·", _inc.group(0), re.M)
              for _d in re.findall(r"\d+", _h)] if _inc else [])
    _incw = len(_inc.group(0).split()) if _inc else 0
    _bind = re.search(r"^## Where these bind.*?(?=^---|\Z)", _lt, re.M | re.S)
    _bindrows = len(re.findall(r"^\|", _bind.group(0), re.M)) - 2 if _bind else 0
    _ret = re.search(r"^### Retired\s*(.*?)(?=^##|\Z)", _lt, re.M | re.S)
    if _ret is None:
        fail("references/learned.md: no `### Retired` log — a rule can only leave on a "
             "logged line, and an absent log is indistinguishable from an empty one "
             "(the file's own *What leaves this file* section)")
    else:
        # NOT `elif _nums`: deleting every row makes the list falsy and skipped the
        # whole check — 21 rules removed at once printed PASS with `rules 0`.
        # Wholesale deletion is the loudest case this guard exists for.
        # The high-water mark comes from the FILE, not from max(_nums): deleting the
        # highest rule shrinks the maximum with it and no gap opens. Proven by running
        # it — deleting rule 21 passed a guard whose whole job is to catch that.
        _hw = re.search(r"Numbers\s+issued\s+so\s+far:\s*(\d+)", _flatten(_ret.group(1)), re.I)
        if not _hw:
            fail("references/learned.md: `### Retired` does not state `Numbers issued so far: N` "
                 "— without a high-water mark, deleting the highest-numbered rule shrinks the "
                 "maximum with it and the guard sees no gap at all")
        else:
            _high = int(_hw.group(1))
            # A high-water mark the same change can lower is not one, and the first
            # version of this check compared the working tree against HEAD — which are
            # the SAME THING on a committed checkout, i.e. in CI, where it therefore
            # never fired. It only worked in the local pre-commit window, which is the
            # only window its self-test exercised. Found by a reader who committed the
            # coordinated edit and watched it pass.
            #
            # So: the mark may never fall below any value it has ever held. One
            # `git log -p` over this file's history carries every version of the line,
            # added or removed, and the maximum of those is the real high-water mark.
            try:
                _hist = subprocess.run(
                    ["git", "-C", ROOT, "log", "-n", "80", "-p", "--format=",
                     "--", "plugins/task-pipeline/skills/task-pipeline/references/learned.md"],
                    capture_output=True, text=True, timeout=30)
                _seen = ([int(_x) for _x in re.findall(
                    r"Numbers\s+issued\s+so\s+far:\s*(\d+)", _flatten(_hist.stdout), re.I)]
                    if _hist.returncode == 0 else [])
            except Exception:
                _seen = []
            if not _seen:
                _UNLOOKED.append("learned.md high-water mark vs its own history (no git, no "
                                 "prior revision, or the mark is new) — a lowering would not "
                                 "be seen")
            elif _high < max(_seen):
                fail(f"references/learned.md: `Numbers issued so far` is {_high} but this "
                     f"file's history has held {max(_seen)} — the mark is a high-water mark "
                     "and may never fall; lowering it alongside a rule's removal is exactly "
                     "how a deletion hides, and comparing only against HEAD cannot see it "
                     "once the edit is committed")
            if _nums and _high < max(_nums):
                fail(f"references/learned.md: `Numbers issued so far: {_high}` is below the "
                     f"highest rule in the table ({max(_nums)}) — a new rule was added without "
                     "advancing the high-water mark, so its later deletion would be invisible")
            _gaps = [_n for _n in range(1, _high + 1) if _n not in _nums]
            # Anchored to the line's LEADING number. A body-wide digit scan lets a
            # subsumption note ("subsumed by rule 9") mask a real deletion of rule 9.
            # The high-water mark lives in this same section, so its digits are not
            # log entries. Strip it before parsing, or every reader of the log — this
            # one and any future one — counts the mark as a retirement.
            _log_body = re.sub(r"Numbers\s+issued\s+so\s+far:\s*\d+\.?", "",
                               _ret.group(1), flags=re.I)
            _logged = set(re.findall(r"^\s*-\s*\*\*(\d+)\s*·", _log_body, re.M))
            # Both directions — rule 2, applied to this guard. A number logged as
            # retired while its row is still in the table means the log is wrong or the
            # rule came back without anyone noticing, and only the reverse pass finds it:
            # a gap has one side, and so does a resurrection.
            _back = sorted(int(_l) for _l in _logged if int(_l) in _nums)
            if _back:
                fail("references/learned.md: rule number(s) "
                     + ", ".join(str(_b) for _b in _back)
                     + " are listed in `### Retired` and still present in the table — "
                     "either the log names the wrong rule or a retired rule came back "
                     "silently, and the binding map now points at both stories")
            _silent = [_g for _g in _gaps if str(_g) not in _logged]
            if _silent:
                fail("references/learned.md: rule number(s) "
                     + ", ".join(str(_s) for _s in _silent)
                     + " are missing from the table and named in no line of `### Retired` — "
                     "a rule that vanishes silently takes its incident with it, and the "
                     "next run re-learns it at full price")
    # "rules with an incident", not "incidents": one write-up can cover two rules
    # ("**4 and 5 · Probes.**"), so the two numbers differ and a label that does not
    # say which one it means is a number nobody can check.
    _LSHAPE = (f"learned.md — rules {len(_nums)} · rules with an incident {len(_incs)} · "
               f"incident words {_incw} · binding rows {_bindrows}")

# The board (references/backlog.md). The carry-over ledger's last column has always
# offered `backlog` as a home for a deferred row — a place the pipeline named and did
# not own. Measured before building it: across ten ledgers in this repo, **not one row
# ever used that value**, and sixteen rows sat `open` with no home at all. The dangling
# pointer was not `backlog`; it was `open`.
#
# Ten ledgers, six header shapes, and FIVE with two status-ish columns. Neither a
# positional read nor a by-name read survives that: both pick one cell per file and the
# wrong one in half the corpus. The test below asks neither question — see POSITION-FREE
# where the work actually happens.
#
# Floor 0, and it is a ratchet: every open row was given a board id at the seam's
# closing, so a new one arriving unhomed fails rather than joining a backlog of debt.
_BOARD = os.path.join(ARTP, "backlog.md")
_UNHOMED = []
_BOARD_IDS = set()
if os.path.isfile(_BOARD):
    _bt = open(_BOARD, encoding="utf-8").read()
    _BOARD_IDS = set(re.findall(r"\bB-(\d+)\b", _bt))
    # Each board file read ONCE and shared by both loops below. Re-opening them was
    # compounding the very cost this PR put on the board as row B-010.
    _BOARD_TEXT = {_BOARD: _bt}
    _tmplb = os.path.join(os.path.dirname(refdir), "templates", "backlog.md")
    if os.path.isfile(_tmplb):
        _BOARD_TEXT[_tmplb] = open(_tmplb, encoding="utf-8").read()
    if not _BOARD_IDS:
        fail(f"{ART}/backlog.md: no `B-NNN` row — an empty board and a missing "
             "board are the same thing to work on, and only one can be appended to")
    # POSITION-FREE, and the first version of this guard was not. Ten ledgers here carry
    # six header shapes and FIVE of them have two status-ish columns ('status'+'home',
    # 'resolution'+'state', …) — "take the last one" then read a different cell per file
    # and missed genuinely open rows in silence. Three rows also carry more cells than
    # their header, and skipping those was a second silent path.
    #
    # So: a row is OPEN if any of its cells *is* the word open (or says it needs a home),
    # and HOMED if a board id appears anywhere in the row. Neither test asks which column
    # it came from, so neither can be defeated by a shape nobody anticipated.
    # Neither pure-positional nor pure-textual survives this corpus, and both were
    # tried. Positional read the wrong cell in the five ledgers that carry TWO
    # status-ish columns. Text-only broke in both directions at once: too strict on a
    # real row worded "open as a printed exclusion", too loose on a description reading
    # "Open-source …", because a hyphen is punctuation and so is an arrow.
    #
    # So: the header names the candidate columns — ALL of them, never just the last —
    # and inside those columns a status is matched on a word boundary. A cell in the
    # What column cannot masquerade as a status because it is never looked at.
    _LEDGER_ID = {"#", "id", "row"}
    _LEDGER_STATUS = {"home", "where it lives now", "resolution", "status", "state"}
    _UNRES_RE = re.compile(r"^(?:open|unresolved|backlog)\b", re.I)
    _LEDGERS = sorted(glob.glob(os.path.join(ARTP, "specs/*carryover.md")))
    # ...and the SEEDED template, whose worked example is the first ledger every host
    # project ever sees. It showed a bare `backlog` home as a settled outcome for as
    # long as this seam existed, which is where the value nobody owned came from.
    _ctmpl = os.path.join(os.path.dirname(refdir), "templates", "carryover.md")
    if os.path.isfile(_ctmpl):
        _LEDGERS.append(_ctmpl)
    for _lf in _LEDGERS:
        _lt = open(_lf, encoding="utf-8").read()
        _rel = os.path.relpath(_lf, ROOT)
        _hdr = None
        for _l in _lt.splitlines():
            if _l.startswith("|") and _l.split("|")[1].strip().lower() in _LEDGER_ID:
                _hdr = _row_cells(_l)
                break
        if _hdr is None:
            continue                       # a ledger with no table yet
        _sidx = [_i for _i, _c in enumerate(_hdr) if _c in _LEDGER_STATUS]
        if not _sidx:
            fail(f"{_rel}: no status column among {sorted(_LEDGER_STATUS)} — a ledger "
                 "whose rows have no home column cannot be checked for dangling ones")
            continue
        for _l in _lt.splitlines():
            if not _l.startswith("|") or set(_l.strip()) <= set("|- "):
                continue
            _c = _row_cells(_l)
            if not _c or _c[0] in _LEDGER_ID:
                continue
            if len(_c) == len(_hdr):
                _cells = [_c[_i] for _i in _sidx]
            else:
                # The row's shape does not match its header — an embedded `|` inside
                # backticked text shifts the count on three rows here. Exact equality was
                # tried and was wrong: a resolved cell reads `open → B-019` and equals
                # nothing, so the row was skipped before the dangling-id check ran.
                #
                # So the fallback uses the same word-boundary match and looks at every
                # cell. On a row that cannot be mapped to columns that risks flagging a
                # description beginning "Open…", and that trade is deliberate: a false
                # positive is loud and fixable, a false negative is a check that passes
                # by looking at nothing.
                _cells = _c
            if not any(_UNRES_RE.match(_x) or "needs a home" in _x for _x in _cells):
                continue
            _ref = re.search(r"\bB-(\d+)\b", _l)
            if not _ref:
                _UNHOMED.append(f"{_rel} row {_c[0][:8]}")
            elif _ref.group(1) not in _BOARD_IDS:
                fail(f"{_rel} row {_c[0][:8]}: names `B-{_ref.group(1)}`, which is on no "
                     "board row — a pointer to an id nobody issued reads as filed and is not")
    if _UNHOMED:
        fail("carry-over rows still `open` with no board id: "
             + " · ".join(_UNHOMED)
             + " — the board exists so a deferred row has somewhere to be ranked; an open "
               "row with no id is the dangling pointer it was built to resolve "
               "(references/backlog.md)")
    # The priority is the one number on the board that a reader is invited to CHECK,
    # so it is checked. The template shipped with three rows that contradicted the
    # formula printed two lines below them — in the file seeded verbatim into every
    # host project as its first board, whose stated point is that the arithmetic is
    # visible. Found by a reader.
    for _bf, _btext in _BOARD_TEXT.items():
        _bfr = os.path.relpath(os.path.realpath(_bf), ROOT)
        for _l in _btext.splitlines():
            if not re.match(r"^\|\s*B-\d+\s*\|", _l):
                continue
            _cl = [_flatten(_x).strip() for _x in _l.split("|")[1:-1]]
            if len(_cl) < 8:
                fail(f"{_bfr}: row {_cl[0]} has {len(_cl)} cells where the board's shape "
                     "needs at least 8 — skipping it silently is how a malformed row "
                     "carries any priority it likes past a check built to compute one")
                continue
            try:
                _sev, _bl, _age, _pr = (int(_cl[4]), int(_cl[5]), int(_cl[6]), int(_cl[7]))
            except ValueError:
                fail(f"{_bfr}: row {_cl[0]} has a non-numeric sev/blast/age/prio — the four "
                     "are what make the ranking checkable, and prose in any of them makes "
                     "it an opinion again")
                continue
            _want = _sev * _bl + (2 if _age > 30 else 1 if _age > 14 else 0)
            if _want != _pr:
                fail(f"{_bfr}: row {_cl[0]} states prio {_pr} but sev {_sev} × blast {_bl} "
                     f"+ age bonus computes to {_want} — a priority that does not follow "
                     "from its own inputs is the hand-assigned number this column replaced")

    # Both directions: a board row invented with no source is the other failure, and only
    # the reverse pass finds it (learned.md rule 2).
    for _srcf, _stext in _BOARD_TEXT.items():
      for _row in re.findall(r"^\|\s*B-\d+\s*\|(.+)$", _stext, re.M):
        _cells = [_x.strip() for _x in _row.split("|")]
        if len(_cells) < 2 or not _cells[1]:
            fail(f"{os.path.relpath(_srcf, ROOT)}: a row names no Source — a row nobody can "
                 "trace back is a wish somebody typed, and six weeks later it is either "
                 "done twice or dropped by whoever trusts it least")
            break

# A blank line inside a table ENDS it. Every row after the gap loses the header and
# renders as pipe-delimited prose — on GitHub, in any CommonMark reader, and silently.
# This repo's own board carries a row about exactly this class ("a blank line silently
# splits a markdown table, and the documentation gate does not catch it"), and the class
# then hit that very board: three rows appended after a stray blank line rendered as
# text. audit.md says a class seen twice becomes a script rather than a third ledger
# row, so here is the script. The shape is precise — a table row, one blank line, a
# table row — so two genuinely separate tables are untouched.
# Routed through _discover_md rather than an eighth hand-rolled walk — its docstring
# says the shape was promoted into a function so it would not be pasted again, and
# board row B-010 already tracks what these repeated full-tree reads cost.
_TBL_FILES, _TBL_TEXT = _discover_md((), lambda _c: "|" in _c)
for _rel in _TBL_FILES:
    _ls = _TBL_TEXT[_rel].splitlines()
    _fence = False
    for _i in range(len(_ls) - 2):
        if _ls[_i].lstrip().startswith("```"):
            _fence = not _fence
        if _fence:
            continue
        # ...and "separate tables" is a real shape, so it is actually tested for: a new
        # table opens with a header whose NEXT line is a `|---|` delimiter. Without this
        # the guard fires on two valid adjacent tables and its own comment would be false.
        # Any number of blank lines, not exactly one: GFM ends a table at the FIRST
        # blank line whatever follows, so two blanks produce the identical defect and
        # the one-blank pattern could not see it.
        _j = _i + 1
        while _j < len(_ls) and not _ls[_j].strip():
            _j += 1
        _gap = _j - (_i + 1)
        _opens_new = (_j + 1 < len(_ls)
                      and re.match(r"^\|[\s:|-]+\|\s*$", _ls[_j + 1] or ""))
        if (_ls[_i].startswith("|") and _gap >= 1
                and _j < len(_ls) and _ls[_j].startswith("|") and not _opens_new):
            fail(f"{_rel}:{_j}: a blank line splits a table — every row below it "
                 "loses the header and renders as pipe-delimited text, which looks "
                 "like a table only in the editor")

# The trigger list is written in code and enumerated in prose, and in one module the
# two disagreed FOUR times — `open` alone while the doctrine said `backlog`, then
# `backlog` added while `unresolved` was still only promised, then "two triggers" in a
# file whose code checked three. Every instance was found by a reader. A class seen
# twice becomes a script (audit.md), so the enumeration is now computed FROM the regex
# and required to appear wherever the doctrine enumerates it.
_UNRES_SRC = re.search(r'_UNRES_RE = re\.compile\(r"\^\(\?:([a-z|]+)\)', _OWN_SRC)
if _UNRES_SRC:
    _TRIGGERS = set(_UNRES_SRC.group(1).split("|"))
    for _tf in ("plugins/task-pipeline/skills/task-pipeline/references/backlog.md",
                "plugins/task-pipeline/skills/task-pipeline/templates/backlog.md"):
        _tp = os.path.join(ROOT, _tf)
        if not os.path.isfile(_tp):
            continue
        # Scoped to the paragraph that enumerates them. Checking the whole page was the
        # first version and it is the very class this guard exists to close: a passage
        # saying "those are the only two triggers" would pass on the strength of the
        # third word appearing somewhere else entirely.
        #
        # What it still does not cover, said out loud: prose that names all three inside
        # one paragraph while denying one of them. No check decides that; a reader does.
        _paras = [_flatten(_x, lower=True) for _x in _paragraphs(open(_tp, encoding="utf-8").read())]
        _enum = [_x for _x in _paras if "trigger" in _x and any(_t in _x for _t in _TRIGGERS)]
        if not _enum:
            continue                       # this file does not enumerate the triggers
        _tt = max(_enum, key=len)
        _absent = sorted(_t for _t in _TRIGGERS if _t not in _tt)
        if _absent:
            fail(f"{_tf}: the paragraph enumerating resolution triggers omits "
                 + ", ".join(repr(_a) for _a in _absent)
                 + " — the check in test/validate.py accepts them, and a doctrine that "
                   "names fewer than the code accepts is how three of them shipped "
                   "described-but-unenforced in a single module")
else:
    fail("test/validate.py: cannot read the trigger literals out of _UNRES_RE — the "
         "doctrine-vs-code comparison has no source and is silently passing")

# The verification ledger. Keyed to the BRIEF's REQ table, not to the stage-10 coverage
# table: measured before building, ten acceptance files here carry the first REQ-bearing
# table in nearly as many shapes, because acceptance.md fixes it in prose. Eight of nine
# briefs carry machine-readable `| REQ-NNN |` rows, and the ninth was fixed the day this
# was measured. Prose does not hold a shape across ten runs; a template does.
_VERIF = os.path.join(ARTP, "verification.md")
_VERIF_NEVER = 0
_VERIF_TOTAL = 0
_VERIF_ROWS = []     # (shipped-in, req, what) for every unconfirmed row
_VERIF_DATES = []    # every date a person actually wrote
if os.path.isfile(_VERIF):
    _vt = open(_VERIF, encoding="utf-8").read()
    _vrows = re.findall(r"^\|\s*(REQ-\d+)\s*\|(.+)$", _vt, re.M)
    if not _vrows:
        fail(f"{ART}/verification.md: no `REQ-NNN` row — an empty ledger and a "
             "missing one are the same thing to a reader, and only one of them means "
             "nothing has shipped")
    # The Human column is found BY NAME in this file's own header. Scanning every cell
    # was the first version and it is N1's lesson carried forward by its wrong half:
    # that module concluded "the header names the candidate columns and the match happens
    # inside them", not "never look at columns". Scanning all cells let a bare date in
    # the Note column satisfy a row whose Human said "soon" — the single thing this guard
    # exists to reject.
    _vhdr = None
    for _l in _vt.splitlines():
        if _l.startswith("|") and "human" in _flatten(_l, lower=True):
            _vhdr = _row_cells(_l)
            break
    if _vhdr is None or "human" not in _vhdr:
        fail(f"{ART}/verification.md: no header row naming a `Human` column — "
             "the one column this file exists for cannot be located, and a guard that "
             "cannot find its subject passes everything")
        _hidx = None
    else:
        _hidx = _vhdr.index("human")

    _brief_reqs = set()
    _brief_by_slug = {}
    for _bf in glob.glob(os.path.join(ARTP, "specs/*brief.md")):
        _slug = os.path.basename(_bf).replace("-brief.md", "")
        _ids = set(re.findall(r"^\|\s*(REQ-\d+)\s*\|", open(_bf, encoding="utf-8").read(), re.M))
        _brief_by_slug[_slug] = _ids
        _brief_reqs |= _ids
    for _rid, _rest in _vrows:
        # Built over the WHOLE row, REQ included, so it is shaped like the header and
        # `_hidx` indexes it directly. The first version dropped REQ from the cells but
        # not from the header and bridged the gap with `_hidx - 1` — correct only while
        # Human sits mid-table, and silently wrong the day somebody reorders columns.
        _cells = [_flatten(_x).strip() for _x in (_rid + "|" + _rest).split("|")]
        # Reverse direction: a row about nothing. Different failure from a shipped REQ
        # that entered no ledger, and only this pass finds it (learned.md rule 2).
        # Against the brief this row NAMES, not the union of all of them. Ids 001-014
        # recur across every brief, so the union check passed a row paired with the wrong
        # run almost always — it was asking "does this id exist anywhere", which is not
        # the question.
        _run = next((_x.strip("`") for _x in _cells if _x.strip("`") in _brief_by_slug), None)
        if _run:
            if _rid not in _brief_by_slug[_run]:
                fail(f"{ART}/verification.md: {_rid} is not in the REQ table of "
                     f"`{_run}`, the run this row names — an id that exists in some other "
                     "brief is not the same requirement")
        elif _brief_reqs and _rid not in _brief_reqs:
            fail(f"{ART}/verification.md: {_rid} is in no brief's REQ table — a "
                 "ledger row about a requirement nobody wrote down is a row about nothing")
        # The Human column is the point of the file, so it is the one that is checked:
        # a date or the literal `never`. "soon" and "mostly" are how it stops being
        # answerable, and this is the only column a machine may not fill.
        _human = ([_cells[_hidx]] if _hidx is not None and len(_cells) > _hidx else [])
        _human = [_x for _x in _human if re.fullmatch(r"never|\d{4}-\d{2}-\d{2}", _x.lower())]
        if _hidx is None:
            pass                           # already failed above; do not report twice
        elif not _human:
            fail(f"{ART}/verification.md: {_rid} has no `Human` value that is "
                 "either a date or the literal `never` — prose in that column is how the "
                 "one question this file exists to answer stops being answerable")
        _VERIF_TOTAL += 1
        _ship = _cells[_vhdr.index("shipped in")] if "shipped in" in _vhdr and len(_cells) > _vhdr.index("shipped in") else ""
        if _human and _human[0].lower() == "never":
            _VERIF_NEVER += 1
            _VERIF_ROWS.append((_ship.strip("`"), _rid, _cells[1] if len(_cells) > 1 else ""))
        elif _human:
            _VERIF_DATES.append(_human[0])

# artifacts.md carries the same truth twice: an ASCII layout tree and a set of tables.
# They drifted for two modules — the tree never gained `backlog.md` or
# `verification.md` while both were named in the tables of the same file, and a reader
# found it, not a check. Every `<artifacts>/*.md` the tables name must appear in
# the tree, computed from the tables so neither side can be the one that is right.
# Reads artifacts.md ONCE and hands it to the stage-input check below, which used to
# open the same file again on the next line. Board row B-010 tracks this class.
_artf = os.path.join(refdir, "artifacts.md")
_AT_TEXT = open(_artf, encoding="utf-8").read() if os.path.isfile(_artf) else None
if _AT_TEXT is not None:
    _at = _AT_TEXT
    # Anchored on the SYMBOL the doctrine writes, not on the resolved literal.
    # v1.53.0 rewrote these paths from `docs/superpowers/…` to `<artifacts>/…`, and a
    # first draft of this guard searched for the resolved name instead: it found
    # nothing, `_named` went empty, and the guard passed by having no subject —
    # reported by the negative self-test as "does not actually fire". That is standing
    # instruction #6's corollary in this repository's own validator, one release after
    # the instruction was written. The symbol is the stable anchor; the literal moves.
    _named = set(re.findall(r"`<artifacts>/([a-z-]+\.md)`", _at))
    # The tree's own line for the root may carry a trailing comment, so the match
    # stops at the newline rather than requiring the line to end at the slash.
    _tree = re.search(rf"^  {re.escape(os.path.basename(ART))}/[^\n]*\n((?:    .*\n)+)",
                      _at, re.M)
    if _named and not _tree:
        fail(f"references/artifacts.md: the tables name files under `<artifacts>/` and "
             f"the layout tree that should list them under `{os.path.basename(ART)}/` "
             "cannot be found — one of the two statements of the same truth has moved")
    elif _named:
        _absent = sorted(_f for _f in _named if _f not in _tree.group(1))
        if _absent:
            fail("references/artifacts.md: the layout tree omits "
                 + ", ".join(repr(_a) for _a in _absent)
                 + " — named in this same file's tables. Two statements of one truth in one "
                   "file, and they drifted for two modules before a reader noticed")

# The TOP CHANGELOG section describes the release being cut, so its guard and
# property counts are claims about now — and they went stale twice in one programme,
# because checks get added after the entry is written. Older sections are history and
# correct as of their own day; only the newest is checked.
_cl = os.path.join(ROOT, "CHANGELOG.md")
_wf = os.path.join(ROOT, ".github/workflows/validate.yml")
if os.path.isfile(_cl) and os.path.isfile(_wf):
    _true_neg, _true_prop = _neg_n, _prop_n
    _clt = chg
    _top = _clt.split("\n## v", 2)
    _top = _top[1] if len(_top) > 1 else ""
    _g = re.search(r"Guards:\s*\d+\s*(?:→|->)\s*(\d+)", _flatten(_top))
    # 2026-08-10: this guard went DORMANT on its own release. The v1.39.0 entry was
    # written as `Guards **218 → 226**` — no colon — the pattern missed, the check
    # stayed silent, and `npm test` was green over a count it had never read. The
    # negatives suite caught it only because its probe could no longer plant. A
    # mechanism with nothing to look at must say so rather than pass (gates.md →
    # progressive arming); a count-shaped sentence with no count is the one case
    # where silence and agreement are indistinguishable.
    if _g is None and re.search(r"\b(guard|check|probe|negative self-test)s?\b",
                                _flatten(_top), re.I):
        fail("CHANGELOG.md: the newest section talks about guards but states no "
             "`Guards: N → M` count this check can read — it went dormant here once "
             "and the suite stayed green over an unread number; write the count in "
             "that shape or say nothing about guards")
    if _g and int(_g.group(1)) != _true_neg:
        fail(f"CHANGELOG.md: the newest section claims {_g.group(1)} guards but the "
             f"workflow defines {_true_neg} — the entry is written before the last "
             "checks are added, and this count went stale twice in one programme")
    _p = re.search(r"property checks\s*\d+\s*(?:→|->)\s*(\d+)", _flatten(_top))
    if _p and int(_p.group(1)) != _true_prop:
        fail(f"CHANGELOG.md: the newest section claims {_p.group(1)} property checks but "
             f"the workflow defines {_true_prop}")

# The exposure line may never render as a probability. The request that produced it
# asked for one; `P(defect)` is not computable from these inputs, and a number dressed
# as one is the class this repository has spent its history removing. So: no `%` on that
# line, and the doctrine that says why must say it where somebody proposing a percentage
# will read it.
_expo = os.path.join(refdir, "exposure.md")
if os.path.isfile(_expo):
    _et = open(_expo, encoding="utf-8").read()
    # Needles matched against the doctrine's ACTUAL words. The first draft looked for
    # "never a percentage" while the file says "no percentage, ever" — the guard and the
    # prose it guards, written an hour apart by the same author, already disagreed.
    for _needle, _why in (
            ("no percentage", "the ban on rendering exposure as a probability"),
            ("never checked", "the literal printed when NO row has ever been confirmed — "
                              "`0 days` would read as *checked today*"),
            ("checkup", "the command mode that prints the full check-list")):
        if _needle not in _flatten(_et, lower=True):
            fail(f"references/exposure.md: says nothing about {_why} — the doctrine has to "
                 "carry it where the next reader looks, or the guard below is the only "
                 "record of a decision nobody can find")
    # And the code must agree with it: a `%` reaching the exposure print is the defect.
    # Scoped to the print statement itself, not a window around the first mention of the
    # word: the first draft took 1200 characters from wherever "exposure:" appeared and
    # swept in unrelated code, failing on somebody else's `%`.
    # Matched on the PRINT, not on the word: the first draft searched for the literal
    # and found its own line, which necessarily contains it. A detector that matches
    # itself first checks the wrong thing and passes.
    # The WHOLE statement, not its first physical line: a `%` on the continuation
    # ("releases carry one") rendered `10% releases` and passed, which is the class this
    # guard exists for. Scope was the first draft's second scoping bug in one module.
    _src_lines = _OWN_SRC.splitlines()
    _pr = []
    for _i, _l in enumerate(_src_lines):
        if _l.lstrip().startswith('print(f"  exposure:'):
            _stmt = _l
            _j = _i + 1
            while _j < len(_src_lines) and not _stmt.rstrip().endswith(")"):
                _stmt += _src_lines[_j]
                _j += 1
            _pr.append(_stmt)
    if _pr and "%" in _pr[0]:
        fail("test/validate.py: a `%` appears in the exposure print — the one rendering "
             "this line may never take (references/exposure.md)")
else:
    fail("references/exposure.md: absent, and the exposure line is printed anyway — a "
         "number with no doctrine is the estimate-as-measurement this file forbids")

# references/artifacts.md maps stage -> what it WRITES. The reverse direction — what
# each stage READS and from where — is the one an agent actually needs at runtime,
# and it was absent for nine releases: learned.md rule 2 (compute the mapping in both
# directions) unapplied to this file itself. A stage whose inputs are unnamed reads
# whatever the context happens to hold.
_art = _artf
if _AT_TEXT is not None:
    _at = _AT_TEXT
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
    _cited = [_lit for _par in re.findall(r"\*\(guard: (.+?)\)\*", _ct, re.S)
                     for _lit in re.findall(r"`([^`]+)`", _par)]
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
                               ("retro.md", f"{ART}/retro.md")):
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

    # Stage 0 is stage 9's sibling here — the same doctrine file ships both duties,
    # one READING the graph and one REFRESHING it — so standing instruction R-003
    # puts the check above on both. The word "graph" is not the test at stage 0: it
    # is already there ("query the graph"). What must be enforced is the MEASURED
    # lag, because a build date is the graph's own reply about itself and passes any
    # check that only looks for the word (references/gates.md -> False success).
    _kg_txt = open(os.path.join(refdir, "knowledge-graph.md"), encoding="utf-8").read()
    _s0_cfg = next(
        (s for s in (_pipe_stages or []) if isinstance(s, dict) and s.get("state") == "intake"),
        None,
    )
    if _s0_cfg is not None and "measured lag" not in str((_s0_cfg.get("gate") or {}).get("check", "")).lower():
        fail(f"{EXAMPLE_REL} stage 'intake': references/knowledge-graph.md ships the measured-lag "
             "rule but the stage-0 gate.check never requires it — a run passes intake quoting a "
             "graph whose staleness nobody measured, which is the one source the harvest reads "
             "first")
    _s0_doc = re.search(r"^## 0 — .*?(?=^## |\Z)", _st_txt, re.M | re.S)
    if _s0_doc and "measured lag" not in _s0_doc.group(0).lower():
        fail("references/stages.md stage 0: references/knowledge-graph.md ships the measured-lag "
             "rule but the stage-0 section never states it — an agent reading the stage detail "
             "records a build date and believes it has recorded freshness")
    # The surfaces above cite a section by name; if it stops delivering the commands
    # or drops a state, they cite an empty promise. All three states are load-bearing:
    # graph.json carries built_at_commit only when the caller passed it, so a doctrine
    # with one state makes "no stamp" print like "fresh".
    for _need, _what in (
        ("git rev-list --count", "the command that counts commits behind HEAD"),
        ("git log -1 --format=%ct", "the command that dates the build commit"),
        ("git rev-parse --verify", "the probe that decides which state applies"),
    ):
        if _need not in _kg_txt:
            fail(f"references/knowledge-graph.md: the measured-lag rule no longer names "
                 f"`{_need}` — {_what}. Without the command the rule is an intention and the "
                 "number goes back to being typed (references/learned.md rule 8)")
    for _state in ("exact", "approximate", "unresolvable"):
        if f"**{_state}**" not in _kg_txt:
            fail(f"references/knowledge-graph.md: the measured-lag rule no longer names the "
                 f"'{_state}' state — with a state missing, a graph that could not be measured "
                 "prints indistinguishably from a fresh one")
    # One marker, one spelling. The distrust marker was written four different ways
    # inside the release that introduced it — the doctrine table omitted it entirely,
    # the unresolvable row invented "treat as stale until refreshed", and the Cursor
    # rule and the config both dropped the sigil. A marker with four spellings is not
    # greppable, which is the only property it has: a ledger row is prose, and the
    # marker is the one string a reader (or a later check) can look for. audit.md:
    # a class seen twice becomes a mechanism rather than a third ledger row.
    _MARKER = "⚠ not trusted for reach until refreshed"
    _marker_scope = [
        os.path.join(ROOT, "README.md"),
        os.path.join(ROOT, "cursor/rules/task-pipeline.mdc"),
        os.path.join(_skill_dir, "pipeline.example.json"),
        os.path.join(_skill_dir, "templates", "brief.md"),
    ] + [os.path.join(refdir, _f) for _f in sorted(os.listdir(refdir)) if _f.endswith(".md")]
    for _p in _marker_scope:
        if not os.path.isfile(_p):
            continue
        _rel = os.path.relpath(_p, ROOT)
        _t = open(_p, encoding="utf-8").read()
        if "treat as stale until refreshed" in _t:
            fail(f"{_rel}: 'treat as stale until refreshed' is a second spelling of the "
                 f"distrust marker — use the canonical '{_MARKER}', because a marker with "
                 "two spellings is greppable as neither")
        # Whitespace-normalised, not per line: this doctrine wraps at ~80 columns, so
        # the marker is routinely split across two lines. A per-line check would find
        # nothing in README.md and stages.md and report that as a pass — a guard that
        # is green because it never looked (references/gates.md -> False success).
        _norm = re.sub(r"\s+", " ", _t)
        _bare = _norm.count("not trusted for reach until refreshed")
        _full = _norm.count(_MARKER)
        if _bare != _full:
            fail(f"{_rel}: the distrust marker appears {_bare - _full} time(s) without its "
                 f"sigil — the canonical string is '{_MARKER}' and nothing else, so one grep "
                 "finds every ledger row that admitted it could not be trusted")

    # The seeded brief is what every new project starts from. Leaving the superseded
    # bare-date form in the template ships the defect this release removes.
    _brief_p = os.path.join(_skill_dir, "templates", "brief.md")
    if os.path.isfile(_brief_p):
        for _ln in open(_brief_p, encoding="utf-8").read().splitlines():
            if "graphify-out/graph.json" in _ln and "built YYYY-MM-DD" in _ln:
                fail("templates/brief.md: the seeded code-graph ledger row still reads "
                     "`built YYYY-MM-DD` — every project scaffolded from this template starts "
                     "by recording the graph's own reply instead of measuring it")

# The negatives floor is a number in a living document, so rule 8 binds it like any
# other: MIN_EXPECTED must EQUAL the workflow's count, not merely be below it. Its own
# comment records the first time it lagged (20 while the workflow carried 34); the
# second was v1.15.0, where four canon self-tests landed and the floor stayed at 104.
# A floor below the count cannot notice losing the difference, which is the whole job.
_neg_py = os.path.join(ROOT, "test/negatives.py")
if os.path.isfile(_neg_py) and os.path.isfile(_neg_wf):
    _neg_py_txt = open(_neg_py, encoding="utf-8").read()
    _m_floor = re.search(r"^MIN_EXPECTED\s*=\s*(\d+)", _neg_py_txt, re.M)
    if _m_floor and int(_m_floor.group(1)) != _neg_n:
        fail(f"test/negatives.py: MIN_EXPECTED is {_m_floor.group(1)} but the workflow defines "
             f"{_neg_n} negative self-tests — a floor below the count is a floor that cannot "
             "notice losing the difference; raise it in the same change that adds the tests")
    # MIN_PROPS had NO such check at all — zero mentions in this file — while its sibling
    # has been tied since v1.15.0 and still went stale twice. A floor nothing compares is
    # not a floor, it is a number somebody typed once.
    _p_floor = re.search(r"^MIN_PROPS\s*=\s*(\d+)", _neg_py_txt, re.M)
    if _p_floor and int(_p_floor.group(1)) != _prop_n:
        fail(f"test/negatives.py: MIN_PROPS is {_p_floor.group(1)} but the workflow defines "
             f"{_prop_n} property checks — the same drift MIN_EXPECTED suffered twice, on the "
             "floor nobody had wired up")

# The CI verdict (references/conventions.md). A workflow run that nobody reads is the
# fail-open hook with extra steps: on 2026-08-06 this repo's `validate` was
# completed/failure on a push to main and on a release tag, the guard that failed was
# CORRECT, and nothing obliged anyone to look. So the method must keep its commands,
# must keep all three states -- the third, "no run found", is the one that stops
# silence from reading as green -- and every stage that PUSHES must cite it.
_conv_p = os.path.join(refdir, "conventions.md")
if os.path.isfile(_conv_p):
    _conv = open(_conv_p, encoding="utf-8").read()
    for _need, _why in (
        ("gh run list --branch", "the command that finds the run"),
        ("--log-failed", "the command that reads WHY it failed; a conclusion says only THAT"),
        ("check-runs", "the unauthenticated path — a dead token must not end the check"),
    ):
        if _need not in _conv:
            fail(f"references/conventions.md: *The CI verdict* no longer names `{_need}` — "
                 f"{_why}. Without the command the rule is an intention, and 'CI is green' "
                 "goes back to being a sentence anyone can write without looking")
    for _state in ("concluded", "in progress", "no run found"):
        if f"**{_state}**" not in _conv:
            fail(f"references/conventions.md: the CI verdict's '{_state}' state is gone — "
                 "with a state missing, a push whose run could not be established prints "
                 "indistinguishably from a green one")
    # Declared in one file and enforced nowhere is the inert-gate failure this repo has
    # now hit at stage 9, stage 10 and stage 0. Every stage of the flow that pushes must
    # name the rule -- and cite it rather than carry a second copy of the commands.
    _st_all = open(os.path.join(refdir, "stages.md"), encoding="utf-8").read()
    for _num in ("7", "8", "9"):
        _sec = re.search(r"^## %s — .*?(?=^## |\Z)" % _num, _st_all, re.M | re.S)
        if _sec and "the ci verdict" not in _sec.group(0).lower():
            fail(f"references/stages.md stage {_num}: this stage pushes, and "
                 "references/conventions.md ships the CI-verdict rule, but the section "
                 "never names it — the run it triggers is closed on an unread verdict")
        if _sec and "gh run list --branch" in _sec.group(0):
            fail(f"references/stages.md stage {_num}: carries its own copy of the CI-verdict "
                 "commands — cite conventions.md instead; two homes do not disagree the day "
                 "they are written, they disagree the day one is updated")
    _s8_cfg = next(
        (s for s in (_pipe_stages or []) if isinstance(s, dict) and s.get("state") == "post-deploy"),
        None,
    )
    if _s8_cfg is not None and "ci verdict" not in str((_s8_cfg.get("gate") or {}).get("check", "")).lower():
        fail(f"{EXAMPLE_REL} stage 'post-deploy': the CI-verdict rule ships in "
             "references/conventions.md but the stage-8 gate.check never requires it — "
             "declared where it is not enforced")

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
    # The legal set is READ from the schema, never listed here. It was listed once —
    # ("off", "interval") — and adding `dynamic` in v1.40.0 failed this guard on a
    # correct example, which is a check enforcing its own staleness (learned.md
    # rule 8: compute, never restate).
    def _loop_modes(node):
        if isinstance(node, dict):
            _pr = node.get("properties")
            if isinstance(_pr, dict) and "loop" in _pr:
                return ((_pr["loop"].get("properties") or {}).get("mode") or {}).get("enum")
            for _v in node.values():
                _r = _loop_modes(_v)
                if _r: return _r
        elif isinstance(node, list):
            for _v in node:
                _r = _loop_modes(_v)
                if _r: return _r
        return None
    _legal = _loop_modes(_sch) if _sch else None
    if not _legal:
        _UNLOOKED.append("skip: run.loop.mode in the example — the schema states no "
                         "enum for it, so there is nothing to check the example against")
    elif _mode not in _legal:
        fail("pipeline.example.json: run.loop.mode is "
             f"{_mode!r}, and the schema's legal set is {_legal} — the example must "
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
    # A step that deletes one directory and copies into another was harmless while the
    # suite ran serially, and became a race the hour it went parallel: `rm -rf /tmp/X &&
    # cp -R . /tmp/X-2` wipes the live scratch of whichever test owns X. Three shipped
    # that way, and the reuse guard below never saw them because it only ever compared
    # `cp` targets.
    for _l in _wf_scan:
        _m = re.search(r"rm -rf (/tmp/[A-Za-z0-9._-]+) && cp -R \. (/tmp/[A-Za-z0-9._-]+)", _l)
        if _m and _m.group(1) != _m.group(2):
            fail(f"`.github/workflows/validate.yml`: a step removes `{_m.group(1)}` and "
                 f"copies into `{_m.group(2)}` — it wipes a directory it does not own, "
                 "which is a race the moment two tests run at once")
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

# A guard added below the verdict block is dead code that reads as a guard: on a clean
# run it executes after PASS is printed, and on a corrupted one sys.exit() fires first
# so it never executes at all. Fourteen checks shipped that way in this file's own
# v1.14.0 draft and every one of them was green because it could not run.
_src = open(__file__, encoding="utf-8").read()
_verdict = _src.rfind('print("PASS: task-pipeline structure valid")')
# literal also appears in this guard's own source, and find() would match itself
if _verdict != -1 and "fail(" in _src[_verdict:]:
    fail("test/validate.py: a fail() call appears after the verdict is printed — a "
         "check below the verdict block never runs on a corrupted repo and runs too "
         "late on a clean one; move it above `if errors:`")

# The canons (v1.15.0). Ten laws saying what makes a claim documentation, as opposed to
# learned.md's rules, which say what to do at a trigger. A canon list is worth having only
# while it is complete and while each law still names where it is enforced instead of
# restating the mechanism -- a canon that repeats its own gate is the second home the
# first canon forbids.
_dp = os.path.join(refdir, "documentation.md")
if os.path.isfile(_dp):
    _dt = open(_dp, encoding="utf-8").read()
    if "## The canons" not in _dt:
        fail("references/documentation.md: the canons are gone -- the laws the rest of "
             "this file serves")
    _canons = (
        "A claim carries its address",
        "Numbers are computed, never restated",
        "Every fact has exactly one home",
        "A reference resolves from where the document is read",
        "Green nobody watched turn red is not evidence",
        "A check proves its scope and nothing beyond it",
        "Silence is not a pass",
        "An estimate is never announced as a measurement",
        "What was not checked is printed beside what was",
        "The document ships in the change that made it true",
    )
    _missing = [c for c in _canons if c not in _dt]
    if _missing:
        fail(f"references/documentation.md: canon(s) dropped: {_missing} -- a list that "
             "loses a law silently is worse than no list, because everyone believes it "
             "is covered")
    _seg = _dt.split("## The canons", 1)[1].split("### What these are not", 1)[0]
    # Per canon, not a total: a count threshold only fires when most of them are gone,
    # which is the check proving less than it claims (canon 6 applied to itself).
    for _i, _c in enumerate(_canons):
        _start = _seg.find(_c)
        if _start == -1:
            continue
        _end = len(_seg)
        for _n in _canons[_i + 1:]:
            _nx = _seg.find(_n, _start)
            if _nx != -1:
                _end = _nx
                break
        if "\u2192" not in _seg[_start:_end]:
            fail(f"references/documentation.md: canon '{_c}' names no enforcement -- a "
                 "canon that does not point at its mechanism becomes a second copy of it")
    if "epistemic" not in _dt:
        fail("references/documentation.md: the canons no longer say how they differ from "
             "learned.md's operational rules -- two undifferentiated rule lists is the "
             "duplication canon 3 forbids")

# The evidence-docs navigator (v1.16.0). A second skill in the same plugin: the canons
# as an index plus where to go next. It ships beside the doctrine rather than carrying a
# copy of it, so the whole risk is drift -- an index that still lists ten laws after the
# doctrine has nine reads as authoritative and is wrong.
_ed = os.path.join(ROOT, "plugins/task-pipeline/skills/evidence-docs/SKILL.md")
if not os.path.isfile(_ed):
    fail("plugins/task-pipeline/skills/evidence-docs/SKILL.md is missing -- the router "
         "names evidence-docs, and a routed name that resolves to nothing is the shape "
         "learned.md rule 14 forbids")
else:
    _et = open(_ed, encoding="utf-8").read()
    _fm = _et.split("---")[1] if _et.startswith("---") else ""
    _nm = re.search(r"^name:\s*(.+)$", _fm, re.M)
    _ds = re.search(r"^description:\s*(.+)$", _fm, re.M)
    if not _nm or _nm.group(1).strip() != "evidence-docs":
        fail("skills/evidence-docs/SKILL.md: frontmatter name must be 'evidence-docs' — "
             "the directory, the name and the routed id are one identity")
    if not _ds or len(_ds.group(1).strip()) > 1024:
        fail("skills/evidence-docs/SKILL.md: description missing or over the 1024-char "
             "limit the Agent Skills spec sets")
    # The index must carry every canon and no invented one.
    for _c in _canons:
        if _c not in _et:
            fail(f"skills/evidence-docs/SKILL.md: the index no longer lists '{_c}' — an "
                 "index that has drifted from its doctrine reads as authoritative and is "
                 "wrong")
    if "documentation.md) → *The canons*" not in _et:
        fail("skills/evidence-docs/SKILL.md: no pointer to the one home of the canons — "
             "without it the index becomes the second copy canon 3 forbids")
    # Canon 4 applied to the navigator itself: it lives one directory over from every
    # file it names, so its links resolve from a different place than the doctrine's do.
    _edir = os.path.dirname(_ed)
    for _rel in re.findall(r"\]\((\.\./[^)]+)\)", _et):
        if not os.path.exists(os.path.normpath(os.path.join(_edir, _rel))):
            fail(f"skills/evidence-docs/SKILL.md: '{_rel}' does not resolve from the "
                 "navigator's own directory — canon 4, in the file that publishes it")

# Frontmatter must parse as YAML, not merely match a regex (v1.16.1). The evidence-docs
# description carried "read as true: a decision record" -- a colon-space inside a plain
# scalar, which YAML reads as a nested mapping. The regex check above called it valid; the
# official plugin validator called it "loads with empty metadata, all fields silently
# dropped". A check proving less than it claims is canon 6, and it shipped in the release
# that publishes canon 6. Applied to every SKILL.md in the plugin, not just the new one.
for _sk in sorted(glob.glob(os.path.join(ROOT, "plugins/*/skills/*/SKILL.md"))):
    _st = open(_sk, encoding="utf-8").read()
    _rel_sk = os.path.relpath(_sk, ROOT)
    if not _st.startswith("---"):
        fail(f"{_rel_sk}: no YAML frontmatter block")
        continue
    for _line in _st.split("---")[1].splitlines():
        _m = re.match(r"^([A-Za-z_][\w-]*):\s*(\S.*)$", _line)
        if not _m:
            continue
        _val = _m.group(2).strip()
        if _val[:1] in ("'", '"', "|", ">", "[", "{"):
            continue
        if ": " in _val:
            fail(f"{_rel_sk}: frontmatter '{_m.group(1)}' is a plain scalar containing "
                 "a colon-space, so YAML parses it as a mapping and the field is "
                 "silently dropped at load time -- quote the value or rephrase")

# --- P1: what the run prints about itself (v1.34.0) ---------------------------
# SCOPE: these four check the DOCTRINE's internal consistency — the header block's
# field set, the glyph legend, the computed-rail promise, and the run ledger's line
# shapes. They do NOT check that any run ever printed a block; a static validator
# cannot see a transcript, and naming that limit here is the whole point of a scope
# header (gates.md -> Anatomy of a project gate).
_PROG_REL = "references/progress.md"
_PROG = os.path.join(ROOT, _SKILLDIR, _PROG_REL)
_PTXT = open(_PROG, encoding="utf-8").read() if os.path.isfile(_PROG) else ""


def _header_fields(_path):
    """Field labels of the header block, read from the block itself, never listed.

    Unit: the INDENTED, dot-separated lines of the first fence whose body opens
    `task-pipeline v`. Two exclusions, each with its reason. The rail line is out
    because it uses the middle dot as a GLYPH rather than a separator, so a segment
    split would read its stage numbers as field names. The title line is out by
    indentation, because its middle segment is the topic — which legitimately
    differs between the doctrine's example and a restatement of it.
    """
    if not os.path.isfile(_path):
        return None
    for _blk in re.findall(r"```[a-zA-Z]*\n(.*?)```", open(_path, encoding="utf-8").read(), re.S):
        if not _blk.startswith("task-pipeline v"):
            continue
        _out = set()
        for _ln in _blk.split("\n")[1:]:
            if not _ln[:1].isspace() or "·" not in _ln:
                continue
            if re.match(r"\s*\d+\s", _ln):
                continue                      # the rail
            for _seg in _ln.split("·"):
                _m = re.match(r"([a-z][a-z-]*)\b", _seg.strip(" █░").strip())
                if _m:
                    _out.add(_m.group(1))
        return _out
    return None


# P1-G1. The header block exists in TWO files, which is learned.md rule 20's shape:
# a thing that exists twice drifts, and the drift is silent because each copy reads
# complete on its own. Both directions, because they are different failures — a
# field in the doctrine and absent from the stage list is a reader who never meets
# it; a field on the stage list and absent from the doctrine is a number with no
# home, which is the one thing progress.md forbids outright.
_pf = _header_fields(_PROG)
_sf = _header_fields(os.path.join(ROOT, _SKILLDIR, "references/stages.md"))
if _pf is None or _sf is None or not _pf or not _sf:
    _UNLOOKED.append("skip: header-block field set — no `task-pipeline v` fence in "
                     "progress.md or stages.md")
else:
    for _miss, _where, _other in ((_pf - _sf, "references/stages.md", "progress.md"),
                                  (_sf - _pf, _PROG_REL, "stages.md")):
        if _miss:
            fail(f"{_where}: the header block omits {sorted(_miss)}, which "
                 f"{_other} prints — one block, two copies, already drifted")

# P1-G2. Every glyph a rail prints is defined in the legend. SCOPE: one direction
# only, and deliberately. A legend row for a glyph no example happens to use is a
# vocabulary entry rather than a defect — `✗` is exactly that — so the reverse
# check would fail on correct doctrine. The failure worth catching is the other
# one: a symbol a reader meets with nothing to look it up in.
if _PTXT:
    _legend = set(re.findall(r"^\|\s*`(\S)`\s*\|", _PTXT, re.M))
    _used = set()
    for _blk in re.findall(r"```[a-zA-Z]*\n(.*?)```", _PTXT, re.S):
        for _ln in _blk.split("\n"):
            if re.match(r"\s*\d+\s", _ln):
                _used |= set(re.findall(r"\d+\s(\S)", _ln))
    if not _legend:
        fail(f"{_PROG_REL}: no glyph legend — the rail's symbols are printed and "
             "defined nowhere")
    for _g in sorted(_used - _legend):
        fail(f"{_PROG_REL}: the rail prints {_g!r} and "
             "the legend does not define it"
             " — a symbol a reader meets with nothing to look it up in")

# P1-G3. REQ-013's promise, stated where a reader meets it. A rail that hardcodes
# this plugin's eleven EXAMPLE stages is confidently wrong in every project that
# replaced them, in the one place a run is trusted at a glance.
if _PTXT:
    _pn = _flatten(_PTXT, lower=True)
    for _clause in ("come from the project's pipeline.json",
                    "carries no stage count of its own"):
        if _clause not in _pn:
            fail(f"{_PROG_REL}: missing the clause {_clause!r} — without it the "
                 "rail's stage set is whatever the agent assumed")


def _md_section(_txt, _title):
    _m = re.search(r"^##\s+" + re.escape(_title) + r"\s*$(.*?)(?=^##\s|\Z)",
                   _txt, re.S | re.M)
    return _m.group(1) if _m else ""


def _line_prefixes(_txt):
    return set(re.findall(r"^(\w+):\s", "\n".join(
        re.findall(r"```[a-zA-Z]*\n(.*?)```", _txt, re.S)), re.M))


# P1-G4. The ledger declares three line shapes and then shows them. Declared and
# shown are two enumerations of one list, and N1's whole retro is about what
# happens to those: five times the prose promised what nothing enforced. Both
# directions — a shape declared and never shown is a rule with no worked example,
# a shape shown and never declared is an example teaching an unowned format.
_RUN_TPL = os.path.join(ROOT, _SKILLDIR, "templates/run.md")
if os.path.isfile(_RUN_TPL):
    _rt = open(_RUN_TPL, encoding="utf-8").read()
    _declared = _line_prefixes(_md_section(_rt, "Lines"))
    _shown = _line_prefixes(_md_section(_rt, "Log"))
    if not _declared:
        fail("templates/run.md: no line shapes declared under `## Lines` — the "
             "ledger two mechanisms read has no stated format")
    for _miss, _msg in ((_declared - _shown, "declared under `## Lines` and never "
                                             "shown in `## Log`"),
                        (_shown - _declared, "shown in `## Log` and never declared "
                                             "under `## Lines`")):
        if _miss:
            fail(f"templates/run.md: line shape(s) {sorted(_miss)} {_msg}")
    # And the cross-file direction: a shape nobody reads is a shape nobody writes.
    _readers = _PTXT + (open(os.path.join(ROOT, _SKILLDIR, "references/loop-guard.md"),
                             encoding="utf-8").read()
                        if os.path.isfile(os.path.join(ROOT, _SKILLDIR,
                                                       "references/loop-guard.md")) else "")
    for _pfx in sorted(_declared):
        if _pfx + ":" not in _readers:
            fail(f"templates/run.md declares the {_pfx + ':'!r} line and neither "
                 f"{_PROG_REL} nor references/loop-guard.md names it — "
                 "a ledger shape with no reader"
                 " is written by nobody")

# --- P2: the gate fixes (v1.35.0) ---------------------------------------------
# SCOPE: the DOCTRINE's own agreement — the review cap stated in two files, the
# short path's glyph defined where glyphs are defined, and the exposure example
# matching the statement that prints it. None of these observes a run.
_LG_P = os.path.join(ROOT, _SKILLDIR, "references/loop-guard.md")
_ST_P = os.path.join(ROOT, _SKILLDIR, "references/stages.md")

# P2-G1. The review cap is a number, and a number written twice drifts. It is
# computed from loop-guard.md — the file that owns the caps — and required in the
# stage that runs the loop. This loop was capped by nothing at all while a ceiling
# of two re-entries per stage sat one paragraph above it, so the failure here is
# not hypothetical: it is what the last ten-round run was.
if os.path.isfile(_LG_P) and os.path.isfile(_ST_P):
    _lg_t = open(_LG_P, encoding="utf-8").read()
    _st_t = open(_ST_P, encoding="utf-8").read()
    _cap = re.search(r"\*\*(\d+) review rounds\*\* per artifact", _lg_t)
    if not _cap:
        fail("references/loop-guard.md: no review-round cap — the loop this "
             "repository ran ten rounds of is capped by nothing")
    else:
        _want = f"{_cap.group(1)} rounds per artifact"
        if _want not in _flatten(_st_t, lower=True):
            fail(f"references/stages.md: the stage running the review loop does not "
                 f"state {_want!r}, which references/loop-guard.md sets — "
                 "the cap exists in one file and the loop runs in the other")
    for _f, _t in (("references/loop-guard.md", _lg_t), ("references/stages.md", _st_t)):
        if "run.review.maxRounds" not in _t:
            fail(f"{_f}: the review cap is stated with no config key — a default "
                 "nobody can change is a default everybody overrides in their head")

# P2-G2. The short path marks stages with a glyph, and a glyph is only safe if it
# is defined where glyphs are defined. A skipped stage that reads as a stage never
# entered is the exact inversion progress.md's legend exists to prevent.
# Unit: the BULLET, not the paragraph. The bullet carries a fenced block with blank
# lines around it, so a paragraph-scoped read stops three lines in and never reaches
# the glyph — which is what the first version did, silently. gates.md says to write
# down which unit was chosen and what it misses: this one ends at the next top-level
# bullet, so a glyph introduced in a following bullet is out of scope.
if _PTXT and os.path.isfile(_ST_P):
    _legend2 = set(re.findall(r"^\|\s*`(\S)`\s*\|", _PTXT, re.M))
    _stx = open(_ST_P, encoding="utf-8").read()
    _at = _stx.find("short-path triage")
    if _at == -1:
        fail("references/stages.md: no short-path triage — a pipeline with eleven "
             "stages and no measured exemption runs all of them over a typo")
    else:
        _end = _stx.find("\n- **", _at)
        # Fences out first: ``` is three backticks, so the naive span matches its own
        # middle one and reports the delimiter as an undefined glyph. The check found
        # itself before it found anything else — the shape gates.md calls a detector
        # that matches itself first.
        _slice = FENCE_RE.sub("", _stx[_at:_end if _end > 0 else len(_stx)])
        for _tok in set(re.findall(r"`(\S)`", _slice)):
            if not _tok.isalnum() and _tok != "`" and _tok not in _legend2:
                fail(f"references/stages.md: the short path marks a stage {_tok!r} "
                     "and references/progress.md's legend does not define it — "
                     "a skip a reader cannot tell from a stage never entered")

# P2-G3. The exposure example and the statement that prints it are two statements
# of one format. They disagreed for a whole release — the doctrine taught
# `31 releases since the last human confirmation` while the code printed
# `releases carry one`, and it hardcoded a live count that drifts. Computed from
# the print, required in the doctrine, and the example is required to carry no
# digits at all: a worked example with a number in it is a number nobody updates.
_EXP_P = os.path.join(ROOT, _SKILLDIR, "references/exposure.md")
if os.path.isfile(_EXP_P):
    _exp_t = open(_EXP_P, encoding="utf-8").read()
    _lines = _OWN_SRC.splitlines()
    _stmt = ""
    for _i, _l in enumerate(_lines):
        if _l.lstrip().startswith('print(f"  exposure:'):
            _stmt = _l
            _j = _i + 1
            while _j < len(_lines) and not _stmt.rstrip().endswith(")"):
                _stmt += _lines[_j]
                _j += 1
            break
    if not _stmt:
        _UNLOOKED.append("skip: exposure example vs its print — no exposure print "
                         "statement found in this file")
    else:
        # Placeholders out, then the alphabetic word-runs that remain are the
        # format's own vocabulary. Anything the code prints, the doctrine shows.
        _words = [w.strip() for w in
                  re.findall(r"[A-Za-z][A-Za-z ]{2,}", re.sub(r"\{[^}]*\}", " ", _stmt))]
        _expn = _flatten(_exp_t, lower=True)
        for _w in {" ".join(w.split()).lower() for w in _words}:
            if _w in ("print f exposure", "f") or len(_w.split()) < 2:
                continue
            if _w not in _expn:
                fail(f"references/exposure.md: the print says {_w!r} and the doctrine "
                     "does not — the worked example and its own output have drifted")
    _ex_line = [_l for _b in re.findall(r"```[a-zA-Z]*\n(.*?)```", _exp_t, re.S)
                for _l in _b.split("\n") if _l.startswith("exposure:")]
    for _l in _ex_line:
        if re.search(r"\d", _l):
            fail(f"references/exposure.md: the worked example carries a digit "
                 f"({_l.strip()!r}) — a live count in a doctrine is a count nobody "
                 "updates, and this one was eight releases stale")

# --- P3: the tracks a companion owns (v1.36.0) --------------------------------
# The matrix's second cell says which stage needs a companion. Nothing checked that
# the stage had ever heard of it — which is how `sheleg-design` reached one mention
# in the whole bundle and super-ux's entire copy half reached none, while the
# matrix read complete on its own. SCOPE: name presence in the stage's section. It
# does not check that the stage USES the companion well, only that the stage the
# matrix points at names it at all.
# ONE pattern, used by the check that derives a row's stages and by the check that
# refuses a row deriving none. Two copies would drift, and the drift would be silent in
# exactly the direction that hurts: a spelling the deriver misses and the emptiness check
# accepts is a row nobody compares. `stage-10` is in here because a shipped row wrote it
# that way and cost this table a companion's coverage.
_STAGE_REF = re.compile(
    r"[Ss]tages?[\s-]+(\d+)\s*[–—-]\s*(\d+)"      # a range: stages 5–6
    r"|[Ss]tages?[\s-]+(\d+)"                      # a single: stage 8, stage-10
)

_CS_P = os.path.join(ROOT, _SKILLDIR, "references/companion-skills.md")
if os.path.isfile(_CS_P) and os.path.isfile(_ST_P):
    _cs_t = open(_CS_P, encoding="utf-8").read()
    _st_t2 = open(_ST_P, encoding="utf-8").read()
    # Stage sections of stages.md, keyed by id.
    _sections = {}
    _heads = list(re.finditer(r"^##\s+(\d+)\s+—", _st_t2, re.M))
    for _i, _h in enumerate(_heads):
        _to = _heads[_i + 1].start() if _i + 1 < len(_heads) else len(_st_t2)
        _sections[_h.group(1)] = _flatten(_st_t2[_h.start():_to], lower=True)
    for _row in re.findall(r"^\|\s*\*\*([^*|]+)\*\*[^|]*\|([^|]*)\|", _cs_t, re.M):
        _nm = re.sub(r"^\[|\]$", "", re.split(r"\s*\(", _row[0])[0].strip())
        _need = _row[1]
        _want = set()
        for _m in _STAGE_REF.finditer(_need):
            if _m.group(1):
                _want |= {str(_n) for _n in range(int(_m.group(1)), int(_m.group(2)) + 1)}
            else:
                _want.add(_m.group(3))
        for _sid in sorted(_want):
            if _sid not in _sections:
                continue          # a stage this example flow does not have
            if _nm.lower() not in _sections[_sid]:
                fail(f"references/companion-skills.md points {_nm!r} at stage {_sid} "
                     f"and references/stages.md's stage {_sid} never names it — "
                     "a companion the operator is told to install for a stage that "
                     "has not heard of it")

    # P3-G0. Both readers of this table parse a cell as `[^|]*`, so ANY extra pipe in a
    # row ends that cell early and silently hands the next guard a different column.
    # Found on this repo while adding the `playwright` row: the row listed
    # `open\|click\|type` in its first cell, the matrix->stages check read the second
    # cell as "click", parsed no stage numbers out of it, and passed without ever
    # comparing anything. A guard that is quiet because its input was truncated is
    # indistinguishable from a guard that looked and agreed.
    #
    # THE FIRST DRAFT OF THIS GUARD CHECKED `\\|` ONLY, and the reader R-005 dispatched
    # broke it in one move: a BARE `|` truncates the identical way and passed, with a
    # control proving it masked real matrix->stages drift. The umbrella's B-40 was that
    # same unescaped form. So the check is now the cell COUNT against the header, which
    # is blind to how the pipe was written — the property that matters is *the readers
    # disagree with the table about where cell two ends*, not the author's escaping.
    _hdr = next((l for l in _cs_t.splitlines()
                 if l.startswith("| Skill / tool")), None)
    if _hdr:
        _want_cells = _hdr.count("|")
        for _ln, _line in enumerate(_cs_t.splitlines(), 1):
            if not re.match(r"^\|\s*\*\*[^*|]+\*\*", _line):
                continue
            if _line.count("|") != _want_cells:
                _how = ("an escaped `\\|`" if "\\|" in _line else "a bare `|`")
                fail(f"references/companion-skills.md:{_ln}: a matrix row has "
                     f"{_line.count('|')} pipes where the header has {_want_cells} — it "
                     f"carries {_how} inside a cell. Every reader of this table splits "
                     "on `|` and neither decodes the escaped form, so cell two is not "
                     "the cell the table shows and the matrix->stages check compares "
                     "something else, or nothing. Use commas, or a code span per item")

    # P3-G0b. The failure mode P3-G0 exists to prevent is *a row whose stage set comes
    # out empty*, and a pipe is only one way to get there. The `agent-sync` row got there
    # by writing `stage-10` with a hyphen, which the stage regex below does not match —
    # one row under the `graphify` row this release fixed, in the same table, found by
    # the same reader. So assert the outcome directly: every matrix row must yield at
    # least one stage. A row that names no stage is a companion the operator is told to
    # install for nothing, and a row that means to name one and fails to is a check
    # standing over an empty set, reporting agreement.
    if _hdr:
        for _ln, _line in enumerate(_cs_t.splitlines(), 1):
            _m = re.match(r"^\|\s*\*\*([^*|]+)\*\*[^|]*\|([^|]*)\|", _line)
            if not _m:
                continue
            if not _STAGE_REF.search(_m.group(2)):
                _nm = re.sub(r"^\[|\]$", "", re.split(r"\s*\(", _m.group(1))[0].strip())
                fail(f"references/companion-skills.md:{_ln}: the matrix row for {_nm!r} "
                     "names no stage its second cell can be read from, so the "
                     "matrix->stages check has nothing to compare and passes in silence. "
                     "Write `stage N` or `stages N–M` — `stage-N` with a hyphen is the "
                     "spelling that produced this defect")

    # P3-G0c. A stage that demands a look at the rendered surface must say HOW one is
    # taken. From v1.36.0 to v1.55.0 stages 5, 6 and 8 demanded it and named only which
    # companion to install — so *check it in a browser* had no mechanism behind it
    # anywhere in the bundle, which is exactly how a run reports "I checked the browser"
    # and means "I ran the unit tests". `references/browser.md` is that mechanism, and
    # this check is that no stage can go back to demanding the look without pointing at it.
    _BR = os.path.join(ROOT, _SKILLDIR, "references/browser.md")
    if os.path.isfile(_BR):
        for _sid, _sec in sorted(_sections.items()):
            if "playwright" not in _sec and "chrome-devtools" not in _sec:
                continue
            if "browser.md" not in _sec:
                fail(f"references/stages.md: stage {_sid} asks for a browser channel and "
                     "never points at references/browser.md — a stage that demands a look "
                     "at the rendered surface and names no mechanism is how 'checked in a "
                     "browser' comes to mean 'ran the unit tests'")
        # The four moves the look IS. A file that stops naming one of them stops being the
        # mechanism the stages were pointed at, and nothing else would notice.
        _brt = open(_BR, encoding="utf-8").read()
        for _move in ("open", "snapshot", "console", "requests"):
            if not re.search(rf"playwright-cli (?:-s=\S+ )?{_move}(?=\s|$)", _brt, re.M):
                fail(f"references/browser.md no longer shows `playwright-cli {_move}` — "
                     "the look is open + snapshot + console + requests, and a mechanism "
                     "file missing one of the four leaves that step to taste")

    # P3-G2. The guard above reads matrix ROW NAMES, so a sub-skill named inside a
    # row's own cell is out of its scope — and that is exactly where super-ux's copy
    # half lived while being invisible to every stage. A probe found the hole, which
    # is why this second, narrower check exists: the three stage-3 tracks by name,
    # each naming the companion that owns it. Narrow on purpose. Generalising the
    # sub-skill mapping would demand that stage 3 name `/brand-lint` and `ux-audit`
    # too, which belong to other stages, and a check that over-reaches is switched
    # off by the third person who hits it.
    _s3 = _sections.get("3", "")
    if not _s3:
        _UNLOOKED.append("skip: the stage-3 tracks — this flow has no stage 3")
    else:
        for _track, _owner in (("ux track", "super-ux"),
                               ("copy track", "copywriting"),
                               ("visual track", "sheleg-design")):
            if _track not in _s3:
                fail(f"references/stages.md stage 3: no {_track!r} — the stage names "
                     "what the interface must do, and not how it sounds or looks")
            elif _owner not in _s3:
                fail(f"references/stages.md stage 3: the {_track!r} names no owner — "
                     f"{_owner!r} is absent, so the track is a heading with no skill "
                     "behind it")

# --- P4: publishing a retro insight (v1.37.0) ---------------------------------
# SCOPE: the doctrine and the schema agreeing, the rule count being computed, and
# the worked example obeying the rules it teaches. It cannot check that a run
# redacted anything — no static check can read an issue that was opened.
_RT_P = os.path.join(ROOT, _SKILLDIR, "references/retrospective.md")
_SCHEMA_P = os.path.join(ROOT, _SKILLDIR, "pipeline.schema.json")
if os.path.isfile(_RT_P):
    _rt_t = open(_RT_P, encoding="utf-8").read()
    _rt_f = _flatten(_rt_t, lower=True)

    # P4-G1. The rule list is an enumeration stated twice — as a word in the
    # sentence that introduces it, and as the numbered items. N1 spent six review
    # rounds on exactly this shape, so the count is COMPUTED from the items and
    # required in the sentence rather than compared by eye.
    _sec = ""
    _m_sec = re.search(r"^##\s+What may leave the project.*?$(.*?)(?=^##\s|\Z)",
                       _rt_t, re.S | re.M)
    if not _m_sec:
        fail("references/retrospective.md: no redaction section — the doctrine "
             "publishes to another repository and says nothing about what leaves")
    else:
        _sec = _m_sec.group(1)
        _rules = re.findall(r"^\s*(\d+)\.\s+\*\*", _sec, re.M)
        _n = len(_rules)
        _words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
                  7: "seven", 8: "eight", 9: "nine", 10: "ten"}
        if _n == 0:
            fail("references/retrospective.md: the redaction rules are prose, not an "
                 "enumeration — a list nobody can point at an item of is advice")
        else:
            # R-003 sweep, 2026-08-10: the sibling shape `_words.get(n, n)` reaches a
            # CEILING at ten and then compares against the digit alone — the same
            # word-map ceiling that produced R-006. Accept either form, and say which
            # ones were looked for, so a count past the map is a legible failure
            # rather than a message quoting a number the prose never uses.
            _forms = {str(_n)}
            if _n in _words:
                _forms.add(_words[_n])
            _flat_sec = _flatten(_sec, lower=True)
            if not any(f"{_f} rules" in _flat_sec for _f in _forms):
                fail(f"references/retrospective.md: {_n} numbered redaction rules and "
                     "the sentence introducing them says none of "
                     f"{sorted(_forms)!r} — an enumeration counted in prose is a "
                     "count that drifts")

    # P4-G2. The worked issue block must obey the rules it teaches. A doctrine whose
    # own example breaks its own rule is the class that shipped in templates/backlog.md,
    # seeded into every host project with arithmetic contradicting its own formula.
    for _blk in re.findall(r"```[a-zA-Z]*\n(.*?)```", _rt_t, re.S):
        if "would open issue" not in _blk:
            continue
        if re.search(r"(?m)^\s*/|\s/(Users|home|var|opt)/", _blk):
            fail("references/retrospective.md: the worked issue body carries an "
                 "absolute path — rule 1 of the list it is printed beside")
        if re.search(r"\b[0-9a-f]{7,40}\b", _blk):
            fail("references/retrospective.md: the worked issue body carries what "
                 "reads as a commit — rule 2 of the list it is printed beside")
        for _slug in set(re.findall(r"\b([\w.-]+/[\w.-]+)\b", _blk)):
            if "task-pipeline" not in _slug and not _slug.startswith(
                    ("references/", "templates/", "test/", "plugins/", "docs/")):
                fail(f"references/retrospective.md: the worked issue body names "
                     f"{_slug!r}, which is neither the skill's own repository nor a "
                     "path inside it — rule 2 of the list it is printed beside")

    # P4-G3. Doctrine and schema, both directions. An opt-in described in prose and
    # absent from the schema validates nothing; a schema key no doctrine explains is
    # a switch with no stated consequence.
    if "retro.publish" not in _rt_t:
        fail("references/retrospective.md: publishing is described with no config key "
             "— an outward act armed by nothing nameable is armed by assumption")
    if os.path.isfile(_SCHEMA_P):
        _sch_t = open(_SCHEMA_P, encoding="utf-8").read()
        _pub = json.loads(_sch_t).get("definitions", {}).get("retro", {}) \
            .get("properties", {}).get("publish")
        if _pub is None:
            fail("pipeline.schema.json: references/retrospective.md documents "
                 "`retro.publish` and the schema does not define it — the key the "
                 "doctrine tells an operator to set validates nothing")
        elif "off" not in _pub.get("description", "").lower():
            fail("pipeline.schema.json: `retro.publish` does not state that it is OFF "
                 "when absent — a default nobody reads as off is a default that "
                 "publishes")
    if "retro.publish" not in open(_ST_P, encoding="utf-8").read():
        fail("references/stages.md: no stage names `retro.publish` — a step described "
             "in the retro's doctrine and in no stage is a step that never runs")

# --- Tier 2 of the skill audit: make a green mean something (v1.38.0) ---------
# SCOPE: the doctrine's own agreement and the harness's existence. Neither can
# observe a review that happened, which is the point of the NO READER state.
_RV_P = os.path.join(ROOT, _SKILLDIR, "references/review.md")

# T2-G1. The reader's three states are an enumeration stated in two files. The third
# state is the whole mechanism: `NO READER` printed is what stops "a reader was
# requested" from reading as "a reader reported". Both directions, because a state
# in the doctrine and not in the stage never gets emitted, and a state emitted by a
# stage and not in the doctrine is a vocabulary nobody defined.
if os.path.isfile(_RV_P) and os.path.isfile(_ST_P):
    _rv_t = open(_RV_P, encoding="utf-8").read()
    _st_t3 = open(_ST_P, encoding="utf-8").read()
    _states = set()
    for _blk in re.findall(r"```[a-zA-Z]*\n(.*?)```", _rv_t, re.S):
        for _ln in _blk.split("\n"):
            _m = re.match(r"\s*reader:\s*(.+?)(?:\s{2,}|—|$)", _ln)
            if _m:
                _states.add(re.sub(r"\d+", "N", _m.group(1)).strip().lower())
    if len(_states) < 3:
        fail(f"references/review.md: the independent reader has {len(_states)} recorded "
             "state(s), not three — without a printed NO READER, a reader that never "
             "read is indistinguishable from one that found nothing")
    if not any("no reader" in _s for _s in _states):
        fail("references/review.md: no `NO READER` state — the other two say what a "
             "reader found, and the whole mechanism is the one that says nobody read")
    _stn = _flatten(_st_t3, lower=True)
    for _s in sorted(_states):
        # Matched WITH its `reader:` prefix. Keyed on the bare words, `none found`
        # matched stage 0's source-ledger sentence — a coincidence in another
        # paragraph, and the guard passed over a stage that had dropped the state.
        _key = "reader: " + _s.split(",")[0].strip()
        if _key not in _stn:
            fail(f"references/stages.md: the stage running the review never names the "
                 f"reader state {_key!r}, which references/review.md defines — "
                 "a state no stage emits is a state nobody records")

# T2-G2. R-001's retirement condition, written at birth in 2026-08-03: a probe
# harness that asserts the plant changed the parsed text. It must exist, expose the
# two names a caller uses, be runnable from package.json, and be named where probing
# is taught — a harness nobody is pointed at is a fourth hand-rolled loop waiting.
_PB_P = os.path.join(ROOT, "test", "probe.py")
if not os.path.isfile(_PB_P):
    fail("test/probe.py is absent — R-001 has asked for a probe harness since "
         "2026-08-03 and three hand-rolled probes failed in one day for want of it")
else:
    _pb = open(_PB_P, encoding="utf-8").read()
    for _sym in ("class Plant", "def run_probes", "expect"):
        if _sym not in _pb:
            fail(f"test/probe.py does not define {_sym!r} — the harness must name the "
                 "guard a plant targets, or it proves only that something broke")
    _pkg = json.loads(open(os.path.join(ROOT, "package.json"), encoding="utf-8").read())
    if "probe.py" not in json.dumps(_pkg.get("scripts", {})):
        fail("package.json: no script runs test/probe.py — a harness with no entry "
             "point is a file, not a gate")
    _gt = open(os.path.join(ROOT, _SKILLDIR, "references/gates.md"), encoding="utf-8").read()
    if "test/probe.py" not in _gt:
        fail("references/gates.md teaches probing and never names test/probe.py — "
             "the next probe will be hand-rolled for the fourth time")

# T3-G1. What stage 0 reads IN FULL is an obligation stated in four files, and the
# one section nothing caps must not be in it. Measured 2026-08-10: the narrative log
# was 10 937 of retro.md's 14 756 tokens — 74% of a source whose cap is the entire
# argument for reading it. An uncapped section inside a binding source is what makes
# the capped part get skimmed, so the log is queried like the archive.
# SCOPE: the SENTENCE, not the paragraph. Paragraph-scoped, the word "queried" —
# which legitimately describes the archive one clause away — cancelled the check, so
# both plants landed and the guard stayed quiet. The unit is stated here because
# choosing it wrongly is how three earlier guards in this file went silent.
# It cannot tell whether a run actually read anything.
_FULL_READERS = [
    (f"{ART}/retro.md", os.path.join(ARTP, "retro.md")),
    ("references/retrospective.md", os.path.join(ROOT, _SKILLDIR, "references/retrospective.md")),
    ("references/knowledge-sources.md", os.path.join(ROOT, _SKILLDIR, "references/knowledge-sources.md")),
    ("references/stages.md", _ST_P),
    ("SKILL.md", os.path.join(ROOT, _SKILLDIR, "SKILL.md")),
]
_seen_reader = 0
for _label, _path in _FULL_READERS:
    if not os.path.isfile(_path):
        continue
    _seen_reader += 1
    _flat = _flatten(open(_path, encoding="utf-8").read(), lower=True)
    for _sent in re.split(r"(?<=[.;:!?])\s+|\s\|\s", _flat):
        if "recent log" not in _sent:
            continue
        if "in full" in _sent and "queried" not in _sent:
            fail(f"{_label}: a sentence binds the retro's *Recent log* to "
                 "'in full' — it is the one section nothing caps, and it measured "
                 "74% of the file. Query it by the task's nouns like the archive")
if _seen_reader < 3:
    _UNLOOKED.append("skip: the read-in-full obligation — fewer than three of its "
                     "stated consumers are present in this checkout")

# T4-G1. The preflight reports companion availability in detail; until 2026-08-10 it
# reported this skill's own evidence not at all, which reads as tested. While the eval
# results record no blind run, the preflight says so. SCOPE: the line's presence and
# the results file's honesty about the count — it cannot verify a run happened.
_EV_P = os.path.join(ROOT, "evals", "RESULTS.md")
if os.path.isfile(_CS_P) and os.path.isfile(_EV_P):
    _cs2 = open(_CS_P, encoding="utf-8").read()
    _ev = _flatten(open(_EV_P, encoding="utf-8").read(), lower=True)
    _blind_claimed = "no blind run has been made" in _ev
    if _blind_claimed and "behaviour is unverified" not in _flatten(_cs2, lower=True):
        fail("references/companion-skills.md: evals/RESULTS.md records no blind run "
             "and the preflight does not say so — a skill silent about its own "
             "evidence is read as tested, by the bundle that demands evidence of "
             "everyone else")

# ---------------------------------------------------------------------------
# The routing boundary (v1.39.0). Measured 2026-08-10: three of ten routing
# queries were refused with this skill's OWN exclusion clause quoted back as the
# reason, while references/audit.md says an audit may be the whole task. The
# boundary is what a request ENDS IN — an answer, or something that lands in the
# tree — and these guards hold the three surfaces that state it to one another.
#
# Every check below was rewritten after an independent reader (R-005) defeated the
# first version fifteen ways, each verified by planting the text and watching the
# validator still PASS. What it found, in one sentence: a presence test over a whole
# file proves a word exists, not that the rule says it, and a regex over prose is one
# innocent rewrite from dormancy. Both lessons are why the skips below are LOUD.
_SK_P = os.path.join(_skill_dir, "SKILL.md")
_RR_P = os.path.join(_skill_dir, "templates", "routing-rule.md")
_CR_P = os.path.join(ROOT, "cursor", "rules", "task-pipeline.mdc")
# A reading exclusion may return in any of these forms, in either language. The first
# version matched `\breading\b` alone; `a code read`, `read-through` and `чтение кода`
# all sailed past it, and the incident sentence itself will not be reproduced verbatim
# by whoever rewords it next.
# Narrowed after it fired on `mapping code so a person can read it` — a sentence that
# excludes MAPPING, not reading, and is exactly the wording a careful author uses.
# gates.md puts the false-positive budget at zero, so the heuristic is the reading
# word ADJACENT to code, which is the harmful construct; three intervening words
# are enough to mean something else.
_READ_RE = re.compile(
    r"(?:read\w*|чтени\w*|читат\w*)\W+(?:\w+\W+){0,2}(?:code|код\w*)"
    r"|(?:code|код\w*)\W+(?:\w+\W+){0,2}(?:read\w*|чтени\w*|читат\w*)", re.I)


def _routing_section(path):
    """The `## Routing` section, or None. Scoped, because a file-wide presence test
    proves a word appears somewhere in seven hundred lines — the reader deleted the
    whole boundary clause, added one unrelated sentence containing the same four
    words elsewhere, and the first version passed."""
    if not os.path.isfile(path):
        return None
    _t = open(path, encoding="utf-8").read()
    _m = re.search(r"^##\s+Routing\b.*?$(.*?)(?=^##\s|\Z)", _t, re.S | re.M)
    return _m.group(1) if _m else None


_DESC_M = None
if os.path.isfile(_SK_P):
    _DESC_M = re.search(r'^description:\s*"(.*?)"\s*$',
                        open(_SK_P, encoding="utf-8").read(), re.M | re.S)
if _DESC_M is None:
    _UNLOOKED.append("skip: the routing boundary — SKILL.md has no double-quoted "
                     "description, so none of its seven checks ran")
else:
    _desc_txt = _DESC_M.group(1)
    _not_for = _desc_txt.split("Not for:")[-1] if "Not for:" in _desc_txt else ""
    _use_when = _desc_txt.split("Not for:")[0]

    # 1. Both halves of the criterion, or the boundary reads as build-work-only —
    #    which is the state that produced the three measured refusals.
    if "changes the repository" not in _desc_txt:
        fail("SKILL.md description: the change half of the boundary is gone — "
             "'changes the repository' is what routes a feature, fix or refactor")
    if "finding that lands in it" not in _desc_txt:
        fail("SKILL.md description: the findings half of the boundary is gone. "
             "audit.md says an audit may be the whole task; without this phrase "
             "an agent reads the skill as build-work-only and refuses an audit, "
             "which was measured on three of ten routing queries")

    # 2. Reading may not be an exclusion, on ANY of the three surfaces. It is the
    #    opening move of every findings class this skill routes. The first version
    #    checked the description only, so the exact defect that produced the measured
    #    refusals could return verbatim in both files that ship the rule elsewhere.
    for _p, _label, _txt in (
            (_SK_P, "SKILL.md description", _not_for),
            (_RR_P, "templates/routing-rule.md", None),
            (_CR_P, "cursor/rules/task-pipeline.mdc", None)):
        if _txt is None:
            _sec = _routing_section(_p)
            if _sec is None:
                if os.path.isfile(_p):
                    _UNLOOKED.append(f"skip: reading-exclusion check on {_label} — no "
                                     "`## Routing` section to scope it to")
                continue
            # The WHOLE section. Filtering to lines containing "not" was the first
            # try and it was wrong: an exclusion list's bullets do not repeat the
            # word — it stands in the sentence above them — so the one harmful line
            # never reached the check. Its own probe caught that. The section's
            # correct prose ("reading is not the test", "all begin by reading") is
            # safe because none of it puts a reading word within three of `code`.
            _txt = _sec
        if _READ_RE.search(_txt):
            fail(f"{_label}: reading is named as an exclusion again. An audit, a bug "
                 "hunt and a PR review all OPEN by reading and all three end in the "
                 "tree — the boundary is what the request ends in, and this exact "
                 "sentence is what three measured routing queries quoted when they "
                 "refused")

    # ...and the three exclusions v1.9.0 locked must survive the rewording, or the
    #    clause and the NOTRIG evals drift, which that design forbade by name.
    for _needed, _why in (("answering a question", "the question exclusion"),
                          ("explaining", "the explanation exclusion"),
                          ("one-line edit", "the one-line-edit exclusion")):
        if _needed not in _not_for:
            fail(f"SKILL.md description: {_why} left the 'Not for:' clause — the "
                 "2026-08-03 design locked these three against the NOTRIG evals "
                 "and said the two must not drift")

    # 3. Every verb the v1.9.0 design locked must be on the TRIGGER half of the
    #    surface. DISCOVERED from that design: `перевести` was locked on 2026-08-03,
    #    never shipped, and REQ-003 was accepted `verified` anyway because the evidence
    #    recorded was the clause's shape and its character count — neither of which can
    #    see a missing member of the list the REQ locked. Searching the WHOLE
    #    description was the first version's bug: `Not for: перевести one file` satisfied
    #    it, which is the locked verb's exact inversion.
    _LOCK_P = os.path.join(ARTP, "specs",
                           "2026-08-03-default-routing-adoption-design.md")
    if not os.path.isfile(_LOCK_P):
        _UNLOOKED.append("skip: locked-verb check — the 2026-08-03 design is gone")
    else:
        _lock = open(_LOCK_P, encoding="utf-8").read()
        _lm = re.search(r"\*\*work verbs, RU \+ EN:\*\*(.+?)[;.]", _lock, re.S)
        if _lm is None:
            # The anti-drift guard for a verb list, one innocent rewrite from silence,
            # in a document this repo forbids maintaining. Loud, not dormant.
            fail(f"{ART}/specs/2026-08-03-default-routing-adoption-design.md: "
                 "no `**work verbs, RU + EN:** … ;` list this check can read. It is a "
                 "superseded record and must not be edited to suit a guard — if the "
                 "shape genuinely changed, move the locked list somewhere maintained "
                 "and point this check at it")
        else:
            _verbs = [v.strip(" \n*`") for v in _lm.group(1).split("·")]
            _absent = [v for v in _verbs if v and v.lower() not in _use_when.lower()]
            if _absent:
                fail("SKILL.md description: verb(s) locked by the 2026-08-03 design "
                     f"and absent from the trigger half: {', '.join(_absent)}. "
                     "A decision that never reached the text is the L1->L2 seam "
                     "audit.md exists to walk")

    # 4. The findings classes, DISCOVERED from the description so a class added there
    #    joins this check by existing. Pairs are EXTRACTED rather than split on commas:
    #    the reader added a fifth class with `and` instead of a comma and it vanished
    #    from every downstream check at once.
    _fm = re.search(r"finding that lands in it:(.+?)—", _desc_txt, re.S)
    if _fm is None:
        fail("SKILL.md description: the findings clause no longer has the shape "
             "`finding that lands in it: <class>/<ru>, … —`. Four checks read that "
             "span — the two portable surfaces and both eval-coverage checks — and a "
             "colon changed to a dash takes all four offline in silence")
    else:
        _span = _fm.group(1)
        _classes = [c.strip() for c in re.findall(r"([A-Za-z][A-Za-z ]*?)\s*/\s*[^,—]+",
                                                  _span)]
        # A delimiter this parser cannot see must be a failure, never a shorter list.
        if len(_classes) != _span.count("/"):
            fail("SKILL.md description: the findings clause lists "
                 f"{_span.count('/')} class/alias pairs and this check could extract "
                 f"{len(_classes)} — a separator it cannot see silently shrinks every "
                 "downstream check; use `, ` between pairs")
        for _surface, _label in ((_RR_P, "templates/routing-rule.md"),
                                 (_CR_P, "cursor/rules/task-pipeline.mdc")):
            _sec = _routing_section(_surface)
            if _sec is None:
                if os.path.isfile(_surface):
                    _UNLOOKED.append(f"skip: findings classes on {_label} — no "
                                     "`## Routing` section")
                continue
            _sf = _flatten(_sec, lower=True)
            _miss = [c for c in _classes if c.lower() not in _sf]
            if _miss:
                fail(f"{_label}: the boundary is stated here too, and its `## Routing` "
                     f"section is missing these findings classes: {', '.join(_miss)}. "
                     "A rule that is portable must agree with the description an agent "
                     "routed on")
        # ...and each class needs a TRIGGERING eval. Counting every query was the first
        #    version's worst bug: a `should_not_trigger` control mentioning the word
        #    satisfied it, so the guard could certify "named and untested" — the exact
        #    state it cites B-046 for — as covered.
        _EVJ = os.path.join(ROOT, "evals", "task-pipeline.evals.json")
        if not os.path.isfile(_EVJ):
            _UNLOOKED.append("skip: findings-class eval coverage — no eval suite")
        else:
            try:
                _cases = json.load(open(_EVJ, encoding="utf-8"))["evals"]
            except Exception:
                _cases = None
            if _cases is None:
                _UNLOOKED.append("skip: findings-class eval coverage — the suite did "
                                 "not parse")
            else:
                _q = " ".join((_c.get("query") or "").lower() for _c in _cases
                              if _c.get("category") == "should_trigger")
                # The link between an English class name and the operator's Russian
                # query cannot be discovered — it is declared. What IS mechanical:
                # a class with no declared link fails loudly instead of matching
                # nothing and passing.
                _KEY = {"audit": "аудит", "bug hunt": "ошибок",
                        "production check": "проде", "pr review": "pr #"}
                _unmapped = [c for c in _classes if c.lower() not in _KEY]
                if _unmapped:
                    fail("test/validate.py: findings class(es) with no eval-query alias "
                         f"declared in this guard: {', '.join(_unmapped)}. Add the alias "
                         "in the same change that adds the class, or the guard reports "
                         "coverage it never looked for")
                _noev = [c for c in _classes
                         if c.lower() in _KEY and _KEY[c.lower()] not in _q]
                if _noev:
                    fail("evals/task-pipeline.evals.json: findings class(es) named in "
                         f"the description with no should_trigger query: "
                         f"{', '.join(_noev)}. Named and untested is the state B-046 "
                         "measured across six of the eight build verbs — and a "
                         "should_not_trigger control naming the word is not coverage")


# --- the loop as a mechanism (v1.40.0) ----------------------------------------
# B-054's occasion: a run wrote "продолжаю без остановки" and the turn ended,
# because a sentence about future behaviour is not a wakeup. The mode existed and
# said how OFTEN to continue, never WHAT the next item is. These guards hold the
# three halves of the new contract to each other: the queue, the arming point, and
# the disclosure a self-pacing run owes in place of a job id.
_CONT_P = os.path.join(_skill_dir, "references", "continuity.md")
_STG_P = os.path.join(_skill_dir, "references", "stages.md")
_SCHEMA_P = os.path.join(_skill_dir, "pipeline.schema.json")
_EX_P = os.path.join(_skill_dir, "pipeline.example.json")


def _loop_block(node):
    """run.loop's schema node, by ADDRESS.

    The first version walked the document and returned the first `properties` dict
    holding a "loop" key. A reader gutted the real block and added a deprecated
    top-level `loop` carrying the expected fields: the decoy answered for the
    contract and every check below passed. A path cannot be shadowed."""
    try:
        return node["definitions"]["run"]["properties"]["loop"]
    except (KeyError, TypeError):
        return None


_schema_j = load_json(os.path.relpath(_SCHEMA_P, ROOT)) if os.path.isfile(_SCHEMA_P) else None
_loop_s = _loop_block(_schema_j) if _schema_j else None
if _loop_s is None:
    # This was an _UNLOOKED skip and a reader deleted the whole block: the release's
    # entire contract vanished and CI stayed green with two tidy skip lines. A skip is
    # for what may legitimately be absent; a file this repository ships is not that.
    fail("pipeline.schema.json: no run.loop block at definitions.run.properties.loop — "
         "the queue, the arming point and the modes have no contract, and `run` allows "
         "additional properties, so the example still conforms while meaning nothing")
else:
    _lp = _loop_s.get("properties") or {}
    # G1. A loop with no queue is a timer. The field is what stops an armed mode from
    #     picking its next item by recollection, which is learned.md rule 16 once per fire.
    if "queue" not in _lp:
        fail("pipeline.schema.json: run.loop has no `queue` — a loop that says how often "
             "to continue and never what the next item is leaves the run choosing by "
             "recollection, which is the failure the mode was supposed to remove")
    if "arm" not in _lp:
        fail("pipeline.schema.json: run.loop has no `arm` — arming at preflight is arming "
             "a loop with nothing to walk when the queue is stage 2's module map")
    _modes = (_lp.get("mode") or {}).get("enum") or []
    if "dynamic" not in _modes:
        fail("pipeline.schema.json: run.loop.mode has no `dynamic` — a harness that can "
             "schedule its own next turn has no way to record that it does, so a "
             "self-pacing run is indistinguishable from an unarmed one")
    # G2. The queue's legal values must be the artefacts that actually exist, or the
    #     field names a source no stage produces.
    _qv = set((_lp.get("queue") or {}).get("enum") or [])
    if "queue" in _lp and not _qv:
        # `if _qv and ...` short-circuited itself: replacing the enum with an open
        # string passed silently, and an open string is precisely "a field that names
        # a source no stage produces".
        fail("pipeline.schema.json: run.loop.queue has no enum — an open string is not "
             "a queue, it is a field that accepts the name of a list nobody builds")
    _av = set((_lp.get("arm") or {}).get("enum") or [])
    if "arm" in _lp and "after-decomposition" not in _av:
        fail("pipeline.schema.json: run.loop.arm does not offer `after-decomposition` — "
             "the field exists and the only arming point it allows is the one this "
             "release moved away from")
    for _need in ("module-map", "plan-tasks"):
        if _qv and _need not in _qv:
            fail(f"pipeline.schema.json: run.loop.queue does not offer `{_need}` — the "
                 "two ordered lists this pipeline already builds are stage 2's module "
                 "map and stage 4's task list; a queue that names neither has no source")

if os.path.isfile(_CONT_P):
    _cont = open(_CONT_P, encoding="utf-8").read()
    _contf = _flatten(_cont, lower=True)
    # G3. The floor the mode may never lower, in the file that defines the mode. It is
    #     the sentence that keeps arming from reading as blanket permission.
    _PHRASE = "generic flag is not a specific authorization"
    # A file-wide `in` test was satisfied by prose from v1.11.0 — twenty-nine releases
    # before the section this guard was written for — and stayed green after BOTH
    # doctrinal statements were deleted, answered by a Rationalizations row. Scope it,
    # and require the floor in each section that states it.
    for _sec_re, _label in (
            (r"^##\s*The limit, before the capability.*?$(.*?)(?=^##\s)", "The limit"),
            # ...stopping at ANY heading depth: the span swallowed its own `###`
            # subsections, so an aside there answered for the section body.
            (r"^##\s*Part 1a\b.*?$(.*?)(?=^#{2,3}\s)", "Part 1a")):
        _sm = re.search(_sec_re, _cont, re.S | re.M)
        if _sm is None:
            fail(f"references/continuity.md: the `{_label}` section is gone — the "
                 "authorization floor is stated there and a guard cannot check a "
                 "section that does not exist")
        elif _PHRASE not in _flatten(_sm.group(1), lower=True):
            fail(f"references/continuity.md `{_label}`: the sentence that keeps arming "
                 "from reading as blanket permission is gone from this section. A "
                 "recorded loop mode is a generic flag, the deploy floor in grill.md "
                 "rests on that distinction, and a copy elsewhere in the file is not "
                 "the copy a reader of this section will meet")
    # ...and Part 1a must state its precondition, or it makes arming unconditional and
    # silently overrides the default-off floor stated three surfaces away.
    # reads: `## Part 1a`, stopping at the next heading of ANY depth — the span
    # swallowed its own `###` subsections, so an aside there answered for the body.
    # Flattened: one disjunct was dead (the source wraps `Where the mode\nis
    # **recorded**`) and the live one was a literal any reword broke.
    _p1a = re.search(r"^##\s*Part 1a\b.*?$(.*?)(?=^#{2,3}\s)", _cont, re.S | re.M)
    if _p1a and not re.search(r"nothing is recorded, nothing arms",
                              _flatten(_p1a.group(1), lower=True)):
        fail("references/continuity.md Part 1a: arming is stated with no precondition "
             "about the recorded mode. Read cold, that arms a loop in a project with no "
             "pipeline.json at all — the reading an independent reader took before this "
             "shipped, and the one `Default off` exists to forbid")
    # G4. A self-pacing run owes the same disclosure an interval run owes. An interval
    #     run prints a job id; a dynamic run has none, so it prints the delay it chose.
    #     Without this a run can report itself as looping while nothing is scheduled —
    #     the exact claim this file already forbids for harnesses with no primitive.
    _dyn_offered = "dynamic" in ((_lp.get("mode") or {}).get("enum") or []) \
        if _loop_s is not None else ("dynamic" in _contf)
    # Triggering on the prose word was the first version: renaming the mode in the file
    # switched the guard off. And the noun-pair regex passed a sentence that INVERTED
    # the rule while keeping the words, so the verb and the consequence are both required.
    if _dyn_offered and not (re.search(r"prints? \*{0,2}the delay it chose", _contf)
                             and "indistinguishable from" in _contf):
        fail("references/continuity.md: `dynamic` is offered and the file never says a "
             "self-pacing run prints the delay it chose. An interval run discloses a job "
             "id; a dynamic run has none, and a run silent about its pacing cannot be "
             "told apart from one that quietly stopped")

# G5. Stage 2 owns the arming point, and both the prose and the machine-readable
#     stage list must say so — the pair that has drifted before.
if os.path.isfile(_STG_P):
    _stg = open(_STG_P, encoding="utf-8").read()
    _m2 = re.search(r"^##\s*2\s*—.*?$(.*?)(?=^##\s)", _stg, re.S | re.M)
    if _m2 is None:
        _UNLOOKED.append("skip: stage-2 arming — no `## 2 —` section in stages.md")
    # reads: the GATE bullet of stage 2, and nothing else in the section.
    # Keyed on the OBLIGATION rather than the discussion around it. A predicate over
    # the whole section was satisfied first by a bare "arm" (from `it arms the UX
    # track`, present since v1.7.0), then by a bullet FORBIDDING arming, then — under
    # a neighbour probe — by a sentence merely containing `after-decomposition`. What
    # a stage must DO lives in its gate; prose above it can say anything.
    # reads: the FIRST PARAGRAPH of the GATE bullet. The bullet is last in the section,
    # so the split hands it everything to the section end and a trailing note answered
    # for it; and `startswith("- **GATE")` took `- **GATEways…` as the gate.
    elif "arming state" not in _flatten(
            next((_b for _b in re.split(r"\n(?=- )", _m2.group(1))
                  if re.match(r"- \*\*GATE\b", _b.lstrip())), "").split("\n\n", 1)[0],
            lower=True):
        # A bare "arm" was the first predicate and it was satisfied from the day it was
        # written — this stage has said "it arms the UX track in stage 3" since v1.7.0,
        # so the guard passed for a reason that had nothing to do with the loop. Found
        # by its own probe, which could not make it fail. The predicate now names the
        # thing it is about.
        fail("references/stages.md stage 2: the GATE does not require the loop's arming "
             "state to be printed. Arming at preflight arms a loop with nothing to walk, "
             "and what a stage must DO lives in its gate — prose above it can say anything")
    elif not re.search(r"loop arms here", _flatten(_m2.group(1), lower=True)):
        # Rekeying to the gate silently dropped this: deleting the whole queue bullet
        # passed, while lp07 kept firing only because it ALSO deletes the gate clause.
        # A probe whose stated claim has quietly become another probe's claim is the
        # coverage loss this release nearly shipped.
        fail("references/stages.md stage 2: the gate requires the arming state and the "
             "body no longer explains where the queue comes from. The obligation and its "
             "reason are two statements of one rule, and this file has lost that pair "
             "before")
_ex_j = load_json(os.path.relpath(_EX_P, ROOT)) if os.path.isfile(_EX_P) else None
if _ex_j:
    # By ID: a reader renamed the stage on all seven surfaces and this guard went
    # silent while the example's gate lost the arming.
    _b2 = [_s for _s in (_ex_j.get("stages") or [])
           if isinstance(_s, dict) and _s.get("id") == 2]
    if _b2 and "arming state" not in str((_b2[0].get("gate") or {}).get("check", "")).lower():
        fail("pipeline.example.json stage 'Brainstorm + decompose': its gate does not "
             "require the loop's arming state to be printed. stages.md says it does, and "
             "the pair of surfaces that states one rule is the pair that drifts")

    # The example is what gets copied — the premise this block inherits from v1.11.0 —
    # and the two fields this release added could leave it silently. A reader reverted
    # run.loop to its pre-v1.40 shape and the whole contract passed.
    _exl = ((_ex_j.get("run") or {}).get("loop") or {})
    if _exl:
        for _f in ("queue", "arm"):
            if _f not in _exl:
                fail(f"pipeline.example.json: run.loop has no `{_f}` — the schema offers "
                     "it and the example is what a project copies, so a field absent "
                     "here is a field nobody discovers")
        if _exl.get("mode") == "interval" and not _exl.get("interval"):
            fail("pipeline.example.json: run.loop.mode is 'interval' with no interval — "
                 "the schema says the field is required for that mode and states it in "
                 "prose only")
        if _exl.get("mode") == "dynamic" and _exl.get("interval"):
            fail("pipeline.example.json: run.loop.mode is 'dynamic' and an interval is "
                 "set — the schema calls it meaningless for a self-pacing run, and an "
                 "example carrying a meaningless field teaches it")


# The run-stamp table is read in full at stage 0 and had no cap until v1.41.0 —
# ~2 099 tok over 27 rows against the standing instructions' ~1 234 behind a cap of ten,
# while the doctrine called both "bounded by construction". One line per run is a slope.
# The cold trigger reads the last FIVE stamps, so ten is that with a margin.
#
# Rewritten after a reader defeated the first version six ways. The lessons, all of them
# this session's recurring class — a check answered by text that is not its subject:
#   * it counted rows under ONE heading; a second `## Run stamps — …` heading in the same
#     file held forty more and passed. Stage 0 reads the FILE;
#   * it required a `|` at column zero; one leading space, still a valid table row, hid a
#     row from it;
#   * the doctrine's own stamp command appends `<date> · <sha>` as PROSE, so an agent
#     obeying the shipped instruction literally produced stamps it could not see;
#   * it named one file, while `templates/retro.md` ships the same table to every host
#     project — the fourth hand-written corpus this repository has caught (invariant 4).
_STAMP_ROW = re.compile(r"^[ \t]{0,3}\|\s*\d{4}-\d{2}-\d{2}\s*\|", re.M)
_STAMP_LIST = re.compile(r"^[ \t]{0,3}[-*]\s+\d{4}-\d{2}-\d{2}\b[^\n]*`[0-9a-f]{7,40}`", re.M)
_STAMP_LINE = re.compile(r"^[ \t]{0,3}\d{4}-\d{2}-\d{2}\s*·\s*`?[0-9a-f]{7,40}`?", re.M)
STAMP_CAP = 10


def _count_stamps(text):
    return (len(_STAMP_ROW.findall(text)) + len(_STAMP_LIST.findall(text))
            + len(_STAMP_LINE.findall(text)))


# DISCOVERED: every `retro.md` this repository ships or keeps, excluding the archive,
# which the doctrine says is append-only and never read in full.
_RETRO_FILES, _ = _discover_md(
    # the archive is append-only and never read in full, so its stamps are not a floor
    (f"{ART}/retro/",),
    lambda _c: bool(re.search(r"^##\s*Run stamps\b", _c, re.M)))
if not _RETRO_FILES:
    fail("no file with a `## Run stamps` section found — the stamp cap has no corpus, "
         "and a check with an empty corpus passes by looking at nothing")
for _rel in _RETRO_FILES:
    _rp = os.path.join(ROOT, _rel)
    if not os.path.isfile(_rp):
        continue
    _n = _count_stamps(open(_rp, encoding="utf-8").read())
    if _n > STAMP_CAP:
        fail(f"{_rel}: {_n} run stamps in a file read in full at stage 0, and the cap is "
             f"{STAMP_CAP}. Rotate the oldest into {ART}/retro/YYYY-QN.md — "
             "the cold trigger reads the last five, so ten leaves it a margin it cannot "
             "lose. Counted in every shape the doctrine writes them: table rows, list "
             "items and the `<date> · <sha>` line its own command appends")

# ...and the doctrine must give the stamps a cap of their own. Scoped to the SEGMENT of
# the row that names them: the first version read the whole file and could not tell a
# claim from the sentence refuting it; the second read the row and was answered by the
# standing instructions' `max 10` in the same cell; the third read everything after
# "run stamps" and was defeated by swapping the two items around the `·`.
_RETRO_DOC = os.path.join(_skill_dir, "references", "retrospective.md")
if os.path.isfile(_RETRO_DOC):
    _seg = None
    for _l in open(_RETRO_DOC, encoding="utf-8").read().splitlines():
        # reads: the ONE row whose first cell names the artifact root's retro.md. Scanning
        # every `|` line let a decoy row for the ARCHIVE answer for the live file; and
        # splitting on `·` made the scope depend on punctuation no doctrine requires,
        # so `, and` in its place restored the v1.41.0 defeat.
        if not _l.startswith("|") or f"{ART}/retro.md" not in _l.split("|")[1]:
            continue
        for _cell in _l.split("|"):
            for _s in re.split(r"(?=\*\*[A-Z])", _cell):
                if "run stamps" in _flatten(_s, lower=True):
                    _seg = _s
                    break
            if _seg is not None:
                break
        if _seg is not None:
            break
    if _seg is None:
        fail("references/retrospective.md: the source table has no segment naming "
             "retro.md's run stamps — `**Run** **stamps**` renders identically and sent "
             "an earlier version of this check into a silent skip, so the phrase is "
             "matched on flattened text and its absence is a failure, not a disclosure")
    elif not re.search(r"max\s*\*{0,2}\s*10\b|capped at ten", _flatten(_seg), re.I):
        fail("references/retrospective.md: the run stamps are given no cap where they "
             "are described. One line per run is a slope, not a bound — the shape the "
             "2026-08-10 audit removed from the narrative log and left in its neighbour")


# --- the hand-back (v1.43.0) --------------------------------------------------
# The rail says WHERE a run is; it never said what happened, and an operator who
# stepped away rebuilt that by asking. Measured on this project: a fourteen-iteration
# session in which every return began with the same question. The hand-back is a gate
# criterion because this same file already carried one instruction with no gate behind
# it — "copy it, tick it" — and no run had ever obeyed it.
_PROG_P = os.path.join(_skill_dir, "references", "progress.md")
_STG_P2 = os.path.join(_skill_dir, "references", "stages.md")
_EX_P2 = os.path.join(_skill_dir, "pipeline.example.json")

if not os.path.isfile(_PROG_P):
    fail("references/progress.md is gone — the boundaries and the hand-back have no home")
else:
    _pg = open(_PROG_P, encoding="utf-8").read()
    # reads: the `## The hand-back` section INCLUDING its `###` subsections, which is
    # where the computed ambiguity sources live. v1.42.0 narrowed a different span to
    # `#{2,3}` because THAT subject excluded its subsections; this one contains them.
    # The span follows the subject, not a house style — narrowing by reflex would have
    # cut this guard off from four of the things it checks.
    _hb = re.search(r"^##\s*The hand-back\b.*?$(.*?)(?=^##\s|\Z)", _pg, re.S | re.M)
    if _hb is None:
        fail("references/progress.md: no `## The hand-back` section — the rail states "
             "position and nothing states what happened, which is the gap it was added "
             "for")
    else:
        _hbf = _flatten(_hb.group(1), lower=True)
        # ...and the SECTION NAMES are read from the fenced template, not the prose
        # around it. Caught by its own probe: `SURFACED` also appears in the sentence
        # explaining why SURFACED matters, so renaming the template row left the guard
        # green — this session's recurring class, in the guard written to end it.
        _hb_fences = re.findall(r"```[^\n]*\n(.*?)```", _hb.group(1), re.S)
        _hb_tpl = _hb_fences[0] if _hb_fences else ""
        if not _hb_tpl.strip():
            fail("references/progress.md → The hand-back: no fenced template — the four "
                 "sections are stated in prose only, and prose about a section is not "
                 "the section")
        # The four sections, by name. A hand-back missing one is a report with a hole
        # exactly where a returning reader looks.
        for _need, _why in (
                ("task", "the request as it was GIVEN — a run that restates it in its own "
                         "words after eight iterations has rewritten it unobserved"),
                ("progress", "where the run stands against that request"),
                ("done", "what was solved, each with its evidence"),
                ("surfaced", "what came up that nobody asked for — the only part "
                             "recoverable from no artefact"),
                ("decisions waiting", "the questions the boundary must ASK"),
                ("ambiguities", "the computed count, which is the half a run cannot "
                                "quietly decide")):
            if not re.search(rf"^\s*{_need}\s{{2,}}", _hb_tpl, re.M | re.I):
                fail(f"references/progress.md → The hand-back: the `{_need.upper()}` "
                     f"section is gone. It carries {_why}")
        # Questions are ASKED, not parked. A question in a report is answered days later.
        # reads: the DECISIONS line of the template plus the paragraph that owns it —
        # not the section. `asked` appears in SURFACED's own description ("nobody asked
        # for"), so a section-wide test was answered by a neighbour. Third time in this
        # release, each caught by the probe rather than by a reader, which is the
        # neighbour-probe habit paying for itself.
        _dec = re.search(r"^\s*DECISIONS WAITING[^\n]*", _hb_tpl, re.M)
        _dec_para = re.search(r"\*\*DECISIONS WAITING[^*]*\*\*[^\n]*(?:\n(?!\n)[^\n]*)*",
                              _hb.group(1))
        _dec_txt = (_dec.group(0) if _dec else "") + " " + (_dec_para.group(0) if _dec_para else "")
        if not re.search(r"\bask(ed|s|ing)?\b", _dec_txt, re.I):
            fail("references/progress.md → The hand-back: the DECISIONS WAITING line does "
                 "not say the question is ASKED at the boundary. A question parked in a "
                 "report is a question the operator answers days later, if at all")
        # ...and the ambiguity list is computed, or it becomes a ritual sentence.
        # reads: the `### AMBIGUITIES` subsection's TABLE, not the section. Keeping the
        # four words as *examples* in a paragraph satisfied a section-wide test while the
        # table and the word `computed` were both gone — the subsection then said the
        # opposite of its own title.
        _amb = re.search(r"^###\s*AMBIGUITIES\b.*?$(.*?)(?=^#{2,3}\s|\Z)", _pg, re.S | re.M)
        _amb_rows = "\n".join(re.findall(r"^\|.*\|\s*$", _amb.group(1), re.M)) if _amb else ""
        if _amb is None or not _amb_rows:
            fail("references/progress.md → AMBIGUITIES: no table of sources. The list is "
                 "stated in prose, and prose naming the four as examples is judgement "
                 "wearing a computation's title")
        if _amb and not re.search(r"read by a command|computed", _flatten(_amb.group(1), lower=True)):
            fail("references/progress.md → AMBIGUITIES: the subsection no longer says the "
                 "sources are computed. Its title says they are")
        _srcs = [_s for _s in ("oq-", "carry-over", "review", "none")
                 if _s not in _flatten(_amb_rows, lower=True)]
        if _srcs:
            fail("references/progress.md → The hand-back: the ambiguity list no longer "
                 f"names these computed sources: {', '.join(_srcs)}. An unbounded 'is "
                 "anything unclear?' becomes a ritual sentence within three runs; these "
                 "four are registers an earlier stage already wrote")
        if "zero prints as zero" not in _hbf and "prints as zero" not in _hbf:
            fail("references/progress.md → The hand-back: nothing states that zero "
                 "prints. Silence and 'I looked and found none' are the two states this "
                 "file exists to keep apart")

# The gate must require it, on both surfaces that state stage 10.
if os.path.isfile(_STG_P2):
    _s10 = re.search(r"^##\s*10\s*—.*?$(.*?)(?=^##\s)",
                     open(_STG_P2, encoding="utf-8").read(), re.S | re.M)
    if _s10 is None:
        _UNLOOKED.append("skip: the hand-back gate — no `## 10 —` section in stages.md")
    else:
        _g10 = _gate_bullet(_s10.group(1))
        # The NORMATIVE phrase, not the noun. A bare substring could not tell a gate
        # requiring the hand-back from one excusing it: `the hand-back is OPTIONAL and
        # may be skipped` passed, in the release whose entire argument is that this must
        # be a criterion rather than a good intention.
        if "the hand-back is written" not in _flatten(_g10, lower=True):
            fail("references/stages.md stage 10: the GATE does not require the hand-back. "
                 "An instruction to report with no gate behind it is what 'copy it, tick "
                 "it' was, and no run ever obeyed that one")
_ex2 = load_json(os.path.relpath(_EX_P2, ROOT)) if os.path.isfile(_EX_P2) else None
if _ex2:
    _a10 = [_s for _s in (_ex2.get("stages") or [])
            if isinstance(_s, dict) and _s.get("state") == "acceptance"]
    if _a10 and "the hand-back is written" not in str((_a10[0].get("gate") or {}).get("check", "")).lower():
        fail("pipeline.example.json stage 'acceptance': its gate does not require the "
             "hand-back while stages.md does — the pair of surfaces that states one rule "
             "is the pair that drifts")


# The hand-back's ARTEFACT. v1.43.0's first draft shipped a gate criterion with no trace:
# every guard read the doctrine files, so all any of them could establish was that the
# instruction was still written down. A reader constructed a conforming hand-back that
# concealed a weakened test and showed that nothing in the repository would notice — and
# that an audit a year later could reach no verdict either way, because there were no run
# records to check. The `hand:` line is what a later audit reads.
_RUN_T = os.path.join(_skill_dir, "templates", "run.md")
if os.path.isfile(_RUN_T):
    _rt2 = open(_RUN_T, encoding="utf-8").read()
    # reads: the `## Lines` DECLARATION block. A file-wide search was answered by the
    # worked example under `## Log`, which is the same file's illustration of the shape
    # rather than its contract — this session's recurring class, sixth instance, and
    # again caught by the probe rather than by a reader.
    _lines_sec = re.search(r"^##\s*Lines\b.*?$(.*?)(?=^##\s|\Z)", _rt2, re.S | re.M)
    _decl = "\n".join(re.findall(r"```[^\n]*\n(.*?)```", _lines_sec.group(1), re.S)) \
        if _lines_sec else ""
    if not re.search(r"^hand:\s", _decl, re.M):
        fail("templates/run.md: no `hand:` line shape. The hand-back is a gate criterion "
             "at stage 10 and, without a shape in the ledger, it leaves no trace — which "
             "is the shape this repository convicted as 'copy it, tick it', one level up")
    _pgt = open(_PROG_P, encoding="utf-8").read() if os.path.isfile(_PROG_P) else ""
    _hb2 = re.search(r"^##\s*The hand-back\b.*?$(.*?)(?=^##\s|\Z)", _pgt, re.S | re.M)
    # ...on the BACKTICKED shape, which is how this bundle names a ledger line
    # everywhere. A bare `hand:` was answered by the sentence `grep -c '^hand:'`, where
    # the same substring lives legitimately — a neighbour inside the same paragraph.
    if _hb2 and "`hand:`" not in _hb2.group(1):
        fail("references/progress.md → The hand-back: the doctrine never names the "
             "ledger line its trace lands on. A narrative with no address is a narrative "
             "no audit can find")


# --- six insights published by other projects through retro.publish (v1.44.0) -------
# The mechanism this bundle shipped for skill-level lessons carried six of them home in
# one day. These guards hold what each one bought. Two arrived at classes this repository
# had reached independently — the ratchet matcher is the neighbour probe, and the unlanded
# plant is R-001, retired here in v1.38.0 and still costing another project three
# incidents in a day. Independent arrival is the strongest evidence either had.
_GATES_P = os.path.join(_skill_dir, "references", "gates.md")
_ACC_P = os.path.join(_skill_dir, "references", "acceptance.md")
_TDD_P = os.path.join(_skill_dir, "references", "tdd.md")
_RETRO_D = os.path.join(_skill_dir, "references", "retrospective.md")

def _section(path, heading_re):
    """A named section, stopping at the next heading of the SAME depth or shallower.

    The first version said that and did something else: its lookahead was a flat
    `^#{1,3}\s`, which stops at a DEEPER heading too. Every section wired to it happened
    to have no `###` inside, so the span was right by luck — and the first subheading
    anyone added would have truncated it before the phrase the guard requires, turning a
    correct doctrine edit into a red build. Found by the PR review app, independently of
    the dispatched reader that found the same shape. The depth is measured, then used."""
    if not os.path.isfile(path):
        return None
    # Read from the cache the module builds at load. The first version reopened
    # gates.md and acceptance.md from disk twice each, beside a comment in this file
    # saying "each living document is read ONCE, not once per class" — and board row
    # B-010 tracks exactly this cost.
    _rel = os.path.relpath(path, ROOT)
    _t = _LIVING_TEXT.get(_rel) or open(path, encoding="utf-8").read()
    _h = re.search(rf"^(#{{2,3}})\s*{heading_re}.*?$", _t, re.M)
    if _h is None:
        return None
    _depth = len(_h.group(1))
    _rest = _t[_h.end():]
    _stop = re.search(rf"^#{{1,{_depth}}}\s", _rest, re.M)
    return _rest[:_stop.start()] if _stop else _rest

# #35 — a ratchet's matcher is a check. The near-miss is the whole rule: a guard that
#       reacts is not a guard that discriminates.
_rm = _section(_GATES_P, r"A ratchet's matcher")
if _rm is None:
    fail("references/gates.md: no section on a ratchet's matcher. A matcher looser than "
         "its subject shrinks the ratchet, credits work nobody did, and compounds for as "
         "long as the ratchet exists — reported from another project through retro.publish")
elif not ("feed its matcher a near-miss it must reject" in _flatten(_rm, lower=True)
              and "re-derive the whole ratchet and print both numbers" in _flatten(_rm, lower=True)):
    fail("references/gates.md → A ratchet's matcher: the near-miss is gone. Seeing a guard "
         "go red on a real change proves it reacts; only a look-alike it must reject "
         "proves it discriminates, and only the second makes its number worth trusting")

# #31 — R-001's class, returned by another project. Scoped to MUTATING probes, because
#       this repository measured itself and found the file-writing ones structurally immune.
_gp = _section(_GATES_P, r"A green probe is evidence")
if _gp is not None and "asserts its plant landed" not in _flatten(_gp, lower=True):
    fail("references/gates.md → A green probe: the obligation is gone. The section can be "
         "emptied to a bare heading and its own rule — a probe that mutates an existing "
         "file asserts its plant landed — leaves with it")
if _gp is None:
    fail("references/gates.md: no section on a green probe whose mutation may not have "
         "landed. `See it fail once` has an unstated precondition — that the thing you "
         "changed is the thing the check reads — and a plant that missed produces the same "
         "green as a check that cannot fail")

# ...and the rule is enforced on the probes themselves: a probe that MUTATES a file must
#    assert its plant landed. Measured 2026-08-11 before the guard existed: 206 of 206
#    mutating probes already did, 55 file-writing ones needed nothing.
_wf2 = os.path.join(ROOT, ".github/workflows/validate.yml")
if os.path.isfile(_wf2):
    _steps = re.findall(r"      - name: Negative self-test \(([^)]*)\)\n        run: \|\n"
                        r"((?:          .*\n|\n)*)", open(_wf2, encoding="utf-8").read())
    # Read-then-write, not two spellings of substitution. Keyed to `.replace(`/`re.sub(`
    # it missed every probe that slices, or that mutates a parsed structure and dumps it —
    # 40 shipped probes, 14 of them with no assertion.
    _mutating = [(_n, _b) for _n, _b in _steps
                 if re.search(r"\.read\(\)|json\.load\(", _b)
                 and re.search(r"""["']w["']|json\.dump\(""", _b)]
    # Case- and wording-insensitive: six probes carried the assertion in lower case
    # (`plant would not land`) and a first version of this check called them defective,
    # which sent a sweep to "fix" six probes that were already sound and corrupt five of
    # them. The rule is about the assertion existing, not about one spelling of it.
    # ...and it must be an `assert` statement, not the phrase in a comment or an echo.
    # All three shapes were watched passing a first version of this check.
    _unasserted = [_n for _n, _b in _mutating
                   if not re.search(r"^\s*assert\b[^\n]*"
                                    r"(?:plant\s+(?:did not|would not|not)\s+land|plant missed)",
                                    _b, re.I | re.M)]
    if _unasserted:
        fail(f"{len(_unasserted)} negative self-test(s) mutate a file and never assert the "
             f"plant landed: {', '.join(_unasserted[:3])}"
             + (" …" if len(_unasserted) > 3 else "")
             + ". A substitution that missed reports the same green as a sound check — "
               "three incidents in one day in the project that reported this")

# #30 — a name in `verified by` is a claim until it resolves.
_vb = _section(_ACC_P, r"A `verified by` name")
if _vb is None:
    fail("references/acceptance.md: no section requiring a `verified by` name to resolve. "
         "A cell can name a check that does not exist and the row reads as covered — the "
         "table stops measuring the run and starts recording its author's intent")
elif "a req with status unknown, never verified" not in _flatten(_vb, lower=True):
    fail("references/acceptance.md → A `verified by` name: the status an unresolvable "
         "name earns is gone. `unknown` is the point — without it the row keeps reading "
         "`verified`, which is the defect")

# #32 — a seam has no file, and REQ rows are written against deliverables.
_sm = _section(_ACC_P, r"A seam is not a deliverable")
if _sm is None:
    fail("references/acceptance.md: no section on the seam. Two halves each correct and "
         "each green formed a closed loop that turned away the population the feature "
         "existed to serve; the coverage table had a row per artefact and no row shape "
         "for the boundary between them")
elif not ("writes an explicit req for the boundary" in _flatten(_sm, lower=True)
              and "the table says so under unlooked" in _flatten(_sm, lower=True)):
    fail("references/acceptance.md → A seam is not a deliverable: the `unlooked` fallback "
         "is gone. Where no check can span the seam, two green halves reporting a working "
         "whole is the false-success shape this file spends its length refusing")

# #33 — the harness is part of the system under test.
_cc = _section(_TDD_P, r"What a case consumes")
if _cc is None:
    fail("references/tdd.md: no section on what a case consumes. A suite that exhausts a "
         "production limit is measuring the limit, and a throttled case reports as a "
         "timeout — noise that costs more than silence because it looks like data")
elif not ("name what each case consumes from the product" in _flatten(_cc, lower=True)
              and "is an unclassified result, not a slow one" in _flatten(_cc, lower=True)):
    fail("references/tdd.md → What a case consumes: the rule that a timeout is an "
         "UNCLASSIFIED result is gone. Read as a slow one, it sends a run to investigate "
         "compilation and hydration while the harness is the cause")

# #34 — an unarmed publish path and one with nothing to say.
_pb = _section(_RETRO_D, r"`publish:` is a line in the verdict")
if _pb is None:
    fail("references/retrospective.md: no section giving publication a line in the "
         "verdict. An unarmed mechanism and a mechanism with nothing to say are "
         "indistinguishable, which is how this instruction went unread for eight releases")
elif not ("stage 10's block carries one line for publication" in _flatten(_pb, lower=True)
              and "not configured" in _flatten(_pb, lower=True)):
    fail("references/retrospective.md → `publish:`: the `not configured` form is gone. A "
         "count of zero beside `configured` is an answer; a blank where configuration is "
         "absent is the silence the section exists to end")
if os.path.isfile(_STG_P2):
    _s10b = re.search(r"^##\s*10\s*—.*?$(.*?)(?=^##\s)",
                      open(_STG_P2, encoding="utf-8").read(), re.S | re.M)
    # On the OBLIGATION, not the token. `publish:` also occurs inside the citation to
    # retrospective.md — flattened, "→ publish: is a line in the verdict" — so the
    # reference to the rule answered for the rule. Seventh instance of that class this
    # session, and again the probe found it rather than a reader.
    if _s10b is None:
        _UNLOOKED.append("skip: the publish: line — no `## 10 —` section in stages.md")
    else:
        _g10c = _gate_bullet(_s10b.group(1))
    if _s10b is not None and "either way the verdict carries a publish" not in _flatten(_g10c, lower=True):
        fail("references/stages.md stage 10: the verdict carries no `publish:` line. The "
             "doctrine says publication is disclosed at the only moment anyone is reading, "
             "and this is that moment")


# --- residue: what the run leaves running, and what it leaves behind ------------
_RES_D = os.path.join(_skill_dir, "references", "residue.md")
if not os.path.isfile(_RES_D):
    fail("references/residue.md is gone. Every gate prints `holds:` and stage 10 will not "
         "close without the teardown; the doctrine behind both has to exist")
else:
    # The ASYMMETRY is the rule, not the word "residue". A run that ends another
    # session's monitor to tidy its own number breaks work that was going fine, and
    # the cost of the two mistakes is not symmetric. Scoped to its own section so the
    # inventory table's mention of leases cannot answer for it.
    _res_own = _section(_RES_D, r"What must \*\*not\*\* be torn down")
    if _res_own is None:
        fail("references/residue.md: no section on what must not be torn down. Without it "
             "the doctrine reads as 'reach zero', and reaching zero across a machine-wide "
             "inventory means ending work this run does not own")
    elif not ("tear down what this run started" in _flatten(_res_own, lower=True)
              and "report what it did not" in _flatten(_res_own, lower=True)):
        fail("references/residue.md → not torn down: the two halves are no longer stated "
             "together. 'End what you started' without 'report what you did not' is the "
             "half that kills another agent's lease")

    # holds: is a disclosure. The moment it acquires a direction it stops describing
    # the environment and starts instructing the run to lie about it.
    _res_t = _LIVING_TEXT.get(os.path.relpath(_RES_D, ROOT)) or open(_RES_D, encoding="utf-8").read()
    if "is never a target" not in _flatten(_res_t, lower=True):
        fail("references/residue.md: `holds:` is no longer declared a non-target. Every other "
             "disclosure in this bundle carries that sentence, and the one that loses it is "
             "the one a run starts optimising")

# Stage 10's gate list must carry the obligation, not a pointer to it. residue.md is
# cited three lines above the criterion, so a check on the filename would be answered
# by the citation — the class this repository has now met nine times.
_ACC_D = os.path.join(_skill_dir, "references", "acceptance.md")
if os.path.isfile(_ACC_D):
    _acc_t = _LIVING_TEXT.get(os.path.relpath(_ACC_D, ROOT)) or open(_ACC_D, encoding="utf-8").read()
    # Scope to the ITEM, not to the region before the next heading. The first draft
    # ran to `^##`, so anything parked between the last criterion and that heading
    # sat inside the span — and the neighbour probe went green on its first use by
    # planting the needle in a comment there. Continuation lines are indented; the
    # item ends at the next line starting in column 0.
    _c13 = re.search(r"^13\.\s(.*?)(?=^\S)", _acc_t, re.S | re.M)
    if _c13 is None:
        fail("references/acceptance.md: stage 10 has no criterion 13. The teardown was added "
             "as a gate criterion precisely because a cleanup written as good intention runs "
             "on the runs that did not need it and is skipped by the ones that did")
    elif not ("eight classes enumerated" in _flatten(_c13.group(1), lower=True)
              and "reported, never ended" in _flatten(_c13.group(1), lower=True)):
        fail("references/acceptance.md criterion 13: the give-back obligation lost one of its "
             "halves — enumerate all eight classes, and report rather than end what this run "
             "did not start. A criterion holding only the first teaches a run to tidy someone "
             "else's environment")
    else:
        # A keyword guard cannot see a clause added BESIDE its needle that inverts the
        # rule — measured on this release: "reported, never ended — unless it looks
        # stale, in which case end it" kept every needle and passed. This rule admits
        # no exception by design, so an exception marker inside its span is itself the
        # defect, and that IS decidable. Narrow on purpose: it fires on a legitimate
        # rewrite too, and a guard that makes you argue beats one that sleeps.
        _ex = re.search(_EXCEPTION_MARKER, _flatten(_c13.group(1), lower=True))
        if _ex:
            fail("references/acceptance.md criterion 13: an exception marker "
                 f"(`{_ex.group(1)}`) appears inside a rule that admits none. Ending work "
                 "this run did not start is not conditional on how stale it looks — stale "
                 "is a judgement about someone else's work and the holder is a fact")

# The two absolute sentences in residue.md, guarded as sentences rather than as topics.
# Both survived an inversion planted next to their keywords on this release.
if os.path.isfile(_RES_D):
    _rt_raw = (_LIVING_TEXT.get(os.path.relpath(_RES_D, ROOT))
               or open(_RES_D, encoding="utf-8").read())
    _rt = _flatten(_rt_raw, lower=True)
    # Both of this file's absolute rules get the same treatment criterion 13 gets:
    # presence of the sentence, AND no exception marker in the sentence that carries
    # it. Guarding only presence was this release's own class — "never released by
    # this run, unless it has clearly expired" keeps every substring and inverts the
    # rule. Fixed on criterion 13 and not swept to the siblings until a reader said so,
    # which is R-003's third failure to be applied to itself today.
    _abs = [("never released by this run",
             "references/residue.md: the lease rule lost its absolute form. 'May be "
             "released once it looks stale' is the same sentence with the protection "
             "removed, and it reads identically to a reader skimming for the topic"),
            ("a foreign item never becomes spent",
             "references/residue.md: nothing stops the third owner state from reaching "
             "outside the project. Three days of uptime is information for whoever owns "
             "the container, not permission to stop it")]
    for _needle, _msg in _abs:
        if _needle not in _rt:
            fail(_msg)
            continue
        # The SPAN, not the sentence. Criterion 13's guard reads its whole multi-line
        # item; this one split the file into sentences and read only the one holding
        # the needle, so a carve-out phrased as the NEXT sentence — "…never becomes
        # spent. Except when a container has been idle for a week." — was invisible.
        # A weaker copy of the guard it was written to mirror.
        _hit = _carve_out(_rt_raw, _needle)
        if _hit:
            fail(f"references/residue.md: `{_needle}` still reads, and an exception "
                 f"marker (`{_hit.group(1)}`) sits beside it, in the same item. An absolute "
                 "rule with a carve-out is the inversion this release added a guard "
                 "for on criterion 13 — the siblings need it too")
    # The third owner state widens what a run may clean INSIDE its own project. Both
    # halves are load-bearing: "provably spent" is what keeps it from becoming a
    # judgement, and "a foreign item never becomes spent" is what keeps it from
    # widening outward. Either alone reads as a licence.
    # Scope to the TABLE ROW. `provably spent` also appears in the paragraph that
    # explains it, so a file-wide check was answered by the explanation while the rule
    # it explains had been gutted — caught by attacking it, third time this session.
    # One CELL, not the rest of the line. The row's third column explains the phrase
    # — "*provably spent* is a fact rather than a judgement" — so a capture running to
    # end-of-line was answered by the sibling cell while the rule cell was gutted.
    # Fourth instance this session and the same sub-shape the concept page records.
    _own_line = next((_l for _l in _rt_raw.splitlines()
                      if "an earlier run of this project" in _flatten(_l, lower=True)
                      and _l.lstrip().startswith("|")), None)
    _own_row = _row_cells(_own_line)[1] if _own_line and len(_row_cells(_own_line)) > 1 else None
    if _own_row is None:
        fail("references/residue.md: the owner table lost its `an earlier run of this "
             "project` row — the state that says which accumulated debris a run may clear")
    elif "provably spent" not in _own_row:
        fail("references/residue.md: the third owner state lost `provably spent` from its "
             "own row. Without it, 'an earlier run of this project' becomes a judgement "
             "about whether something looks abandoned, which is the guess this file stops")
    # SKILL.md is the routing surface and residue.md is the doctrine; they name the
    # same ledger field. They shipped disagreeing once — SKILL.md said `residue: N`
    # after the field was renamed to avoid colliding with gates.md's `unmarked
    # residue:`, and the coverage table caught it rather than any guard.
    # `_sk` is a loop variable earlier in this file; a distinct name keeps this guard
    # from depending on where that loop happened to stop.
    _sk_txt = _LIVING_TEXT.get(os.path.relpath(_SK_P, ROOT)) or open(_SK_P, encoding="utf-8").read()
    _cross = re.search(r"every gate\s+prints `([^`]+)`", _sk_txt)
    if _cross is None:
        fail("plugins/task-pipeline/skills/task-pipeline/SKILL.md: the cross-cutting rules "
             "no longer name the field every gate prints. A gate disclosure nobody is told "
             "to print is a disclosure that does not exist")
    elif not _cross.group(1).startswith("holds:"):
        fail(f"SKILL.md names the gate field `{_cross.group(1)}` while references/residue.md "
             "defines `holds:`. The routing surface and the doctrine must agree on a "
             "ledger field's name, or a run writes a line no reader parses")

    if "only stage 10 requires the count to reach zero" not in _rt:
        fail("references/residue.md: `holds:` acquired a direction. 'Every stage should "
             "drive the count toward zero' leaves 'is never a target' standing three "
             "paragraphs above it and means the opposite")


# The workflow is counted by regex everywhere above, and a regex is happy with YAML
# that GitHub will reject. Twice on one branch a step title containing `holds: ` broke
# the file: `npm test` stayed green and only CI would have noticed. Parse it.
try:
    import yaml as _yaml
    _wf_p = os.path.join(ROOT, ".github", "workflows", "validate.yml")
    if os.path.isfile(_wf_p):
        try:
            _yaml.safe_load(open(_wf_p, encoding="utf-8").read())
        except Exception as _e:
            fail(f"`.github/workflows/validate.yml` is not valid YAML ({type(_e).__name__}). "
                 "Every count in this validator reads it with a regex, which cannot tell — "
                 "a colon-space inside an unquoted step name is the way this happens")
except ImportError:
    _UNLOOKED.append("skip: workflow YAML parse — PyYAML not installed")


# --- what this session paid for, made mechanical -----------------------------
# 1. DEC-0001. SURFACED is the one hand-back field with no lower bound; the decision
#    was recorded and nothing implemented it for a release, which is R-006's subject
#    applied to a decision instead of a finding.
_PROG_D = os.path.join(_skill_dir, "references", "progress.md")
if os.path.isfile(_PROG_D):
    _pg = _flatten(_LIVING_TEXT.get(os.path.relpath(_PROG_D, ROOT))
                   or open(_PROG_D, encoding="utf-8").read(), lower=True)
    if "is checked against what the run filed" not in _pg:
        fail("references/progress.md: `SURFACED: 0` is no longer checked against the "
             "artefacts the run created. A field with no lower bound decays to a zero "
             "nobody reads, which is worse than no field")
    if "nothing will notice" not in _pg:
        fail("references/progress.md: the SURFACED check lost its residual. It kills the "
             "silent zero and not the blind spot, and a check sold as more than it is "
             "buys exactly the false confidence this file exists to refuse")

# 2. R-006 made readable. "Reported the gap" and "closed the gap" have looked identical
#    in every close-out that did not say which.
if os.path.isfile(_ACC_D):
    _a12a = re.search(r"^12a\.\s(.*?)(?=^\S)", _acc_t, re.S | re.M)
    if _a12a is None:
        fail("references/acceptance.md: stage 10 no longer records, per finding, whether "
             "the behaviour or only the reporting changed. R-006 has been in force for "
             "four releases because nothing could read that distinction")
    # The PAIR, not two loose words. `reporting` occurs again lower in the same item —
    # "a finding whose row says `reporting` stays open" — so a check for both words
    # present was answered by that second mention while the field itself was gutted.
    elif "behaviour or reporting" not in _flatten(_a12a.group(1), lower=True):
        fail("references/acceptance.md criterion 12a: the field no longer offers both "
             "values as a pair. One value alone cannot distinguish anything, and the word "
             "appearing elsewhere in the item is not the field offering it")

# 3. A tag is not evidence. Two releases shipped over a red suite because the release
#    path never ran the negatives — the PR ran them and the tag did not.
_REL_Y = os.path.join(ROOT, ".github", "workflows", "release.yml")
if os.path.isfile(_REL_Y):
    _ry = open(_REL_Y, encoding="utf-8").read()
    # In a LIVE step, not anywhere in the text: `# run: npm run test:all` keeps the
    # phrase and runs nothing, which is this file's own recurring class one level out.
    try:
        import yaml as _y
        _live = any("npm run test:all" in (_st.get("run") or "")
                    for _j in (_y.safe_load(_ry) or {}).get("jobs", {}).values()
                    for _st in (_j.get("steps") or []))
    except Exception:
        _live = None
    if _live is False or (_live is None and "npm run test:all" not in _ry):
        fail("`.github/workflows/release.yml` publishes without running `npm run test:all`. "
             "A release that does not run the suite it advertises can ship a red one, and "
             "has")

# 4. A version number already spoken for. Four collisions in one session, each found at
#    merge time, each costing a renumber of an entire branch.
try:
    _pkgv = json.load(open(os.path.join(ROOT, "package.json"), encoding="utf-8"))["version"]
    _tagged = subprocess.run(["git", "-C", ROOT, "rev-list", "-n", "1", f"v{_pkgv}"],
                             capture_output=True, text=True)
    _head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                           capture_output=True, text=True)
    # A tag that does not exist yet is the normal state of every commit before a
    # release — a pass, not a refusal to look. Reporting it as unlooked inflates the
    # one disclosure whose whole job is to be believed.
    _shallow = subprocess.run(["git", "-C", ROOT, "rev-parse", "--is-shallow-repository"],
                              capture_output=True, text=True).stdout.strip() == "true"
    if _head.returncode != 0:
        _UNLOOKED.append(f"skip: version v{_pkgv} vs its tag — no git history here")
    elif _shallow:
        # A shallow clone cannot answer ancestry, so every pair reads as divergent and
        # the guard would call a legitimate release a collision — which it did, blocking
        # its own. Cannot look is not the same as found, and saying so is the whole
        # point of this disclosure.
        _UNLOOKED.append(f"skip: version v{_pkgv} vs its tag — shallow clone, ancestry unknowable")
    elif _tagged.returncode != 0:
        pass
    # A collision is DIVERGENCE, not difference. A commit before the tag carries the
    # version it will ship under; a commit after it carries the version it shipped,
    # until the next bump — flagging either would make `main` red after every release.
    # What is wrong is another lineage claiming the same number.
    elif _tagged.stdout.strip() and _tagged.stdout.strip() != _head.stdout.strip() and all(
            subprocess.run(["git", "-C", ROOT, "merge-base", "--is-ancestor", _a, _b],
                           capture_output=True).returncode != 0
            for _a, _b in ((_head.stdout.strip(), _tagged.stdout.strip()),
                           (_tagged.stdout.strip(), _head.stdout.strip()))):
        fail(f"package.json claims {_pkgv} and tag v{_pkgv} already points at "
             f"{_tagged.stdout.strip()[:7]}, which is not this commit. The number is spoken "
             "for; pick the next one before the merge finds out for you")
except Exception as _e:
    _UNLOOKED.append(f"skip: version-vs-tag ({type(_e).__name__})")


# 5. A screen is the frame, implemented. Three halves, and each alone is a different
#    rule: the order of authority, the honest width, and what happens with no frame.
_BLD_D = os.path.join(_skill_dir, "references", "build.md")
if os.path.isfile(_BLD_D):
    _scr = _section(_BLD_D, r"4a\. A screen is the frame, implemented")
    if _scr is None:
        fail("references/build.md: no section making a screen the implemented frame. "
             "Without it Figma is an address and a link, which is what it was")
    else:
        _sf = _flatten(_scr, lower=True)
        if "runs after the file, never instead of it" not in _sf:
            fail("references/build.md 4a: the order of authority is gone. sheleg-design "
                 "before the frame invents what the frame already decided")
        if "contract at its own width" not in _sf:
            fail("references/build.md 4a: the frame is stated as a contract without its "
                 "width. A frame is one width and said nothing about the others; a rule "
                 "that ignores that is either unfollowable or vacuous")
        if not ("offers to draw" in _sf and "marked as coming from implementation" in _sf):
            fail("references/build.md 4a: the no-frame branch lost a half. Building and "
                 "naming without offering leaves the file drifting; offering without "
                 "marking puts generated frames where a designer reads decisions")


# 6. Another agent in the same repository. Two mechanisms answering different
#    questions, and the asymmetry that keeps the second one from becoming a licence.
if os.path.isfile(_BLD_D):
    _oth = _section(_BLD_D, r"1a\. Another agent may be in this repository right now")
    if _oth is None:
        fail("references/build.md: nothing tells a run that another agent may hold this "
             "repository. Measured cost of not saying it: four version collisions, a "
             "manifest entry lost to a merge, and a test run corrupted by a copy taken "
             "mid-write")
    else:
        _of = _flatten(_oth, lower=True)
        if "a worktree per agent" not in _of:
            fail("references/build.md 1a: the worktree rule is gone. Sharing a checkout is "
                 "what turns two independent changes into one corrupted state")
        if "a lease before any shared register" not in _of:
            fail("references/build.md 1a: the lease rule is gone. A worktree separates "
                 "files and answers nothing about who may edit the board")
        if "leave their work alone" not in _of:
            fail("references/build.md 1a: what to do on finding the other agent mid-run is "
                 "gone. Ending someone else's work to unblock your own is the asymmetry "
                 "residue.md refuses, one layer up")


if errors:
    print("FAIL: task-pipeline structure invalid")
    for e in errors:
        print(" - " + e)
    sys.exit(1)
print("PASS: task-pipeline structure valid")
print("  claim registry — " + " · ".join(_CLAIM_STATES)
      + (" · UNREAD number-words: " + ", ".join(sorted(_UNPARSED_WORDS)) if _UNPARSED_WORDS else ""))
if _LSHAPE:
    # A disclosure, not a ratchet: no floor, no direction, and never a target.
    print("  " + _LSHAPE + "  (disclosure — no floor, no target)")
# The other disclosure: what this run did not look at. Printed even when empty, because
# "unlooked: 0" and a missing line are the same silence to a reader.
# The never-count, printed. It was computed and dropped on the floor for one release —
# a measurement nobody surfaces is the same silence as no measurement, which is the
# failure this file's own doctrine is loudest about. No floor, no direction, never a
# target: N of M rows have not been looked at by a person, and that is the whole claim.
if _VERIF_TOTAL:
    print(f"  verification: {_VERIF_TOTAL} shipped REQ · {_VERIF_NEVER} never confirmed by "
          "a person  (disclosure — no floor, no target)")
    # The exposure vector. Components named, never summed into a score: a single number
    # invites a threshold, and a threshold here is a target on `never`, which the ledger
    # says may never have one. And NEVER a percentage — `P(defect)` is not computable
    # from these inputs and a number dressed as one is the class this repo removes.
    if _VERIF_NEVER:
        if _VERIF_DATES:
            _newest = max(_VERIF_DATES)
            _d = (datetime.date.today() - datetime.date(*(int(_x) for _x in _newest.split("-")))).days
            _since = f"{_d} days since the last human confirmation ({_newest})"
        else:
            # Zero would read as "checked today", which is the opposite of the truth.
            _since = "never checked"
        _rel = len([_x for _x in _VERIF_ROWS if _x[0]])
        print(f"  exposure: {_VERIF_NEVER} unverified · {_since} · "
              f"{len(set(_x[0] for _x in _VERIF_ROWS if _x[0]))} releases carry one")
        # Oldest first: the longest-unconfirmed row is the one whose context is most gone.
        # Version-aware, not lexicographic: "1" < "9" char-by-char puts v1.10.0 before
        # v1.9.0, which inverts the one ordering rule exposure.md promises — and with the
        # list truncated, the genuinely oldest rows never printed at all.
        def _verkey(_x):
            _m = re.findall(r"\d+", _x[0])
            return ([int(_n) for _n in _m], _x[0]) if _m else ([9999], _x[0])
        for _s, _r, _w in sorted(_VERIF_ROWS, key=_verkey)[:8]:
            print(f"      {_r}  {_w[:58]:60} {_s}")
        if len(_VERIF_ROWS) > 8:
            print(f"      … and {len(_VERIF_ROWS) - 8} more — the full list is "
                  "`/task-pipeline checkup`, which prints all of them")
print(f"  unlooked: {len(_UNLOOKED)}"
      + ("".join("\n    · " + _u for _u in _UNLOOKED) if _UNLOOKED else ""))
