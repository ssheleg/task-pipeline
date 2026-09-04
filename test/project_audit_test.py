#!/usr/bin/env python3
"""`project-audit`'s collector, exercised against planted defects.

Every check here was watched failing before the code existed, which is the only
thing that makes a green one evidence (`references/tdd.md`).

**Why the fixtures build whole trees rather than mocking.** REQ-01 is the claim
that discovery *distinguishes* projects, and a mock returns whatever it was told
to. Standing instruction #4 — *a measurement that returns the same answer for
every input is a broken measurement* — is exactly the failure a mocked discovery
cannot detect, so the three trees are real directories with real manifests.

**Why `git init` and not a bare directory.** Standing instruction #10 — *a check
that reads a working tree reports a state no clone can reproduce*. The probes
read committed state, so a fixture with no commit would exercise the fallback
instead of the rule.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(
    ROOT, "plugins/task-pipeline/skills/project-audit/scripts/audit.py")

sys.path.insert(0, os.path.dirname(SCRIPT))
import audit  # noqa: E402  (the subject; the path above is how a bundled script is reached)


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------

def git(tree, *args):
    return subprocess.run(["git", "-C", tree] + list(args),
                          capture_output=True, text=True)


def commit_all(tree, message="fixture"):
    git(tree, "add", "-A")
    git(tree, "-c", "user.email=t@t", "-c", "user.name=t",
        "commit", "-q", "-m", message)


def write(tree, rel, body):
    path = os.path.join(tree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


def make_tree(kind):
    """Three deliberately different projects. Returns the directory."""
    tree = tempfile.mkdtemp(prefix="pa-fixture-")
    git(tree, "init", "-q", "-b", "main")
    if kind == "node-mono":
        write(tree, "package.json", json.dumps({
            "name": "fixture-mono", "version": "1.2.3", "private": True,
            "workspaces": ["packages/*"],
            "scripts": {"test": "node test/run.js"},
        }))
        write(tree, "package-lock.json", '{"lockfileVersion":3}')
        write(tree, "packages/a/package.json", '{"name":"a","version":"1.2.3"}')
        write(tree, "packages/b/package.json", '{"name":"b","version":"1.2.3"}')
        write(tree, ".github/workflows/ci.yml", "name: ci\non: [push]\n")
        write(tree, "Dockerfile", "FROM node:20\n")
        write(tree, "README.md", "# fixture-mono\n")
    elif kind == "python-single":
        write(tree, "pyproject.toml",
              '[project]\nname = "fixture-py"\nversion = "0.4.0"\n')
        write(tree, "src/fixture_py/__init__.py", "VERSION = '0.4.0'\n")
        write(tree, "tests/test_smoke.py", "def test_ok():\n    assert True\n")
        write(tree, "README.md", "# fixture-py\n")
    elif kind == "go-no-ci":
        write(tree, "go.mod", "module example.com/fixture\n\ngo 1.22\n")
        write(tree, "main.go", "package main\n\nfunc main() {}\n")
    else:
        raise ValueError(kind)
    commit_all(tree)
    return tree


class Fixtures(unittest.TestCase):
    trees = {}

    @classmethod
    def setUpClass(cls):
        for kind in ("node-mono", "python-single", "go-no-ci"):
            cls.trees[kind] = make_tree(kind)

    @classmethod
    def tearDownClass(cls):
        for tree in cls.trees.values():
            shutil.rmtree(tree, ignore_errors=True)
        cls.trees.clear()


# --------------------------------------------------------------------------
# REQ-01 — discovery distinguishes, and instruction #4 is the reason
# --------------------------------------------------------------------------

class TestDiscovery(Fixtures):

    def test_three_trees_give_three_different_profiles(self):
        profiles = {k: audit.discover(t) for k, t in self.trees.items()}
        fingerprints = {k: json.dumps(_comparable(p), sort_keys=True)
                        for k, p in profiles.items()}
        self.assertEqual(
            len(set(fingerprints.values())), 3,
            "discovery returned the same answer for different projects — "
            "standing instruction #4: that is a fact about the instrument")

    def test_languages_and_managers_are_named(self):
        node = audit.discover(self.trees["node-mono"])
        self.assertIn("javascript", node["languages"])
        self.assertIn("npm", node["managers"])
        py = audit.discover(self.trees["python-single"])
        self.assertIn("python", py["languages"])
        go = audit.discover(self.trees["go-no-ci"])
        self.assertIn("go", go["languages"])

    def test_monorepo_is_detected_only_where_it_is_one(self):
        self.assertTrue(audit.discover(self.trees["node-mono"])["monorepo"])
        self.assertFalse(audit.discover(self.trees["python-single"])["monorepo"])

    def test_ci_absence_is_recorded_as_absence_not_omitted(self):
        go = audit.discover(self.trees["go-no-ci"])
        self.assertIn("ci", go)
        self.assertEqual(go["ci"], [],
                         "a project with no CI must say so, not leave the key out")

    def test_version_is_read_from_the_manifest_the_project_actually_uses(self):
        self.assertEqual(
            audit.discover(self.trees["node-mono"])["version"], "1.2.3")
        self.assertEqual(
            audit.discover(self.trees["python-single"])["version"], "0.4.0")


def _comparable(profile):
    """Everything but the absolute path — two trees differ trivially by tmpdir."""
    return {k: v for k, v in profile.items() if k not in ("root", "name")}


# --------------------------------------------------------------------------
# REQ-05 — committed state is the subject; the working tree is disclosed
# --------------------------------------------------------------------------

class TestCommittedState(Fixtures):

    def test_an_ignored_artefact_is_not_a_finding(self):
        """Yesterday's audit defect (7): the standard-keeper read the working
        tree and reported three clean repositories as having nested bundles."""
        tree = self.trees["python-single"]
        write(tree, ".gitignore", "__pycache__/\n")
        commit_all(tree, "ignore pycache")
        os.makedirs(os.path.join(tree, "src/fixture_py/__pycache__"),
                    exist_ok=True)
        write(tree, "src/fixture_py/__pycache__/x.pyc", "not-really")
        tracked = audit.tracked_files(tree)
        self.assertFalse(
            any("__pycache__" in p for p in tracked),
            "an ignored path reached the tracked set — the audit would report "
            "a defect no clone can reproduce (standing instruction #10)")

    def test_the_audits_own_output_is_not_part_of_its_reading(self):
        """Found by the three-run fixture: run 1 saw a clean tree, run 2 saw
        `docs/audit/` — its own artefacts — and called the tree dirty. An
        instrument that perturbs its subject reports the perturbation."""
        tree = self.trees["node-mono"]
        os.makedirs(os.path.join(tree, "docs/audit"), exist_ok=True)
        write(tree, "docs/audit/2026-01-01-audit.html", "<html></html>")
        write(tree, "docs/audit/2026-01-01-audit.json", "{}")
        state = audit.worktree_state(tree, ignore=("docs/audit",))
        self.assertFalse(
            any("docs/audit" in p for p in state["paths"]),
            "the audit read its own output as project state")
        shutil.rmtree(os.path.join(tree, "docs/audit"), ignore_errors=True)

    def test_an_excluded_directory_does_not_hide_its_siblings(self):
        """The over-broad fix for the line above: matching either way round
        would drop `docs/anything-else` with `docs/audit`, and the audit would
        stop seeing new project files entirely."""
        tree = self.trees["node-mono"]
        os.makedirs(os.path.join(tree, "docs/audit"), exist_ok=True)
        write(tree, "docs/audit/2026-01-01-audit.json", "{}")
        write(tree, "docs/a-real-new-doc.md", "# real\n")
        state = audit.worktree_state(tree, ignore=("docs/audit",))
        self.assertTrue(any("a-real-new-doc" in p for p in state["paths"]),
                        "excluding docs/audit also hid a sibling under docs/")
        self.assertFalse(any("docs/audit" in p for p in state["paths"]))
        shutil.rmtree(os.path.join(tree, "docs"), ignore_errors=True)

    def test_the_working_tree_disagreement_is_disclosed_not_dropped(self):
        tree = self.trees["go-no-ci"]
        write(tree, "uncommitted.go", "package main\n")
        state = audit.worktree_state(tree)
        self.assertTrue(state["dirty"])
        self.assertIn("uncommitted.go", " ".join(state["paths"]))
        os.remove(os.path.join(tree, "uncommitted.go"))


# --------------------------------------------------------------------------
# REQ-02 / REQ-03 — the registry, and blind as a third value
# --------------------------------------------------------------------------

class TestRegistry(unittest.TestCase):

    def test_every_registered_probe_declares_its_needs_and_phase(self):
        self.assertTrue(audit.PROBES, "the registry is empty")
        for p in audit.PROBES:
            self.assertIn(p.phase, audit.PHASES, f"{p.id}: unknown phase")
            self.assertIsInstance(p.needs, tuple, f"{p.id}: needs is not a tuple")

    def test_probe_ids_are_unique(self):
        ids = [p.id for p in audit.PROBES]
        self.assertEqual(len(ids), len(set(ids)), "duplicate probe id")

    def test_an_unmet_need_is_blind_with_a_reason_never_clean(self):
        ctx = audit.Ctx(root=os.getcwd(), profile={}, capabilities=set())
        result = audit.run_probe(
            audit.Probe(id="fixture-needs", phase="probe",
                        needs=("a-capability-nothing-has",),
                        run=lambda c: audit.Result("clean", "should not run")),
            ctx)
        self.assertEqual(result.verdict, "blind")
        self.assertIn("a-capability-nothing-has", result.reason)

    def test_a_probe_that_raises_is_blind_and_the_run_continues(self):
        def boom(_ctx):
            raise RuntimeError("planted")
        ctx = audit.Ctx(root=os.getcwd(), profile={}, capabilities=set())
        result = audit.run_probe(
            audit.Probe(id="fixture-raises", phase="probe", needs=(), run=boom),
            ctx)
        self.assertEqual(result.verdict, "blind")
        self.assertIn("RuntimeError", result.reason)
        self.assertIn("planted", result.reason)

    def test_verdict_vocabulary_is_closed(self):
        self.assertEqual(audit.VERDICTS, ("clean", "finding", "blind"))
        with self.assertRaises(ValueError):
            audit.Result("maybe", "a fourth verdict must be refused")

    def test_an_empty_command_output_is_blind_not_clean(self):
        """`silence is not a reading`, raised from a command to a probe."""
        got = audit.classify_output(returncode=127, out="", err="not found")
        self.assertEqual(got, "blind")
        got = audit.classify_output(returncode=0, out="", err="")
        self.assertEqual(got, "blind",
                         "a zero exit with no output has not answered")
        got = audit.classify_output(returncode=0, out="something", err="")
        self.assertEqual(got, "read")


# --------------------------------------------------------------------------
# REQ-04 — one version, two trees
# --------------------------------------------------------------------------

class TestChannelDivergence(unittest.TestCase):

    def test_same_version_different_trees_is_a_finding(self):
        a = {"agent_sync.py": "x" * 100}
        b = {"agent_sync.py": "x" * 120}
        got = audit.compare_channels("1.15.0", {"npm": a, "git-tag": b})
        self.assertEqual(got["diverged"], True)
        self.assertIn("agent_sync.py", got["differing"])

    def test_identical_trees_are_silent(self):
        a = {"f": "same"}
        got = audit.compare_channels("1.0.0", {"npm": a, "git-tag": dict(a)})
        self.assertEqual(got["diverged"], False)
        self.assertEqual(got["differing"], [])

    def test_a_version_string_match_alone_never_satisfies_the_check(self):
        """`check_pins.py` was green through yesterday's defect because it
        compared the string. Comparing strings must not be reachable here."""
        source = open(SCRIPT, encoding="utf-8").read()
        fn = _function_source(source, "compare_channels")
        self.assertNotIn("version ==", fn,
                         "compare_channels decided on a version string")

    def test_a_path_in_one_channel_only_is_packaging_not_divergence(self):
        """An npm tarball ships what `files` allows. Counting `.github/` as a
        divergence is the false-positive class this skill exists to catch, and
        the first draft of this function produced 22 of them on one member."""
        got = audit.compare_channels("1.0.0", {
            "npm": {"lib/a.js": "same"},
            "git-tag": {"lib/a.js": "same", ".github/workflows/ci.yml": "x"},
        })
        self.assertFalse(got["diverged"],
                         "a file absent from a tarball by design read as a "
                         "version disagreement")
        self.assertIn(".github/workflows/ci.yml", got["only_in"]["npm"])

    def test_a_shared_path_that_differs_is_still_divergence(self):
        got = audit.compare_channels("1.0.0", {
            "npm": {"lib/a.js": "one", ".gitignore": "x"},
            "git-tag": {"lib/a.js": "two"},
        })
        self.assertTrue(got["diverged"])
        self.assertEqual(got["differing"], ["lib/a.js"])

    def test_a_channel_that_could_not_be_fetched_is_blind_not_equal(self):
        got = audit.compare_channels("1.0.0", {"npm": None, "git-tag": {"f": "x"}})
        self.assertEqual(got["diverged"], None)
        self.assertIn("npm", got["blind"])


# --------------------------------------------------------------------------
# REQ-09 — a secret's place, never its value
# --------------------------------------------------------------------------

class TestSecrets(Fixtures):

    PLANT = "npm_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"

    def setUp(self):
        """Each test plants its own. A fixture shared through alphabetical
        method order is a test that passes because of its own name."""
        tree = self.trees["node-mono"]
        write(tree, ".npmrc", "//registry.npmjs.org/:_authToken=%s\n" % self.PLANT)
        commit_all(tree, "plant")

    def test_a_planted_token_is_found(self):
        tree = self.trees["node-mono"]
        findings = audit.scan_secrets(tree)
        self.assertTrue(findings, "the planted token was not found")
        self.assertTrue(any(".npmrc" in f["where"] for f in findings))
        self.assertTrue(any("npm" in f["class"].lower() for f in findings))

    def test_the_value_appears_in_no_artefact(self):
        tree = self.trees["node-mono"]
        findings = audit.scan_secrets(tree)
        blob = json.dumps(findings)
        self.assertNotIn(self.PLANT, blob,
                         "the finding carried the secret — the report becomes "
                         "the second place it leaks")
        self.assertNotIn(self.PLANT[8:], blob, "a suffix of the value survived")

    def test_the_redaction_still_says_which_secret_it_was(self):
        tree = self.trees["node-mono"]
        f = audit.scan_secrets(tree)[0]
        self.assertIn("class", f)
        self.assertIn("where", f)
        self.assertIn("remedy", f)
        self.assertTrue(f["remedy"], "a refusal with no next step")


# --------------------------------------------------------------------------
# REQ-07 — the sidecar, and the diff that makes it a ratchet
# --------------------------------------------------------------------------

class TestRatchet(unittest.TestCase):

    def _payload(self, ids, run_no):
        return {
            "schema": audit.SCHEMA,
            "generated_at": "2026-08-%02dT00:00:00Z" % (20 + run_no),
            "findings": [{"id": i, "title": i, "severity": "medium",
                          "first_seen": "2026-08-20", "runs_open": 1}
                         for i in ids],
        }

    def test_a_stable_id_survives_a_reworded_title(self):
        a = audit.finding_id("probe-x", "lib/a.js:12", "The thing is broken")
        b = audit.finding_id("probe-x", "lib/a.js:12", "the thing  is BROKEN.")
        self.assertEqual(a, b, "an id that moves on rewording makes every run "
                               "report everything as new")

    def test_a_different_place_is_a_different_finding(self):
        a = audit.finding_id("probe-x", "lib/a.js:12", "t")
        b = audit.finding_id("probe-x", "lib/b.js:12", "t")
        self.assertNotEqual(a, b)

    def test_the_diff_names_closed_new_and_stale(self):
        prior = self._payload(["keep", "gone"], 0)
        current = self._payload(["keep", "fresh"], 1)
        d = audit.ratchet(current, prior)
        self.assertEqual(d["closed"], ["gone"])
        self.assertEqual(d["new"], ["fresh"])
        self.assertEqual(d["carried"], ["keep"])

    def test_a_first_run_says_so_rather_than_reporting_zeros(self):
        d = audit.ratchet(self._payload(["a"], 0), None)
        self.assertTrue(d["first_run"])
        self.assertEqual(d["closed"], [])
        self.assertEqual(d["new"], [],
                         "a first run has nothing to compare; calling every "
                         "finding new is a claim about a run that never ran")

    def test_a_carried_finding_accumulates_runs_open(self):
        prior = {"schema": audit.SCHEMA, "generated_at": "2026-08-20T00:00:00Z",
                 "findings": [{"id": "keep", "title": "k", "severity": "medium",
                               "first_seen": "2026-08-20", "runs_open": 3}]}
        current = self._payload(["keep"], 1)
        merged = audit.carry_forward(current, prior)
        row = [f for f in merged["findings"] if f["id"] == "keep"][0]
        self.assertEqual(row["runs_open"], 4)
        self.assertEqual(row["first_seen"], "2026-08-20")

    def test_the_sidecar_declares_its_schema(self):
        self.assertEqual(audit.SCHEMA, "project-audit/1")


# --------------------------------------------------------------------------
# REQ-06 / REQ-10 — the page, and the open that must not take the run down
# --------------------------------------------------------------------------

class TestReport(unittest.TestCase):

    def _page(self):
        payload = {
            "schema": audit.SCHEMA,
            "generated_at": "2026-08-23T00:00:00Z",
            "root": "/tmp/x", "profile": {"name": "x", "languages": ["python"],
                                          "managers": [], "ci": [], "monorepo": False,
                                          "version": "1.0.0"},
            "probes": [{"id": "p1", "phase": "probe", "verdict": "blind",
                        "reason": "gh is not installed", "needs": ["gh"]}],
            "findings": [{"id": "f1", "title": "A thing <b>&</b> another",
                          "severity": "high", "where": "a.py:1",
                          "evidence": "cmd", "remedy": "do x",
                          "blast": 3, "effort": 1, "p": 3.0,
                          "first_seen": "2026-08-23", "runs_open": 1}],
            "counts": {"probes_run": 1, "probes_blind": 1, "findings": 1},
            "ratchet": {"first_run": True, "closed": [], "new": [], "carried": []},
        }
        return audit.render_html(payload), payload

    def test_the_page_makes_no_external_request(self):
        page, _ = self._page()
        for pattern in (r'src\s*=\s*["\']https?://', r'href\s*=\s*["\']https?://[^"\']+\.css',
                        r'@import\s+url\(', r'fonts\.googleapis'):
            self.assertIsNone(re.search(pattern, page),
                              f"the page reaches outward: {pattern}")

    def test_the_page_carries_both_themes(self):
        page, _ = self._page()
        self.assertIn("prefers-color-scheme: dark", page)
        self.assertIn(":root", page)

    def test_finding_text_is_escaped(self):
        page, _ = self._page()
        self.assertIn("&lt;b&gt;", page, "a finding's text was injected as markup")

    def test_a_blind_probe_is_visible_on_the_page_with_its_reason(self):
        page, _ = self._page()
        self.assertIn("gh is not installed", page,
                      "the page hid what was not looked at, which is how "
                      "absence reads as clean")

    def test_a_first_run_page_says_first_run(self):
        page, _ = self._page()
        self.assertRegex(page, r"(?i)first run|перв")

    def test_open_failure_warns_and_does_not_fail_the_run(self):
        ok, note = audit.open_in_browser("/nonexistent/path/report.html",
                                         opener="definitely-not-a-real-opener")
        self.assertFalse(ok)
        self.assertTrue(note)


# --------------------------------------------------------------------------
# REQ-08 — findings leave as board rows in the project's own vocabulary
# --------------------------------------------------------------------------

class TestBoardRows(unittest.TestCase):

    def test_priority_uses_the_projects_formula(self):
        self.assertAlmostEqual(audit.priority(blast=3, age_runs=0, effort=1), 3.0)
        # The board prints B-29 (blast 2, age 3, effort 3) as **2.67**, so two
        # places is the project's contract, not a convenience.
        self.assertEqual(audit.priority(blast=2, age_runs=3, effort=3), 2.67)
        self.assertEqual(round(2 * 4 / 3, 2), audit.priority(2, 3, 3),
                         "the rounding is the board's, not a second rule")

    def test_the_age_term_is_not_a_constant(self):
        """The umbrella board ranked newest-first for eleven days because the
        age term was a constant. A formula that ignores an input is #4."""
        self.assertNotEqual(audit.priority(2, 0, 2), audit.priority(2, 5, 2))

    def test_a_row_is_a_single_line_with_escaped_pipes(self):
        row = audit.board_row({
            "id": "f1", "title": "A pipe | inside", "where": "a.py:1",
            "evidence": "cmd", "remedy": "do x", "blast": 3, "effort": 1,
            "p": 3.0, "runs_open": 0,
        }, board_id="B-200", source="project-audit 2026-08-23")
        self.assertEqual(row.count("\n"), 0, "a row that spans lines breaks the board")
        self.assertIn("B-200", row)
        self.assertNotIn("A pipe | inside", row)
        self.assertIn(r"\|", row, "an unescaped pipe shifts every later column")

    def test_no_new_severity_vocabulary_is_invented(self):
        source = open(SCRIPT, encoding="utf-8").read()
        self.assertIn("blast", source)
        self.assertNotIn("SEVERITY_WEIGHTS", source,
                         "a second scale beside the board's formula")


