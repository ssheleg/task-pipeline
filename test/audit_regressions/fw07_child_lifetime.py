#!/usr/bin/env python3
"""Owned actual runner/barrier controls; never acquire the public family lock."""
import importlib.util
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / 'test/negative_lock.py'
count = 0

def check(value, name):
    global count
    assert value, name
    count += 1

def wait_file(path, timeout=8):
    stop = time.monotonic() + timeout
    while not path.exists():
        if time.monotonic() > stop:
            raise AssertionError('owned barrier missing: ' + str(path))
        time.sleep(.02)
    return path.read_text()

def line(proc):
    assert select.select([proc.stdout], [], [], 8)[0], 'owned output timeout'
    return proc.stdout.readline().strip()

BOOT = '''import sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import negatives,negative_lock
base=Path(sys.argv[2]); negative_lock.scratch_lock_path=lambda:str(base/'lock')
negatives.ROOT=str(base/'source'); negatives.NEG_DIR=str(base/'source/negatives')
negatives.MIN_EXPECTED=1; negatives.MIN_PROPS=0
sys.exit(negatives.main(['fixture']))
'''
CONTEND = '''import sys,os
sys.path.insert(0,sys.argv[1]);import negative_lock
negative_lock.scratch_lock_path=lambda:sys.argv[2]
with negative_lock.acquire_scratch_lock() as held:
 print('ACQUIRED:'+str(os.fstat(held.fileno()).st_ino),flush=True)
'''
WRITER = '''import os,sys,time,json,signal
from pathlib import Path
b=Path(sys.argv[1]);lock=(b/'lock').stat()
if len(sys.argv)>2:signal.signal(signal.SIGTERM,signal.SIG_IGN)
fds=[]
for fd in range(3,256):
 try:
  s=os.fstat(fd)
  if (s.st_dev,s.st_ino)==(lock.st_dev,lock.st_ino):fds.append(fd)
 except OSError:pass
(b/'ready').write_text(json.dumps({'pid':os.getpid(),'bash':os.getppid(),'fds':fds}))
stop=time.monotonic()+12
while not (b/'go').exists():
 if time.monotonic()>stop:sys.exit(5)
 time.sleep(.02)
(b/'written').write_text('last writer completed')
print('OK: owned writer complete',flush=True)
'''

