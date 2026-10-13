#!/usr/bin/env python3
"""Real local Git refs and existing hook; fake expensive suite at Python test seam."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import time
import subprocess
import sys
import tempfile
import types

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('release_candidate', ROOT / 'scripts/release_candidate.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
checks = 0


def git(root, *args):
    r = subprocess.run(['git', *args], cwd=root, text=True, capture_output=True)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout.strip()


def refuse(fn, phrase):
    global checks
    try: fn()
    except (m.Refusal, OSError, ValueError) as e:
        assert phrase in str(e), str(e)
    else: raise AssertionError('accepted: ' + phrase)
    checks += 1


def fake_suite(candidate, code=0, reason=None, extra=''):
    def run(self, stream):
        assert self.git('cat-file', '-t', self.tag) == 'tag'
        assert self.git('rev-parse', self.tag + '^{}') == self.git('rev-parse', 'HEAD')
        stream.write((extra + 'PASS: task-pipeline structure valid\n').encode())
        return code, reason
    candidate._run_suite = types.MethodType(run, candidate)


with tempfile.TemporaryDirectory(prefix='tp-release-candidate-') as folder:
    base = Path(folder); origin = base / 'origin.git'; seed = base / 'seed'
    git(base, 'init', '--bare', str(origin)); git(origin, 'symbolic-ref', 'HEAD', 'refs/heads/main')
    git(base, 'clone', str(origin), str(seed))
    git(seed, 'config', 'user.email', 'fixture@example.invalid'); git(seed, 'config', 'user.name', 'Fixture')
    files = {
        'package.json': json.dumps({'name':'@ssheleg/task-pipeline','version':'1.2.3','scripts':{'test:all':'fixed-owner-suite'}}),
        '.claude-plugin/marketplace.json':json.dumps({'plugins':[{'version':'1.2.3'}]}),
        'plugins/task-pipeline/.claude-plugin/plugin.json':json.dumps({'version':'1.2.3'}),
        'CHANGELOG.md':'## v1.2.3\nFixture\n', 'SKILL-CARD.md':'| **Version** | 1.2.3 |\n',
        'pipeline.json':json.dumps({'stages':[{'id':6,'state':'tests'}]}),
        '.gitignore':'.task-pipeline/\n', m.HOOK:(ROOT / m.HOOK).read_text(),
    }
    for name, text in files.items():
        path=seed/name; path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
    git(seed,'add','.');git(seed,'commit','-m','fixture');git(seed,'push','origin','main')
    index=0
    def fresh(context=True):
        global index
        index+=1; root=base/('case'+str(index))
        git(base,'clone','--no-local',str(origin),str(root))
        git(root,'config','user.email','fixture@example.invalid');git(root,'config','user.name','Fixture')
        if context:
            (root/'.task-pipeline').mkdir()
            (root/'.task-pipeline/run.md').write_text('Run: fixture\nstage: 6 tests — gate manual — verdict pass\n')
        return m.Candidate(root,'v1.2.3')
    def prepared(context=True):
        c=fresh(context);c.prepare(c.root if context else None);fake_suite(c);return c
    def remote_absent():
        assert not git(origin,'tag','-l','v1.2.3')

    c=prepared();assert c.git('cat-file','-t',c.tag)=='tag';remote_absent();checks+=1
    refuse(c.publish,'successful complete receipt')
    c.check();assert c.load()['mechanical_evidence']['release_gap_looked'];checks+=1
    c.publish();assert git(origin,'rev-parse',c.tag)==c.load()['object'];checks+=1
    # Delete only our synthetic fixture remote ref to reset later independent cases.
    git(origin,'tag','-d',c.tag)
    for annotated in (False,True):
        c=fresh();args=['tag']+(['-a','-m','foreign'] if annotated else [])+[c.tag]
        git(c.root,*args);original=git(c.root,'rev-parse',c.tag)
        refuse(lambda:c.prepare(c.root),'unowned local tag');assert git(c.root,'rev-parse',c.tag)==original
    git(seed,'tag','-a','v1.2.3','-m','published fixture');git(seed,'push','origin','refs/tags/v1.2.3')
    c=fresh();refuse(lambda:c.prepare(c.root),'remote tag exists')
    git(origin,'tag','-d','v1.2.3');git(seed,'tag','-d','v1.2.3')
    linked=base/'linked';git(seed,'worktree','add','--detach',str(linked),'HEAD')
    refuse(lambda:m.Candidate(linked,'v1.2.3'),'standalone clone')
    shallow=base/'shallow';git(base,'clone','--depth','1','file://'+str(origin),str(shallow))
    c=m.Candidate(shallow,'v1.2.3');refuse(c.prepare,'full history')
    c=fresh();(c.root/'extra').write_text('new');git(c.root,'add','.');git(c.root,'commit','-m','unaccepted')
    refuse(lambda:c.prepare(c.root),'not reachable')
    for code,reason,extra in [(7,None,''),(-15,'interrupted',''),(0,None,'unlooked: release stamps: no v* tags\n')]:
        c=prepared();fake_suite(c,code,reason,extra)
        refuse(c.check,'did not pass');assert c.log.exists();refuse(c.publish,'successful complete receipt');remote_absent()
    c=prepared();c.check();(c.root/'CHANGELOG.md').write_text('dirty')
    refuse(c.publish,'clean source')
    c=prepared();c.check();git(c.root,'tag','-d',c.tag);git(c.root,'tag','-a',c.tag,'-m','changed')
    refuse(c.publish,'tag object changed')
    c=prepared();c.check();c.log.write_text('truncated')
    refuse(c.publish,'suite output changed')
    c=prepared();c.check();target=c.directory/'original.json';c.record.rename(target);c.record.symlink_to(target)
    before=target.read_bytes();refuse(c.publish,'regular bounded input');assert target.read_bytes()==before
    c=prepared();c.check();(c.root/'.task-pipeline/run.md').write_text('Run: fixture\nstage: 6 tests — verdict fail\n')
    refuse(c.publish,'hook refused publication');assert c.load()['hook_observation']['exit']==2;remote_absent()
    c=prepared(False);c.check();refuse(c.publish,'no bound actual project context')
    c=prepared();c.check();(c.root/'.task-pipeline/run.md').write_text('Run: a different task\nstage: 6 tests — verdict pass\n')
    refuse(c.publish,'context changed')
    c=prepared();c.check();(c.root/'.task-pipeline/run.md').unlink()
    refuse(c.publish,'run.md')
    c=prepared();c.check();other=fresh();git(other.root,'tag','-a',c.tag,'-m','racing other candidate')
    original_git=c.git
    def raced(*args,**kwargs):
        if args[:1]==('push',):git(other.root,'push','origin','refs/tags/'+c.tag)
        return original_git(*args,**kwargs)
    c.git=raced
    refuse(c.publish,'push not confirmed');assert git(origin,'rev-parse',c.tag)==git(other.root,'rev-parse',c.tag)
    git(origin,'tag','-d',c.tag)
    c=fresh();(c.root/'.task-pipeline/run.md').write_text('Run: fixture\nstage: 6 tests — verdict fail\n')
    refuse(lambda:c.prepare(c.root),'hook refused local preparation')
    assert not git(c.root,'tag','-l',c.tag)
    c=prepared();c.check();before=c.record.read_bytes()
    refuse(c.check,'suite log already exists');assert c.record.read_bytes()==before
    c=prepared();c.check();(c.root/'pipeline.json').write_text('{}')
    refuse(c.publish,'clean source')
    c=prepared();c.check();c.record.unlink();os.mkfifo(c.record)
    refuse(c.publish,'regular bounded input')
    c=prepared()
    def silent(self,stream):stream.write(b'other success\n');return 0,None
    c._run_suite=types.MethodType(silent,c)
    refuse(c.check,'did not pass')
    c=prepared()
    def nested(self,stream):
        stream.write(b'PASS: task-pipeline structure valid\nfixture unlooked: release stamps: no tags\n')
        return 0,None
    c._run_suite=types.MethodType(nested,c);c.check()
    assert c.load()['mechanical_evidence']['release_gap_looked'];checks+=1
    bad = subprocess.run([sys.executable,str(ROOT/'scripts/release_candidate.py'),
                          'check','--tag','v1.2.3','--command','true'],cwd=c.root,capture_output=True,text=True)
    assert bad.returncode==2 and 'unrecognized arguments' in bad.stderr;checks+=1
    # Real owned child-process cleanup, without invoking an actual broad suite.
    driver=base/'suite-driver.py'
    driver.write_text("""import importlib.util,json,pathlib,sys,types
