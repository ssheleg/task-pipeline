#!/usr/bin/env python3
r"""anchors.py — which negative self-tests are pinned to a value a release can move.

Board row **B-113**, confirmed four times: *"negative-test anchors are pinned to
literals that the releases they guard move, so a release disarms its own checks."*
Every confirmation had the same shape and the same reason nobody noticed — the
plants were disarmed by the repository getting **healthier**. The board re-derived
its ages and `bd5`'s needle stopped existing; the first blind eval runs shipped and
`pf1`'s guard went dormant; a release finally carried an honest run stamp and
`gap1`'s precondition emptied. Each was found by a 35-minute suite at release time,
one release after the damage.

The row states the whole question in one line, and this module answers it
mechanically, in the cheap gate:

    is the number the plant WRITES, or the number it LOOKS FOR?

A number the plant writes is its planted defect and is *supposed* to be a literal.
A number the plant looks for is an **anchor**, and an anchor is a promise that the
tree will keep saying what it said the day the plant was written.

## What counts as a needle

Only what the plant reads **out of a file, before it writes**. Three filters, each
one closing a false positive that the first draft of this module produced:

1. **The subject must be file content.** `verb.replace('chr(34)', '"')` builds a
   payload out of local strings; it reads nothing and can go stale in no way. Names
   assigned from `open(...).read()` — and names derived from those — are tracked, and
   nothing else is a needle.
2. **Post-write assertions are not needles.** `assert "the 250 guards" in
   open(p).read()` after the write is the plant confirming its own landing. Its
   literal is the planted value by construction. Ordering decides this, not spelling.
3. **Regex shape is not a value.** `[0-9a-f]{7,40}` and `\d{4}-\d\d-\d\d` describe a
   shape; `\u2192` inside a raw string is an escape, not the year 2192. Character
   classes, quantifiers, class escapes and `\uXXXX` are stripped before the value
   test runs.

Filter 2 is tracked **per path**, not per plant. A plant-wide "everything after
the first write is a read-back" rule is one line shorter and wrong: `pf1` writes
`evals/RESULTS.md` and then reads `references/companion-skills.md`, and the
plant-wide rule exempts the second file's needle, which is a genuine anchor. An
earlier draft also exempted any value the plant writes anywhere — which quietly
excused the worst case in the corpus, a live-board plant that echoed `B-008` into
its own replacement. Both retractions are fixtures in `anchors_test.py`.

## What counts as moving

A digit-run of two or more; a version token; a number alone in a markdown table
cell; a bolded number. All four are the shapes this repository's own claims take —
counts, priorities, ages, caps, ids and tags — and all four have moved under a
plant here at least once.

## The escape hatch, and why it is narrow

Some values genuinely cannot be derived. Such a plant declares itself:

    # anchor: 2026-08-11 — the containers measurement is frozen; deriving the date
    #   would make the plant agree with whatever the file says, which is the defect.
    #   Falsified if the measurement is ever re-taken and re-dated.

The declaration must name a substring of the needle and carry a reason. It is not a
silencer: `python3 test/anchors.py` prints every declaration by name on every run,
so the set can be read rather than trusted.
"""
from __future__ import annotations

import ast
import os
import re
import sys
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(ROOT, ".github/workflows/validate.yml")

MARKER = "Negative self-test"
PROP_MARKER = "Property check"
DORM_RE = re.compile(r"^\s*#\s*dormant-when:\s*(.*)$")
DECL_RE = re.compile(r"^\s*#\s*anchor:\s*(\S+)(?:\s*(?:—|--)\s*(.*))?\s*$")
MIN_REASON = 60          # characters of actual prose, continuation lines included
MIN_WORDS = 8            # a length threshold alone is satisfied by 60 dots

# The heredoc a plant runs its python in. `<<'EOF'` is quoted on purpose in every
# plant here — the shell must not expand it — so the opening line is unambiguous.
# `(?:\n|$)` because a step whose script ENDS at the heredoc terminator is still a
# heredoc — the fixtures in `anchors_test.py` are exactly that shape, and requiring a
# trailing newline made every python-bodied fixture parse as no plant at all: a
# detector reporting silence over a corpus it could not read.
HEREDOC_RE = re.compile(r"python3 - <<'(\w+)'\n(.*?)\n\1(?:\n|$)", re.S)

