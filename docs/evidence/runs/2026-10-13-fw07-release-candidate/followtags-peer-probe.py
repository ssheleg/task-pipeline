import pathlib,subprocess,tempfile,json
repo=pathlib.Path(__file__).resolve().parents[4];revision='ce548b363dffcf2952026dbcd4e56426719565db'
with tempfile.TemporaryDirectory(prefix='fresh-fw07-followtags-peer-') as d:
 root=pathlib.Path(d)
 for rel in ['package.json','scripts/release_candidate.py','plugins/task-pipeline/hooks/release-gate.sh','test/audit_regressions/fw07_release_candidate.py']:
  p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(subprocess.check_output(['git','show',revision+':'+rel],cwd=repo))
 p=root/'test/audit_regressions/fw07_release_candidate.py';before=p.read_text().split('    c=prepared();assert c.git')[0]
 probe='''    c=prepared();c.check()
    git(c.root,'tag','-a','v9.9.9','-m','unrelated unpublished local tag')
    git(c.root,'config','push.followTags','true')
    result=c.publish()
    print(json.dumps({'source':'ce548b363dffcf2952026dbcd4e56426719565db','case':'ambient push.followTags=true','result':result['state'],'remote_tags':git(origin,'tag','-l'),'scope':'Real disposable bare fixture remote only; every owned temporary tree removed on exit.'}))
'''
 exec(compile(before+probe,str(p),'exec'),{'__file__':str(p),'__name__':'peer_probe'})
