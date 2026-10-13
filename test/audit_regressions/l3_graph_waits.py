#!/usr/bin/env python3
"""TP-2 graph waits and mutation admission: real processes, synthetic graphs."""
from pathlib import Path
import json
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'test'))
import residue
GRAPH = ROOT / 'plugins/task-pipeline/skills/task-pipeline/scripts/graph.py'
failures = []
checks = 0


def case(name):
    def wrap(fn):
        global checks
        checks += 1
        residue.open_case(name)
        try:
            fn()
        except Exception as exc:
            failures.append(name)
            print('FAIL:', name, str(exc))
        else:
            residue.close_case(name)
            print('PASS:', name)
    return wrap


def node(identity='N-001', status='pending', blockers=()):
    return {'id': identity, 'title': 'synthetic task', 'owner': 'implementer',
            'status': status, 'blocked_by': list(blockers), 'serves': 'REQ-001',
            'check': 'synthetic check', 'evidence': None}


def graph(*nodes):
    return {'goal': 'synthetic watched-wait contract', 'requirements': ['REQ-001'],
            'nodes': list(nodes), 'edges': [
                {'from': b, 'to': n['id'], 'payload': 'synthetic input'}
                for n in nodes for b in n['blocked_by']]}


def written(data=None):
    box = Path(residue.workspace('l3-graph-waits'))
    target = box / 'graph.json'
    target.write_text(json.dumps(data if data is not None else graph(node())))
    return target


def run(target, *args, injection=None):
    argv = [str(GRAPH), *args, '--graph', str(target)]
    if injection is None:
        command = [sys.executable, '-B', *argv]
    else:
        code = 'import runpy,sys,types\n' + injection + '\nsys.argv=' + repr(argv) + '\nrunpy.run_path(sys.argv[0],run_name="__main__")'
        command = [sys.executable, '-B', '-c', code]
    return subprocess.run(command, cwd=target.parent, capture_output=True, text=True)


ADD = ('add', '--title', 'another task', '--owner', 'implementer', '--serves',
       'REQ-001', '--check', 'synthetic check', '--why', 'synthetic addition')


def lock_refusal(injection=None, collision=False):
    target = written()
    before = target.read_bytes()
    if collision:
        (target.parent / '.graph.lock').mkdir()
    result = run(target, *ADD, injection=injection)
    assert result.returncode == 1, result.stdout + result.stderr
    assert 'lock' in result.stderr and 'nothing was written' in result.stderr, result.stderr
    assert target.read_bytes() == before, 'refused mutation changed graph bytes'


@case('lock path collision refuses without writing')
def _():
    lock_refusal(collision=True)


@case('unavailable locking refuses without writing')
def _():
    lock_refusal(injection='sys.modules["fcntl"]=None')


@case('flock failure refuses without writing')
def _():
    lock_refusal(injection='def broken(*args): raise OSError("synthetic lock failure")\nsys.modules["fcntl"]=types.SimpleNamespace(flock=broken,LOCK_EX=2)')


@case('valid lock permits mutation')
def _():
    target = written()
    result = run(target, *ADD)
    assert result.returncode == 0, result.stderr
    assert len(json.loads(target.read_text())['nodes']) == 2



@case('read-only validation remains available without locking')
def _():
    target = written()
    before = target.read_bytes()
    result = run(target, 'validate', injection='sys.modules["fcntl"]=None')
    assert result.returncode == 0, result.stderr
    assert target.read_bytes() == before


