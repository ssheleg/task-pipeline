#!/usr/bin/env python3
"""A workflow checkpoint at every stage boundary, built from the run ledger.

When the host has Project Observatory's memory tools (`observatory_checkpoint_write`, or
`memory.checkpoint.write` under memory/0.1), a run writes one checkpoint each time a gate
returns. A session that runs out of quota, is compacted or is replaced by another agent then
continues from the last finished stage instead of re-deriving it. Without those tools the
run goes on exactly as before, and the ledger says memory was unavailable.

This script never talks to Observatory: the agent calls the tool. The script does the two
deterministic halves around that call, so nothing about the checkpoint is left to recall:

    stage_checkpoint.py emit   [--ledger PATH] [--project-root PATH] [--project project:<slug>]
                               [--constraint TEXT ...] [--credential PROJECT/ENV/NAME ...]
        prints the tool's arguments as JSON, from the ledger and selected project profile
    stage_checkpoint.py record --answer FILE|-   [--ledger PATH]
        reads the tool's answer and keeps `workflowId` and `leaseId` for the next boundary
    stage_checkpoint.py record --unavailable "<reason>" [--for-run]   [--ledger PATH]
        the tools are absent or failed: one ledger line, exit 0, the run continues.
        --for-run says it once for the whole run: a marker in memory.json silences
        hooks/memory-nudge.sh until a later `record --answer` clears it
    stage_checkpoint.py state  [--ledger PATH]
        the workflow this run writes to, for `observatory_checkpoint_latest` after a resume

What it keeps, and where:

- The ledger supplies the observed verdicts; the selected project `pipeline.json` supplies
  stage order and names (bundled default only when project config is absent). The run's topic is the goal, the
  ledger's verdicts are `done`, the next stage is `open`, the operator's constraints come in
  as `--constraint`, keys are passed by NAME only (`--credential`), and the git checkout is
  an artifact (branch and a 12-character head). Observatory redacts what it stores as well.
- `idempotencyKey` is derived from the run's topic and the exact `stage:` line (also the
  profile digest for a configured profile), so a retry
  of the same boundary replays the first answer, and a stage that runs again (a new line, a
  new time) is a new checkpoint.
- The first emit saves a run-scoped profile binding before returning arguments. A changed
  profile/run or unreadable saved state refuses instead of switching an existing workflow.
- `workflowId` and `leaseId` live in `.task-pipeline/memory.json`, mode 0600, beside the
  ledger in the git-ignored run directory, with the constraints and key names given so far:
  they are stated once and carried to every later boundary. The lease token is a write right: it is never
  printed, never appended to the ledger, never put in a commit.
- A refused write (`LeaseLost`: another executor holds the workflow now) is recorded with
  the episode Observatory kept (`keptAs`), the token is dropped, and the run is told to read
  the workflow before writing again. A stale writer therefore stops after one refusal.

Ledger lines it reads besides `stage:`: `review:` (the contact sheet's human rounds, stage 6
and 10 on a visual surface), each carried as evidence on the stage it names.

Ledger lines it appends, all of the existing `event:` shape:

    event: memory — checkpoint <stepId> rev <n> <workflowId> — <ISO-8601>
    event: memory — refused <error> (kept as <id>) — <ISO-8601>
    event: memory — unavailable — <reason> — <ISO-8601>
    event: memory — unavailable for this run — <reason> — <ISO-8601>

Exit codes: 0 done (including "unavailable", which is a state, not a failure); 2 the ledger
or the answer cannot be read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone

DEFAULT_LEDGER = ".task-pipeline/run.md"
STATE_NAME = "memory.json"
OWNER = "agent:task-pipeline"
STAGE = re.compile(r"^stage:\s*(\d+)\s+(.+?)\s+—\s+gate\s+(\S+)\s+—\s+verdict\s+(\S+)\s+—\s+(\S+)\s*$")
TOPIC = re.compile(r"^Run:\s*`([^`]+)`")
# The contact sheet's human rounds (`references/browser.md` → *The visual half*): one line per
# return or approval. Carried into the checkpoint of the stage it names, so the number of
# passes a surface took is measured at the boundary rather than remembered at the end.
REVIEW = re.compile(r"^review:\s*(\d+)\s+—\s+surface\s+(.+?)\s+—\s+rounds\s+(\d+)\s+—\s+(\S+)\s+—\s+\S+\s*$")
STATUS = {"pass": "done", "skip": "done", "fail": "blocked"}
# What `handoff` counts for its idempotency key: the memory events this script appended
# (checkpoint, refused, handoff offered) — never `unavailable`, which records no state change.
MEMORY_EVENT = re.compile(r"^event:\s*memory\s+—\s")
MEMORY_UNAVAILABLE = re.compile(r"^event:\s*memory\s+—\s+unavailable\b")


def _profile(root: pathlib.Path) -> tuple[list[dict], dict]:
    """Admit the selected profile for the numeric checkpoint ledger, not execute gates."""
    path = root / "pipeline.json"
    try:
        path.lstat()
        configured = True
    except FileNotFoundError:
        configured = False
    except OSError:
        raise SystemExit("stage_checkpoint: selected profile cannot be read")
    if not configured:
        path = pathlib.Path(__file__).resolve().parents[1] / "pipeline.example.json"
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        raise SystemExit("stage_checkpoint: selected profile cannot be read as JSON")
    if not isinstance(doc, dict) or not isinstance(doc.get("stages"), list) or not doc["stages"]:
        raise SystemExit("stage_checkpoint: selected profile needs a nonempty stages array")
    mandatory = doc.get("must_understand", [])
    if not isinstance(mandatory, list) or mandatory:
        raise SystemExit("stage_checkpoint: unsupported mandatory profile capabilities")
    stages, ids, states = [], set(), set()
    for ordinal, stage in enumerate(doc["stages"]):
        if not isinstance(stage, dict):
            raise SystemExit("stage_checkpoint: malformed selected stage")
        sid, state = stage.get("id", ordinal), stage.get("state")
        name = stage.get("name", state)
        skills, gate = stage.get("skills"), stage.get("gate")
        if (type(sid) is not int or sid < 0 or sid in ids or
                not isinstance(state, str) or not state.strip() or state in states or
                not isinstance(name, str) or not name.strip() or "\n" in name or "\r" in name or
                not isinstance(skills, list) or not skills or
                any(not isinstance(v, str) or not v.strip() for v in skills) or
                not isinstance(gate, dict) or gate.get("type") not in ("auto", "manual", "judgment") or
                not isinstance(gate.get("check"), str) or not gate["check"].strip() or
                (gate["type"] == "judgment" and
                 (not isinstance(gate.get("judge"), str) or not gate["judge"].strip()))):
            raise SystemExit("stage_checkpoint: malformed or ambiguous selected stage")
        ids.add(sid)
        states.add(state)
        stages.append({"id": sid, "name": name, "gate": gate["type"]})
    semantic = {k: doc[k] for k in ("stages", "kernel", "must_understand") if k in doc}
    identity = {"root": str(root), "source": "pipeline.json" if configured else "bundled-default",
                "digest": hashlib.sha256(json.dumps(semantic, sort_keys=True,
                                                    ensure_ascii=False).encode()).hexdigest()}
    return stages, identity


def _root(ledger: pathlib.Path, given: str | None) -> pathlib.Path:
    if given:
        root = pathlib.Path(given).resolve()
        if not root.is_dir() or not ledger.is_relative_to(root):
            raise SystemExit("stage_checkpoint: --project-root must contain the ledger")
        return root
    if ledger.parent.name == ".task-pipeline":
        return ledger.parent.parent
    git_root = _git(ledger.parent, "rev-parse", "--show-toplevel")
    if not git_root:
        raise SystemExit("stage_checkpoint: relocated ledger requires --project-root")
    return pathlib.Path(git_root).resolve()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _reviews(path: pathlib.Path) -> dict[int, list[str]]:
    """`review:` lines by the stage id they name, as evidence strings."""
    out: dict[int, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = REVIEW.match(line)
        if m:
            out.setdefault(int(m.group(1)), []).append(
                f"review: {m.group(2)} rounds {m.group(3)} {m.group(4)}")
    return out


def run_line(lines: list[str]) -> str | None:
    """The run's `Run:` line — the first one naming a real topic, not the template's.

    ONE helper for everything that asks "which run is this": `_read_ledger` takes the topic
    from it, and `run_key` hashes it for the run-level memory marker and for
    `hooks/memory-nudge.sh`'s once-per-run pointer, which imports this function."""
    for line in lines:
        m = TOPIC.match(line)
        if m and "<topic>" not in m.group(1):
            return line.strip()
    return None