_LOOK_STR_METHODS = {
    "replace", "index", "rindex", "find", "rfind", "count", "startswith",
    "endswith", "split", "rsplit", "partition", "rpartition",
    "removeprefix", "removesuffix", "get",
}
_RE_LOOK = {"search", "match", "fullmatch", "findall", "finditer", "compile",
            "sub", "subn", "split"}
_RE_MODULES = {"re", "_re", "_re0", "_sre"}

# Regex shape, stripped before the value test. Order matters: `\uXXXX` before the
# class escapes, character classes before quantifiers.
_SHAPE = [
    re.compile(r"\\u[0-9a-fA-F]{4}"),
    re.compile(r"\\x[0-9a-fA-F]{2}"),
    re.compile(r"\[[^\]]*\]"),
    re.compile(r"\{\d+(?:,\d*)?\}"),
    re.compile(r"\\[dswDSWbBAZ]"),
]
# What makes a literal look like a regex at all. A plain sentence is never stripped.
_LOOKS_REGEX = re.compile(r"\\[dswDSWbBAZ]|\[[^\]]*\]|\{\d+(?:,\d*)?\}|\\u[0-9a-fA-F]{4}"
                          r"|\(\?:|\^|\$")

_DIGITS = re.compile(r"\d+")
_VERSION = re.compile(r"\bv\d+\.\d+")
_CELL_NUM = re.compile(r"\|\s*\**\s*\d+\s*\**\s*\|")
_BOLD_NUM = re.compile(r"\*\*\s*\d+\s*\*")


def _strip_shape(text: str) -> str:
    if not _LOOKS_REGEX.search(text):
        return text
    for pat in _SHAPE:
        text = pat.sub("", text)
    return text


def moving_values(text: str) -> list[str]:
    """The digit-runs in `text` that a release can move, in order of appearance."""
    stripped = _strip_shape(text)
    out = []
    for m in _DIGITS.finditer(stripped):
        run = m.group(0)
        around = stripped[max(0, m.start() - 4):m.end() + 4]
        if (len(run) >= 2
                or _VERSION.search(around)
                or _CELL_NUM.search(around)
                or _BOLD_NUM.search(around)):
            out.append(run)
    return out


