#!/usr/bin/env python3
"""The mechanical half of a project audit: collect, compare, report.

**What this file is for, and what it deliberately is not.** The skill beside it
owns *judgement* — which seams matter, how to read a silence, when an axis is
exhausted. This owns *mechanics*: what the project is, what can be measured
without being asked twice, and the two artefacts a run leaves behind. The split
is not tidiness. A judgement encoded in a script becomes a gate that refuses
things nobody decided to refuse; a mechanic left in prose becomes a step nobody
runs. Both failures have shipped in this family and both are on its boards.

**Stdlib only** (`references/portability.md`): `scripts/` is the one Claude Code
capability that travels to every channel, and a dependency here would make the
audit Claude-Code-shaped. That constraint is why the HTML is a string and the
tokeniser is a ratio nobody is asked to trust.

**Three verdicts, not two.** `clean`, `finding`, and `blind`. A probe that could
not look returns `blind` with the reason, and the reason reaches the page. This
is `references/audit.md`'s *silence is not a reading* raised from a command to a
probe: without the third value, "no Sentry configured" and "no errors" produce
the same empty section, and the second is what a reader takes away.

**Committed state is the subject.** Every probe reads `git ls-files` /
`git show`, and the working tree's disagreement is disclosed rather than failing
the run — the family's standing instruction #10, learned from two guards that
reported a state no clone could reproduce.

Exit codes: `0` the audit ran, findings or not; `1` it could not start. Findings
never change the code, because the operator asked for a report and a report that
exits non-zero is a gate somebody has to disarm.
"""
import argparse
import collections
import datetime
import hashlib
import html as _html
import json
import os
import re
import shutil
import subprocess
import sys

SCHEMA = "project-audit/1"
VERDICTS = ("clean", "finding", "blind")
PHASES = ("discover", "probe", "prod", "seams", "report", "propose")
OUT_DIR = os.path.join("docs", "audit")

# How long a command may run before the probe behind it is called blind. A probe
# that hangs is worse than one that fails: it takes the whole audit with it.
TIMEOUT = 45


# ---------------------------------------------------------------------------
# the three values a probe may return
# ---------------------------------------------------------------------------

class Result(object):
    """A probe's answer. Constructing one with a fourth verdict is refused.

    The vocabulary is closed on purpose. An open one grows a `partial` and a
    `warn` within a month, and then the page has five sections nobody can rank.
    """

    __slots__ = ("verdict", "reason", "evidence", "findings")

    def __init__(self, verdict, reason="", evidence=None, findings=()):
        if verdict not in VERDICTS:
            raise ValueError(
                "verdict %r is not one of %r" % (verdict, list(VERDICTS)))
        self.verdict = verdict
        self.reason = reason
        self.evidence = evidence
        self.findings = list(findings)


Probe = collections.namedtuple("Probe", "id phase needs run")

PROBES = []


def probe(id, phase, needs=()):
    """Register a probe. `needs` are capability names, checked before it runs."""
    def wrap(fn):
        PROBES.append(Probe(id=id, phase=phase, needs=tuple(needs), run=fn))
        return fn
    return wrap


class Ctx(object):
    """What a probe is given. Never a live handle — probes ask, they do not own."""

    def __init__(self, root, profile, capabilities, offline=False,
                 out_rel=OUT_DIR):
        self.root = root
        self.profile = profile
        self.capabilities = set(capabilities)
        self.offline = offline
        # Where this run writes. A probe excludes it so the audit does not
        # read its own artefacts as project state.
        self.out_rel = out_rel

    def sh(self, *args, **kw):
        """Run a command and return `(returncode, stdout, stderr)`.

        Never raises. A probe decides what an empty answer means; this only
        reports what happened, including the case where the binary is absent.
        """
        cwd = kw.pop("cwd", self.root)
        try:
            p = subprocess.run(list(args), cwd=cwd, capture_output=True,
                               text=True, timeout=TIMEOUT)
            return p.returncode, p.stdout, p.stderr
        except FileNotFoundError as exc:
            return 127, "", str(exc)
        except subprocess.TimeoutExpired:
            return 124, "", "timed out after %ss" % TIMEOUT
        except OSError as exc:                       # permissions, exec format
            return 126, "", "%s: %s" % (type(exc).__name__, exc)


def classify_output(returncode, out, err):
    """`read` only when something actually came back.

    A zero exit with no output is the exact shape of both *nothing is wrong* and
    *the instrument never looked*, so this refuses to call it an answer.
    """
    if returncode != 0:
        return "blind"
    if not (out or "").strip():
        return "blind"
    return "read"


def run_probe(p, ctx):
    """Run one probe with its two guards, and never let it take the run down."""
    missing = [n for n in p.needs if n not in ctx.capabilities]
    if missing:
        return Result("blind", "needs %s, not available here"
                               % ", ".join(sorted(missing)))
    try:
        result = p.run(ctx)
    except Exception as exc:                          # noqa: BLE001 — deliberate
        return Result("blind", "%s: %s" % (type(exc).__name__, exc))
    if result is None:
        # Standing instruction #1: a component that never received its input
        # fails OPEN and is indistinguishable from one that approved.
        return Result("blind", "the probe returned nothing")
    return result


# ---------------------------------------------------------------------------
# git — the committed tree is the subject
# ---------------------------------------------------------------------------

def _git(root, *args):
    try:
        p = subprocess.run(["git", "-C", root] + list(args),
                           capture_output=True, text=True, timeout=TIMEOUT)
        return p.returncode, p.stdout, p.stderr
    except Exception as exc:                          # noqa: BLE001
        return 127, "", str(exc)


def is_repo(root):
    rc, out, _ = _git(root, "rev-parse", "--is-inside-work-tree")
    return rc == 0 and out.strip() == "true"


def tracked_files(root):
    """What a clone would get. Never `os.walk` — that reads build residue."""
    rc, out, _ = _git(root, "ls-files")
    if rc != 0:
        return []
    return [line for line in out.split("\n") if line.strip()]


