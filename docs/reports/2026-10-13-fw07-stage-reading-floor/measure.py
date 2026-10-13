#!/usr/bin/env python3
"""Read a frozen Git tree; emit bounded token and literal-consumer evidence.
Requires installed tiktoken. Does not alter source, run suites or contact a provider.
"""
import hashlib,json,re,subprocess
from collections import Counter
from pathlib import Path
import tiktoken
SOURCE='4d750573ce53ea4c7ffa2bde192ee35b59acefa7'
BASE='plugins/task-pipeline/skills/task-pipeline/'
OUT=Path(__file__).resolve().parent/'raw'

def git(*args):
    return subprocess.check_output(['git',*args],text=True)
def text(path):return git('show',SOURCE+':'+path)
def tok(value):return len(enc.encode(value))
enc=tiktoken.get_encoding('cl100k_base')
s=text(BASE+'references/stages.md');lines=s.splitlines()
heads=list(re.finditer(r'^## (\d+) — (.+)$',s,re.M));assert [int(x.group(1)) for x in heads]==list(range(11))
sections=[];pieces=[]
for i,m in enumerate(heads):
    end=heads[i+1].start() if i+1<len(heads) else s.index('## The program loop')
    part=s[m.start():end];gate=part.index('- **GATE (');assert part.count('- **GATE (')==1
    heading=part.splitlines()[0]+'\n'
    freedom=next(x for x in part.splitlines() if x.startswith('- **Freedom:'))+'\n'
    suffix=part[gate:]
    pieces.append(heading+freedom+suffix)
    sections.append({'stage':int(m.group(1)),'title':m.group(2),'start_line':s.count('\n',0,m.start())+1,'end_line':s.count('\n',0,end),'section_tokens':tok(part),'gate_suffix_tokens':tok(suffix),'detail_prefix_tokens':tok(part[:gate]),'section_sha256':hashlib.sha256(part.encode()).hexdigest(),'gate_suffix_sha256':hashlib.sha256(suffix.encode()).hexdigest()})
front=s[:heads[0].start()];cross=s[s.index('## The program loop'):]
# Conservative syntactic model only: keeps complete gate suffixes, headings,
# freedom levels and all run-wide sections. No semantic relocation is performed.
model=front+''.join(pieces)+cross
skill=text(BASE+'SKILL.md');body=skill.split('---',2)[2].strip()
refs=git('ls-tree','-r','--name-only',SOURCE).splitlines()
refpaths=[p for p in refs if p.startswith(BASE+'references/') and p.endswith('.md')]
consumer=[]
raw=git('grep','-n','-I','-F','stages.md',SOURCE,'--','.')
for line in raw.splitlines():
    _,path,number,content=line.split(':',3)
    category=('test-negative' if path.startswith('test/negatives/') else 'test' if path.startswith('test/') else 'shipped' if path.startswith(('plugins/','cursor/')) else 'historical-evidence' if path.startswith('docs/evidence/') else 'documentation')
    consumer.append({'path':path,'line':int(number),'category':category,'text':content})
summary={'source':SOURCE,'source_path':BASE+'references/stages.md','source_sha256':hashlib.sha256(s.encode()).hexdigest(),'tokenizer':'tiktoken cl100k_base','version':json.loads(text('package.json'))['version'],'stages_tokens':tok(s),'stages_lines':len(lines),'skill_body_tokens':tok(body),'skill_body_lines':len(body.splitlines()),'reference_files':len(refpaths),'pre_stage_tokens':tok(front),'cross_cutting_tokens':tok(cross),'spine_model_tokens_before_routes':tok(model),'entry_model_tokens_before_routes':tok(model)+sections[0]['detail_prefix_tokens'],'model_limit':'Syntactic estimate only; heading/freedom overhead is conservative double counting in the stage-0 detail. Final routes, conditions and actual host reads are unmeasured. Cumulative full-run savings are not asserted.','literal_consumer_lines':len(consumer),'literal_consumer_files':len({r['path'] for r in consumer}),'consumer_categories':dict(Counter(x['category'] for x in consumer)),'stage_sections':sections}
OUT.mkdir(exist_ok=True)
(OUT/'measurement.json').write_text(json.dumps(summary,indent=2)+'\n')
(OUT/'consumers.json').write_text(json.dumps(consumer,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='stage_sections'},indent=2))
