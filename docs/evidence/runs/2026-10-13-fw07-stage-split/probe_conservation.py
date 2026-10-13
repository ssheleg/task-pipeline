#!/usr/bin/env python3
"""One-time exact-source conservation controls; owns and removes its tiny fixture."""
import json
from pathlib import Path
import shutil
import tempfile
from conservation import problems

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = Path('plugins/task-pipeline/skills/task-pipeline')
manifest = json.loads((HERE / 'conservation.json').read_text())
count = 0
assert not problems(ROOT, manifest)
count += 1
with tempfile.TemporaryDirectory(prefix='fw07-conservation-') as folder:
    root = Path(folder)
    for name in {c['destination'] for c in manifest['chunks']}:
        target = root / BASE / name;target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / BASE / name, target)
    for chunk in manifest['chunks']:
        if chunk['kind'] not in ('stage-detail', 'complete-gate-suffix'):continue
        target = root / BASE / chunk['destination']; original = target.read_bytes()
        lines = original.splitlines(keepends=True)
        start, end = chunk['destination_start'] - 1, chunk['destination_end']
        # Drop an internal line, preserving headings/routes and unrelated stages.
        eligible = [i for i in range(start, end) if lines[i].strip() and lines[i].strip() != b'---']
        index = eligible[min(2, len(eligible) - 1)]
        target.write_bytes(b''.join(lines[:index] + lines[index + 1:]))
        errors = problems(root, manifest)
        assert any(chunk['kind'] + ' changed at ' + chunk['destination'] in e for e in errors), errors
        target.write_bytes(original);count += 1
    for mutation in ('gap', 'duplicate', 'reorder'):
        bad = json.loads(json.dumps(manifest))
        if mutation == 'gap':bad['chunks'].pop(1)
        elif mutation == 'duplicate':bad['chunks'].insert(1,bad['chunks'][0])
        else:bad['chunks'][0],bad['chunks'][1]=bad['chunks'][1],bad['chunks'][0]
        assert 'conservation: original line partition has a gap, duplicate or reorder' in problems(root,bad)
        count += 1
print(f'PASS: exact-source conservation — {count} controls; no native or semantic-equivalence judgment inferred')