def worktree_state(root, ignore=()):
    """Disclose the disagreement; do not fail on it (standing instruction #10).

    `ignore` exists because of a defect this suite caught on its own three-run
    fixture: run 1 read a clean tree, run 2 read `docs/audit/` — the artefacts
    run 1 had just written — and reported the project dirty. An instrument that
    reads its own output is measuring itself, and the second reading is the one
    an operator would have acted on.
    """
    # `-uall` matters and is not a preference. Plain `--porcelain` collapses an
    # untracked directory to its shallowest path -- `?? docs/`, never
    # `?? docs/audit/x.html` -- so an exclusion by path silently fails to match.
    # Widening the match to "either is a prefix of the other" would fix this run
    # and hide every other new file under `docs/`, which is worse than the bug.
    rc, out, _ = _git(root, "status", "--porcelain", "-uall")
    if rc != 0:
        return {"dirty": None, "paths": [], "reason": "not a git repository"}
    skip = tuple(i.rstrip("/") + "/" for i in ignore)
    paths = [line[3:].strip().strip('"') for line in out.split("\n") if line.strip()]
    paths = [p for p in paths if not any(p.startswith(s) for s in skip)]
    return {"dirty": bool(paths), "paths": paths, "reason": ""}


def submodules(root):
    rc, out, _ = _git(root, "submodule", "status")
    if rc != 0 or not out.strip():
        return []
    rows = []
    for line in out.split("\n"):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 2:
            rows.append({"sha": parts[0].lstrip("+-U"), "path": parts[1],
                         "describe": parts[2].strip("()") if len(parts) > 2 else ""})
    return rows


# ---------------------------------------------------------------------------
# discovery — what this project IS, before anything is measured about it
# ---------------------------------------------------------------------------

MANIFESTS = [
    ("package.json", "javascript", "npm"),
    ("pyproject.toml", "python", ""),
    ("setup.py", "python", ""),
    ("requirements.txt", "python", "pip"),
    ("go.mod", "go", "go"),
    ("Cargo.toml", "rust", "cargo"),
    ("composer.json", "php", "composer"),
    ("Gemfile", "ruby", "bundler"),
    ("pom.xml", "java", "maven"),
    ("build.gradle", "java", "gradle"),
    ("pubspec.yaml", "dart", "pub"),
    ("Package.swift", "swift", "spm"),
]

LOCKS = {
    "package-lock.json": "npm", "yarn.lock": "yarn", "pnpm-lock.yaml": "pnpm",
    "bun.lockb": "bun", "poetry.lock": "poetry", "uv.lock": "uv",
    "Pipfile.lock": "pipenv", "Cargo.lock": "cargo", "go.sum": "go",
    "composer.lock": "composer", "Gemfile.lock": "bundler",
}

CI_MARKERS = [
    (".github/workflows", "github-actions"),
    (".gitlab-ci.yml", "gitlab-ci"),
    ("Jenkinsfile", "jenkins"),
    (".circleci/config.yml", "circleci"),
    ("azure-pipelines.yml", "azure"),
    (".drone.yml", "drone"),
]

DEPLOY_MARKERS = [
    ("Dockerfile", "docker"), ("docker-compose.yml", "compose"),
    ("fly.toml", "fly"), ("vercel.json", "vercel"),
    ("netlify.toml", "netlify"), ("wrangler.toml", "cloudflare-workers"),
    ("app.yaml", "app-engine"), ("Procfile", "procfile"),
    ("serverless.yml", "serverless"), ("k8s", "kubernetes"),
    ("charts", "helm"), ("terraform", "terraform"),
]

TELEMETRY_HINTS = [
    ("sentry", "sentry"), ("@sentry/", "sentry"), ("sentry-sdk", "sentry"),
    ("opentelemetry", "opentelemetry"), ("bugsnag", "bugsnag"),
    ("rollbar", "rollbar"), ("datadog", "datadog"), ("dd-trace", "datadog"),
    ("posthog", "posthog"), ("mixpanel", "mixpanel"), ("amplitude", "amplitude"),
    ("newrelic", "new-relic"), ("prometheus", "prometheus"),
]

DOC_MARKERS = ["README.md", "docs", "CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md",
               "CHANGELOG.md", "docs/adr", "docs/evidence", "ARCHITECTURE.md"]


def _read(path, limit=200000):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read(limit)
    except OSError:
        return ""


def _manifest_version(root):
    """The version the project states about itself, from the manifest it uses."""
    pj = os.path.join(root, "package.json")
    if os.path.exists(pj):
        try:
            return (json.loads(_read(pj)) or {}).get("version")
        except ValueError:
            return None
    pt = os.path.join(root, "pyproject.toml")
    if os.path.exists(pt):
        m = re.search(r'(?m)^\s*version\s*=\s*["\']([^"\']+)', _read(pt))
        if m:
            return m.group(1)
    cg = os.path.join(root, "Cargo.toml")
    if os.path.exists(cg):
        m = re.search(r'(?m)^\s*version\s*=\s*["\']([^"\']+)', _read(cg))
        if m:
            return m.group(1)
    return None


def _manifest_name(root):
    pj = os.path.join(root, "package.json")
    if os.path.exists(pj):
        try:
            return (json.loads(_read(pj)) or {}).get("name")
        except ValueError:
            pass
    pt = os.path.join(root, "pyproject.toml")
    if os.path.exists(pt):
        m = re.search(r'(?m)^\s*name\s*=\s*["\']([^"\']+)', _read(pt))
        if m:
            return m.group(1)
    return os.path.basename(os.path.abspath(root))


