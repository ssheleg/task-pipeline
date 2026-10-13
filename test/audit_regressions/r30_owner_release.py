#!/usr/bin/env python3
# shared-mechanism: sshlg-skills/owner-release-controls-v1
# diverges: none
"""Bounded workflow mutants and local Git execution of the real release guards."""
from pathlib import Path
import os
import re
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'test'))
from owner_release import release_errors, check

text=(ROOT/'.github/workflows/release.yml').read_text()
checks=0

def expect(value, needle=None):
    global checks
    errors=release_errors(value)
    assert (any(needle in e for e in errors) if needle else not errors),(needle,errors)
    checks+=1

expect(text)
for before,after,needle in [
    ('git merge-base --is-ancestor','git merge-base-removed --is-ancestor','guard missing'),
    ('fetch-depth: 0','fetch-depth: 1','full-history'),
    ('      - name: The tag must be reachable','      - if: false\n        name: The tag must be reachable','conditional'),
    ('      - name: The tag must be reachable','      - continue-on-error: true\n        name: The tag must be reachable','ignored'),
    ('          if ! git merge-base','          exit 0\n          if ! git merge-base','unsupported setup'),
    ('git fetch --no-tags origin "$DEF"','git fetch --no-tags origin "$DEF" || true','unsupported setup'),
    ('          fetch-depth: 0','          fetch-depth: 0\n          "fetch-depth": 1','quoted mapping'),
    ('          fetch-depth: 0','          fetch-depth: 0\n          \'fetch-depth\': 1','quoted mapping'),
    ('    steps:','    steps:\n    "steps": []','quoted mapping'),
    ('    steps:','    steps:\n    <<: *override','merge keys'),
    ('  release:','  release:\n    continue-on-error: true','ignored at job'),
    ('          if ! git merge-base','          if git merge-base','guard missing'),
]:
    assert before in text,before
    expect(text.replace(before,after,1),needle)
expect(text+'\n  "release":\n    uses: ./.github/workflows/validate.yml\n','quoted mapping')
expect(text.replace('fetch-depth: 0','fetch-depth: "0"',1))
expect('# ignored comment mentioning an absent guard\n'+text)

# Execute shell extracted from the workflow, with only expression substitution.
# The only stand-in is gh's repository-metadata response; Git/tag operations are real.
def script(name):
    step=next(s for s in re.split(r'(?=^      - )',text,flags=re.M) if name in s)
    match=re.search(r'^        run: \|\n((?:          [^\n]*\n?|\n)*)',step,re.M)
    assert match,name
    return re.sub(r'\$\{\{.*?\}\}', '${CANDIDATE_TAG}', ''.join(line[10:]+'\n' for line in match.group(1).splitlines()))
annotation=script('name: The tag must be annotated')
ancestry=script('name: The tag must be reachable')

def git(path,*args):
    proc=subprocess.run(['git',*args],cwd=path,env=env,text=True,capture_output=True)
    assert proc.returncode==0,(args,proc.stderr)
    return proc.stdout.strip()

with tempfile.TemporaryDirectory(prefix='r30-release-local-') as temporary:
    root=Path(temporary);home=root/'home';home.mkdir();repo=root/'repo';repo.mkdir()
    env=os.environ.copy();env.update(HOME=str(home),GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GITHUB_REPOSITORY='fixture/owner')
    # git subprocesses below use local identity; no credential or provider calls.
    git(repo,'init','-b','main');git(repo,'config','user.name','R30 fixture');git(repo,'config','user.email','r30@example.invalid')
    (repo/'data').write_text('first');git(repo,'add','data');git(repo,'commit','-m','first');git(repo,'tag','-a','v1','-m','first')
    (repo/'data').write_text('second');git(repo,'commit','-am','second');git(repo,'tag','-a','v2','-m','second');git(repo,'tag','light')
    remote=root/'remote.git';git(root,'clone','--bare',str(repo),str(remote));git(repo,'remote','add','origin',str(remote));git(repo,'fetch','origin')
    tools=root/'bin';tools.mkdir();gh=tools/'gh';gh.write_text('#!/bin/sh\n[ "$1" = api ] || exit 2\nprintf "main\\n"\n');gh.chmod(0o755);env['PATH']=str(tools)+os.pathsep+env['PATH']
    for tag,want in [('v1',0),('v2',0),('light',1),('absent',1)]:
        env['CANDIDATE_TAG']=tag
        out=subprocess.run(['bash','-c',annotation],cwd=repo,env=env,capture_output=True,text=True)
        assert (out.returncode==0)==(want==0),(tag,out.stdout,out.stderr);checks+=1
    for tag in ['v1','v2']:
        git(repo,'checkout','--detach',tag);env['CANDIDATE_TAG']=tag
        out=subprocess.run(['bash','-c',ancestry],cwd=repo,env=env,capture_output=True,text=True)
        assert out.returncode==0,out.stderr;checks+=1
    git(repo,'checkout','-b','unmerged');(repo/'data').write_text('unmerged');git(repo,'commit','-am','unmerged');git(repo,'tag','-a','v3','-m','unmerged')
    env['CANDIDATE_TAG']='v3';out=subprocess.run(['bash','-c',ancestry],cwd=repo,env=env,capture_output=True,text=True)
    assert out.returncode==1 and 'not an' in out.stdout,(out.stdout,out.stderr);checks+=1
    shallow=root/'shallow';git(root,'clone','--depth','1','file://'+str(remote),str(shallow));assert git(shallow,'rev-parse','--is-shallow-repository')=='true';checks+=1
    # The structural guard rejects checkout depth 1 before a release can rely on it;
    # a shallow history itself is not falsely called proof of non-ancestry.
    expect(text.replace('fetch-depth: 0','fetch-depth: 1',1),'full-history')
    missing=root/'missing';missing.mkdir();errors=[];check(missing,errors.append);assert errors;checks+=1
    path=missing/'.github/workflows/release.yml';path.parent.mkdir(parents=True);path.write_bytes(b'\xff');errors=[];check(missing,errors.append);assert errors;checks+=1
print(f'PASS: owner release {checks} focused controls (local Git; no publication)')
