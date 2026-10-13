"""One safe lock for fixed /tmp scratch paths shared by family test runners."""
# shared-mechanism: negative_lock.py — identical owner-only test helper in three members.
# diverges: none
import os
import stat


def scratch_lock_path():
    return os.path.join(os.path.realpath('/tmp'), 'sshlg-family-negatives.lock')


def _admit(info):
    if not stat.S_ISREG(info.st_mode):
        raise RuntimeError('scratch lock must be a regular file')
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1:
        raise RuntimeError('scratch lock must be privately owned, mode600, with one link')


def acquire_scratch_lock():
    """Return a held file; close/process exit releases it. Never unlink or steal."""
    try:
        import fcntl
    except ImportError:
        raise RuntimeError('scratch serialization unavailable: flock is required') from None
    if not hasattr(os, 'O_NOFOLLOW'):
        raise RuntimeError('scratch serialization unavailable: no-follow open is required')
    path = scratch_lock_path()
    try:
        _admit(os.lstat(path))
    except FileNotFoundError:
        pass
    flags = os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK
    try:
        fd = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        fd = os.open(path, flags)
    held = None
    try:
        info = os.fstat(fd)
        _admit(info)
        named = os.lstat(path)
        _admit(named)
        if (info.st_dev, info.st_ino) != (named.st_dev, named.st_ino):
            raise RuntimeError('scratch lock identity changed')
        held = os.fdopen(fd, 'r+')
        try:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('another family runner holds the fixed scratch namespace — waiting', flush=True)
            fcntl.flock(held, fcntl.LOCK_EX)
        named = os.lstat(path)
        _admit(named)
        if (info.st_dev, info.st_ino) != (named.st_dev, named.st_ino):
            raise RuntimeError('scratch lock identity changed while waiting')
        return held
    except BaseException:
        if held is None:
            os.close(fd)
        else:
            held.close()
        raise


class ScratchProcesses:
    """Hold writer admission through supported synchronous plant subprocesses.

    Bash and ordinary exec descendants inherit the lock. Deliberately detached
    descendants that close inherited descriptors are outside this protocol.
    """
    def __init__(self):
        import threading
        self.lock = None
        self._active = set()
        self._mutex = threading.RLock()
        self._cancelled = threading.Event()
        self._handlers = {}

    def __enter__(self):
        import signal
        import threading
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError('plant lifecycle must start on the main thread')
        for sig in (signal.SIGINT, signal.SIGTERM):
            self._handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, self._interrupt)
        return self

    def _interrupt(self, signum, _frame):
        # Record cancellation without raising inside Popen before registration.
        # The next admission/result check refuses; an in-flight spawn is drained.
        self.cancel()
        if self.lock is None:
            # No child can exist before admission; interrupt a blocking flock.
            raise InterruptedError(f'plant lock wait interrupted by signal {signum}')

    def hold(self, lock):
        if self.lock is not None:
            raise RuntimeError('plant lock already bound')
        self.lock = lock
        return lock

    def check_running(self):
        if self._cancelled.is_set():
            raise InterruptedError('plant runner cancelled; no new child admitted')

    @staticmethod
    def _signal_group(proc, sig):
        # Reap an exited leader first: macOS can report EPERM for its zombie group.
        # Another thread may hold the zombie unreaped, so EPERM is still possible:
        # a group whose members have all exited has nothing left to signal.
        proc.poll()
        try:
            os.killpg(proc.pid, sig)
        except (ProcessLookupError, PermissionError):
            pass

    @staticmethod
    def _group_exists(proc, settle=1.0):
        # macOS answers EPERM for a group of unreaped zombies; Linux reports them
        # as present until init reaps them. Give reaping a bounded moment.
        import time
        stop = time.monotonic() + settle
        while True:
            try:
                os.killpg(proc.pid, 0)
            except (ProcessLookupError, PermissionError):
                return False
            if time.monotonic() >= stop:
                return True
            time.sleep(0.02)

    def cancel(self):
        import signal
        import time
        already = self._cancelled.is_set()
        self._cancelled.set()
        with self._mutex:
            active = tuple(self._active)
        for proc in active:
            self._signal_group(proc, signal.SIGTERM)
        if not already:
            # A descendant may ignore TERM while holding captured output pipes.
            # Escalate here, before ThreadPoolExecutor waits for its workers.
            time.sleep(0.1)
            for proc in active:
                self._signal_group(proc, signal.SIGKILL)

    def _drain(self, proc):
        import signal
        import subprocess
        self._signal_group(proc, signal.SIGTERM)
        try:
            proc.communicate(timeout=0.5)
        except subprocess.TimeoutExpired:
            pass
        # The Bash leader can exit before a descendant. Signal the owned group,
        # not just proc.kill(), before waiting for inherited output pipes to close.
        self._signal_group(proc, signal.SIGKILL)
        proc.communicate()

    def run(self, args, *, cwd, timeout=None):
        import subprocess
        if self.lock is None:
            raise RuntimeError('plant writer has no scratch lock')
        with self._mutex:
            self.check_running()
            proc = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True,
                                    start_new_session=True,
                                    pass_fds=(self.lock.fileno(),))
            self._active.add(proc)
        try:
            self.check_running()
            stdout, stderr = proc.communicate(timeout=timeout)
            self.check_running()
            if self._group_exists(proc):
                raise RuntimeError('plant left a live process group after Bash exit')
            return subprocess.CompletedProcess(args, proc.returncode, stdout, stderr)
        except BaseException:
            try:
                self.cancel()
            finally:
                self._drain(proc)
            raise
        finally:
            with self._mutex:
                self._active.discard(proc)

    def __exit__(self, kind, _value, _traceback):
        import signal
        try:
            if kind is not None:
                self.cancel()
            with self._mutex:
                active = tuple(self._active)
            for proc in active:
                self._drain(proc)
            if self.lock is not None:
                # Never LOCK_UN: descendants share the open-file description.
                # Closing our copy cannot release their inherited references.
                self.lock.close()
        finally:
            for sig, handler in self._handlers.items():
                signal.signal(sig, handler)
