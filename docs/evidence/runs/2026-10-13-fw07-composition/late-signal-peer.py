#!/usr/bin/env python3
"""Read-only source probe. In-memory child seam; no provider or real suite."""
import importlib.util, io, json, signal, subprocess, sys
from pathlib import Path
root=Path(sys.argv[1]).resolve()
s=importlib.util.spec_from_file_location('candidate_peer', root/'scripts/release_candidate.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
c=object.__new__(m.Candidate);c.root=root
rows=[]
for sig in (signal.SIGTERM,signal.SIGINT):
 class Finished:
  returncode=0
  calls=0
  def poll(self):
   self.calls+=1
   if self.calls==2:signal.raise_signal(sig)
   return 0
 m.subprocess.Popen=lambda *a,**k:Finished()
 result=c._run_suite(io.BytesIO())
 rows.append({'signal':sig.name,'result':list(result),'interrupt_preserved':result[1]=='interrupted'})
print(json.dumps({'source_argument':str(root),'controls':rows},indent=2))