class _Plant(ast.NodeVisitor):
    """One plant's python, split into what it reads off disk and what it writes back.

    Two facts decide whether a string is a needle, and both are structural rather
    than lexical:

    * **Provenance** — the subject must carry text that came off disk. Reads are
      tracked from `open(...).read()`, `open(...)` bound by a `with`, and
      `Path(...).read_text()`, then propagated through derived names, slices,
      string methods, comprehensions and the **builtin wrappers** that keep the
      same text: `enumerate`, `sorted`, `list`, `map` and their kin. The
      independent reader found that last one by fixture: `for n, ln in
      enumerate(lines)` broke the chain, and two live plants (`wv1`, `wv2`) sat
      pinned to `B-005` behind it while this module reported the corpus clean.
    * **Order, per path** — a read of a path this plant has already written is the
      plant confirming its own landing, and its literal is the planted value by
      construction. The path is keyed by its **source text** when it is not a plain
      constant (`ast.unparse`), so `p = d + "/README.md"` matches itself and a
      legitimate write-then-assert plant is not refused.

    A body this module cannot read is counted, never skipped: `parse_failures`
    surfaces as a refusal, because "no anchors found" and "could not look" are
    otherwise the same sentence.
    """

    # Builtins that hand back the same text under a different shape. Anything that
    # could CONSTRUCT text (`str`, `repr`, `format`, `join`) is deliberately absent.
    _PASSTHROUGH = {"enumerate", "list", "sorted", "reversed", "iter", "tuple",
                    "set", "map", "filter", "zip", "dict", "next", "frozenset"}
    _GREP_TOOLS = {"grep", "egrep", "fgrep", "sed", "awk", "rg", "ack"}

    def __init__(self):
        self.needles: list[tuple[str, str, str, int]] = []   # (literal, how, pathkey, line)
        self.consts: dict[str, str] = {}                     # name -> string constant
        self.reads: dict[str, tuple] = {}                    # name -> (pathkey, line)
        self.writes: dict[str, int] = {}                     # pathkey -> first write line
        self.patterns: dict[str, str] = {}                   # name -> re.compile source
        self.paths: dict[str, str] = {}                      # name -> pathlib.Path target

    # -- string and path resolution ---------------------------------------------
    def _strs(self, node) -> list[str]:
        out = []
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append(node.value)
        elif isinstance(node, ast.Name) and node.id in self.consts:
            out.append(self.consts[node.id])
        elif isinstance(node, ast.JoinedStr):
            for v in node.values:
                out += self._strs(v)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Mod)):
            out += self._strs(node.left) + self._strs(node.right)
        elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            for e in node.elts:
                out += self._strs(e)
        return out

    def _one(self, node):
        s = self._strs(node)
        return s[0] if len(s) == 1 else None

    def _path_key(self, node) -> str:
        """A stable identity for the file a call names.

        The resolved string when it is one, otherwise the expression's own source.
        Returning `None` for an unresolved path made every write-then-assert plant
        whose path is computed look like a fresh read of an unwritten file.
        """
        resolved = self._one(node)
        if resolved is not None:
            return resolved
        try:
            return "expr:" + ast.unparse(node)
        except Exception:                                    # pragma: no cover
            return "expr:?"

    @staticmethod
    def _is_open(node) -> bool:
        return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "open")

    @staticmethod
    def _is_path(node) -> bool:
        """`Path(x)` / `pathlib.Path(x)`."""
        if not isinstance(node, ast.Call):
            return False
        f = node.func
        return ((isinstance(f, ast.Name) and f.id == "Path")
                or (isinstance(f, ast.Attribute) and f.attr == "Path"))

    def _file_src(self, node):
        """`(pathkey, lineno)` when this expression carries text off disk."""
        if isinstance(node, ast.Name):
            return self.reads.get(node.id)
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id in self.paths:
            return None                       # `p.name` etc — the path, not its text
        if isinstance(node, ast.Subscript):
            return self._file_src(node.value)
        if isinstance(node, ast.Starred):
            return self._file_src(node.value)
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name):
                if f.id == "open":
                    # `json.load(open(p))` — the handle IS the file, with no `.read()`
                    # between. Resolved here because `open` is a Name-func Call and the
                    # passthrough test below would return None first.
                    mode = self._one(node.args[1]) if len(node.args) > 1 else ""
                    if "w" in (mode or "") or "a" in (mode or ""):
                        return None
                    return (self._path_key(node.args[0]) if node.args
                            else "expr:?"), node.lineno
                # enumerate(lines), sorted(t.splitlines()), list(...) — same text.
                if f.id in self._PASSTHROUGH:
                    for a in node.args:
                        src = self._file_src(a)
                        if src:
                            return src
                return None
            if isinstance(f, ast.Attribute):
                # `json.loads(Path(p).read_text())` and `yaml.safe_load(open(p))` carry
                # the file onward in a different shape. A look into the result — a key,
                # a `.get`, an equality — is still a look at what the file says.
                if f.attr in ("loads", "load", "safe_load", "full_load", "parse"):
                    for a in node.args:
                        src = self._file_src(a)
                        if src:
                            return src
                    return None
                if f.attr in ("read", "readlines") and self._is_open(f.value):
                    args = f.value.args
                    return (self._path_key(args[0]) if args else "expr:?"), node.lineno
                if f.attr in ("read_text", "read_bytes"):
                    if self._is_path(f.value):
                        args = f.value.args
                        return (self._path_key(args[0]) if args else "expr:?"), node.lineno
                    if isinstance(f.value, ast.Name) and f.value.id in self.paths:
                        return self.paths[f.value.id], node.lineno
                return self._file_src(f.value)
            return None
        if isinstance(node, ast.BinOp):
            return self._file_src(node.left) or self._file_src(node.right)
        if self._is_open(node):
            # `json.load(open(p))` — the handle IS the file, with no `.read()` between.
            mode = self._one(node.args[1]) if len(node.args) > 1 else ""
            if "w" not in (mode or "") and "a" not in (mode or ""):
                return (self._path_key(node.args[0]) if node.args else "expr:?"), node.lineno
            return None
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            for e in node.elts:
                src = self._file_src(e)
                if src:
                    return src
        if isinstance(node, ast.Dict):
            for v in node.values:
                src = self._file_src(v)
                if src:
                    return src
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            # `texts = {f: open(f).read() for f in files}` — the RESULT holds file text,
            # and tracking only the loop variable left the largest plant in the corpus
            # (`gapmention`, reading 1+N files this way) yielding zero needles.
            _saved = dict(self.reads)
            try:
                for c in node.generators:
                    _s = self._file_src(c.iter)
                    if _s:
                        self._bind_targets(c.target, _s)
                for _e in ([node.key, node.value] if isinstance(node, ast.DictComp)
                           else [node.elt]):
                    _s = self._file_src(_e)
                    if _s:
                        return _s
            finally:
                self.reads = _saved
        return None

    def _bind(self, target, value):
        if isinstance(target, (ast.Tuple, ast.List)):
            for e in target.elts:
                self._bind(e, value)
            return
        if not isinstance(target, ast.Name):
            return
        src = self._file_src(value)
        if src:
            self.reads[target.id] = src
        strs = self._strs(value)
        if len(strs) == 1 and isinstance(value, (ast.Constant, ast.JoinedStr, ast.BinOp)):
            self.consts[target.id] = strs[0]
        # `rx = re.compile(pat)` — the pattern travels with the object, and a look
        # through `rx.search(t)` carries no literal of its own for a lexical reader.
        # `p = pathlib.Path(x)` — the handle carries the path, and `p.read_text()` is a
        # read. Seven live plants use this shape and the census reported them as reading
        # no file at all; the independent reader found it by fixture.
        if self._is_path(value) and value.args:
            self.paths[target.id] = self._path_key(value.args[0])
        if (isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute)
                and value.func.attr == "compile" and value.args
                and isinstance(value.func.value, ast.Name)
                and value.func.value.id in _RE_MODULES):
            pat = self._one(value.args[0])
            if pat is not None:
                self.patterns[target.id] = pat

    def _needle(self, literal, how, subject, lineno):
        src = self._file_src(subject)
        if src:
            self.needles.append((literal, how, src[0], src[1]))

    # -- visits -----------------------------------------------------------------
    def visit_Assign(self, node):
        self.generic_visit(node)
        for t in node.targets:
            self._bind(t, node.value)

    def visit_With(self, node):
        # `with open(p) as fh:` — the handle carries the path, and `fh.read()` is a read.
        for item in node.items:
            if item.optional_vars is None:
                continue
            ctx = item.context_expr
            if self._is_open(ctx) and isinstance(item.optional_vars, ast.Name):
                key = self._path_key(ctx.args[0]) if ctx.args else "expr:?"
                mode = self._one(ctx.args[1]) if len(ctx.args) > 1 else ""
                if "w" in (mode or "") or "a" in (mode or ""):
                    self.writes.setdefault(key, node.lineno)
                else:
                    self.reads[item.optional_vars.id] = (key, node.lineno)
        self.generic_visit(node)

    visit_AsyncWith = visit_With

    def _bind_targets(self, target, src):
        for e in ([target] if isinstance(target, ast.Name)
                  else getattr(target, "elts", [])):
            if isinstance(e, ast.Name):
                self.reads[e.id] = src

    def visit_For(self, node):
        # SCOPED. A loop variable that keeps its provenance for the rest of the body
        # makes an unrelated later local read as file text — 33 of 891 needles depended
        # on exactly that, and the R-005 reader measured it by scoping and re-counting.
        _saved = dict(self.reads)
        src = self._file_src(node.iter)
        if src:
            self._bind_targets(node.target, src)
        for _n in node.body:
            self.visit(_n)
        self.reads = _saved
        for _n in node.orelse:
            self.visit(_n)
        self.visit(node.iter)

    visit_AsyncFor = visit_For

    def _visit_comp(self, node, elements):
        """A comprehension's targets live only inside the comprehension."""
        _saved = dict(self.reads)
        for c in node.generators:
            src = self._file_src(c.iter)
            if src:
                self._bind_targets(c.target, src)
            self.visit(c.iter)
            for _if in c.ifs:
                self.visit(_if)
        for e in elements:
            self.visit(e)
        self.reads = _saved

    def visit_ListComp(self, node):
        self._visit_comp(node, [node.elt])

    visit_SetComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp

    def visit_DictComp(self, node):
        self._visit_comp(node, [node.key, node.value])

    def visit_Assert(self, node):
        # The message is commentary, never material: reading it as text the plant
        # writes exempted `B-005` from its own needle, because the assert message
        # names the row it is asserting about.
        self.visit(node.test)

    def visit_Raise(self, node):
        return

    def visit_Compare(self, node):
        for op, comp in zip(node.ops, node.comparators):
            if isinstance(op, (ast.In, ast.NotIn)):
                for s in self._strs(node.left):
                    self._needle(s, "membership", comp, node.lineno)
            elif isinstance(op, (ast.Eq, ast.NotEq)):
                # `d["state"] == "tests"` and `c[9].strip() != "open"` — the literal is
                # looked FOR in what the file says, whichever side of the operator it
                # sits on. Only the side with provenance decides which is the needle.
                if self._file_src(comp) is not None:
                    for s in self._strs(node.left):
                        self._needle(s, "equality", comp, node.lineno)
                elif self._file_src(node.left) is not None:
                    for s in self._strs(comp):
                        self._needle(s, "equality", node.left, node.lineno)
        self.generic_visit(node)

    def _record_write(self, node):
        """`open(p, "w").write(x)`, `fh.write(x)`, `Path(p).write_text(x)`."""
        f = node.func
        tgt = f.value
        if self._is_open(tgt) and len(tgt.args) >= 2:
            if "w" in (self._one(tgt.args[1]) or "") or "a" in (self._one(tgt.args[1]) or ""):
                self.writes.setdefault(self._path_key(tgt.args[0]), node.lineno)
        elif f.attr in ("write_text", "write_bytes") and self._is_path(tgt) and tgt.args:
            self.writes.setdefault(self._path_key(tgt.args[0]), node.lineno)
        elif f.attr in ("write_text", "write_bytes") and isinstance(tgt, ast.Name) \
                and tgt.id in self.paths:
            self.writes.setdefault(self.paths[tgt.id], node.lineno)
        elif isinstance(tgt, ast.Name) and tgt.id in self.reads:
            # a handle opened for reading, written through: same path either way
            self.writes.setdefault(self.reads[tgt.id][0], node.lineno)

    def _subprocess_needles(self, node):
        """`subprocess.run(["grep", "-c", NEEDLE, path])` reads a file too."""
        for arg in node.args:
            if not isinstance(arg, (ast.List, ast.Tuple)):
                continue
            parts = [self._one(e) for e in arg.elts]
            if not parts or parts[0] not in self._GREP_TOOLS:
                continue
            for s in parts[1:]:
                if s and not s.startswith("-"):
                    self.needles.append((s, "subprocess " + parts[0], "expr:argv",
                                         node.lineno))
                    break

    def visit_Call(self, node):
        f = node.func
        # `json.dump(d, open(p, "w"))` writes the file without any `.write` this visitor
        # can see, so 39 live plants' own read-backs were being refused. An `open` in
        # WRITE mode is a write wherever it appears — as a receiver, as an argument, or
        # in a `with`. The two halves of this rule landed unmatched in one commit:
        # `Path().write_text()` was added and `json.dump` was not.
        if self._is_open(node) and len(node.args) > 1:
            _m = self._one(node.args[1]) or ""
            if "w" in _m or "a" in _m:
                self.writes.setdefault(self._path_key(node.args[0]), node.lineno)
        if isinstance(f, ast.Attribute):
            if f.attr in ("write", "writelines", "write_text", "write_bytes"):
                self._record_write(node)
            elif f.attr in ("run", "check_output", "call", "Popen", "check_call"):
                self._subprocess_needles(node)
            elif (isinstance(f.value, ast.Name) and f.value.id in _RE_MODULES
                    and f.attr in _RE_LOOK and len(node.args) >= 2):
                subject = (node.args[2] if f.attr in ("sub", "subn") and len(node.args) > 2
                           else node.args[1] if f.attr not in ("sub", "subn") else None)
                if subject is not None:
                    for s in self._strs(node.args[0]):
                        self._needle(s, "re." + f.attr, subject, node.lineno)
            elif (isinstance(f.value, ast.Name) and f.value.id in self.patterns
                    and f.attr in _RE_LOOK and node.args):
                # a compiled pattern, looked up through the object it was compiled into
                self._needle(self.patterns[f.value.id], "compiled." + f.attr,
                             node.args[-1], node.lineno)
            elif f.attr in _LOOK_STR_METHODS and node.args:
                for s in self._strs(node.args[0]):
                    self._needle(s, "." + f.attr, f.value, node.lineno)
        self.generic_visit(node)

    def anchors(self) -> list[tuple[str, str]]:
        """Needles that pin a moving value and were read before that path was written."""
        out = []
        for literal, how, pathkey, read_line in self.needles:
            if self.writes.get(pathkey, 10 ** 9) < read_line:
                continue                 # a read-back of what this plant just wrote
            if moving_values(literal):
                out.append((literal, how))
        return out


