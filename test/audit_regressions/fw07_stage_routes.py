#!/usr/bin/env python3
"""Default-profile source routes; no host read or task-quality assertion."""
from pathlib import Path
import shutil
import sys
import tempfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'test'))
from stage_routes import DETAILS, ROUTE, route_errors


def main():
    count = 0
    def check(condition, label):
        nonlocal count
        assert condition, label
        count += 1
    original = ROOT / 'plugins/task-pipeline/skills/task-pipeline/references'
    check(not route_errors(original), 'live source routes')
    with tempfile.TemporaryDirectory(prefix='fw07-routes-') as folder:
        refs = Path(folder)
        for name in ('stages.md', *DETAILS):shutil.copyfile(original / name, refs / name)
        check(not route_errors(refs), 'isolated plain-skill routes without repo or sibling packs')
        spine = (refs / 'stages.md').read_text()
        for sid, name in enumerate(DETAILS):
            target = refs / name; data = target.read_bytes()
            target.unlink();check(bool(route_errors(refs)), f'missing stage {sid}');target.write_bytes(data)
            wrong = DETAILS[(sid + 1) % len(DETAILS)]
            (refs / 'stages.md').write_text(spine.replace(f'[{name}]({name})', f'[{wrong}]({wrong})'))
            check(bool(route_errors(refs)), f'wrong stage {sid} route')
            (refs / 'stages.md').write_text(spine)
            check(f'[{name}]({name}) before stage work' in spine, f'exact entry/resume route {sid}')
        target = refs / DETAILS[0]; data = target.read_bytes()
        for malformed in (b'', b'\xff', data.replace(b'## 0 ', b'## 1 '), data + b'\n- **GATE (manual):** duplicate\n'):
            target.write_bytes(malformed);check(bool(route_errors(refs)), 'unreadable/empty/wrong-stage/duplicate-gate detail')
        target.write_bytes(data)
        route = ROUTE.search(spine).group(0)
        for bad in (spine.replace(route, route+'\n'+route), spine.replace('## 1 — Docs study','## 0 — Docs study'), route+'\n'+spine):
            (refs / 'stages.md').write_text(bad);check(bool(route_errors(refs)), 'duplicate route or stage / route outside stage')
        (refs / 'stages.md').write_text(spine.replace('\n', '\r\n'))
        check(not route_errors(refs), 'universal newline read')
    skill = (original.parent / 'SKILL.md').read_text()
    check('CUSTOM profiles use their own declared doctrine' in ' '.join(skill.split()), 'custom profile route boundary')
    check('numeric ids do not select' in spine and 'kernel still applies' in spine, 'custom ids do not inject default semantics')
    check('including wave' in spine and 'approved short paths' in spine, 'wave and approved-short-path scope')
    check('Do not preload all stage details' in spine, 'no all-stage preload')
    print(f'PASS: FW07 stage route source controls — {count}; native reads and task quality NOT_RUN')


if __name__ == '__main__':main()