# --------------------------------------------------------------------------
# REQ-11 — idempotence at the layer that repeats (standing instruction #2)
# --------------------------------------------------------------------------

class TestIdempotence(Fixtures):

    def test_three_runs_agree_once_the_stamp_is_normalised(self):
        tree = self.trees["python-single"]
        hashes = []
        for _ in range(3):
            # `--report`, because the page is opt-in now and this test is about
            # the page being byte-stable across runs — the property still holds
            # and the flag is what produces the subject.
            proc = subprocess.run(
                [sys.executable, SCRIPT, "--root", tree, "--report", "--no-open",
                 "--offline"],
                capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr[-800:])
            page = os.path.join(tree, "docs/audit")
            newest = sorted(f for f in os.listdir(page) if f.endswith(".html"))[-1]
            body = open(os.path.join(page, newest), encoding="utf-8").read()
            hashes.append(hashlib.sha256(
                audit.normalise_for_compare(body).encode()).hexdigest())
        self.assertEqual(len(set(hashes)), 1,
                         "three runs against one tree produced three pages; "
                         "standing instruction #2 is about this layer")
        shutil.rmtree(os.path.join(tree, "docs/audit"), ignore_errors=True)

    def test_a_plain_run_writes_the_sidecar_and_no_page(self):
        """A report is an artefact that outlives the conversation, so it is asked for.

        The sidecar is NOT optional: `carry_forward` reads the previous one, so
        skipping it would silently turn every future run into a first run. The page
        is what nobody ordered — untracked HTML under `docs/`, one `git add -A` from
        the product's history.
        """
        tree = self.trees["go-no-ci"]
        proc = subprocess.run([sys.executable, SCRIPT, "--root", tree, "--offline"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr[-800:])
        out = os.path.join(tree, "docs/audit")
        names = sorted(os.listdir(out))
        self.assertEqual([n for n in names if n.endswith(".html")], [],
                         f"a page was written without --report: {names}")
        self.assertTrue(any(n.endswith(".json") for n in names),
                        f"the sidecar is not optional and is missing: {names}")
        self.assertIn("no page written", proc.stdout,
                      "the run did not say the page was skipped, so its absence "
                      "reads as a failure to write one")
        shutil.rmtree(out, ignore_errors=True)

    def test_report_writes_both_artefacts(self):
        tree = self.trees["go-no-ci"]
        subprocess.run([sys.executable, SCRIPT, "--root", tree, "--report",
                        "--no-open", "--offline"], capture_output=True, text=True)
        out = os.path.join(tree, "docs/audit")
        names = sorted(os.listdir(out))
        self.assertEqual(len(names), 2, f"expected html+json, got {names}")
        self.assertTrue(any(n.endswith(".html") for n in names))
        self.assertTrue(any(n.endswith(".json") for n in names))
        shutil.rmtree(out, ignore_errors=True)

    def test_a_homegrown_error_channel_is_not_reported_as_absent(self):
        """The probe read manifests and asserted about the product. (#83)

        A project with a working home-grown error channel and no SDK dependency was
        reported as `no error reporting found` — an assertion about the product made
        from evidence about the manifest. The verdicts differ by the KIND of
        evidence: code or schema is clean, a document alone cannot establish that
        the channel works OR that it is absent.
        """
        tree = tempfile.mkdtemp(prefix="pa-homegrown-")
        self.addCleanup(shutil.rmtree, tree, True)
        subprocess.run(["git", "init", "-q", tree], capture_output=True)
        with open(os.path.join(tree, "package.json"), "w", encoding="utf-8") as fh:
            fh.write('{"name":"p","version":"1.0.0","dependencies":{}}\n')
        os.makedirs(os.path.join(tree, "src"), exist_ok=True)
        # No dependency names a telemetry SDK; the capability is a module.
        with open(os.path.join(tree, "src", "error-reporter.js"), "w",
                  encoding="utf-8") as fh:
            fh.write("export function report(e) { /* our own channel */ }\n")
        with open(os.path.join(tree, "Dockerfile"), "w", encoding="utf-8") as fh:
            fh.write("FROM node:20\n")
        subprocess.run(["git", "add", "-A"], cwd=tree, capture_output=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "x"], cwd=tree, capture_output=True)
        proc = subprocess.run([sys.executable, SCRIPT, "--root", tree, "--offline",
                               "--json"], capture_output=True, text=True)
        payload = json.loads(proc.stdout)
        tele = [p for p in payload["probes"] if p["id"] == "telemetry"]
        self.assertTrue(tele, "the telemetry probe did not run")
        self.assertNotEqual(
            tele[0]["verdict"], "finding",
            "a module named for an error channel was still reported as no error "
            "reporting — the manifest was the wrong place to look")
        self.assertIn("error-reporter", tele[0].get("reason", ""),
                      "the verdict does not name the evidence it found")

    def test_the_sidecar_validates_against_its_own_schema_claim(self):
        tree = self.trees["go-no-ci"]
        subprocess.run([sys.executable, SCRIPT, "--root", tree, "--no-open",
                        "--offline"], capture_output=True, text=True)
        out = os.path.join(tree, "docs/audit")
        js = [n for n in os.listdir(out) if n.endswith(".json")][0]
        payload = json.load(open(os.path.join(out, js), encoding="utf-8"))
        for key in ("schema", "generated_at", "root", "profile", "probes",
                    "findings", "counts", "ratchet"):
            self.assertIn(key, payload, f"sidecar is missing {key}")
        self.assertEqual(payload["schema"], audit.SCHEMA)
        shutil.rmtree(out, ignore_errors=True)


# --------------------------------------------------------------------------
# the self-test: every check above must have been watched failing
# --------------------------------------------------------------------------

def _function_source(source, name):
    m = re.search(r"^def %s\(.*?(?=^def |\Z)" % re.escape(name),
                  source, re.S | re.M)
    if not m:
        raise AssertionError("no function %s in %s" % (name, SCRIPT))
    return m.group(0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
