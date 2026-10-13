#!/usr/bin/env python3
# shared-mechanism: sshlg-skills/owner-process-controls-v1
# diverges: none
"""Real validator processes in owned copies, including legitimate escaped pipes."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
BOARD='docs/evidence/backlog.md'
RELEASE='.github/workflows/release.yml'
board=(ROOT/BOARD).read_text()
row=next(line for line in board.splitlines() if re.match(r'^\| [A-Z]{1,4}-\d+',line))

def duplicate(text):return text.replace(row,row+'\n'+row,1)
def width(text):return text.replace(row,row.rsplit('|',2)[0]+'| extra |'+ '|'.join(row.rsplit('|',2)[1:]),1)
def escaped(text):
    cells=row.split('|');cells[3]=' escaped \\| pipe '+cells[3]
    return text.replace(row,'|'.join(cells),1)

cases=[
 ('healthy',BOARD,lambda s:s,None),
 ('duplicate',BOARD,duplicate,'board duplicate ID'),
 ('width',BOARD,width,'row width'),
 ('ancestry removed',RELEASE,lambda s:s.replace('git merge-base --is-ancestor','git merge-base-removed --is-ancestor',1),'release ancestry guard'),
 ('shallow',RELEASE,lambda s:s.replace('fetch-depth: 0','fetch-depth: 1',1),'release full-history checkout'),
 ('escaped pipe',BOARD,escaped,None),
]
observed=[]
for label,relative,mutate,needle in cases:
    with tempfile.TemporaryDirectory(prefix='r30-owner-process-') as temporary:
        base=Path(temporary);copy=base/'repo';home=base/'home';home.mkdir();tmp=base/'tmp';tmp.mkdir()
        shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('.git','node_modules','__pycache__','.agent-sync'))
        target=copy/relative;before=target.read_text();after=mutate(before)
        assert label=='healthy' or after!=before,label
        target.write_text(after)
        env=os.environ.copy();env.update(HOME=str(home),TMPDIR=str(tmp),GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,PYTHONDONTWRITEBYTECODE='1')
        p=subprocess.run([sys.executable,str(copy/'test/validate.py')],cwd=copy,env=env,text=True,capture_output=True,timeout=180)
        output=p.stdout+p.stderr
        good=(p.returncode==1 and needle in output) if needle else p.returncode==0
        observed.append({'case':label,'returncode':p.returncode,'expected_diagnostic':needle,'accepted':good,'output':output})
        if not good:print(json.dumps(observed,indent=2));raise SystemExit(1)
print(json.dumps({'source_hashes':{path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in ['test/validate.py','test/owner_board.py','test/owner_release.py']},'cases':observed},indent=2))