STARTED = re.compile(r"started\s*`([^`]+)`")


def run_key(lines: list[str]) -> str | None:
    """16 hex of the run's topic and start date — not the whole `Run:` line, whose module-map
    field an agent may fill in mid-run. The same topic started on another day is another run;
    a same-day restart is told apart by `marker_for_this_run`'s ledger-line test."""
    line = run_line(lines)
    if not line:
        return None
    topic = TOPIC.match(line).group(1)
    started = STARTED.search(line)
    ident = f"{topic}\n{started.group(1) if started else ''}"
    return hashlib.sha256(ident.encode()).hexdigest()[:16]


def _read_ledger(path: pathlib.Path) -> tuple[str, list[tuple]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"stage_checkpoint: the ledger {path} cannot be read ({type(exc).__name__})")
    lines = text.splitlines()
    rl = run_line(lines)
    topic, stages = (TOPIC.match(rl).group(1) if rl else None), []
    for line in lines:
        s = STAGE.match(line)
        if line.startswith("stage:") and not s:
            raise SystemExit("stage_checkpoint: malformed stage ledger line")
        if s:
            stages.append((int(s.group(1)), s.group(2), s.group(3), s.group(4), s.group(5), line))
    if not topic:
        raise SystemExit("stage_checkpoint: the ledger names no run (`Run: `<topic>`` line)")
    return topic, stages


