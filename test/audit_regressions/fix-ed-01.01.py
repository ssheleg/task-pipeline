#!/usr/bin/env python3
"""FIX-ED-01.01 — the single-skill dependency closure (sherlock audit, ED-01).

Generation is a deterministic transform, not a byte copy: links inside the
copied set stay relative, links outside it point at the source home's
canonical URL — copying the transitive closure would have pulled in the whole
neighbouring skill (measured: 38 of 38 references).

The finding: an isolated copy of evidence-docs carried 11 broken links —
every required reference lived in the NEIGHBOURING skill's directory, so the
skill resolved only when the whole plugin travelled together.

The fix under test:
* evidence-docs carries its required references/templates INSIDE its own
  directory; the source home stays skills/task-pipeline/ and the local files
  are GENERATED copies (byte-equal, checked here);
* SKILL.md links resolve inside the directory — zero ../ escapes;
* an isolated copy of the directory resolves every link (simulated by
  copying it alone into a temp dir);
* --sync regenerates the copies from the source home.

Standard library only.
"""
import os
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SKILLS = os.path.join(ROOT, "plugins", "task-pipeline", "skills")
ED = os.path.join(SKILLS, "evidence-docs")
TP = os.path.join(SKILLS, "task-pipeline")

REFS = ["documentation.md", "learned.md", "gates.md", "hooks.md",
        "setup.md", "retrospective.md"]
TPLS = ["decisions.md", "docgate.sh"]


HOME_URL = ("https://github.com/ssheleg/task-pipeline/blob/main/"
            "plugins/task-pipeline/skills/task-pipeline/")
_LINK = re.compile(r"\]\((?!https?://)([^)#]+?)((?:#[^)]*)?)\)")


def generate(src_text, kind):
    """The deterministic single-skill edition of a source-home file.

    Links to files INSIDE the copied set stay relative (they resolve in the
    isolated directory); links outside it are rewritten to the source home's
    canonical URL — resolvable from anywhere, so the closure stays 8 files
    instead of the whole neighbouring skill.
    """
    local_refs = set(REFS)
    local_tpls = set(TPLS)

    def rewrite(m):
        target, anchor = m.group(1), m.group(2)
        plain = target.lstrip("./")
        if kind == "ref":
            if plain in local_refs:
                return f"]({plain}{anchor})"
            if plain.startswith("templates/") and plain.split("/", 1)[1] in local_tpls:
                return f"](../{plain}{anchor})"
            if plain.startswith("../templates/") and plain.split("/", 2)[2] in local_tpls:
                return f"]({plain}{anchor})"
            base = "references/" if "/" not in plain else ""
            return f"]({HOME_URL}{base}{plain.replace('../', '')}{anchor})"
        # template kind: sh/json/md seeds carry no md links worth rewriting
        return m.group(0)

    return _LINK.sub(rewrite, src_text)


def sync():
    os.makedirs(os.path.join(ED, "references"), exist_ok=True)
    os.makedirs(os.path.join(ED, "templates"), exist_ok=True)
    for f in REFS:
        src = open(os.path.join(TP, "references", f), encoding="utf-8").read()
        with open(os.path.join(ED, "references", f), "w", encoding="utf-8") as fh:
            fh.write(generate(src, "ref"))
    for f in TPLS:
        shutil.copy(os.path.join(TP, "templates", f),
                    os.path.join(ED, "templates", f))
    print(f"generated {len(REFS)} references + {len(TPLS)} templates from the source home")


failures = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def t_no_escaping_links():
    t = read(os.path.join(ED, "SKILL.md"))
    escapes = re.findall(r"\]\((\.\./[^)]*)\)", t)
    assert escapes == [], f"links escape the directory: {escapes}"


def t_copies_match_source_home():
    for f in REFS:
        src = generate(read(os.path.join(TP, "references", f)), "ref")
        cp = read(os.path.join(ED, "references", f))
        assert src == cp, f"references/{f} drifted from the source home — re-run --sync"
    for f in TPLS:
        src = read(os.path.join(TP, "templates", f))
        cp = read(os.path.join(ED, "templates", f))
        assert src == cp, f"templates/{f} drifted from the source home — re-run --sync"


def t_generated_marker():
    m = read(os.path.join(ED, "references", "GENERATED.md"))
    assert "do not edit here" in m and "source home" in m


def t_isolated_copy_resolves():
    with tempfile.TemporaryDirectory() as d:
        iso = os.path.join(d, "evidence-docs")
        shutil.copytree(ED, iso)
        broken = []
        for rel_dir, name in [(".", "SKILL.md")] + \
                [("references", f) for f in REFS]:
            t = read(os.path.join(iso, rel_dir, name))
            for target in re.findall(r"\]\(([^)#]+?)(?:#[^)]*)?\)", t):
                if target.startswith(("http://", "https://")):
                    continue
                if not os.path.exists(os.path.join(iso, rel_dir, target)):
                    broken.append(f"{rel_dir}/{name} -> {target}")
        assert broken == [], f"an isolated copy still breaks: {broken}"


def main():
    if "--sync" in sys.argv:
        sync()
        return 0
    case("no link escapes the skill directory", t_no_escaping_links)
    case("every generated copy is byte-equal to the source home",
         t_copies_match_source_home)
    case("the GENERATED marker names the source home and the sync",
         t_generated_marker)
    case("an isolated copy of the directory resolves every link",
         t_isolated_copy_resolves)
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