spec=importlib.util.spec_from_file_location('m',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
c=m.Candidate(sys.argv[2],'v1.2.3')
m.COMMAND=[sys.executable,'-c',"import os,time,pathlib;pathlib.Path("+repr(sys.argv[3])+").write_text(str(os.getpid()));time.sleep(60)"]
m.shutil.disk_usage=lambda p:types.SimpleNamespace(free=0 if sys.argv[4]=='disk' else 2**40)
with open(sys.argv[3]+'.log','wb') as out: result=c._run_suite(out)
print(json.dumps(result))
""")
    for mode in ('interrupt','disk'):
        c=fresh();marker=base/('child-'+mode)
        proc=subprocess.Popen([sys.executable,'-B',str(driver),str(ROOT/'scripts/release_candidate.py'),
                               str(c.root),str(marker),mode],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            if mode=='interrupt':
                deadline=time.monotonic()+5
                while not marker.exists() and time.monotonic()<deadline:time.sleep(.02)
                assert marker.exists(), 'owned child did not start'
                proc.send_signal(signal.SIGTERM)
            stdout,stderr=proc.communicate(timeout=10)
            assert proc.returncode==0,stderr
            code,reason=json.loads(stdout)
            assert code!=0 and reason==('interrupted' if mode=='interrupt' else 'disk-stopped')
            if marker.exists():
                pid=int(marker.read_text())
                try:os.kill(pid,0)
                except ProcessLookupError:pass
                else:raise AssertionError('owned suite child survived')
            checks+=1
        finally:
            if proc.poll() is None:proc.kill();proc.wait()
    print(f'PASS: owner release candidate — {checks} controls; fixture refs only; owned tree removed on exit')
