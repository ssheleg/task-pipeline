import os,subprocess,tempfile,time,json,hashlib,shutil,signal,datetime,pathlib
root=pathlib.Path('/Users/sshlg/DATA/_wt/tp-fw07-composed')
base=pathlib.Path('/tmp/tp-fw07-preintegration-875c6e6')
def git(*args): return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
sha=git('rev-parse','HEAD'); tree=git('rev-parse','HEAD^{tree}')
assert sha=='875c6e6a9a02c5c18e77945fc4fa56a43588cb5c'
assert not git('status','--porcelain')
assert shutil.disk_usage(root).free>=700*1024**2
start=time.monotonic(); started=datetime.datetime.now(datetime.timezone.utc).isoformat(); reason=None; minimum=shutil.disk_usage(root).free
refs=git('show-ref','--tags'); tmp=tempfile.mkdtemp(prefix='tp-fw07-875c6e6-owned-'); env=dict(os.environ,TMPDIR=tmp,PYTHONUNBUFFERED='1')
with open(str(base)+'.log','xb') as out:
 p=subprocess.Popen(['npm','run','test:all'],cwd=root,env=env,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
 pathlib.Path(str(base)+'.active.json').write_text(json.dumps({'pid':p.pid,'sha':sha,'tree':tree,'tmp':tmp,'started':started,'command':['npm','run','test:all']}))
 try:
  while p.poll() is None:
   free=shutil.disk_usage(root).free; minimum=min(minimum,free)
   if free<300*1024**2:
    reason='disk threshold below 300MiB'; os.killpg(p.pid,signal.SIGTERM)
    try:p.wait(timeout=8)
    except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
    break
   time.sleep(2)
 except BaseException as exc:
  reason=type(exc).__name__
  if p.poll() is None:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=8)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
  raise
 finally:
  code=p.wait(); duration=time.monotonic()-start
  raw=pathlib.Path(str(base)+'.log').read_bytes()
  receipt={'source':sha,'tree':tree,'kind':'pre-integration complete owner gate, not accepted-tag release gate','command':['npm','run','test:all'],'started':started,'duration_seconds':duration,'exit':code,'interruption':reason,'min_free_bytes':minimum,'log_sha256':hashlib.sha256(raw).hexdigest(),'log_bytes':len(raw),'source_after':git('rev-parse','HEAD'),'tree_after':git('rev-parse','HEAD^{tree}'),'status_after':git('status','--porcelain'),'tag_refs_before':refs,'tag_refs_after':git('show-ref','--tags'),'tmp':tmp,'owned_tmp_removed':False,'terminal_output':raw.decode(errors='replace').splitlines()[-55:]}
  shutil.rmtree(tmp);receipt['owned_tmp_removed']=not pathlib.Path(tmp).exists()
  pathlib.Path(str(base)+'.json').write_text(json.dumps(receipt,indent=2)+'\n')
  print(json.dumps({k:receipt[k] for k in ['source','exit','interruption','duration_seconds','min_free_bytes','log_sha256','status_after']}),flush=True)