def _shell_needles(script: str) -> list[tuple[str, str]]:
    """Needles a plant reads with a shell tool rather than with python.

    A `validate.py … | grep 'message'` is assertion 3 — the guard that fired is the
    guard under test — and its literal is the guard's message, not an anchor. The
    test is POSITIONAL: `validate.py` must appear *before* the `grep` on the line.
    Skipping every line that merely names the script threw away real needles, which
    the independent reader found by fixture.

    `sed`, `awk` and an unquoted `grep` pattern are read too — a reader that knows
    only quoted `grep` reports a corpus clean that it never looked at.
    """
    out = []
    for line in script.splitlines():
        if line.lstrip().startswith("#"):
            continue
        vpos = line.find("validate.py")
        for m in re.finditer(r"\b(?:grep|egrep|fgrep|rg)\s+(?:-{1,2}[\w-]+\s+)*"
                             r"(?:(['\"])(.*?)\1|([^\s|;&]+))", line):
            if 0 <= vpos < m.start():
                continue                     # the guard's own message, not a needle
            pat = m.group(2) if m.group(2) is not None else m.group(3)
            # An unquoted token holding a path separator is the FILE, not the pattern:
            # `grep -q pat /tmp/x-copy/2026-08-08-…md` yielded `2026` as a needle.
            if m.group(2) is None and ("/" in pat or pat.startswith("$")):
                continue
            out.append((pat, "grep"))
        # Both halves of `s/OLD/NEW/` and an address `/ADDR/p`, with `/` or `|` as the
        # delimiter — the one live `sed` here uses `|`, so a `/`-only reader is blind to
        # it while flagging the search half of an edit it can see.
        for m in re.finditer(r"\bsed\b[^\n]*?['\"]\s*(?:-n\s*)?s?([/|])([^/|'\"]{3,})\1",
                             line):
            out.append((m.group(2), "sed"))
        for m in re.finditer(r"\bawk\b[^\n]*?['\"]\s*([/|])([^/|'\"]{3,})\1", line):
            out.append((m.group(2), "awk"))
    return out


