#!/usr/bin/env python3
"""Actual owned lock subprocesses; never touch public scratch or run a plant."""
import importlib.util
import json
import os
from pathlib import Path
import select
import signal
import stat
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / 'test/negative_lock.py'
spec = importlib.util.spec_from_file_location('negative_lock', HELPER)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
count = 0

def check(ok, label):
    global count
    assert ok, label
    count += 1

def line(proc, timeout=5):
    assert select.select([proc.stdout], [], [], timeout)[0], 'owned child output timeout'
    return proc.stdout.readline().strip()

with tempfile.TemporaryDirectory(prefix='fw07-scratch-lock-') as folder:
    base = Path(folder); shared = base / 'shared'; shared.mkdir()
    lockpath = shared / 'sshlg-family-negatives.lock'
    worker = base / 'worker.py'
    worker.write_text('''import importlib.util,os,pathlib,sys
s=importlib.util.spec_from_file_location('lock',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
if sys.argv[2]=='identity':print(m.scratch_lock_path());sys.exit(0)
m.scratch_lock_path=lambda:sys.argv[2]
try:held=m.acquire_scratch_lock()
except (OSError,RuntimeError) as e:print('REFUSED:'+type(e).__name__,flush=True);sys.exit(4)
print('ACQUIRED:'+str(os.fstat(held.fileno()).st_ino),flush=True)
sys.stdin.readline();held.close()
''')
    identities = []
    for label in ('task-pipeline', 'seo-aeo-audit', 'sheleg-dev'):
        tmp = base / label; tmp.mkdir()
        r = subprocess.run([sys.executable, '-B', str(worker), str(HELPER), 'identity'],
                           cwd=tmp, env=dict(os.environ, TMPDIR=str(tmp)), text=True, capture_output=True)
        check(r.returncode == 0, 'identity reads without public lock')
        identities.append(r.stdout.strip())
    check(len(set(identities)) == 1 and identities[0] == m.scratch_lock_path(), 'all TMPDIR/cwd identities equal')
    check(Path(identities[0]).parent == Path('/tmp').resolve(), 'physical fixed scratch root')
    children = []
    def start(label):
        p = subprocess.Popen([sys.executable, '-u', '-B', str(worker), str(HELPER), str(lockpath)],
                             cwd=base/label, env=dict(os.environ, TMPDIR=str(base/label)),
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        children.append(p); return p
    try:
        a = start('task-pipeline'); first = line(a)
        check(first.startswith('ACQUIRED:'), 'first owner acquires')
        info = lockpath.stat(); check(stat.S_IMODE(info.st_mode) == 0o600, 'private new file')
        b = start('seo-aeo-audit'); check('waiting' in line(b), 'second owner waits')
        check(not select.select([b.stdout], [], [], .15)[0] and b.poll() is None, 'held inode excludes contender')
        a.stdin.write('\n'); a.stdin.flush(); a.wait(timeout=5)
        check(line(b) == first, 'different TMPDIR owner acquires same inode after release')
        b.stdin.write('\n'); b.stdin.flush(); b.wait(timeout=5)
        c = start('sheleg-dev'); check(line(c) == first, 'third owner same inode')
        c.send_signal(signal.SIGTERM); c.wait(timeout=5)
        d = start('task-pipeline'); check(line(d) == first, 'process exit releases; same owner retries')
        d.stdin.write('\n'); d.stdin.flush(); d.wait(timeout=5)
    finally:
        for child in children:
            if child.poll() is None: child.kill(); child.wait()
            for stream in (child.stdin, child.stdout, child.stderr): stream.close()
    lockpath.write_bytes(b'owned sentinel')
    m.scratch_lock_path = lambda: str(lockpath)
    with m.acquire_scratch_lock(): pass
    check(lockpath.read_bytes() == b'owned sentinel', 'existing bytes not truncated')
    def refused(label):
        try: m.acquire_scratch_lock()
        except (OSError, RuntimeError): check(True, label)
        else: raise AssertionError(label)
    lockpath.chmod(0o644); refused('public mode refuses'); check(stat.S_IMODE(lockpath.stat().st_mode) == 0o644, 'mode not silently changed')
    lockpath.chmod(0o600)
    with patch.object(m.os, 'getuid', return_value=os.getuid()+1): refused('foreign ownership refuses')
    target = shared / 'target'; lockpath.rename(target); lockpath.symlink_to(target)
    refused('symlink refuses'); check(lockpath.is_symlink() and target.read_bytes() == b'owned sentinel', 'symlink target preserved')
    # Actual runner entry with only its lock namespace redirected into this fixture.
    runner = "import sys;sys.path.insert(0,sys.argv[1]);import negatives,negative_lock;negative_lock.scratch_lock_path=lambda:sys.argv[2];sys.exit(negatives.main(['runner','--list']))"
    r = subprocess.run([sys.executable, '-B', '-c', runner, str(ROOT/'test'), str(lockpath)], capture_output=True, text=True)
    check(r.returncode == 1 and 'cannot acquire family scratch lock' in r.stdout, 'actual runner refuses unsafe owned lock before listing/plants')
    check(target.read_bytes() == b'owned sentinel', 'actual runner preserves symlink target')
    lockpath.unlink(); lockpath.write_bytes(b'owned sentinel'); lockpath.chmod(0o600)
    r = subprocess.run([sys.executable, '-B', '-c', runner, str(ROOT/'test'), str(lockpath)], capture_output=True, text=True)
    check(r.returncode == 0 and 'negative self-tests' in r.stdout, 'actual runner listing remains usable with owned lock')
    check(lockpath.read_bytes() == b'owned sentinel', 'actual runner listing does not truncate lock')
    lockpath.unlink(); lockpath.mkdir(); refused('directory refuses'); check(lockpath.is_dir(), 'directory preserved')
    lockpath.rmdir(); os.mkfifo(lockpath); refused('FIFO refuses without open/hang'); check(stat.S_ISFIFO(lockpath.stat().st_mode), 'FIFO preserved')
    lockpath.unlink(); os.link(target, lockpath); refused('hardlink refuses'); check(target.read_bytes() == b'owned sentinel', 'hardlink target preserved')
    lockpath.unlink(); lockpath.write_bytes(b'owned sentinel'); lockpath.chmod(0o600)
    real_open = os.open
    def replace_before_open(path, flags, *args):
        if flags & os.O_EXCL:
            lockpath.unlink(); lockpath.symlink_to(target)
        return real_open(path, flags, *args)
    with patch.object(m.os, 'open', side_effect=replace_before_open): refused('replacement symlink refuses at no-follow open')
    check(target.read_bytes() == b'owned sentinel' and lockpath.is_symlink(), 'replacement target preserved')
print(f'PASS: shared scratch lock — {count} controls; owned namespace only')
