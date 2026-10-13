#!/usr/bin/env python3
"""Offline actual-CLI selected-profile checkpoints; no Observatory/provider calls."""
import copy
import json
import os
import pathlib
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'plugins/task-pipeline/skills/task-pipeline/scripts/stage_checkpoint.py'
COUNT = 0
HEAD = 'Run: `profile fixture` · started `2026-10-13`\n'


def check(value, label):
    global COUNT
    COUNT += 1
    assert value, label


def stage(state, name=None, sid=None):
    out = {'state': state, 'skills': ['fixture'], 'gate': {'type': 'auto', 'check': 'fixture'}}
    if name is not None:
        out['name'] = name
    if sid is not None:
        out['id'] = sid
    return out


def profile():
    return {'stages': [stage('collect', 'Collect', 0), stage('build', 'Build', 1),
                       stage('accept', 'Accept', 2)], 'paths': {'artifacts': 'notes/runs'}}


def fixture(base, label, cfg=None, sid=2, name='Accept', verdict='pass'):
    root = base / label
    (root / '.task-pipeline').mkdir(parents=True)
    ledger = root / '.task-pipeline/run.md'
    ledger.write_text(HEAD + f'stage: {sid} {name} — gate auto — verdict {verdict} — 2026-10-13T10:00:00Z\n')
    if cfg is not None:
        (root / 'pipeline.json').write_text(json.dumps(cfg))
    return root, ledger


def cli(root, *args):
    return subprocess.run([sys.executable, '-B', str(SCRIPT), *args], cwd=root,
                          text=True, capture_output=True, timeout=20)


def emit(root, *args):
    result = cli(root, 'emit', '--project', 'project:offline-fixture', *args)
    check(result.returncode == 0, f'emit passes: {result.stderr}')
    return json.loads(result.stdout)


def refuse(root, *args, text=None):
    state = root / '.task-pipeline/memory.json'
    before = state.read_bytes() if state.exists() else None
    result = cli(root, 'emit', '--project', 'project:offline-fixture', *args)
    check(result.returncode != 0 and result.stdout == '', 'refusal emits no tool payload')
    check((state.read_bytes() if state.exists() else None) == before, 'refusal preserves state bytes')
    if text:
        check(text in result.stderr, 'named refusal')
    check('do-not-disclose-fixture' not in result.stderr, 'raw config values are not diagnostics')


