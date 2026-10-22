#!/usr/bin/env python3
"""The machine a browser run borrows: check its load, record what the run starts, close
exactly that, and prove nothing is left. Stdlib only; macOS and Linux.

    resource_guard.py check  [--max-load-ratio 1.0] [--min-free-gb 5]
                             [--max-memory-pressure normal|warn] [--json]
        before a run and between scenarios: load average against cores, memory pressure,
        free disk. Exit 0 go; 4 wait (over a line: wait, then run with fewer pages).
    resource_guard.py record <ledger.json> <pid> <what> [--cap-kind browser|page|server]
                             [--max-browsers 2] [--max-pages 4] [--max-servers 1]
        after starting a process: append it with its command line. Exit 5 when the cap for
        its kind is already reached; the caller closes something first.
    resource_guard.py close  <ledger.json> [--grace 5]
        at the end: SIGTERM, then SIGKILL after the grace, every RECORDED process that is
        still alive and still the same process (its start time is compared, which survives
        an exec, so a reused pid is never touched), and the descendants it spawned (browser
        helpers, a launcher's child). Nothing else is ever signalled.
    resource_guard.py verify <ledger.json> [--json]
        exit 0 when every recorded process is gone; 1 naming the live ones; 2 when a process
        cannot be inspected (no `ps`): never silently clean. Prints the receipt the
        design-review report carries (`resources`).

The operator's own browser windows are never in the ledger, so they are never touched.
Exit codes: 0 ok · 1 live processes · 2 usage · 4 wait · 5 cap reached.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import tempfile
import shutil
import signal
import subprocess
import sys
import time


def cpu_count():
    return os.cpu_count() or 1


def load_avg():
    try:
        return os.getloadavg()[0]
    except OSError:
        return None


def memory_pressure():
    """'normal' | 'warn' | 'critical' | None (unknown)."""
    if sys.platform == "darwin":
        try:
            out = subprocess.run(["sysctl", "-n", "kern.memorystatus_vm_pressure_level"],
                                 capture_output=True, text=True, timeout=5).stdout.strip()
            return {"1": "normal", "2": "warn", "4": "critical"}.get(out)
        except (OSError, subprocess.SubprocessError):
            return None
    try:
        with open("/proc/meminfo") as fh:
            info = {l.split(":")[0]: int(l.split()[1]) for l in fh if ":" in l}
        avail = info.get("MemAvailable", 0) / max(info.get("MemTotal", 1), 1)
        return "critical" if avail < 0.05 else "warn" if avail < 0.15 else "normal"
    except (OSError, ValueError, IndexError):
        return None


LEVELS = ("normal", "warn", "critical")


def check(max_load_ratio, min_free_gb, max_memory="normal"):
    la, cores = load_avg(), cpu_count()
    mem = memory_pressure()
    free_gb = shutil.disk_usage(os.path.expanduser("~")).free / 1e9
    reasons = []
    if la is not None and la > cores * max_load_ratio:
        reasons.append("load %.1f over %d cores × %.1f" % (la, cores, max_load_ratio))
    if mem in LEVELS and LEVELS.index(mem) > LEVELS.index(max_memory):
        reasons.append("memory pressure %s over %s" % (mem, max_memory))
    if free_gb < min_free_gb:
        reasons.append("free disk %.1f GB under %.0f GB" % (free_gb, min_free_gb))
    return dict(go=not reasons, load=la, cores=cores, memory=mem or "unknown",
                free_gb=round(free_gb, 1), reasons=reasons)


class Uninspectable(Exception):
    pass


def exists(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


# Every ps runs in one locale and one zone: `lstart` is a different string under each, and a
# start time read under another TZ would make a live process look like a stranger.
PS_ENV = dict(os.environ, LC_ALL="C", LANG="C", TZ="UTC")


def ps_field(pid, field):
    """A `ps -o <field>=` value for one pid; None when the pid is gone; Uninspectable when
    `ps` itself cannot run (the caller must not read that as gone)."""
    try:
        out = subprocess.run(["ps", "-o", field + "=", "-p", str(pid)], capture_output=True,
                             text=True, timeout=5, env=PS_ENV)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Uninspectable("ps unavailable (%s)" % exc)
    if out.returncode not in (0, 1):
        raise Uninspectable("ps exited %s" % out.returncode)
    return out.stdout.strip() or None


def started(pid):
    return ps_field(pid, "lstart")


def alive_same(entry):
    """True: the recorded process is still running (same pid, same start time). False: it is
    gone, or the pid now belongs to another process. Uninspectable: cannot tell."""
    if not exists(entry["pid"]):
        return False
    now = started(entry["pid"])
    if now is None:
        return False
    return now == entry.get("started")


def descendants(pids):
    """Every live descendant of the given pids, from one `ps -A -o pid=,ppid=` table."""
    try:
        out = subprocess.run(["ps", "-A", "-o", "pid=,ppid="], capture_output=True, text=True, timeout=5,
                             env=PS_ENV).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        raise Uninspectable("ps unavailable (%s)" % exc)
    kids = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            kids.setdefault(int(parts[1]), []).append(int(parts[0]))
    seen, todo = set(), list(pids)
    while todo:
        p = todo.pop()
        for c in kids.get(p, []):
            if c not in seen:
                seen.add(c)
                todo.append(c)
    return sorted(seen)


def load_ledger(path):
    if not os.path.exists(path):
        return {"schema": "resource-ledger/1", "started": []}
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if doc.get("schema") != "resource-ledger/1" or not isinstance(doc.get("started"), list):
        raise ValueError("not a resource-ledger/1 file")
    return doc


def save_ledger(path, doc):
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".resource-ledger.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


class locked:
    """An exclusive lock on the ledger's sidecar for a whole read-modify-write: two agents
    recording at once both land."""
    def __init__(self, path):
        self.lock = os.path.abspath(path) + ".lock"

    def __enter__(self):
        os.makedirs(os.path.dirname(self.lock), exist_ok=True)
        self.fh = open(self.lock, "a")
        fcntl.flock(self.fh, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()


def ancestors():
    """This process and every ancestor up to pid 1: never recorded, never signalled."""
    out, p = {os.getpid()}, os.getpid()
    for _ in range(64):
        try:
            pp = int(ps_field(p, "ppid") or 0)
        except ValueError:
            break
        if pp <= 1 or pp in out:
            break
        out.add(pp)
        p = pp
    return out | {1}


def record(path, pid, what, kind, caps):
    if int(pid) in ancestors():
        return 2, "pid %s is this process, one of its ancestors or pid 1: never recorded" % pid
    with locked(path):
        doc = load_ledger(path)
        live = [e for e in doc["started"] if e.get("kind") == kind and alive_same(e)]
        if len(live) >= caps[kind]:
            return 5, "cap reached: %d live %s(s), the cap is %d; close one first" % (len(live), kind, caps[kind])
        if not exists(pid):
            return 2, "pid %s is not running; nothing to record" % pid
        st = started(pid)
        if not st:
            return 2, "pid %s is not running; nothing to record" % pid
        doc["started"].append(dict(pid=int(pid), what=what, kind=kind, started=st,
                                   command=ps_field(pid, "command") or "", at=int(time.time())))
        save_ledger(path, doc)
        return 0, "recorded %s %s (%s)" % (kind, pid, what)


def close(path, grace):
    with locked(path):
        doc = load_ledger(path)
    keep = ancestors()
    alive = [e for e in doc["started"] if alive_same(e)]
    # A protected pid (this process, an ancestor, pid 1) in the ledger is refused with its whole
    # subtree: its descendants are the operator's session, never this run's.
    protected = [e["pid"] for e in alive if e["pid"] in keep]
    targets = [e for e in alive if e["pid"] not in keep]
    # Children first are found while their parents still live; each keeps its own start time
    # so a pid reused during the grace is not signalled.
    kids = [dict(pid=k, started=started(k)) for k in descendants([e["pid"] for e in targets])]
    victims = [dict(pid=e["pid"], started=e["started"]) for e in targets] + \
              [k for k in kids if k["started"] and k["pid"] not in keep]
    refused = list(protected)
    for v in victims:
        try:
            os.kill(v["pid"], signal.SIGTERM)
        except ProcessLookupError:
            pass
        except PermissionError:
            refused.append(v["pid"])
    deadline = time.time() + grace
    while time.time() < deadline and any(alive_same(v) for v in victims):
        time.sleep(0.2)
    for v in victims:
        if v["pid"] not in refused and alive_same(v):
            try:
                os.kill(v["pid"], signal.SIGKILL)
            except ProcessLookupError:
                pass
            except PermissionError:
                refused.append(v["pid"])
    skipped = [e["pid"] for e in doc["started"] if e not in targets]
    return [e["pid"] for e in targets], [k["pid"] for k in kids], skipped, refused


def verify(path):
    doc = load_ledger(path)
    live = [e["pid"] for e in doc["started"] if alive_same(e)]
    return dict(started=[dict(pid=e["pid"], what=e["what"], kind=e.get("kind")) for e in doc["started"]],
                live=live, closed=not live)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--max-load-ratio", type=float, default=1.0)
    c.add_argument("--min-free-gb", type=float, default=5)
    c.add_argument("--max-memory-pressure", default="normal", choices=("normal", "warn"))
    c.add_argument("--json", action="store_true")
    r = sub.add_parser("record")
    r.add_argument("ledger")
    r.add_argument("pid", type=int)
    r.add_argument("what")
    r.add_argument("--cap-kind", dest="kind", default="browser", choices=("browser", "page", "server"))
    r.add_argument("--max-browsers", type=int, default=2)
    r.add_argument("--max-pages", type=int, default=4)
    r.add_argument("--max-servers", type=int, default=1)
    k = sub.add_parser("close")
    k.add_argument("ledger")
    k.add_argument("--grace", type=float, default=5)
    v = sub.add_parser("verify")
    v.add_argument("ledger")
    v.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "check":
            res = check(a.max_load_ratio, a.min_free_gb, a.max_memory_pressure)
            if a.json:
                print(json.dumps(res, indent=2))
            else:
                print("resource_guard: %s · load %s/%d cores · memory %s · free %.1f GB%s" % (
                    "go" if res["go"] else "wait", res["load"], res["cores"], res["memory"], res["free_gb"],
                    "" if res["go"] else " · " + "; ".join(res["reasons"])))
            return 0 if res["go"] else 4
        if a.cmd == "record":
            caps = dict(browser=a.max_browsers, page=a.max_pages, server=a.max_servers)
            code, msg = record(a.ledger, a.pid, a.what, a.kind, caps)
            print("resource_guard: %s" % msg, file=sys.stderr if code else sys.stdout)
            return code
        if a.cmd == "close":
            closed, kids, skipped, refused = close(a.ledger, a.grace)
            print("resource_guard: closed %d recorded process(es) and %d descendant(s); %d already gone"
                  % (len(closed), len(kids), len(skipped))
                  + ("; refused (permission): %s" % ", ".join(map(str, refused)) if refused else ""))
            return 1 if refused else 0
        res = verify(a.ledger)
        # The zero-byte lock sidecar stays: unlinking it while another agent holds it would let
        # two writers in. It lives beside the ledger in .task-pipeline/, outside the tracked tree.
        if a.json:
            print(json.dumps(res, indent=2))
        else:
            print("resource_guard: %s · %d started · live: %s" % (
                "clean" if res["closed"] else "LIVE", len(res["started"]), ", ".join(map(str, res["live"])) or "none"))
        return 0 if res["closed"] else 1
    except Uninspectable as exc:
        print("resource_guard: NOT_RUN: %s; a process that cannot be inspected is never reported gone" % exc,
              file=sys.stderr)
        return 2
    except (ValueError, OSError) as exc:
        print("resource_guard: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