def discover(root):
    """The profile every later phase is chosen from.

    Deliberately answers about the *committed* project where git is available:
    a `node_modules` directory says nothing about what the project is, and a
    walk of the working tree would find thousands of them.
    """
    root = os.path.abspath(root)
    tracked = set(tracked_files(root)) if is_repo(root) else set()

    def present(rel):
        if tracked:
            return rel in tracked or any(p.startswith(rel.rstrip("/") + "/")
                                         for p in tracked)
        return os.path.exists(os.path.join(root, rel))

    languages, managers = [], []
    for fname, lang, mgr in MANIFESTS:
        if present(fname):
            if lang not in languages:
                languages.append(lang)
            if mgr and mgr not in managers:
                managers.append(mgr)
    for lock, mgr in LOCKS.items():
        if present(lock) and mgr not in managers:
            managers.append(mgr)

    ci = [name for marker, name in CI_MARKERS if present(marker)]
    deploy = [name for marker, name in DEPLOY_MARKERS if present(marker)]
    docs = [d for d in DOC_MARKERS if present(d)]
    subs = submodules(root)

    # A monorepo by any of the three shapes that actually change how it is read.
    nested_manifests = [p for p in tracked
                        if p.count("/") >= 1 and os.path.basename(p) in
                        {m[0] for m in MANIFESTS}]
    workspaces = False
    pj = os.path.join(root, "package.json")
    if os.path.exists(pj):
        try:
            workspaces = bool((json.loads(_read(pj)) or {}).get("workspaces"))
        except ValueError:
            workspaces = False

    manifest_blob = " ".join(
        _read(os.path.join(root, f)) for f in
        ("package.json", "pyproject.toml", "requirements.txt", "go.mod",
         "Cargo.toml", "composer.json") if os.path.exists(os.path.join(root, f))
    ).lower()
    telemetry = sorted({name for hint, name in TELEMETRY_HINTS
                        if hint in manifest_blob})

    return {
        "root": root,
        "name": _manifest_name(root),
        "version": _manifest_version(root),
        "vcs": "git" if is_repo(root) else "none",
        "languages": sorted(languages),
        "managers": sorted(managers),
        "monorepo": bool(workspaces or subs or len(nested_manifests) > 1),
        "workspaces": workspaces,
        "submodules": subs,
        "ci": ci,
        "deploy": deploy,
        "docs": docs,
        "telemetry": telemetry,
        "tracked_files": len(tracked),
    }


# ---------------------------------------------------------------------------
# REQ-04 — one version, two trees
# ---------------------------------------------------------------------------

def _digest(blob):
    if isinstance(blob, str):
        blob = blob.encode("utf-8", "replace")
    return hashlib.sha256(blob).hexdigest()


def compare_channels(label, trees):
    """Do the channels that claim one label actually ship one tree?

    `trees` maps a channel name to `{path: content}`, or to `None` where the
    channel could not be fetched. The whole point of this function is that it
    never looks at the label: yesterday's family defect shipped three channels
    agreeing on `1.15.0` and disagreeing by 231 lines, under a pin checker that
    was green because it compared the two strings.
    """
    blind = sorted(name for name, tree in trees.items() if tree is None)
    readable = {name: tree for name, tree in trees.items() if tree is not None}
    if len(readable) < 2:
        return {"label": label, "diverged": None, "differing": [],
                "blind": blind, "channels": sorted(trees)}

    per_path = collections.defaultdict(dict)
    for channel, tree in readable.items():
        for path, content in tree.items():
            per_path[path][channel] = _digest(content)

    # Two different facts, and conflating them produces a false positive of the
    # exact shape this whole skill exists to catch. A path in one channel and
    # not another is *packaging* -- an npm tarball ships what `files` allows and
    # nothing else, so `.github/` is absent by design. A path in BOTH channels
    # whose bytes differ is *divergence*: one version string, two artefacts.
    # The first draft counted both and reported 22 differing paths on a member
    # where one file had actually moved.
    differing, only_in = [], collections.defaultdict(list)
    for path, by_channel in per_path.items():
        if len(by_channel) != len(readable):
            for channel in readable:
                if channel not in by_channel:
                    only_in[channel].append(path)
            continue
        if len(set(by_channel.values())) > 1:
            differing.append(path)
    return {"label": label, "diverged": bool(differing),
            "differing": sorted(differing), "blind": blind,
            "only_in": {k: sorted(v) for k, v in only_in.items()},
            "channels": sorted(trees)}


# ---------------------------------------------------------------------------
# REQ-09 — a secret's place and class, never its value
# ---------------------------------------------------------------------------

SECRET_PATTERNS = [
    ("npm token", re.compile(r"\bnpm_[A-Za-z0-9]{36}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("openai-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("linear api key", re.compile(r"\blin_api_[A-Za-z0-9]{20,}\b")),
    ("aws access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("stripe secret", re.compile(r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{20,}\b")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\."
                       r"[A-Za-z0-9_-]{10,}\b")),
]

SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
            ".gz", ".tgz", ".woff", ".woff2", ".ttf", ".mp4", ".mp3", ".lockb"}


def scan_secrets(root, paths=None):
    """Findings that name where and which, and carry no part of the value.

    The redaction is total rather than a prefix: a report is a file people
    forward, and half a credential plus its context is often enough to finish.
    """
    root = os.path.abspath(root)
    if paths is None:
        paths = tracked_files(root) or []
    out = []
    for rel in paths:
        if os.path.splitext(rel)[1].lower() in SKIP_EXT:
            continue
        full = os.path.join(root, rel)
        if not os.path.isfile(full):
            continue
        try:
            if os.path.getsize(full) > 2_000_000:
                continue
        except OSError:
            continue
        text = _read(full)
        if not text:
            continue
        for line_no, line in enumerate(text.split("\n"), 1):
            for name, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    out.append({
                        "where": "%s:%d" % (rel, line_no),
                        "class": name,
                        "remedy": "rotate the credential at its issuer, then "
                                  "remove it from the tree; if it is in "
                                  "history, rotation is the fix and rewriting "
                                  "history is not",
                        "in_history": False,
                    })
                    break
    return out


def scan_secret_history(root, limit=400):
    """The same classes, in what git still holds. Also value-free."""
    rc, out, _ = _git(root, "log", "--format=%H", "-n", str(limit))
    if rc != 0:
        return []
    found = []
    for sha in [s for s in out.split("\n") if s.strip()][:limit]:
        rc2, diff, _ = _git(root, "show", "--format=", "--unified=0", sha)
        if rc2 != 0 or not diff:
            continue
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(diff):
                found.append({"where": "commit %s" % sha[:12], "class": name,
                              "remedy": "rotate the credential at its issuer",
                              "in_history": True})
                break
    return found


# ---------------------------------------------------------------------------
# findings, their identity, and the board's own arithmetic
# ---------------------------------------------------------------------------