with tempfile.TemporaryDirectory(prefix='tp-fw07-profile-') as temp:
    base = pathlib.Path(temp)
    root, ledger = fixture(base, 'custom', profile())
    a = emit(root)
    check([s['title'] for s in a['body']['plan']] == ['Collect', 'Build', 'Accept'], 'only selected stages')
    check(a['close'] is True and a['body']['open'] == [], 'custom final pass closes')
    check(not (root / 'notes/runs').exists(), 'artifact root is not replaced or created')
    check(emit(root)['idempotencyKey'] == a['idempotencyKey'], 'retry stable')
    saved = json.loads((ledger.parent / 'memory.json').read_text())
    check(saved['profile']['source'] == 'pipeline.json', 'selected source bound locally')
    check((ledger.parent / 'memory.json').stat().st_mode & 0o777 == 0o600, 'state mode preserved')
    answer = root / 'answer.json'
    answer.write_text(json.dumps({'workflowId': 'workflow:fixture', 'leaseId': 'lease-fixture', 'revision': 1}))
    check(cli(root, 'record', '--answer', str(answer)).returncode == 0, 'record accepts fixture response')
    check(json.loads((ledger.parent / 'memory.json').read_text())['profile'] == saved['profile'], 'record keeps binding')
    check(emit(root)['workflowId'] == 'workflow:fixture', 'workflow continuation retained')
    changed = profile(); changed['stages'][0]['gate']['check'] = 'changed authority'
    (root / 'pipeline.json').write_text(json.dumps(changed))
    refuse(root, text='profile or run changed')
    (root / 'pipeline.json').unlink()
    refuse(root, text='profile or run changed')
    (root / 'pipeline.json').write_text(json.dumps(profile(), indent=4))
    check(emit(root)['idempotencyKey'] == a['idempotencyKey'], 'restored semantic profile retries; formatting irrelevant')
    ledger.write_text(ledger.read_text().replace('started `2026-10-13`', 'started `2026-10-14`'))
    refuse(root, text='profile or run changed')

    root, _ = fixture(base, 'default', sid=0, name='Intake grill')
    a = emit(root)
    check(len(a['body']['plan']) == 11 and a['body']['open'][0]['step_id'] == 'stage-1', 'absent config selects default')
    default = json.loads((SCRIPT.parent.parent / 'pipeline.example.json').read_text())
    root, ledger = fixture(base, 'explicit-default', default, sid=0, name='Intake grill')
    ledger.write_text(ledger.read_text().replace('gate auto', 'gate manual'))
    check(len(emit(root)['body']['plan']) == 11, 'configured default profile remains supported')
    root, _ = fixture(base, 'ordinal', {'stages': [stage('one'), stage('two')]}, sid=0, name='one')
    a = emit(root)
    check(a['body']['open'][0] == {'step_id': 'stage-1', 'next_action': 'enter stage 1 two'}, 'optional ids/names project deterministically')
    for i, label in enumerate(('', '   ')):
        cfg = {'stages': [stage('one', label)]}
        root, _ = fixture(base, f'empty-name-{i}', cfg, sid=0, name='one')
        a = emit(root)
        check(a['body']['plan'] == [{'step_id': 'stage-0', 'title': 'one'}] and a['close'],
              'empty optional label uses required stable state')
    cfg = {'stages': [stage('one', 'One', 9), stage('two', 'Two', 3)]}
    root, _ = fixture(base, 'ordered', cfg, sid=9, name='One')
    a = emit(root)
    check([p['step_id'] for p in a['body']['plan']] == ['stage-9', 'stage-3'], 'declared order not numeric sort')
    check(a['body']['open'][0]['step_id'] == 'stage-3' and not a['close'], 'next declared id not sid+1/max')
    for verdict in ('fail', 'pending', 'skip'):
        root, _ = fixture(base, verdict, profile(), verdict=verdict)
        a = emit(root)
        check(not a['close'] and a['body']['open'][0]['step_id'] == 'stage-2', 'unpassed final gate remains open')

    variants = [[], {}, {'stages': []}, {'stages': ['secret:do-not-disclose-fixture']}]
    for mutate in ('duplicate-id', 'duplicate-state', 'bool-id', 'negative-id', 'unknown-gate',
                   'unknown-capability', 'bad-skills', 'judge-absent'):
        cfg = profile()
        if mutate == 'duplicate-id': cfg['stages'][1]['id'] = 0
        elif mutate == 'duplicate-state': cfg['stages'][1]['state'] = 'collect'
        elif mutate == 'bool-id': cfg['stages'][0]['id'] = True
        elif mutate == 'negative-id': cfg['stages'][0]['id'] = -1
        elif mutate == 'unknown-gate': cfg['stages'][0]['gate']['type'] = 'do-not-disclose-fixture'
        elif mutate == 'unknown-capability': cfg['must_understand'] = ['do-not-disclose-fixture']
        elif mutate == 'bad-skills': cfg['stages'][0]['skills'] = []
        elif mutate == 'judge-absent': cfg['stages'][0]['gate']['type'] = 'judgment'
        variants.append(cfg)
    for i, cfg in enumerate(variants):
        root, _ = fixture(base, f'bad-{i}', cfg)
        refuse(root)
    root, _ = fixture(base, 'broken-json', profile())
    (root / 'pipeline.json').write_text('{do-not-disclose-fixture')
    refuse(root)
    root, _ = fixture(base, 'unreadable', profile())
    path = root / 'pipeline.json'; path.chmod(0)
    try:
        if os.geteuid() != 0: refuse(root)
    finally:
        path.chmod(0o600)
    root, _ = fixture(base, 'dangling', profile())
    path = root / 'pipeline.json'; path.unlink(); path.symlink_to('missing-profile.json')
    refuse(root)
    root, _ = fixture(base, 'wrong-name', profile(), name='Brainstorm')
    refuse(root, text='ledger stage does not match')
    root, _ = fixture(base, 'unknown-id', profile(), sid=10)
    refuse(root, text='ledger stage does not match')
    root, ledger = fixture(base, 'bad-line', profile())
    ledger.write_text(ledger.read_text() + 'stage: broken\n')
    refuse(root, text='malformed stage ledger line')
    root, ledger = fixture(base, 'bad-state', profile())
    (ledger.parent / 'memory.json').write_text('{do-not-disclose-fixture')
    refuse(root, text='memory state cannot be read')
    root, ledger = fixture(base, 'legacy', profile())
    (ledger.parent / 'memory.json').write_text(json.dumps({'workflowId': 'workflow:legacy'}))
    refuse(root, text='legacy workflow has no selected-profile binding')
    root, ledger = fixture(base, 'relocated', profile())
    target = root / 'notes/runs/run.md'; target.parent.mkdir(parents=True)
    target.write_bytes(ledger.read_bytes()); ledger.unlink()
    a = emit(root, '--ledger', str(target), '--project-root', str(root))
    check(a['close'] and len(a['body']['plan']) == 3, 'explicit root keeps relocated ledger in selected profile')
    result = cli(root, 'emit', '--ledger', str(target))
    check(result.returncode != 0 and 'requires --project-root' in result.stderr, 'non-Git relocated root never guessed')
    subprocess.run(['git', 'init', '-q', str(root)], check=True, capture_output=True)
    check(emit(root, '--ledger', str(target))['close'], 'Git root resolves relocated ledger consistently')
    result = cli(root, 'emit', '--ledger', str(target), '--project-root', str(base / 'default'))
    check(result.returncode != 0 and not result.stdout, 'foreign root refused')
    root, ledger = fixture(base, 'missing-ledger', profile()); ledger.unlink()
    refuse(root, text='cannot be read')

print(f'PASS: FW07 selected-profile checkpoint — {COUNT} controls')