def _comment_block(lines, i):
    """The comment paragraph starting at `lines[i]`, markers stripped.

    A declaration's reason wraps. Judging only the first line refused
    `# dormant-when: no v* tag` followed by three informative lines, and accepted
    `# dormant-when:` with nothing on it at all — both found by fixture.
    """
    out = [lines[i].split(":", 1)[1] if ":" in lines[i] else ""]
    for ln in lines[i + 1:]:
        s = ln.strip()
        if not s.startswith("#"):
            break
        body = s.lstrip("#")
        if not body.startswith(("  ", "\t")):       # a new comment, not a continuation
            break
        out.append(body)
    return " ".join(x.strip() for x in out).strip()


def _substantive(text):
    """(chars, distinct words of 3+ letters) — the two numbers a reason is judged on."""
    words = {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text)}
    return len(text.strip()), len(words)


class Step:
    def __init__(self, name, script):
        self.name = name
        self.script = script
        self.label = name.replace(MARKER, "").replace(PROP_MARKER, "").strip().strip("()")
        _lines = script.splitlines()
        # `_comment_block` already returns the first line's own text, so concatenating
        # `m.group(2)` with it counted every one-line reason TWICE — a 47-character
        # reason stored as 108 and passed a floor of 60.
        self.declarations = [(m.group(1), _comment_block(_lines, i))
                             for i, line in enumerate(_lines)
                             if (m := DECL_RE.match(line))]
        self.dormancy = next((_comment_block(_lines, i) for i, line in enumerate(_lines)
                              if DORM_RE.match(line)), None)
        # `SKIP:` in a COMMENT is a plant discussing dormancy, not a plant that can
        # decline. Reading the whole script textually demanded a `# dormant-when:`
        # from a plant with no skip branch — a false refusal, and a false refusal is
        # how an operator learns to switch a guard off.
        self.skip_capable = any(
            "SKIP:" in ln for ln in script.splitlines()
            if not ln.lstrip().startswith("#"))
        self.needles: list[tuple[str, str]] = []      # every literal read off disk
        self.anchors: list[tuple[str, str, list[str]]] = []
        self.parse_failures = 0
        # A heredoc this module cannot recognise makes the whole body invisible, and
        # `needles = 0` then reads exactly like a clean plant. Count the python
        # heredocs the shell actually opens and compare with the ones parsed.
        # A GUARD READS WHAT WOULD RUN, NOT WHAT A PAYLOAD CONTAINS. Counting every
        # `python3 … <<` in the text called `ri13` unreadable, because that plant's
        # payload is the source of a workflow step and quotes the opener inside a
        # string. Only a LINE that begins with the interpreter opens a heredoc.
        # No QUOTE may precede the interpreter: that is what separates
        # `HOOK_INPUT=x python3 - <<EOF` and `echo hi | python3 <<'EOF'`, which open a
        # heredoc, from `"          python3 - <<'XEOF'\n"`, which is `ri13`'s payload
        # quoting one inside a string.
        _opened = len([ln for ln in script.splitlines()
                       if re.match(r"""[^"'#\n]*\bpython3?\b[^"'\n]*<<""", ln)])
        _read = 0
        for m in HEREDOC_RE.finditer(script):
            _read += 1
            body = textwrap.dedent(m.group(2))
            try:
                tree = ast.parse(body)
            except SyntaxError:
                # A body this module cannot read is a body it cannot vouch for. Counted
                # and surfaced rather than skipped: "no anchors found" and "could not
                # look" are the same sentence otherwise.
                self.parse_failures += 1
                continue
            p = _Plant()
            p.visit(tree)
            self.needles += [(lit, how) for lit, how, _src, _ln in p.needles]
            self.anchors += [(lit, how, moving_values(lit)) for lit, how in p.anchors()]
        self.unreadable_bodies = max(0, _opened - _read)
        for lit, how in _shell_needles(script):
            self.needles.append((lit, how))
            if moving_values(lit):
                self.anchors.append((lit, how, moving_values(lit)))

    def undeclared(self) -> list[tuple[str, str, list[str]]]:
        """Anchors this plant has not declared. A declaration names a substring."""
        out = []
        for needle, how, values in self.anchors:
            covered = any(d[0] and d[0] in needle
                          and _substantive(d[1])[0] >= MIN_REASON
                          and _substantive(d[1])[1] >= MIN_WORDS
                          for d in self.declarations)
            if not covered:
                out.append((needle, how, values))
        return out

    def bad_declarations(self) -> list[tuple[str, str]]:
        """Declarations that name nothing in a needle, or carry no reason."""
        bad = []
        for target, reason in self.declarations:
            _chars, _words = _substantive(reason)
            if _chars < MIN_REASON or _words < MIN_WORDS:
                bad.append((target, f"its reason is {_chars} characters and {_words} "
                            f"distinct words, below {MIN_REASON}/{MIN_WORDS} — a length "
                            "threshold alone is satisfied by a row of dots, so both are "
                            "checked"))
            elif not any(target in n for n, _h in self.needles):
                bad.append((target, "names nothing this plant looks for"))
        return bad


