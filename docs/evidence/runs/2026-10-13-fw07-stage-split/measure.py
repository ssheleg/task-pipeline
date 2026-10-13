#!/usr/bin/env python3
"""Recompute source-reading sizes; these are not observed host or billing costs."""
import hashlib
import gzip
import json
from pathlib import Path
import re
import tiktoken
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE='plugins/task-pipeline/skills/task-pipeline/'
SOURCE='cfa5248240df71a55ca6c1742ab9a02ba7867949'
enc=tiktoken.get_encoding('cl100k_base')
def tok(s):return len(enc.encode(s))
def old(path):
    item=json.loads((HERE/'baseline.json').read_text())['files'][path]
    data=gzip.decompress((HERE/item['archive']).read_bytes())
    assert hashlib.sha256(data).hexdigest()==item['sha256']
    return data.decode('utf-8')
def body(s):return s[re.match(r'^---\n.*?\n---\n',s,re.S).end():]
skill=ROOT/BASE
before=old('references/stages.md');after=(skill/'references/stages.md').read_text()
details=sorted((skill/'references').glob('stage-*.md'))
entry_detail=(skill/'references/stage-00-intake.md').read_text()
old_skill=old('SKILL.md');new_skill=(skill/'SKILL.md').read_text()
fm=lambda s:re.match(r'^---\n.*?\n---\n',s,re.S).group(0)
assert fm(old_skill)==fm(new_skill)
result={'baseline':SOURCE,'tokenizer':'tiktoken cl100k_base','before_stages':tok(before),'after_spine':tok(after),'after_intake_detail':tok(entry_detail),'before_entry_component':tok(before),'after_entry_component':tok(after)+tok(entry_detail),'before_skill_body':tok(body(old_skill)),'after_skill_body':tok(body(new_skill)),'before_body_plus_stage_entry':tok(body(old_skill))+tok(before),'after_body_plus_stage_entry':tok(body(new_skill))+tok(after)+tok(entry_detail),'all_split_files':tok(after)+sum(tok(p.read_text()) for p in details),'detail_files':len(details),'reference_files':len(list((skill/'references').glob('*.md'))),'frontmatter_unchanged':True,'source_hash_before':hashlib.sha256(before.encode()).hexdigest(),'limits':'Source-only reading components, each file read once; other routed subject doctrine and changed inventories are outside this component. Cumulative full run can grow. Native read traces, compaction/re-reads, model quality and billed usage NOT_RUN.'}
assert result['after_entry_component']<result['before_entry_component']
(HERE/'measurement.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
