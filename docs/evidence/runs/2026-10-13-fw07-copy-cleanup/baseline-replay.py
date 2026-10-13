#!/usr/bin/env python3
"""Replay the original eight residue controls against immutable pre-fix runner blobs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

repo = Path(__file__).resolve().parents[4]
base = '7d18df5464fad6fdbaa77a91d48580ebbe3f5d9a'
fixture = repo / 'test/audit_regressions/plant_copy_cleanup.py'
names = ['all_copies_success', 'all_copies_shell_failure', 'all_copies_runner_exception',
         'property_copies_success', 'property_copies_exception',
         'primary_unchanged_stays_broken_despite_secondary_change',
         'secondary_unchanged_does_not_change_primary_verdict',
         'heredoc_and_comment_are_not_cleanup_authority']
with tempfile.TemporaryDirectory(prefix='tp-copy-baseline-') as directory:
    target = Path(directory)
    for name in ['test/negatives.py', 'test/negative_lock.py']:
        output = target / name
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(subprocess.check_output(['git', 'show', base + ':' + name], cwd=repo))
    check = target / 'test/audit_regressions/plant_copy_cleanup.py'
    check.parent.mkdir(parents=True)
    check.write_bytes(fixture.read_bytes())
    result = subprocess.run([sys.executable, '-B', str(check),
                             *['CopyCleanup.test_' + n for n in names]],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sys.stdout.buffer.write(result.stdout)
    assert result.returncode == 1 and b'FAILED (failures=8)' in result.stdout
print(json.dumps({'baseline': base, 'expected_failures': 8,
                  'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(),
                  'owned_temporary_removed': not target.exists()}))