for killed in ('parent', 'bash', 'term', 'int', 'normal'):
    with tempfile.TemporaryDirectory(prefix='fw07-child-lock-') as tmp:
        base=Path(tmp);source=base/'source';neg=source/'negatives';neg.mkdir(parents=True)
        (source/'writer.py').write_text(WRITER)
        suffix=' ignore-term' if killed in ('term','int') else ''
        script='#!/usr/bin/env bash\n# name: Negative self-test (owned child lifetime)\npython3 '+str(source/'writer.py')+' '+str(base)+suffix+'\n'
        (neg/'001-owned-lifetime.sh').write_text(script)
        parent=subprocess.Popen([sys.executable,'-u','-B','-c',BOOT,str(ROOT/'test'),str(base)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        contender=None;info=None
        try:
            info=json.loads(wait_file(base/'ready'))
            check(bool(info['fds']), killed+': actual writing Python inherits lock')
            inode=(base/'lock').stat().st_ino
            if killed in ('parent','bash'):
                os.kill(parent.pid if killed=='parent' else info['bash'],signal.SIGKILL)
            elif killed in ('term','int'):
                parent.send_signal(signal.SIGTERM if killed=='term' else signal.SIGINT)
                out,err=parent.communicate(timeout=8)
                check(parent.returncode!=0 and 'plant lifecycle refused' in out,killed+': actual runner refuses interruption')
                check(not (base/'written').exists(),killed+': cancelled child did not write')
            contender=subprocess.Popen([sys.executable,'-u','-B','-c',CONTEND,str(ROOT/'test'),str(base/'lock')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            first=line(contender)
            if killed in ('parent','bash','normal'):
                check('waiting' in first,killed+': contender waits for live writer')
                check(not select.select([contender.stdout],[],[],.15)[0] and contender.poll() is None,killed+': no premature admission')
                (base/'go').write_text('release')
                check(wait_file(base/'written')=='last writer completed',killed+': original child final write observed')
                first=line(contender)
            else:
                (base/'go').write_text('release after cancelled runner')
                time.sleep(.05)
                check(not (base/'written').exists(),killed+': no writing descendant survived cancellation')
            check(first=='ACQUIRED:'+str(inode),killed+': same inode admits after lifetime')
            contender.communicate(timeout=8);check(contender.returncode==0,killed+': contender completed')
            out,err=parent.communicate(timeout=8)
            if killed=='normal':check(parent.returncode==0 and 'provably reject' in out,'normal actual runner verdict preserved')
        finally:
            if info:
                try:os.killpg(info['bash'],signal.SIGKILL)
                except ProcessLookupError:pass
                try:os.kill(info['pid'],signal.SIGKILL)
                except ProcessLookupError:pass
            for proc in (parent,contender):
                if proc is not None:
                    if proc.poll() is None:proc.kill()
                    proc.communicate(timeout=5)

# Failure/cancellation must prevent new queued work and restore signal handlers.
spec=importlib.util.spec_from_file_location('owned_negative_lock',HELPER)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='fw07-child-errors-') as tmp:
    base=Path(tmp);m.scratch_lock_path=lambda:str(base/'lock')
    handlers={sig:signal.getsignal(sig) for sig in (signal.SIGINT,signal.SIGTERM)}
    try:
        with m.ScratchProcesses() as plants:
            plants.hold(m.acquire_scratch_lock())
            plants.run(['/definitely/missing/owned-command'],cwd=base)
    except FileNotFoundError:check(True,'spawn error propagated')
    else:raise AssertionError('spawn error accepted')
    check(all(signal.getsignal(s)==h for s,h in handlers.items()),'handlers restored after spawn failure')
    with m.ScratchProcesses() as plants:
        plants.hold(m.acquire_scratch_lock());plants.cancel()
        try:plants.run([sys.executable,'-c','raise SystemExit(0)'],cwd=base)
        except InterruptedError:check(True,'cancelled queue cannot launch')
        else:raise AssertionError('cancelled launch accepted')
    with m.acquire_scratch_lock():check(True,'failed owner releases for safe retry')
# Signals while Popen has created a child but has not returned its handle must
# not lose that child or turn interruption into a successful result.
from unittest.mock import patch
for sig in (signal.SIGINT, signal.SIGTERM):
    with tempfile.TemporaryDirectory(prefix='fw07-child-startup-') as tmp:
        base=Path(tmp);m.scratch_lock_path=lambda:str(base/'lock')
        real_popen=subprocess.Popen
        def interrupted_spawn(*args, **kwargs):
            child=real_popen(*args, **kwargs)
            signal.raise_signal(sig)
            return child
        with m.ScratchProcesses() as plants:
            plants.hold(m.acquire_scratch_lock())
            try:
                with patch.object(subprocess,'Popen',side_effect=interrupted_spawn):
                    plants.run([sys.executable,'-c','import time;time.sleep(10)'],cwd=base)
            except InterruptedError:check(True,'startup signal refuses result')
            else:raise AssertionError('startup signal accepted')
            check(not plants._active,'startup child drained and deregistered')
        with m.acquire_scratch_lock():check(True,'startup cancellation permits retry')

# A communicate failure is a fixture error and must kill/drain the writer,
# including one that ignores TERM, before allowing the next lock holder.
with tempfile.TemporaryDirectory(prefix='fw07-child-communicate-') as tmp:
    base=Path(tmp);m.scratch_lock_path=lambda:str(base/'lock')
    real_popen=subprocess.Popen; children=[]
    def broken_communicate_spawn(*args, **kwargs):
        proc=real_popen(*args, **kwargs);children.append(proc)
        original=proc.communicate;first=True
        def communicate(*a, **k):
            nonlocal first
            if first:
                first=False
                raise OSError('owned communicate fault')
            return original(*a, **k)
        proc.communicate=communicate
        return proc
    with m.ScratchProcesses() as plants:
        plants.hold(m.acquire_scratch_lock())
        try:
            with patch.object(subprocess,'Popen',side_effect=broken_communicate_spawn):
                plants.run([sys.executable,'-c','import time;time.sleep(10)'],cwd=base)
        except OSError as exc:check(str(exc)=='owned communicate fault','communicate error preserved')
        else:raise AssertionError('communicate failure accepted')
        check(all(p.poll() is not None for p in children),'communicate failure drains children')
    with m.acquire_scratch_lock():check(True,'communicate failure permits retry')

# Waiting for another owner must remain interruptible before any plant launches.
for sig in (signal.SIGINT, signal.SIGTERM):
    with tempfile.TemporaryDirectory(prefix='fw07-child-wait-') as tmp:
        base=Path(tmp);neg=base/'source/negatives';neg.mkdir(parents=True)
        (neg/'001-owned.sh').write_text('#!/usr/bin/env bash\n# name: Negative self-test (wait admission)\necho OK: unreachable\n')
        m.scratch_lock_path=lambda:str(base/'lock')
        with m.acquire_scratch_lock() as held:
            waiter=subprocess.Popen([sys.executable,'-u','-B','-c',BOOT,str(ROOT/'test'),str(base)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                check('waiting' in line(waiter),'actual runner waits before mutation')
                waiter.send_signal(sig);out,err=waiter.communicate(timeout=5)
                check(waiter.returncode==1 and 'plant lock wait interrupted' in out,'waiting runner interruption refuses promptly')
            finally:
                if waiter.poll() is None:waiter.kill();waiter.communicate(timeout=5)

print(f'PASS: shared scratch child lifetime — {count} controls; owned namespaces only')