class UsageError(Exception):
    """A call the script cannot act on as given: exit 2, nothing written."""


def marker_for_this_run(ledger: pathlib.Path, state: dict) -> dict | None:
    """The run-level "memory unavailable" marker, only when it was written for THIS run.

    Two tests, both needed: the run key (topic and start date) matches, AND the marker's own
    `unavailable for this run` line is still in the ledger. A ledger reseeded at stage 0 the
    same day carries an identical `Run:` line but not that line, so a restart never inherits
    the previous run's silence (verification round 3)."""
    gone = (state.get("memory") or {}).get("unavailable") or {}
    if not gone:
        return None
    try:
        lines = ledger.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    key = run_key(lines)
    if key is None or gone.get("run") != key or gone.get("ledger_line") not in lines:
        return None
    return gone


def _state_path(ledger: pathlib.Path) -> pathlib.Path:
    return ledger.parent / STATE_NAME


def _load_state(ledger: pathlib.Path, strict: bool = False) -> dict:
    try:
        state = json.loads(_state_path(ledger).read_text(encoding="utf-8"))
        if not isinstance(state, dict):
            raise ValueError("state is not an object")
        return state
    except FileNotFoundError:
        return {}
    except (OSError, ValueError, UnicodeError):
        if strict:
            raise SystemExit("stage_checkpoint: memory state cannot be read")
        return {}


def _save_state(ledger: pathlib.Path, state: dict) -> None:
    path = _state_path(ledger)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(state, f)
    os.chmod(path, 0o600)
    ignore = path.parent / ".gitignore"
    lines = ignore.read_text(encoding="utf-8").splitlines() if ignore.exists() else []
    if STATE_NAME not in lines:
        ignore.write_text("\n".join([*lines, STATE_NAME]) + "\n", encoding="utf-8")


