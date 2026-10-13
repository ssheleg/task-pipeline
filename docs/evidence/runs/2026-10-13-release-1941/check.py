#!/usr/bin/env python3
"""Bounded metadata and real release-gap-guard probes; no tag or source writes."""
import builtins
import glob
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
source = (ROOT / 'test/validate.py').read_text()
start = source.index('_GAP_HEAD = "## Releases that carry no stamp"')
end = source.index('\n# The live doctrine at the top of the retro', start)
code = compile(source[start:end], 'test/validate.py:release-gap', 'exec')
retro_path = ROOT / 'docs/evidence/retro.md'
retro = retro_path.read_text()
lead = '**`v1.94.0` and `v1.94.1` carry no stamp.**'
assert retro.count(lead) == 1
results = []

def probe(name, text, missing):
    errors = []
    original = builtins.open
    def opened(path, *args, **kwargs):
        if os.fspath(path) == str(retro_path):
            return io.StringIO(text)
        return original(path, *args, **kwargs)
    scope = dict(ROOT=str(ROOT), ART='docs/evidence', ARTP=str(ROOT/'docs/evidence'),
                 glob=glob, os=os, re=re, shutil=shutil, subprocess=subprocess,
                 _UNLOOKED=[], fail=errors.append, open=opened)
    exec(code, scope)
    assert not scope['_UNLOOKED'], scope['_UNLOOKED']
    if missing:
        assert len(errors) == 1 and missing in errors[0], errors
    else:
        assert errors == [], errors
    results.append(dict(name=name, passed=True, diagnostics=errors))

probe('both declarations accepted', retro, None)
probe('failed tag omitted', retro.replace(lead, '**`v1.94.1` carries no stamp.**'), 'v1.94.0')
probe('candidate tag omitted', retro.replace(lead, '**`v1.94.0` carries no stamp.**'), 'v1.94.1')
probe('plain mention is not a declaration', retro.replace(lead, lead[2:-2]), 'v1.94.0, v1.94.1')

assert json.loads((ROOT/'package.json').read_text())['version'] == '1.94.1'
assert json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())['plugins'][0]['version'] == '1.94.1'
assert json.loads((ROOT/'plugins/task-pipeline/.claude-plugin/plugin.json').read_text())['version'] == '1.94.1'
assert '| **Version** | 1.94.1 |' in (ROOT/'SKILL-CARD.md').read_text()
assert (ROOT/'CHANGELOG.md').read_text().startswith('## v1.94.1 ')
results.append(dict(name='five version surfaces', passed=True))
base='78c42124db910c56e74c8fbd524bdc9a4f8fb6c9'
changed=subprocess.check_output(['git','diff','--name-only',base,'HEAD','--','plugins','bin','install.sh','cursor','.github','test'],cwd=ROOT,text=True).splitlines()
assert changed == ['plugins/task-pipeline/.claude-plugin/plugin.json'], changed
results.append(dict(name='skill runtime and doctrine preserved; plugin version only',passed=True))
old=subprocess.check_output(['git','show',base+':docs/evidence/retro.md'],cwd=ROOT,text=True)
def stamps(s):
    return re.findall(r'^\|\s*\d{4}-\d\d-\d\d\s*\|.*$',s,re.M)
assert stamps(old)==stamps(retro)
results.append(dict(name='no fabricated run-stamp row',passed=True))
assert subprocess.check_output(['git','cat-file','-t','v1.94.1'],cwd=ROOT,text=True).strip()=='tag'
assert subprocess.check_output(['git','rev-parse','v1.94.0^{}'],cwd=ROOT,text=True).strip()==base
results.append(dict(name='annotated candidate; failed tag target unchanged',passed=True))
print(json.dumps({'validator_sha256':hashlib.sha256(source.encode()).hexdigest(),
 'scope':'Extracted actual release-gap guard with actual Git tag/history reads; four in-memory retro variants. Not the entire validator or full release suite.',
 'checks':results},indent=2))