def _parse_steps(path):
    """Reuse the runner's parser rather than growing a second dialect of it."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import negatives
    return negatives.parse_steps(path)


def census(path: str = WORKFLOW) -> list[Step]:
    return [Step(n, s) for n, s in _parse_steps(path) if MARKER in n]


def no_needle_breakdown(steps) -> dict:
    """Why a plant yields no text needle. Computed, because the first gloss was wrong.

    That line read *"their look is a JSON key, which raises rather than passing"* over 41
    plants of which 7 were JSON looks. A count with a false explanation beside it is worse
    than the count alone: it tells the reader not to look.
    """
    out = {}
    for s in steps:
        if s.needles:
            continue
        has_py = bool(HEREDOC_RE.search(s.script))
        reads = bool(re.search(r"read_text|json\.load|\.read\(\)|safe_load|readlines",
                               s.script))
        raw = bool(re.search(r'open\([^)]*"rb"\)|_orig_bytes', s.script))
        k = ("shell only, no python body" if not has_py else
             "a python body that reads no file" if not reads else
             "a whole-file byte comparison" if raw else
             "a JSON or dict key, which raises when it goes stale")
        out[k] = out.get(k, 0) + 1
    return out


def every_check(path: str = WORKFLOW, steps: list | None = None) -> list[Step]:
    """Negative self-tests AND property checks.

    Dormancy is a property of both categories and the first pass covered one: a
    property check that printed `SKIP:` needed no declaration and was still counted
    as one that printed what it asserts.
    """
    if steps is not None:
        # The caller already parsed the negative self-tests; add only the property
        # checks rather than re-reading a 9k-line workflow (board row B-010, which
        # `findings()` cites in its own docstring one screen up).
        _seen = {s.name for s in steps}
        return steps + [Step(n, s) for n, s in _parse_steps(path)
                        if PROP_MARKER in n and n not in _seen]
    return [Step(n, s) for n, s in _parse_steps(path)
            if MARKER in n or PROP_MARKER in n]


def category(step) -> str:
    """What to call this check in a refusal. Both categories can go dormant."""
    return "property check" if PROP_MARKER in step.name else "negative self-test"


def findings(path: str = WORKFLOW, steps: list | None = None) -> list[str]:
    """One line per plant this module refuses. Empty list = the class is closed.

    `steps` lets a caller that already holds a census reuse it: the workflow is 9k lines
    and parsing it twice per validator run is the class board row B-010 counts.
    """
    out, seen = [], set()
    for st in (census(path) if steps is None else steps):
        if st.parse_failures:
            out.append(f"negative self-test `{st.label}` has a python body the anchor "
                       "census cannot parse, so nothing can say whether its needles pin "
                       "a moving value — a plant the census skipped reads exactly like a "
                       "plant it cleared")
        if st.unreadable_bodies:
            # A heredoc opened in any other spelling — `python3 <<'EOF'`, `python3 - <<EOF`
            # — makes the whole body invisible, and `needles: 0` then reads exactly like a
            # clean plant. Found by the R-005 reader, who wrote three such fixtures.
            out.append(f"negative self-test `{st.label}` opens a python heredoc the anchor "
                       "census cannot recognise (it reads `python3 - <<'WORD'` only), so "
                       "its needles are unread and its silence is indistinguishable from "
                       "a clean plant")
        for needle, how, values in st.undeclared():
            if (st.label, needle) in seen:      # one finding per needle, not per read
                continue
            seen.add((st.label, needle))
            out.append(
                # The phrase stays on ONE source line: `CONTRIBUTING.md` cites guard
                # literals and `test/validate.py` looks for them in the source text, so a
                # message split mid-sentence reads as an enforcement that does not exist.
                f"negative self-test `{st.label}` is anchored on a value a release can move: "
                f"{', '.join(sorted(set(values)))} in the {how} needle "
                f"{needle[:70]!r}. Derive it from the tree at run time, or declare it "
                f"with `# anchor: <literal> — <why it cannot be derived, and what would "
                f"falsify it>` (B-113: a plant pinned to a literal is a check the next "
                f"release switches off, and it reports green while it does)")
        for target, why in st.bad_declarations():
            out.append(f"negative self-test `{st.label}` carries `# anchor: {target}` and "
                       f"{why}")
    return out


def _main(argv) -> int:
    steps = census()
    anchored = [s for s in steps if s.anchors]
    declared = [s for s in steps if s.declarations]
    skippers = [s for s in steps if s.skip_capable]
    print(f"{len(steps)} negative self-tests")
    print(f"  {sum(len(s.needles) for s in steps)} needles read out of a file before "
          f"the plant writes")
    print(f"  {len(anchored)} plant(s) still pin a value a release can move")
    print(f"  {len(declared)} plant(s) declare a value they cannot derive")
    print(f"  {len(skippers)} plant(s) can decline to run (dormant, never a pass)")
    _nb = no_needle_breakdown(steps)
    print(f"  {sum(_nb.values())} plant(s) yield no text needle: "
          + " · ".join(f"{v} {k}" for k, v in sorted(_nb.items(), key=lambda x: -x[1])))
    print(f"  {sum(s.parse_failures for s in steps)} python body/bodies this census "
          f"could not parse, {sum(s.unreadable_bodies for s in steps)} heredoc(s) it "
          f"could not recognise — a body it cannot read is a body it cannot vouch for")
    if "-v" in argv or anchored:
        for s in anchored:
            print(f"\n  * {s.label}")
            for needle, how, values in s.anchors:
                mark = "declared" if not any(
                    n == needle for n, _h, _v in s.undeclared()) else "UNDECLARED"
                print(f"      [{mark}] {how}: {', '.join(values)} in {needle[:80]!r}")
    for s in declared:
        for target, reason in s.declarations:
            print(f"\n  declared · {s.label}\n      {target} — {reason}")
    for s in skippers:
        print(f"\n  dormant-capable · {s.label}")
    bad = findings(WORKFLOW, steps)
    if bad:
        print()
        for b in bad:
            print("FAIL: " + b)
        return 1
    print("\nPASS: every negative self-test derives its anchor or declares why it cannot")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
