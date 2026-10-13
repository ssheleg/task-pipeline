import hashlib,json,pathlib,subprocess,sys,tempfile,time
root=pathlib.Path(sys.argv[1]);sha=subprocess.check_output(['git','rev-parse',sys.argv[2]],cwd=root,text=True).strip()
files=['package.json','scripts/release_candidate.py','plugins/task-pipeline/hooks/release-gate.sh','test/audit_regressions/fw07_release_candidate.py']
manifest=[]
with tempfile.TemporaryDirectory(prefix='fw07-peer-frozen-') as temp:
 staging=pathlib.Path(temp)
 for rel in files:
  data=subprocess.check_output(['git','show',sha+':'+rel],cwd=root)
  target=staging/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  manifest.append({'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
 start=time.time()
 result=subprocess.run([sys.executable,'-B',str(staging/files[-1])],cwd=staging,capture_output=True,text=True,timeout=240)
 record={'source':sha,'files':manifest,'command':'python3 -B test/audit_regressions/fw07_release_candidate.py','elapsed_seconds':time.time()-start,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'scope':'Four immutable Git blobs; focused tests use synthetic local Git refs and fake expensive suite. No broad suite/provider calls.'}
record['snapshot_removed']=not staging.exists()
pathlib.Path(sys.argv[3]).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
sys.exit(result.returncode)