def _append(ledger: pathlib.Path, line: str) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def _git(root: pathlib.Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _project(root: pathlib.Path, given: str | None) -> str:
    if given:
        return given
    top = _git(root, "rev-parse", "--show-toplevel")
    name = pathlib.Path(top or root).name.lower()
    slug = re.sub(r"[^a-z0-9._-]+", "-", name).strip("-") or "unnamed"
    return f"project:{slug}"


def emit(ledger: pathlib.Path, project: str | None, constraints: list[str],
         credentials: list[str], project_root: str | None = None) -> dict:
    ledger = ledger.resolve()
    topic, stages = _read_ledger(ledger)
    root = _root(ledger, project_root)
    profile, identity = _profile(root)
    names = {s["id"]: s["name"] for s in profile}
    if not stages:
        raise SystemExit("stage_checkpoint: no `stage:` line yet — a checkpoint follows a gate")
    sid, name, gate, verdict, at, line = stages[-1]
    state = _load_state(ledger, strict=True)
    run = run_key(ledger.read_text(encoding="utf-8").splitlines())
    binding = {**identity, "run": run}
    previous = state.get("profile")
    if previous is None and state.get("workflowId") and identity["source"] != "bundled-default":
        raise SystemExit("stage_checkpoint: legacy workflow has no selected-profile binding; reconcile before emitting")
    if previous is not None and previous != binding:
        raise SystemExit("stage_checkpoint: selected profile or run changed; reconcile the saved workflow before emitting")
    for observed in stages:
        selected = next((s for s in profile if s["id"] == observed[0]), None)
        if selected is None or (identity["source"] != "bundled-default" and
                                (selected["name"] != observed[1] or selected["gate"] != observed[2])):
            raise SystemExit("stage_checkpoint: ledger stage does not match the selected profile")
    # CONSTRAINTS AND KEYS OUTLIVE THE BOUNDARY THEY WERE GIVEN AT. The operator states them
    # once; a later boundary that dropped them would hand a successor an empty list — the
    # one thing a successor must never act without (found by the live receipt, 2026-10-05).
    constraints = list(dict.fromkeys([*state.get("constraints", []), *constraints]))
    credentials = list(dict.fromkeys([*state.get("credentials", []), *credentials]))
    reviews = _reviews(ledger)
    done = [{"step_id": f"stage-{s[0]}", "result": f"{s[1]}: gate {s[2]}, verdict {s[3]} at {s[4]}",
             "evidence": [f"ledger: {ledger.name}", *reviews.get(s[0], [])]}
            for s in stages if s[3] in ("pass", "skip")]
    position = next(i for i, s in enumerate(profile) if s["id"] == sid)
    terminal = position == len(profile) - 1
    closed = terminal and verdict == "pass"
    if closed:
        open_steps = []
    elif verdict in ("pass", "skip") and not terminal:
        nxt = profile[position + 1]["id"]
        open_steps = [{"step_id": f"stage-{nxt}", "next_action": f"enter stage {nxt} {names[nxt]}"}]
    else:
        action = (f"confirm stage {sid} {name}: final stage was skipped" if verdict == "skip"
                  else f"repair stage {sid} {name}: its gate did not pass")
        open_steps = [{"step_id": f"stage-{sid}", "next_action": action}]
    creds = []
    for c in credentials:
        parts = c.split("/")
        if len(parts) != 3 or not all(parts):
            raise SystemExit("stage_checkpoint: --credential is PROJECT/ENV/NAME, a name never a value")
        creds.append({"project": parts[0], "env": parts[1], "name": parts[2]})
    artifacts = []
    branch, head = _git(root, "rev-parse", "--abbrev-ref", "HEAD"), _git(root, "rev-parse", "HEAD")
    if head:
        artifacts.append({"kind": "git", "path": str(root), "branch": branch or "", "head": head[:12]})
    body = {"goal": topic,
            "plan": [{"step_id": f"stage-{i}", "title": names[i]} for i in names],
            "done": done, "open": open_steps, "constraints": constraints,
            "artifacts": artifacts, "notes": f"task-pipeline stage boundary; run ledger {ledger}"}
    if creds:
        body["credentials"] = creds
    key = f"{topic}\n{line}"
    if identity["source"] != "bundled-default":
        key += "\n" + identity["digest"]
    args = {"owner": OWNER,
            "idempotencyKey": "tp-" + hashlib.sha256(key.encode()).hexdigest()[:32],
            "stepId": f"stage-{sid}", "status": STATUS.get(verdict, "in_progress"), "body": body,
            "close": closed}
    if state.get("workflowId") and state.get("leaseId"):
        args["workflowId"], args["leaseId"] = state["workflowId"], state["leaseId"]
    else:
        args["projectId"] = _project(root, project)
    if (previous != binding or constraints != state.get("constraints", []) or
            credentials != state.get("credentials", [])):
        _save_state(ledger, {**state, "constraints": constraints, "credentials": credentials,
                             "profile": binding})
    return args


def record(ledger: pathlib.Path, answer_text: str | None, unavailable: str | None,
           for_run: bool = False) -> str:
    if unavailable is not None:
        reason = " ".join(unavailable.split())[:200] or "no reason given"
        if for_run:
            # ONE marker for the run (CHANGELOG, Unreleased). Without it a run on a machine with no
            # Observatory paid one nudge and one ledger line per gate — about eleven of
            # each — to restate a fact that does not change between gates.
            # The marker carries the run key (topic and start date, hashed): the hook and
            # `state` honour it only while the ledger names the same run AND still carries this
            # line, so a marker left on disk — even after a same-day reseed — cannot silence
            # the next run.
            try:
                key = run_key(ledger.read_text(encoding="utf-8").splitlines())
            except OSError:
                key = None
            if key is None:
                raise UsageError("--for-run needs the ledger's `Run:` line: the marker is "
                                 "keyed to the run, and a ledger that names no run has none")
            line = f"event: memory — unavailable for this run — {reason} — {_now()}"
            state = _load_state(ledger)
            state["memory"] = {"unavailable": {"reason": reason, "at": _now(), "ledger_line": line,
                                               "run": key}}
            _save_state(ledger, state)
        else:
            line = f"event: memory — unavailable — {reason} — {_now()}"
            state = _load_state(ledger)
            if state.get("memory") and marker_for_this_run(ledger, state) is None:
                state.pop("memory")  # another run's marker: cleared, not inherited
                _save_state(ledger, state)
        _append(ledger, line)
        return line
    try:
        answer = json.loads(answer_text or "")
    except ValueError:
        raise SystemExit("stage_checkpoint: the answer is not JSON")
    if not isinstance(answer, dict):
        raise SystemExit("stage_checkpoint: the answer is not an object")
    state = _load_state(ledger)
    # Any answer — a checkpoint or a refusal — means the tools answered: the run-level
    # "unavailable" marker no longer holds, and the nudge comes back.
    cleared = state.pop("memory", None) is not None
    if answer.get("error"):
        kept = answer.get("keptAs")
        if answer["error"] in ("LeaseLost", "WorkflowClosed"):
            # A stale writer stops here: the token is dropped and the next boundary starts
            # by reading the workflow, not by writing to it again.
            state.pop("leaseId", None)
            state["stale"] = answer["error"]
            _save_state(ledger, state)
        line = (f"event: memory — refused {answer['error']}"
                f"{f' (kept as {kept})' if kept else ''} — {_now()}")
        if cleared:
            _save_state(ledger, state)
        _append(ledger, line)
        return line
    if answer.get("handoffId") and not answer.get("leaseId"):
        if cleared:
            _save_state(ledger, state)
        # An offer: the lease stays with this run until the successor accepts.
        line = f"event: memory — handoff offered {answer['handoffId']} — {_now()}"
        _append(ledger, line)
        return line
    wid = (answer.get("workflowId") or (answer.get("checkpoint") or {}).get("workflowId")
           or state.get("workflowId"))
    lease = answer.get("leaseId") or state.get("leaseId")
    if not wid:
        raise SystemExit("stage_checkpoint: the answer names no workflowId")
    _save_state(ledger, {**{k: v for k, v in state.items() if k in ("constraints", "credentials", "profile")},
                         "workflowId": wid, **({"leaseId": lease} if lease else {})})
    rev = (answer.get("checkpoint") or {}).get("revision") or answer.get("revision") or "?"
    step = answer.get("stepId") or "?"
    line = f"event: memory — checkpoint {step} rev {rev} {wid} — {_now()}"
    _append(ledger, line)
    return line


def handoff(ledger: pathlib.Path, provider: str, model: str | None, reason: str,
            ttl: int) -> dict:
    """`observatory_handoff_create` arguments for a PLANNED change of executor (R11).

    Without this the only way a workflow moved was a refusal: the next executor wrote,
    got `LeaseLost`, and read the workflow after the fact. A planned move offers it
    instead — the lease stays with this run until the successor accepts, and the pack
    the successor receives is assembled by Observatory from the last checkpoint.
    """
    state = _load_state(ledger)
    if not state.get("workflowId"):
        raise SystemExit("stage_checkpoint: no workflow yet — write a checkpoint first "
                         "(emit → observatory_checkpoint_write → record)")
    to = {"provider": provider, **({"model": model} if model else {})}
    # Observatory digests the whole request, TTL included, so the TTL is in the key (another
    # TTL is another offer, not an idempotency conflict). So is the count of memory events the
    # ledger holds: once an offer (or a checkpoint) is recorded that count grows, and offering
    # again after it lapsed is a new offer — the same key would replay the first, expired
    # answer. ONLY memory events count. The whole ledger length did, until 1.93.3: a `gate:`
    # line from hooks/gate-observer.sh or a `record --unavailable` line between two retries
    # made the retry a NEW offer, and Observatory replaces an unaccepted older offer with it.
    try:
        seen = sum(1 for ln in ledger.read_text(encoding="utf-8").splitlines()
                   if MEMORY_EVENT.match(ln) and not MEMORY_UNAVAILABLE.match(ln))
    except OSError:
        seen = 0
    key = hashlib.sha256(f"{state['workflowId']}\n{json.dumps(to, sort_keys=True)}\n{reason}"
                         f"\n{ttl}\n{seen}".encode()).hexdigest()[:32]
    args = {"owner": OWNER, "idempotencyKey": "tp-ho-" + key, "workflowId": state["workflowId"],
            "to": to, "reason": reason, "offerTtlSeconds": ttl}
    if state.get("leaseId"):
        args["leaseId"] = state["leaseId"]
    return args


def accept(ledger: pathlib.Path, handoff_id: str, session: str | None) -> dict:
    """`observatory_handoff_accept` arguments for the successor, before its first write."""
    if not handoff_id.startswith("handoff:"):
        raise SystemExit("stage_checkpoint: a handoff id starts with 'handoff:'")
    args = {"owner": OWNER,
            "idempotencyKey": "tp-ac-" + hashlib.sha256(handoff_id.encode()).hexdigest()[:32],
            "handoffId": handoff_id}
    if session:
        args["sessionId"] = session
    return args


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="stage_checkpoint.py",
                                description="A workflow checkpoint at every stage boundary.")
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("emit", help="print the checkpoint tool's arguments")
    e.add_argument("--ledger", default=DEFAULT_LEDGER)
    e.add_argument("--project-root", help="explicit project root for a relocated ledger")
    e.add_argument("--project", help="project:<slug>; default the checkout's folder name")
    e.add_argument("--constraint", action="append", default=[], help="repeatable")
    e.add_argument("--credential", action="append", default=[], help="PROJECT/ENV/NAME, repeatable")
    r = sub.add_parser("record", help="keep the answer, or record that memory is unavailable")
    r.add_argument("--ledger", default=DEFAULT_LEDGER)
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--answer", help="a file with the tool's JSON answer, or - for stdin")
    g.add_argument("--unavailable", help="why the tools could not be used")
    r.add_argument("--for-run", action="store_true",
                   help="with --unavailable: once for the whole run; silences the nudge until an answer")
    s = sub.add_parser("state", help="the workflow this run writes to; never the token")
    s.add_argument("--ledger", default=DEFAULT_LEDGER)
    h = sub.add_parser("handoff", help="observatory_handoff_create arguments: a PLANNED executor change")
    h.add_argument("--ledger", default=DEFAULT_LEDGER)
    h.add_argument("--to-provider", required=True)
    h.add_argument("--to-model")
    h.add_argument("--reason", default="plan_route",
                   choices=["limit", "plan_route", "operator", "crash", "restart"])
    h.add_argument("--offer-ttl", type=int, default=3600)
    ac = sub.add_parser("accept", help="observatory_handoff_accept arguments, before the first write")
    ac.add_argument("--ledger", default=DEFAULT_LEDGER)
    ac.add_argument("--handoff-id", required=True)
    ac.add_argument("--session")
    a = p.parse_args(argv)
    ledger = pathlib.Path(a.ledger)
    if a.cmd == "emit":
        print(json.dumps(emit(ledger, a.project, a.constraint, a.credential, a.project_root), ensure_ascii=False))
        return 0
    if a.cmd == "handoff":
        print(json.dumps(handoff(ledger, a.to_provider, a.to_model, a.reason, a.offer_ttl),
                         ensure_ascii=False))
        return 0
    if a.cmd == "accept":
        print(json.dumps(accept(ledger, a.handoff_id, a.session), ensure_ascii=False))
        return 0
    if a.cmd == "state":
        st = _load_state(ledger)
        print(json.dumps({"workflowId": st.get("workflowId"), "holdsLease": bool(st.get("leaseId")),
                          "stale": st.get("stale"),
                          "memoryUnavailable": (marker_for_this_run(ledger, st) or {}).get("reason")}))
        return 0
    text = None
    if a.answer is not None:
        text = sys.stdin.read() if a.answer == "-" else pathlib.Path(a.answer).read_text(encoding="utf-8")
    if a.for_run and a.unavailable is None:
        p.error("--for-run goes with --unavailable")
    try:
        print(record(ledger, text, a.unavailable, a.for_run))
    except UsageError as exc:
        print(f"stage_checkpoint: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
