import pathlib,subprocess,tempfile,json,sys
repo=pathlib.Path('/Users/sshlg/DATA/_wt/tp-fw07-pretag-admission');revision='abf3dff485788528ab3f0dbfe3139946a6a3ab78'
with tempfile.TemporaryDirectory(prefix='fresh-fw07-pushurl-peer-') as d:
 root=pathlib.Path(d)
 for rel in ['package.json','scripts/release_candidate.py','plugins/task-pipeline/hooks/release-gate.sh','test/audit_regressions/fw07_release_candidate.py']:
  p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(subprocess.check_output(['git','show',revision+':'+rel],cwd=repo))
 p=root/'test/audit_regressions/fw07_release_candidate.py';before=p.read_text().split('    c=prepared();assert c.git')[0]
 probe='''    c=prepared();c.check()
    alternate=base/'alternate.git'
    git(base,'init','--bare',str(alternate))
    git(c.root,'config','remote.origin.pushurl',str(alternate))
    caught=None
    try:c.publish()
    except Exception as e:caught=str(e)
    print(json.dumps({'source':'abf3dff485788528ab3f0dbfe3139946a6a3ab78','case':'configured pushurl differs from checked origin','refusal':caught,'checked_origin_tag':git(origin,'tag','-l',c.tag),'alternate_tag':git(alternate,'tag','-l',c.tag),'receipt_state':c.load()['state'],'scope':'Both remotes are disposable local bare fixtures; all temporary trees removed on exit.'}))
'''
 exec(compile(before+probe,str(p),'exec'),{'__file__':str(p),'__name__':'peer_probe'})