@case('concurrent valid mutations retain all additions')
def _():
    target = written()
    children = [subprocess.Popen([sys.executable, '-B', str(GRAPH), *ADD,
                                 '--graph', str(target)], cwd=target.parent,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                for _ in range(4)]
    results = [(p, p.communicate(timeout=30)) for p in children]
    assert all(p.returncode == 0 for p, _ in results), results
    nodes = json.loads(target.read_text())['nodes']
    assert len(nodes) == 5 and len({n['id'] for n in nodes}) == 5, nodes

def waited(identity='N-001', blockers=(), token='a' * 32):
    n = node(identity, 'waiting', blockers)
    n['waiting_on'] = {'id': token, 'kind': 'ci', 'watcher': 'synthetic watcher'}
    return n


@case('waiting frontier has distinct exit and no dispatch rows')
def _():
    target = written(graph(waited()))
    r = run(target, 'next')
    assert r.returncode == 6 and not r.stdout and 'synthetic watcher' in r.stderr, r


@case('unknown status is refused rather than runnable')
def _():
    target = written(graph(node(status='mystery')))
    r = run(target, 'next')
    assert r.returncode == 1 and not r.stdout, r


@case('wait resume records identity and rejects stale same-watcher resume')
def _():
    target = written()
    r = run(target, 'wait', 'N-001', '--kind', 'ci', '--watcher', 'synthetic watcher', '--why', 'pending check')
    assert r.returncode == 0, r.stderr
    data = json.loads(target.read_text()); first = data['nodes'][0]['waiting_on']
    assert first['id'] and run(target, 'next').returncode == 6
    r = run(target, 'resume', 'N-001', '--wait-id', first['id'], '--why', 'check resolved')
    assert r.returncode == 0 and run(target, 'next').returncode == 0, r.stderr
    assert 'waiting_on' not in json.loads(target.read_text())['nodes'][0]
    assert run(target, 'wait', 'N-001', '--kind', 'ci', '--watcher', 'synthetic watcher', '--why', 'new check').returncode == 0
    before = target.read_bytes(); second = json.loads(before)['nodes'][0]['waiting_on']
    assert first['id'] != second['id']
    r = run(target, 'resume', 'N-001', '--wait-id', first['id'], '--why', 'stale callback')
    assert r.returncode == 1 and target.read_bytes() == before, r.stderr


@case('wait-only dependency closure and mixed barriers keep distinct outcomes')
def _():
    a = waited(); a['wave'] = 1
    b = node('N-002', blockers=('N-001',)); b['wave'] = 2
    c = node('N-003', blockers=('N-002',)); c['wave'] = 2
    for data, extra, expected in [
        (graph(a, b, c), (), 6),
        (graph(a, b, c), ('--wave', '2'), 6),
        (graph(a, waited('N-004')), (), 6),
        (graph(a, node('N-004')), (), 0),
        (graph(a, node('N-004', 'running')), (), 4),
        (graph(), (), 4),
    ]:
        target = written(data); r = run(target, 'next', *extra)
        assert r.returncode == expected, r
        if expected != 0: assert not r.stdout
    parked = node('N-005', 'parked'); parked['parked_reason'] = 'external blocker unavailable'
    target = written(graph(a, parked, node('N-006', blockers=('N-005',))))
    assert run(target, 'next').returncode == 4
    target = written(graph(waited(blockers=('N-002',)), node('N-002', 'running')))
    assert run(target, 'next').returncode == 4, 'waiting label hid a running dependency'
    done = node(status='done'); done['evidence'] = ['synthetic result']
    assert run(written(graph(done)), 'next').returncode == 3


@case('malformed waits and non-waiting metadata fail runtime and schema')
def _():
    schema = json.loads((GRAPH.parent.parent / 'graph.schema.json').read_text())
    try:
        import jsonschema
    except ImportError:
        validator = None
        print('NOT_RUN: optional JSON Schema engine unavailable; runtime negatives still run')
    else:
        validator = jsonschema.Draft7Validator(schema)
    bad = []
    for field, values in {'id': ['', 'a'*31, 'a'*32+'\n', None],
                          'kind': ['human', '', [], None],
                          'watcher': ['', ' ', 'line\nnext', 'line\r', None]}.items():
        for value in values:
            n = waited(); n['waiting_on'][field] = value; bad.append(n)
    for value in (None, {}, 'locator'):
        n = waited(); n['waiting_on'] = value; bad.append(n)
    n = waited(); n['waiting_on']['extra'] = True; bad.append(n)
    n = waited(); n.pop('waiting_on'); bad.append(n)
    n = waited(); n['status'] = 'pending'; bad.append(n)
    n = waited(); n['claim'] = {}; bad.append(n)
    for n in bad:
        data = graph(n); target = written(data); before = target.read_bytes()
        r = run(target, 'validate')
        assert r.returncode == 1 and target.read_bytes() == before, r
        if validator is not None: assert list(validator.iter_errors(data)), n
    for kind in ('ci', 'review', 'peer', 'release', 'time', 'lease'):
        n = waited(); n['waiting_on']['kind'] = kind; data = graph(n)
        if validator is not None: assert not list(validator.iter_errors(data))
        assert run(written(data), 'validate').returncode == 0


@case('transition admission refuses without lossy writes')
def _():
    for status in ('running', 'done', 'parked', 'waiting'):
        n = waited() if status == 'waiting' else node(status=status)
        if status == 'done': n['evidence'] = ['synthetic evidence']
        if status == 'parked': n['parked_reason'] = 'already parked'
        target = written(graph(n)); before = target.read_bytes()
        r = run(target, 'wait', 'N-001', '--kind', 'ci', '--watcher', 'watch', '--why', 'reason')
        assert r.returncode == 1 and target.read_bytes() == before, r
    n = node(); n['claim'] = {'owner': 'another execution'}
    target = written(graph(n)); before = target.read_bytes()
    assert run(target, 'wait', 'N-001', '--kind', 'lease', '--watcher', 'watch', '--why', 'reason').returncode == 1
    assert target.read_bytes() == before
    for flags in [('--watcher', ''), ('--watcher', 'a\nb'), ('--why', ''), ('--why', 'a\rb'), ('--kind', 'human')]:
        target = written(); before = target.read_bytes()
        r = run(target, 'wait', 'N-001', '--kind', 'ci', '--watcher', 'watch', '--why', 'reason', *flags)
        assert r.returncode in (1, 2) and target.read_bytes() == before, r
    target = written(); before = target.read_bytes()
    for args in [('wait', 'N-999', '--kind', 'ci', '--watcher', 'watch', '--why', 'reason'),
                 ('resume', 'N-001', '--wait-id', 'a'*32, '--why', 'not waiting'),
                 ('wait', 'N-001', '--kind', 'ci', '--watcher', 'watch')]:
        r = run(target, *args)
        assert r.returncode in (1, 2) and target.read_bytes() == before, r
    blocked = node(status='blocked'); target = written(graph(blocked))
    assert run(target, 'wait', 'N-001', '--kind', 'review', '--watcher', 'review#1', '--why', 'review pending').returncode == 0


@case('park and invalidation archive waits without stale active metadata')
def _():
    target = written(graph(waited())); record = json.loads(target.read_text())['nodes'][0]['waiting_on']
    r = run(target, 'park', 'N-001', '--reason', 'explicitly dropped')
    assert r.returncode == 0, r.stderr
    data = json.loads(target.read_text()); assert 'waiting_on' not in data['nodes'][0]
    assert data['revisions'][-1]['waiting_on'] == record and run(target, 'validate').returncode == 0
    target = written(graph(node(), waited('N-002', ('N-001',)), waited('N-003')))
    r = run(target, 'invalidate', '--node', 'N-001', '--why', 'contract changed')
    assert r.returncode == 0, r.stderr
    data = json.loads(target.read_text()); affected = data['nodes'][1]
    assert affected['status'] == 'pending' and 'waiting_on' not in affected
    assert data['nodes'][2] == waited('N-003'), 'unrelated wait changed'
    assert any(r.get('waiting_on') for r in data['revisions'] if r['node'] == 'N-002')
    assert run(target, 'validate').returncode == 0


@case('unresolved wait refuses claim certification and close without artifacts')
def _():
    target = written(graph(waited())); before = target.read_bytes()
    auth = target.parent / 'authority.sqlite'
    r = run(target, 'claim', '--node', 'N-001', '--owner', 'test', '--authority', str(auth))
    assert r.returncode == 4 and not auth.exists(), r
    r = run(target, 'recover', '--node', 'N-001', '--owner', 'test', '--authority', str(auth))
    assert r.returncode == 4 and not auth.exists(), r
    r = run(target, 'certify', '--node', 'N-001', '--tier', 'missing.json')
    assert r.returncode == 1 and 'node is waiting' in r.stderr, r
    verdict = target.parent / 'verdict.json'
    verdict.write_text(json.dumps({'node':'N-001','done':['synthetic'],'not_done':[],
        'not_verified':[], 'blockers':[], 'replan': {'possible':True,'next':[]},'evidence':['synthetic']}))
    r = run(target, 'close', '--verdict', str(verdict))
    assert r.returncode == 1 and 'node is waiting' in r.stderr, r
    assert target.read_bytes() == before and not (target.parent / 'verdict-N-001.json').exists()


@case('same-identity concurrent resumes accept exactly one transition')
def _():
    target = written(graph(waited()))
    args = ['resume', 'N-001', '--wait-id', 'a'*32, '--why', 'event resolved', '--graph', str(target)]
    children = [subprocess.Popen([sys.executable, '-B', str(GRAPH), *args], cwd=target.parent,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
    for child in children: child.communicate(timeout=20)
    assert sorted(c.returncode for c in children) == [0, 1]
    data = json.loads(target.read_text()); assert len(data['revisions']) == 1
    assert run(target, 'next').returncode == 0


residue.report()
print(f'Graph wait controls: {checks}, failures: {len(failures)}')
raise SystemExit(bool(failures))
