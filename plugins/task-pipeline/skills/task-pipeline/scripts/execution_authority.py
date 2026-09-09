#!/usr/bin/env python3
"""A durable, single-writer execution authority for the work graph (PF-01.02).

The defect this closes: `graph.py next` computes a FRONTIER and prints it, and
two independent `next` runs both read N-001 `pending` and both dispatched it.
`next` is advisory — it says what COULD run, not who MAY. Who may run a node is
a separate, durable decision, and it is this module's, not the frontier's.

`BEGIN IMMEDIATE` takes SQLite's write lock for the whole read-modify-write, so
two concurrent `claim`s serialise and exactly one wins. The winner gets an
attempt record — owner (a session/attempt identity), a monotonic FENCE token, a
node revision and an expiry — matching `execution-attempt.schema.json`. A stale
holder that wakes and writes carries an OLD fence and is refused; an expired
holder is reclaimable, and the reclaim mints a higher fence.

Deliberate boundaries, stated so a later reader does not assume more:

* **Local filesystem only.** SQLite's locking is a single-host guarantee; this
  makes NO promise on a network share or NAS. Distributed execution is the
  Fabric adapter's job, and `authority_for()` is the seam it will replace.
* **Fail-closed.** If the database cannot be opened or the arbitration cannot
  run, `claim` RAISES rather than returning a grant. `graph.py` external mode
  turns that into a blocked dispatch — no work starts on an authority that
  could not answer.
* **The OS lock is not held for the LLM run.** `claim` takes the write lock for
  milliseconds, records the grant, and releases. The lease (expiry + fence) is
  what bounds the run, not a held file handle — a crashed holder frees its node
  by expiry, not by a lock nobody will release.

Standard library only (`sqlite3`). No network, no third-party package.
"""
import os
import sqlite3

SCHEMA_VERSION = "execution-attempt/1"

_DDL = """
CREATE TABLE IF NOT EXISTS attempts (
    node        TEXT PRIMARY KEY,
    owner       TEXT NOT NULL,
    attempt     INTEGER NOT NULL,
    revision    INTEGER NOT NULL,
    fence       INTEGER NOT NULL,
    expiry      REAL NOT NULL,
    state       TEXT NOT NULL,
    installed_at REAL
);
CREATE TABLE IF NOT EXISTS fence_seq (
    id    INTEGER PRIMARY KEY CHECK (id = 1),
    value INTEGER NOT NULL
);
INSERT OR IGNORE INTO fence_seq (id, value) VALUES (1, 0);
"""


class AuthorityUnavailable(RuntimeError):
    """Arbitration could not run. Fail-closed: the caller must NOT start work."""


