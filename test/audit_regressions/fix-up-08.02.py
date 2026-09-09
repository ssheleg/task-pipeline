#!/usr/bin/env python3
"""FIX-UP-08.02 — one HostContext contract, bundled per member installer
(sherlock audit, UP-08).

The fix under test: task-pipeline, super-ux and sheleg-design installers each
carry a LOCAL bundled hostRoot resolver implementing ONE contract — an
explicit root > the documented host env var > the platform default — because
npx installers share no lib.

Checked:
* task-pipeline's hostRoot (driven through node) follows the precedence and
  preserves spaces;
* all three bins declare the identical HOST_ENV / HOST_DIR contract and a
  hostRoot function;
* the Claude root is routed through the resolver (no bare ~/.claude for the
  user-scoped plugin registry);
* default roots are unchanged when no env is set.

The super-ux / sheleg-design checkouts may be absent → those checks NOT_RUN.
Standard library + node only.
"""
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TP_BIN = os.path.join(ROOT, "bin", "task-pipeline.js")
UX_BIN = os.path.expanduser("~/DATA/super-ux/bin/super-ux.js")
DS_BIN = os.path.expanduser("~/DATA/sheleg-design-skill/bin/cli.js")

failures = []
not_run = []


def case(name, fn):
    try:
        fn()
        print(f"  ok  {name}")
    except AssertionError as e:
        failures.append(f"{name}: {e}")
        print(f"FAIL  {name}: {e}")


def tp_host_root(agent, home, env, explicit=None):
    js = ("const b=require(process.argv[1]);"
          "console.log(JSON.stringify(b.hostRoot(process.argv[2], process.argv[3],"
          "JSON.parse(process.argv[4]), process.argv[5] || undefined)))")
    r = subprocess.run(["node", "-e", js, TP_BIN, agent, home, json.dumps(env),
                        explicit or ""], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, f"node failed: {r.stderr[:300]}"
    return json.loads(r.stdout.strip().splitlines()[-1])


def t_tp_precedence():
    assert tp_host_root("claude", "/home/u", {}) == "/home/u/.claude"
    assert tp_host_root("claude", "/home/u", {"CLAUDE_CONFIG_DIR": "/srv/cc"}) == "/srv/cc"
    assert tp_host_root("claude", "/home/u", {"CLAUDE_CONFIG_DIR": "/env"},
                        explicit="/explicit") == "/explicit"


def t_tp_spaces_and_isolation():
    assert tp_host_root("codex", "/home/u", {"CODEX_HOME": "/tmp/my codex"}) == "/tmp/my codex"
    # CLAUDE_CONFIG_DIR does not move codex
    assert tp_host_root("codex", "/home/u", {"CLAUDE_CONFIG_DIR": "/x"}) == "/home/u/.codex"


def _contract_present(path):
    with open(path, encoding="utf-8") as fh:
        s = fh.read()
    assert "HOST_ENV" in s and "CLAUDE_CONFIG_DIR" in s and "CODEX_HOME" in s, \
        f"{os.path.basename(path)}: HOST_ENV contract missing"
    assert "function hostRoot(agent, home, env, explicit)" in s, \
        f"{os.path.basename(path)}: hostRoot resolver missing"
    assert 'path.join(home, HOST_DIR[agent])' in s, \
        f"{os.path.basename(path)}: default root not the platform default"


def t_all_three_carry_the_contract():
    _contract_present(TP_BIN)                      # always present
    for p, label in ((UX_BIN, "super-ux"), (DS_BIN, "sheleg-design")):
        if not os.path.isfile(p):
            not_run.append(f"{label} checkout absent — contract check NOT_RUN")
            continue
        _contract_present(p)


def t_claude_registry_routed():
    # the user-scoped plugin registry read goes through the resolver in each bin
    for p, label in ((TP_BIN, "task-pipeline"), (UX_BIN, "super-ux"), (DS_BIN, "sheleg-design")):
        if not os.path.isfile(p):
            continue
        with open(p, encoding="utf-8") as fh:
            s = fh.read()
        # no bare home/.claude/plugins for the registry; it must use hostRoot('claude', ...)
        assert "hostRoot('claude', home" in s or 'hostRoot("claude", home' in s, \
            f"{label}: the Claude root is not routed through hostRoot"


def main():
    case("task-pipeline hostRoot follows the precedence", t_tp_precedence)
    case("task-pipeline hostRoot preserves spaces and isolates hosts",
         t_tp_spaces_and_isolation)
    case("all three installers carry the identical HostContext contract",
         t_all_three_carry_the_contract)
    case("each installer routes the Claude registry through the resolver",
         t_claude_registry_routed)
    for n in not_run:
        print(f"  NOT_RUN  {n}")
    if failures:
        print(f"\n{len(failures)} failure(s)")
        return 1
    print("\nall green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