def finding_id(probe_id, where, title):
    """Stable across a rewording, distinct across a place.

    An id derived from the free text makes every run report every finding as
    new, and a ratchet whose diff is always total is a snapshot with extra
    steps.
    """
    norm = re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()
    key = "|".join([probe_id or "", where or "", norm])
    return "f-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def priority(blast, age_runs, effort):
    """The board's formula, unchanged: `P = blast × (1 + age_runs) / effort`."""
    effort = effort or 1
    return round(float(blast) * (1 + float(age_runs)) / float(effort), 2)


def board_row(finding, board_id, source):
    """One line, pipes escaped, in the columns the board already has.

    A row that spans lines, or carries a bare pipe, shifts every later column —
    the family has already lost four ids and one status cell that way.
    """
    def cell(value):
        text = " ".join(str(value or "").split())
        return text.replace("|", r"\|")

    what = "**%s** %s" % (cell(finding.get("title")),
                          cell(finding.get("remedy")))
    return "| %s | %s | %s | %s | %s | %s | %s | open |" % (
        board_id, what, cell(source), finding.get("blast", 2),
        finding.get("runs_open", 0), finding.get("effort", 2),
        finding.get("p", priority(finding.get("blast", 2),
                                  finding.get("runs_open", 0),
                                  finding.get("effort", 2))))


# ---------------------------------------------------------------------------
# the ratchet
# ---------------------------------------------------------------------------

def _ids(payload):
    return [f.get("id") for f in (payload or {}).get("findings", []) if f.get("id")]


def ratchet(current, prior):
    """What moved. A first run says so rather than calling everything new."""
    now = set(_ids(current))
    if prior is None:
        return {"first_run": True, "closed": [], "new": [], "carried": [],
                "unranked": sorted(now)}
    before = set(_ids(prior))
    return {
        "first_run": False,
        "closed": sorted(before - now),
        "new": sorted(now - before),
        "carried": sorted(now & before),
        "unranked": [],
    }


def carry_forward(current, prior):
    """Age a surviving finding, and keep the date it was first seen.

    `runs_open` is the age term in the board's priority, so a row nobody picks
    up rises on its own. Without this, an audit's findings are all equally new
    forever and the ordering never learns anything.
    """
    prior_by_id = {f.get("id"): f for f in (prior or {}).get("findings", [])}
    for f in current.get("findings", []):
        old = prior_by_id.get(f.get("id"))
        if old:
            f["first_seen"] = old.get("first_seen", f.get("first_seen"))
            f["runs_open"] = int(old.get("runs_open", 0)) + 1
        else:
            f.setdefault("runs_open", 0)
        f["p"] = priority(f.get("blast", 2), f.get("runs_open", 0),
                          f.get("effort", 2))
    return current


def load_prior(out_dir, exclude=None):
    """The newest sidecar that is not this run's own."""
    if not os.path.isdir(out_dir):
        return None
    names = sorted(n for n in os.listdir(out_dir)
                   if n.endswith(".json") and n != (exclude or ""))
    for name in reversed(names):
        try:
            with open(os.path.join(out_dir, name), encoding="utf-8") as fh:
                payload = json.load(fh)
            if payload.get("schema") == SCHEMA:
                return payload
        except (ValueError, OSError):
            continue
    return None


# ---------------------------------------------------------------------------
# the page
# ---------------------------------------------------------------------------

STAMP_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:?\d{2})?")


def normalise_for_compare(body):
    """Everything a second run legitimately changes, removed.

    Standing instruction #2 asks for three real runs against a real tree; this
    is what makes their outputs comparable without making the comparison
    vacuous — only timestamps and the absolute root are erased.
    """
    body = STAMP_RE.sub("<STAMP>", body)
    body = re.sub(r"/(?:private/)?(?:tmp|var)/[^\s\"'<]+", "<PATH>", body)
    return body


CSS = """
:root{--bg:#fbfaf8;--surface:#fff;--surface-2:#f4f2ee;--ink:#1a1917;
--ink-soft:#5e5b55;--ink-faint:#8b8780;--line:#e2ded6;--line-2:#c9c4b8;
--ok:#0f7a4a;--ok-bg:#e8f5ee;--warn:#8a5a00;--warn-bg:#fdf3e0;
--bad:#a32a24;--bad-bg:#fdeceb;--info:#1f5c8f;--info-bg:#e9f1f8;--accent:#2a4d8f;
--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
--sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,system-ui,sans-serif}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
--bg:#16171a;--surface:#1d1f23;--surface-2:#23262b;--ink:#eceae6;
--ink-soft:#a8a49c;--ink-faint:#7c7871;--line:#2e3238;--line-2:#40454d;
--ok:#6fd39b;--ok-bg:#17332a;--warn:#e0a94a;--warn-bg:#33290f;
--bad:#f08a84;--bad-bg:#3a1c1a;--info:#8ec2ee;--info-bg:#15293a;--accent:#8fb4ee}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.62 var(--sans);
padding:0 0 5rem}
.wrap{max-width:58rem;margin:0 auto;padding:0 1.5rem}
header.top{border-bottom:1px solid var(--line);background:var(--surface);
padding:2.4rem 0 1.8rem;margin-bottom:2.2rem}
.kicker{font:600 .72rem/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;
color:var(--ink-faint);margin:0 0 .8rem}
h1{font-size:1.95rem;line-height:1.18;margin:0 0 .6rem;letter-spacing:-.02em;font-weight:640}
.lede{font-size:1.03rem;color:var(--ink-soft);margin:0;max-width:44rem}
h2{font-size:1.28rem;margin:2.8rem 0 .5rem;font-weight:640;padding-bottom:.4rem;
border-bottom:2px solid var(--line-2)}
h3{font-size:1rem;margin:1.6rem 0 .35rem;font-weight:650}
p{margin:.6rem 0}
code{font:.85em/1.45 var(--mono);background:var(--surface-2);padding:.1em .34em;
border-radius:4px;border:1px solid var(--line)}
pre{background:var(--surface-2);border:1px solid var(--line);border-radius:8px;
padding:.8rem 1rem;overflow-x:auto;font:.79rem/1.55 var(--mono);margin:.6rem 0}
pre code{background:none;border:none;padding:0}
.tw{overflow-x:auto;margin:.9rem 0;border:1px solid var(--line);border-radius:8px;
background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:.86rem}
th,td{padding:.48rem .7rem;text-align:left;border-bottom:1px solid var(--line);
vertical-align:top}
th{background:var(--surface-2);font-weight:650;font-size:.76rem;letter-spacing:.02em;
text-transform:uppercase;color:var(--ink-soft);white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
td.num,th.num{text-align:right;font-family:var(--mono);font-size:.81rem;white-space:nowrap}
td.mono{font-family:var(--mono);font-size:.79rem}
.pill{display:inline-block;font:600 .7rem/1.35 var(--mono);padding:.12rem .45rem;
border-radius:4px;white-space:nowrap}
.p-ok{background:var(--ok-bg);color:var(--ok)}
.p-warn{background:var(--warn-bg);color:var(--warn)}
.p-bad{background:var(--bad-bg);color:var(--bad)}
.p-info{background:var(--info-bg);color:var(--info)}
.p-neutral{background:var(--surface-2);color:var(--ink-faint)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(8rem,1fr));
gap:.7rem;margin:1.3rem 0}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:8px;
padding:.7rem .85rem}
.stat .v{font:650 1.35rem/1.1 var(--sans);letter-spacing:-.02em;display:block}
.stat .k{font:.69rem/1.3 var(--mono);color:var(--ink-faint);text-transform:uppercase;
letter-spacing:.05em}
.card{border:1px solid var(--line);border-left:3px solid var(--line-2);
background:var(--surface);border-radius:6px;padding:.9rem 1.1rem;margin:1rem 0}
.card.bad{border-left-color:var(--bad)}.card.warn{border-left-color:var(--warn)}
.card.info{border-left-color:var(--info)}.card.ok{border-left-color:var(--ok)}
.card h3{margin-top:0}
.meta{font:.73rem/1.4 var(--mono);color:var(--ink-faint);margin:.3rem 0 .5rem}
.note{font-size:.86rem;color:var(--ink-soft);border-left:2px solid var(--line-2);
padding-left:.8rem;margin:.8rem 0}
footer{margin-top:3.5rem;padding-top:1.3rem;border-top:1px solid var(--line);
font-size:.81rem;color:var(--ink-faint)}
@media (max-width:640px){h1{font-size:1.5rem}}
"""