class Authority:
    def __init__(self, path):
        self.path = path
        try:
            # isolation_level=None → explicit transaction control (BEGIN IMMEDIATE).
            self._db = sqlite3.connect(path, timeout=30, isolation_level=None)
            self._db.execute("PRAGMA journal_mode=WAL;")
            self._db.executescript(_DDL)
        except sqlite3.Error as e:
            raise AuthorityUnavailable(f"cannot open authority at {path}: {e}") from e

    # -- helpers ---------------------------------------------------------------

    def _next_fence(self):
        self._db.execute("UPDATE fence_seq SET value = value + 1 WHERE id = 1;")
        return self._db.execute("SELECT value FROM fence_seq WHERE id = 1;").fetchone()[0]

    @staticmethod
    def _iso(ts):
        # ISO-8601 UTC without pulling datetime.now (kept caller-supplied for testability).
        import datetime
        return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc)\
            .strftime("%Y-%m-%dT%H:%M:%SZ")

    def _grant(self, row):
        node, owner, attempt, revision, fence, expiry, state, installed = row
        g = {
            "schema_version": SCHEMA_VERSION, "node": node, "owner": owner,
            "attempt": attempt, "revision": revision, "fence": fence,
            "expiry": self._iso(expiry), "state": state,
        }
        if installed is not None:
            g["installed_at"] = self._iso(installed)
        return g

    # -- the one arbitrated decision ------------------------------------------

    def claim(self, node, owner, revision, now, ttl_seconds=1800):
        """Atomically move a node ready→claimed for ONE owner. Returns the grant
        dict on success, or None when another owner holds a LIVE claim. Raises
        AuthorityUnavailable if the transaction cannot run (fail-closed)."""
        try:
            self._db.execute("BEGIN IMMEDIATE;")
        except sqlite3.Error as e:
            raise AuthorityUnavailable(f"cannot begin arbitration: {e}") from e
        try:
            cur = self._db.execute(
                "SELECT node, owner, attempt, revision, fence, expiry, state, installed_at "
                "FROM attempts WHERE node = ?;", (node,)).fetchone()
            if cur is not None:
                _n, c_owner, c_attempt, _r, _f, c_expiry, c_state, _i = cur
                live = c_state == "claimed" and now < c_expiry
                if live and c_owner != owner:
                    self._db.execute("COMMIT;")
                    return None                      # a live claim by someone else: this run LOSES
                attempt = c_attempt + 1              # reclaim of an expired/own hold increments
            else:
                attempt = 1
            fence = self._next_fence()
            expiry = now + ttl_seconds
            self._db.execute(
                "INSERT INTO attempts (node, owner, attempt, revision, fence, expiry, state, installed_at) "
                "VALUES (?, ?, ?, ?, ?, ?, 'claimed', ?) "
                "ON CONFLICT(node) DO UPDATE SET owner=excluded.owner, attempt=excluded.attempt, "
                "revision=excluded.revision, fence=excluded.fence, expiry=excluded.expiry, "
                "state='claimed', installed_at=excluded.installed_at;",
                (node, owner, attempt, revision, fence, expiry, now))
            row = self._db.execute(
                "SELECT node, owner, attempt, revision, fence, expiry, state, installed_at "
                "FROM attempts WHERE node = ?;", (node,)).fetchone()
            self._db.execute("COMMIT;")
            return self._grant(row)
        except sqlite3.Error as e:
            self._db.execute("ROLLBACK;")
            raise AuthorityUnavailable(f"arbitration failed: {e}") from e

    def renew(self, node, owner, fence, now, ttl_seconds=1800):
        """Extend the lease only for the current fence-holder. A stale fence is
        refused (the zombie guard). Returns the grant or None."""
        self._db.execute("BEGIN IMMEDIATE;")
        try:
            cur = self._db.execute(
                "SELECT fence, owner FROM attempts WHERE node = ?;", (node,)).fetchone()
            if not cur or cur[0] != fence or cur[1] != owner:
                self._db.execute("COMMIT;")
                return None
            self._db.execute("UPDATE attempts SET expiry = ? WHERE node = ?;",
                             (now + ttl_seconds, node))
            row = self._db.execute(
                "SELECT node, owner, attempt, revision, fence, expiry, state, installed_at "
                "FROM attempts WHERE node = ?;", (node,)).fetchone()
            self._db.execute("COMMIT;")
            return self._grant(row)
        except sqlite3.Error as e:
            self._db.execute("ROLLBACK;")
            raise AuthorityUnavailable(f"renew failed: {e}") from e

    def release(self, node, owner, fence):
        """Release a hold the caller actually owns (matching fence). Returns True
        when a row was cleared."""
        self._db.execute("BEGIN IMMEDIATE;")
        try:
            cur = self._db.execute(
                "SELECT fence, owner FROM attempts WHERE node = ?;", (node,)).fetchone()
            if not cur or cur[0] != fence or cur[1] != owner:
                self._db.execute("COMMIT;")
                return False
            self._db.execute("DELETE FROM attempts WHERE node = ?;", (node,))
            self._db.execute("COMMIT;")
            return True
        except sqlite3.Error as e:
            self._db.execute("ROLLBACK;")
            raise AuthorityUnavailable(f"release failed: {e}") from e

    def holder(self, node):
        row = self._db.execute(
            "SELECT node, owner, attempt, revision, fence, expiry, state, installed_at "
            "FROM attempts WHERE node = ?;", (node,)).fetchone()
        return self._grant(row) if row else None

    def close(self):
        try:
            self._db.close()
        except sqlite3.Error:
            pass


def authority_for(path):
    """The seam a Fabric adapter replaces for distributed execution. Today it
    returns the local SQLite authority; fail-closed if it cannot be built."""
    if not path:
        raise AuthorityUnavailable("no authority path given — external mode needs one")
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.isdir(parent):
        raise AuthorityUnavailable(f"authority directory does not exist: {parent}")
    return Authority(path)
