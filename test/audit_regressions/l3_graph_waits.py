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

residue.report()
print(f'Graph wait controls: {checks}, failures: {len(failures)}')
raise SystemExit(bool(failures))
