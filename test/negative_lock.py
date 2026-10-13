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
