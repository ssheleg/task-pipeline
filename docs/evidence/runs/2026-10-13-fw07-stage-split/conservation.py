#!/usr/bin/env python3
"""One-time migration proof, not a permanent freeze on future doctrine edits."""
import hashlib
import json
from pathlib import Path
import sys


def problems(root, manifest):
    skill = Path(root) / 'plugins/task-pipeline/skills/task-pipeline'
    errors = []; rebuilt = []; covered = []
    for chunk in manifest['chunks']:
        try:
            lines = (skill / chunk['destination']).read_bytes().splitlines(keepends=True)
            data = b''.join(lines[chunk['destination_start'] - 1:chunk['destination_end']])
        except OSError:
            data = b''
        if hashlib.sha256(data).hexdigest() != chunk['sha256']:
            errors.append(f"conservation: {chunk['kind']} changed at {chunk['destination']}:{chunk['destination_start']}")
        rebuilt.append(data)
        covered.extend(range(chunk['source_start'], chunk['source_end'] + 1))
    if covered != list(range(1, manifest['source_lines'] + 1)):
        errors.append('conservation: original line partition has a gap, duplicate or reorder')
    if hashlib.sha256(b''.join(rebuilt)).hexdigest() != manifest['source_sha256']:
        errors.append('conservation: reconstructed original source differs')
    return errors


if __name__ == '__main__':
    here = Path(__file__).resolve().parent
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parents[3]
    manifest = json.loads((here / 'conservation.json').read_text())
    errors = problems(root, manifest)
    print(json.dumps({'errors': errors, 'chunks': len(manifest['chunks']), 'source_lines': manifest['source_lines']}, indent=2))
    raise SystemExit(bool(errors))
