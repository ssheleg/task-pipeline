#!/usr/bin/env python3
"""Extract/evaluate only lock-path expression; never execute suite or plants."""
import ast
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[4]
source = root / 'test/negatives.py'
tree = ast.parse(source.read_text())
values = [n.value for n in ast.walk(tree) if isinstance(n, ast.Assign)
          and any(isinstance(t, ast.Name) and t.id == '_LOCK_PATH' for t in n.targets)]
assert len(values) == 1
expression = ast.unparse(values[0])
# This fixture accepts only the observed expression, never arbitrary repository code.
assert expression == "os.path.join(tempfile.gettempdir(), 'tp-negatives.lock')"
with tempfile.TemporaryDirectory(prefix='fw07-lock-namespace-') as folder:
    base = Path(folder)
    paths = []
    for name in ('a', 'b'):
        temp = base / name; temp.mkdir()
        env = dict(os.environ, TMPDIR=str(temp))
        command = 'import os,tempfile; print(' + expression + ')'
        paths.append(Path(subprocess.check_output([sys.executable, '-c', command], env=env, text=True).strip()))
    assert paths[0] != paths[1]
    with paths[0].open('w') as first:
        fcntl.flock(first, fcntl.LOCK_EX | fcntl.LOCK_NB)
        child = '''import fcntl,sys
with open(sys.argv[1], 'w') as f:
 try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
 except BlockingIOError: sys.exit(3)
'''
        different = subprocess.run([sys.executable, '-c', child, str(paths[1])]).returncode
        same = subprocess.run([sys.executable, '-c', child, str(paths[0])]).returncode
        assert different == 0 and same == 3
    plants = sorted(p.relative_to(root).as_posix() for p in (root/'test/negatives').glob('*.sh')
                    if '/tmp/' in p.read_text() and '-copy' in p.read_text())
    assert plants
    print(json.dumps({'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'expression': expression, 'different_TMPDIR_locks_both_acquired': different == 0,
        'same_lock_contender_refused': same == 3, 'plants_with_tmp_and_copy_literals': len(plants),
        'examples': plants[:5], 'scope': 'Only expression and owned locks executed; no public plant, actual suite lock or scratch path touched.'}, indent=2))