def _e(value):
    return _html.escape(str(value if value is not None else ""), quote=True)


def _sev_pill(sev):
    cls = {"critical": "p-bad", "high": "p-bad", "medium": "p-warn",
           "low": "p-info"}.get(str(sev).lower(), "p-neutral")
    return '<span class="pill %s">%s</span>' % (cls, _e(sev))


def render_html(payload):
    """A self-contained page. No external request is reachable from it.

    Everything a probe could not do is rendered as loudly as everything it
    found — the *what was not looked at* table is not an appendix, because a
    page that hides its blind spots is read as a clean bill.
    """
    p = payload.get("profile", {}) or {}
    counts = payload.get("counts", {}) or {}
    rat = payload.get("ratchet", {}) or {}
    findings = payload.get("findings", []) or []
    probes = payload.get("probes", []) or []
    blind = [x for x in probes if x.get("verdict") == "blind"]

    out = []
    add = out.append
    add("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">")
    add('<meta name="viewport" content="width=device-width, initial-scale=1">')
    add("<title>Audit — %s</title>" % _e(p.get("name") or "project"))
    add("<style>%s</style>\n</head>\n<body>" % CSS)

    add('<header class="top"><div class="wrap">')
    add('<p class="kicker">project-audit · %s · read-only</p>'
        % _e(payload.get("generated_at", "")))
    add("<h1>%s</h1>" % _e(p.get("name") or "project"))
    add('<p class="lede">Every number below was produced by a command this run '
        'executed. What could not be measured is listed as such, never omitted '
        'and never counted as clean.</p>')
    add("</div></header>")

    add('<div class="wrap">')

    # --- headline -----------------------------------------------------------
    add('<div class="stats">')
    for value, key in (
        (counts.get("findings", len(findings)), "findings"),
        (counts.get("probes_run", 0), "probes run"),
        (counts.get("probes_blind", len(blind)), "blind"),
        (len(rat.get("closed", [])), "closed since last"),
        (len(rat.get("new", [])), "new"),
        (sum(1 for f in findings if int(f.get("runs_open", 0)) >= 3), "open 3+ runs"),
    ):
        add('<div class="stat"><span class="v">%s</span>'
            '<span class="k">%s</span></div>' % (_e(value), _e(key)))
    add("</div>")

    if rat.get("first_run"):
        add('<p class="note"><strong>First run.</strong> There is no earlier '
            'sidecar in this directory, so nothing is reported as closed or '
            'new — a diff against a run that never happened would be a claim '
            'about nothing. The next audit will have both columns.</p>')

    # --- what this project is ----------------------------------------------
    add("<h2>What this project is</h2>")
    add('<div class="tw"><table><tbody>')
    for label, value in (
        ("version", p.get("version") or "— (no manifest version)"),
        ("languages", ", ".join(p.get("languages") or []) or "—"),
        ("package managers", ", ".join(p.get("managers") or []) or "—"),
        ("monorepo", "yes" if p.get("monorepo") else "no"),
        ("submodules", len(p.get("submodules") or []) or "0"),
        ("CI", ", ".join(p.get("ci") or []) or "none configured"),
        ("deploy targets", ", ".join(p.get("deploy") or []) or "none declared"),
        ("error telemetry", ", ".join(p.get("telemetry") or [])
         or "none found in manifests"),
        ("tracked files", p.get("tracked_files", 0)),
    ):
        add("<tr><th>%s</th><td>%s</td></tr>" % (_e(label), _e(value)))
    add("</tbody></table></div>")

    # --- findings -----------------------------------------------------------
    add("<h2>Findings</h2>")
    if not findings:
        add('<p>No finding survived this run\'s probes. That is a statement '
            'about the probes that ran — read the next section before taking '
            'it as a clean bill.</p>')
    else:
        for f in sorted(findings, key=lambda x: -float(x.get("p", 0))):
            cls = {"critical": "bad", "high": "bad", "medium": "warn"}.get(
                str(f.get("severity", "")).lower(), "info")
            add('<div class="card %s">' % cls)
            add("<h3>%s %s</h3>" % (_sev_pill(f.get("severity", "info")),
                                    _e(f.get("title"))))
            age = int(f.get("runs_open", 0))
            add('<p class="meta">%s · P=%s · first seen %s%s</p>' % (
                _e(f.get("where") or "—"), _e(f.get("p", "—")),
                _e(f.get("first_seen") or "—"),
                (" · open %d runs" % age) if age else ""))
            if f.get("detail"):
                add("<p>%s</p>" % _e(f["detail"]))
            if f.get("evidence"):
                add("<pre><code>%s</code></pre>" % _e(f["evidence"]))
            if f.get("remedy"):
                add("<p><strong>Remedy.</strong> %s</p>" % _e(f["remedy"]))
            add("</div>")

    # --- the blind spots, deliberately not an appendix ----------------------
    add("<h2>What was not looked at</h2>")
    add('<p>A probe that could not run returns <code>blind</code>, never '
        '<code>clean</code>. An empty section here would mean every probe '
        'answered — not that nothing is wrong.</p>')
    if not blind:
        add('<p><span class="pill p-ok">every probe answered</span></p>')
    else:
        add('<div class="tw"><table><thead><tr><th>Probe</th><th>Phase</th>'
            "<th>Why not</th></tr></thead><tbody>")
        for b in blind:
            add("<tr><td class=\"mono\">%s</td><td>%s</td><td>%s</td></tr>"
                % (_e(b.get("id")), _e(b.get("phase")), _e(b.get("reason"))))
        add("</tbody></table></div>")

    # --- the ratchet --------------------------------------------------------
    if not rat.get("first_run"):
        add("<h2>What moved since the last audit</h2>")
        add('<div class="tw"><table><thead><tr><th>Movement</th>'
            '<th class="num">Count</th><th>Ids</th></tr></thead><tbody>')
        for label, key in (("closed", "closed"), ("new", "new"),
                           ("still open", "carried")):
            ids = rat.get(key, [])
            add('<tr><td>%s</td><td class="num">%d</td><td class="mono">%s</td></tr>'
                % (_e(label), len(ids), _e(", ".join(ids[:12]) or "—")))
        add("</tbody></table></div>")
        stale = [f for f in findings if int(f.get("runs_open", 0)) >= 3]
        if stale:
            add('<p class="note"><strong>%d finding(s) have survived three or '
                'more audits.</strong> That is itself the finding: a defect '
                'nobody picks up is a decision nobody wrote down.</p>'
                % len(stale))

    # --- probes ran ---------------------------------------------------------
    add("<h2>Probes</h2>")
    add('<div class="tw"><table><thead><tr><th>Probe</th><th>Phase</th>'
        "<th>Verdict</th><th>Note</th></tr></thead><tbody>")
    for x in probes:
        v = x.get("verdict", "")
        pill = {"clean": "p-ok", "finding": "p-bad",
                "blind": "p-neutral"}.get(v, "p-neutral")
        add('<tr><td class="mono">%s</td><td>%s</td>'
            '<td><span class="pill %s">%s</span></td><td>%s</td></tr>'
            % (_e(x.get("id")), _e(x.get("phase")), pill, _e(v),
               _e(x.get("reason") or "")))
    add("</tbody></table></div>")

    add("<footer><p>Generated by <code>project-audit</code> at %s against "
        "<code>%s</code>. Read-only: this run changed nothing but the two "
        "files it wrote. Sidecar: <code>%s</code>.</p></footer>"
        % (_e(payload.get("generated_at", "")), _e(payload.get("root", "")),
           _e(payload.get("sidecar", ""))))
    add("</div>\n</body>\n</html>")
    return "\n".join(out)


def open_in_browser(path, opener=None):
    """Best effort, and a miss never fails the run (REQ-10)."""
    candidates = [opener] if opener else (
        ["open"] if sys.platform == "darwin" else
        ["xdg-open"] if sys.platform.startswith("linux") else ["start"])
    for cmd in candidates:
        if not cmd:
            continue
        if shutil.which(cmd) is None:
            return False, "%s is not on PATH — open %s yourself" % (cmd, path)
        try:
            rc = subprocess.run([cmd, path], capture_output=True,
                                timeout=TIMEOUT).returncode
        except Exception as exc:                      # noqa: BLE001
            return False, "%s: %s" % (type(exc).__name__, exc)
        if rc == 0:
            return True, ""
        return False, "%s exited %d — open %s yourself" % (cmd, rc, path)
    return False, "no opener for this platform — open %s yourself" % path


# ---------------------------------------------------------------------------
# the probes that ship with the collector
# ---------------------------------------------------------------------------

def _finding(probe_id, where, title, severity, blast, effort, remedy,
             detail="", evidence=""):
    return {
        "id": finding_id(probe_id, where, title), "probe": probe_id,
        "title": title, "severity": severity, "where": where,
        "detail": detail, "evidence": evidence, "remedy": remedy,
        "blast": blast, "effort": effort, "runs_open": 0,
        "first_seen": datetime.date.today().isoformat(),
    }


@probe("secrets-tree", "probe", needs=("git",))
def _p_secrets_tree(ctx):
    rows = scan_secrets(ctx.root)
    if not rows:
        return Result("clean", "no credential pattern in the tracked tree")
    return Result("finding", "%d credential pattern(s)" % len(rows), findings=[
        _finding("secrets-tree", r["where"],
                 "A %s is committed in the tree" % r["class"],
                 "critical", 3, 1, r["remedy"]) for r in rows])


@probe("secrets-history", "probe", needs=("git",))
def _p_secrets_history(ctx):
    rows = scan_secret_history(ctx.root)
    if not rows:
        return Result("clean", "no credential pattern in the last 400 commits")
    return Result("finding", "%d in history" % len(rows), findings=[
        _finding("secrets-history", r["where"],
                 "A %s appears in git history" % r["class"],
                 "critical", 3, 2, r["remedy"]) for r in rows])


@probe("worktree", "probe", needs=("git",))
def _p_worktree(ctx):
    state = worktree_state(ctx.root, ignore=(ctx.out_rel,))
    if state.get("dirty") is None:
        return Result("blind", state.get("reason") or "cannot read git status")
    if not state["dirty"]:
        return Result("clean", "working tree clean")
    return Result("clean", "%d uncommitted path(s) — disclosed, not a finding: "
                           "an audit reports the committed project"
                           % len(state["paths"]))


@probe("telemetry", "prod", needs=())
def _p_telemetry(ctx):
    found = ctx.profile.get("telemetry") or []
    if found:
        return Result("clean", "declares %s" % ", ".join(found))
    langs = ctx.profile.get("languages") or []
    deploy = ctx.profile.get("deploy") or []
    if not deploy:
        return Result("clean", "no deploy target declared — a library or tool, "
                               "for which absent telemetry is a design, not a gap")
    return Result("finding", "no error reporting found", findings=[_finding(
        "telemetry", "manifests",
        "A deployed surface reports no errors anywhere its maintainer can see",
        "medium", 2, 2,
        "add an error reporter, or record the decision not to — the gap worth "
        "closing is that nobody wrote down which it is",
        detail="Deploy targets declared (%s) with no telemetry dependency in "
               "any manifest. A failure on a user's machine is invisible."
               % (", ".join(deploy) or "none"),
        evidence="languages=%s deploy=%s telemetry=[]"
                 % (",".join(langs), ",".join(deploy)))])


@probe("ci-present", "prod", needs=())
def _p_ci(ctx):
    if ctx.profile.get("ci"):
        return Result("clean", "CI configured: %s"
                               % ", ".join(ctx.profile["ci"]))
    return Result("finding", "no CI configuration", findings=[_finding(
        "ci-present", "repository root",
        "Nothing runs the checks except a person remembering to",
        "medium", 2, 2,
        "add a workflow that runs the project's own test command on push",
        evidence="no .github/workflows, .gitlab-ci.yml, Jenkinsfile or "
                 ".circleci/config.yml in the tracked tree")])


@probe("docs-present", "seams", needs=())
def _p_docs(ctx):
    docs = ctx.profile.get("docs") or []
    if "README.md" in docs:
        return Result("clean", "%d documentation marker(s): %s"
                               % (len(docs), ", ".join(docs)))
    return Result("finding", "no README", findings=[_finding(
        "docs-present", "repository root",
        "The project has no README, so its entry point is a person",
        "low", 1, 1, "write the four lines: what it is, how to run it, how to "
                     "test it, where the docs are")])


@probe("gitignore-secrets", "probe", needs=("git",))
def _p_gitignore(ctx):
    tracked = tracked_files(ctx.root)
    risky = [p for p in tracked
             if os.path.basename(p) in (".env", ".npmrc", ".pypirc",
                                        "id_rsa", "credentials")
             or p.endswith(".pem") or p.endswith(".p12")]
    if not risky:
        return Result("clean", "no credential-shaped file is tracked")
    return Result("finding", "%d tracked" % len(risky), findings=[_finding(
        "gitignore-secrets", p,
        "A file that normally holds credentials is tracked by git",
        "high", 3, 1,
        "move it out of the tree and add it to .gitignore; if it ever held a "
        "live value, rotate that value first") for p in risky])


def _tree_from_tag(root, ref, limit=4000):
    """`{path: content}` for a git ref, read through git rather than the disk."""
    rc, out, _ = _git(root, "ls-tree", "-r", "--name-only", ref)
    if rc != 0:
        return None
    tree = {}
    for rel in [x for x in out.split("\n") if x.strip()][:limit]:
        if os.path.splitext(rel)[1].lower() in SKIP_EXT:
            continue
        rc2, blob, _ = _git(root, "show", "%s:%s" % (ref, rel))
        if rc2 == 0:
            tree[rel] = blob
    return tree


def _tree_from_npm(name, version, workdir):
    """`{path: content}` for what the registry actually serves."""
    import tarfile
    import urllib.request
    spec = "%s@%s" % (name, version)
    try:
        p = subprocess.run(["npm", "view", spec, "dist.tarball"],
                           capture_output=True, text=True, timeout=TIMEOUT)
    except Exception:                                 # noqa: BLE001
        return None
    url = (p.stdout or "").strip().split("\n")[0]
    if p.returncode != 0 or not url.startswith("https://"):
        return None
    tgz = os.path.join(workdir, "pkg.tgz")
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            with open(tgz, "wb") as fh:
                shutil.copyfileobj(resp, fh, length=1 << 20)
        tree = {}
        with tarfile.open(tgz) as tar:
            for member in tar.getmembers():
                if not member.isfile() or member.size > 2_000_000:
                    continue
                rel = member.name.split("/", 1)[-1]   # strip the `package/` root
                if os.path.splitext(rel)[1].lower() in SKIP_EXT:
                    continue
                fh = tar.extractfile(member)
                if fh is None:
                    continue
                tree[rel] = fh.read().decode("utf-8", "replace")
        return tree
    except Exception:                                 # noqa: BLE001
        return None


@probe("channel-divergence", "prod", needs=("git",))
def _p_channels(ctx):
    """One version string, more than one tree — the class a pin check cannot see.

    **Which pair, and why not the obvious one.** The first draft compared the
    npm tarball against the git tag and reported `clean`. Those two agree by
    construction — npm publishes *from* the tag — so the answer was a tautology,
    and a tautology returning green is the `false success` shape `gates.md`
    names: a mechanism trusted by its own reply.

    The channels a consumer actually installs from disagree elsewhere. npm
    serves the **tag**; a plugin marketplace and a skills CLI serve the **branch
    tip**. Measured in this family on 2026-08-22: npm served `agent_sync.py` at
    4344 lines while the marketplace served 4575, and all three answered
    `1.15.0`. The check only means something when the two sides both claim the
    same version, so that is the precondition rather than the finding.
    """
    version = ctx.profile.get("version")
    name = ctx.profile.get("name")
    if not version:
        return Result("blind", "no version in a manifest to make a claim about")
    rc, _, _ = _git(ctx.root, "rev-parse", "--verify", "v%s^{}" % version)
    if rc != 0:
        return Result("blind", "HEAD says %s and no tag v%s exists — the "
                               "channels make no common claim yet"
                               % (version, version))

    channels = {"git-tag v%s" % version: _tree_from_tag(ctx.root, "v%s" % version),
                "branch tip (HEAD)": _tree_from_tag(ctx.root, "HEAD")}
    if {"npm", "network"} <= ctx.capabilities and name:
        import tempfile
        work = tempfile.mkdtemp(prefix="pa-channels-")
        try:
            channels["npm %s" % name] = _tree_from_npm(name, version, work)
        finally:
            shutil.rmtree(work, ignore_errors=True)

    verdict = compare_channels(version, channels)
    if verdict["diverged"] is None:
        return Result("blind", "fewer than two channels were readable: %s"
                               % ", ".join(verdict["blind"]))
    if not verdict["diverged"]:
        return Result("clean", "%d channel(s) claiming %s ship the same tree"
                               % (len(channels) - len(verdict["blind"]), version))

    paths = verdict["differing"]
    shown = ", ".join(paths[:5]) + (" …" if len(paths) > 5 else "")
    return Result("finding", "%d path(s) differ" % len(paths), findings=[_finding(
        "channel-divergence", "v%s" % version,
        "One version string, more than one tree",
        "critical", 3, 1,
        "tag the tree the channels should share — a patch release from the "
        "branch tip, or a revert of what landed after the tag; a version that "
        "identifies two artefacts cannot be reasoned about, and no version "
        "check comparing strings will ever say so",
        detail="%s all answer to %s and disagree on %d path(s). Anything that "
               "compares version STRINGS stays green through this."
               % (", ".join(sorted(verdict["channels"])), version, len(paths)),
        evidence="differing: %s" % shown)])


@probe("published-version", "prod", needs=("npm", "network"))
def _p_published(ctx):
    name = ctx.profile.get("name")
    version = ctx.profile.get("version")
    if not (name and version):
        return Result("blind", "no name+version in a manifest")
    try:
        p = subprocess.run(["npm", "view", name, "version"],
                           capture_output=True, text=True, timeout=TIMEOUT)
    except Exception as exc:                          # noqa: BLE001
        return Result("blind", "%s: %s" % (type(exc).__name__, exc))
    if classify_output(p.returncode, p.stdout, p.stderr) == "blind":
        return Result("blind", "npm view said nothing about %s — unpublished, "
                               "private, or the registry is unreachable" % name)
    latest = p.stdout.strip().split("\n")[0]
    if latest == version:
        return Result("clean", "the registry serves %s, the manifest says %s"
                               % (latest, version))
    return Result("finding", "registry %s vs manifest %s" % (latest, version),
                  findings=[_finding(
        "published-version", "package.json",
        "The registry and the manifest disagree about the current version",
        "high", 3, 1,
        "publish the manifest's version, or bring the manifest back to what "
        "shipped; a reader cannot tell which one is the product",
        evidence="npm view %s version -> %s; manifest -> %s"
                 % (name, latest, version))])


# ---------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------

def capabilities(root, offline):
    """What this machine can actually do, resolved once.

    A probe asks for a capability by name and never shells out to find out —
    that way the reason a probe was skipped is a fact the report can print.
    """
    caps = set()
    if is_repo(root):
        caps.add("git")
    for binary, name in (("gh", "gh"), ("npm", "npm"), ("python3", "python3"),
                         ("node", "node"), ("cargo", "cargo"), ("go", "go"),
                         ("docker", "docker")):
        if shutil.which(binary):
            caps.add(name)
    if not offline:
        caps.add("network")
    return caps


def collect(root, offline=False, out_rel=OUT_DIR):
    root = os.path.abspath(root)
    profile = discover(root)
    caps = capabilities(root, offline)
    ctx = Ctx(root=root, profile=profile, capabilities=caps, offline=offline,
              out_rel=out_rel)

    rows, findings = [], []
    for p in PROBES:
        result = run_probe(p, ctx)
        rows.append({"id": p.id, "phase": p.phase, "needs": list(p.needs),
                     "verdict": result.verdict, "reason": result.reason})
        findings.extend(result.findings)

    return {
        "schema": SCHEMA,
        "generated_at": datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "root": root,
        "profile": profile,
        "capabilities": sorted(caps),
        "probes": rows,
        "findings": findings,
        "counts": {
            "probes_run": sum(1 for r in rows if r["verdict"] != "blind"),
            "probes_blind": sum(1 for r in rows if r["verdict"] == "blind"),
            "findings": len(findings),
        },
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Collect a project audit and write two artefacts.")
    ap.add_argument("--root", default=".", help="project root (default: .)")
    ap.add_argument("--out", default=None,
                    help="output directory (default: <root>/docs/audit)")
    ap.add_argument("--no-open", action="store_true",
                    help="do not open the report in a browser")
    ap.add_argument("--offline", action="store_true",
                    help="skip every probe that needs the network")
    ap.add_argument("--json", action="store_true",
                    help="print the sidecar to stdout instead of a summary")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        sys.stderr.write("not a directory: %s\n" % root)
        return 1

    out_dir = args.out or os.path.join(root, OUT_DIR)
    out_rel = os.path.relpath(out_dir, root)
    payload = collect(root, offline=args.offline, out_rel=out_rel)

    day = payload["generated_at"][:10]
    base = "%s-audit" % day
    os.makedirs(out_dir, exist_ok=True)
    prior = load_prior(out_dir, exclude=base + ".json")
    payload = carry_forward(payload, prior)
    payload["ratchet"] = ratchet(payload, prior)
    payload["sidecar"] = os.path.join(out_dir, base + ".json")

    json_path = os.path.join(out_dir, base + ".json")
    html_path = os.path.join(out_dir, base + ".html")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(render_html(payload))

    if args.json:
        print(json.dumps(payload, indent=1, ensure_ascii=False))
    else:
        c = payload["counts"]
        r = payload["ratchet"]
        print("project-audit %s — %d finding(s), %d probe(s) ran, %d blind"
              % (payload["profile"].get("name"), c["findings"],
                 c["probes_run"], c["probes_blind"]))
        if r["first_run"]:
            print("  first run in %s — no earlier sidecar to compare against"
                  % out_dir)
        else:
            print("  closed %d · new %d · still open %d"
                  % (len(r["closed"]), len(r["new"]), len(r["carried"])))
        print("  %s\n  %s" % (html_path, json_path))

    if not args.no_open:
        ok, note = open_in_browser(html_path)
        if not ok:
            sys.stderr.write("could not open the report: %s\n" % note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
