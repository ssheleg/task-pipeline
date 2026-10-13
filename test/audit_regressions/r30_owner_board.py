#!/usr/bin/env python3
# shared-mechanism: sshlg-skills/owner-board-controls-v1
# diverges: shared 25 grammar/file controls; real owner-validator process cases are in the candidate receipt.
"""R30: declaration parsing, escaped-pipe controls, and missing/unreadable files."""
from pathlib import Path
import importlib.util
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'test'))
from owner_board import board_errors, check

BASE='| ID | What |\n|---|---|\n| AS-1 | healthy |\n'
checks=0

def expect(text, needle=None):
    global checks
    errors=board_errors(text)
    assert (any(needle in e for e in errors) if needle else not errors), (needle,errors)
    checks+=1

expect(BASE)
expect(BASE+'\n| ID | What |\n|---|---|\n| AS-1 | again |\n','duplicate ID')
expect(BASE.replace('healthy','text | shifted'),'row width')
expect(BASE.replace('healthy',r'text \| content'))
expect(BASE.replace('healthy',r'text \\| separator'),'row width')
expect(BASE.replace('AS-1','**AS-1**'))
expect(BASE.replace('AS-1','AW-0906-desc'))
expect(BASE.replace('AS-1','AW-0906-refusal'))
expect(BASE.replace('AS-1','AW-0906-desc')+BASE.replace('AS-1','AW-0906-desc'),'duplicate ID')
expect(BASE.replace('AS-1','not-an-id'),'invalid ID')
expect(BASE.replace('|---|---|\n',''),'matching separator')
expect(BASE.replace('|---|---|','|---|---|---|'),'matching separator')
expect(BASE.replace('| AS-1 |','\n| AS-1 |'),'without ID header')
expect(BASE.replace('| AS-1 |','<!-- break -->\n| AS-1 |'),'without ID header')
expect('| AS-1 | orphan |\n','without ID header')
expect(BASE.replace('| ID |','| Row |'),'Row header unsupported')
expect(BASE.replace('healthy','citation AS-1, not a declaration'))
expect(BASE+'\n```md\n| AS-1 | fenced example |\n```\n')
expect(BASE+'\n| ID | What | More |\n|---|---|---|\n| AS-2 | second shape | accepted |\n')
expect(BASE.replace('healthy |','healthy'),'row width')
expect('','no declared rows')
expect(BASE.replace('| AS-1 | healthy |',''),'no declared rows')
expect((ROOT/'docs/evidence/backlog.md').read_text())
with tempfile.TemporaryDirectory(prefix='r30-board-check-') as tmp:
    out=[];check(Path(tmp),out.append);assert any('board missing' in x for x in out);checks+=1
    board=Path(tmp)/'docs/evidence/backlog.md';board.parent.mkdir(parents=True);board.write_bytes(b'\xff')
    out=[];check(Path(tmp),out.append);assert any('board unreadable' in x for x in out);checks+=1
print(f'PASS: owner board {checks} focused controls')
