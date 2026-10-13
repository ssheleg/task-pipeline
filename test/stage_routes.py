"""Bounded default-stage route checks, independent of native host execution."""
from pathlib import Path
import re

DETAILS = (
    'stage-00-intake.md', 'stage-01-docs-study.md', 'stage-02-brainstorm.md',
    'stage-03-spec.md', 'stage-04-plan.md', 'stage-05-dev.md', 'stage-06-tests.md',
    'stage-07-lint-deploy.md', 'stage-08-post-deploy.md', 'stage-09-docs-wiki.md',
    'stage-10-acceptance.md',
)
ROUTE = re.compile(r'^\*\*On entry or resume:\*\* read \[([^\]]+)\]\(([^)]+)\) before stage work\.$', re.M)


def detail_path(refs, stage):
    index = int(stage)
    if not 0 <= index < len(DETAILS):
        raise ValueError("not a default stage id")
    return Path(refs) / DETAILS[index]


def detail_text(refs, stage):
    # route_errors separately reports absent/unreadable targets, never a silent pass.
    try:
        return detail_path(refs, stage).read_text(encoding='utf-8')
    except (OSError, UnicodeError, ValueError, TypeError):
        return ''


def route_errors(refs):
    refs = Path(refs)
    try:
        spine = (refs / 'stages.md').read_text(encoding='utf-8')
    except (OSError, UnicodeError):
        return ['stage routes: unreadable spine']
    errors = []
    heads = list(re.finditer(r'^## (\d+) — (.+)$', spine, re.M))
    if [int(h[1]) for h in heads] != list(range(len(DETAILS))):
        errors.append('stage routes: default stage ids are missing, duplicate or reordered')
    found = []
    for index, head in enumerate(heads):
        sid = int(head[1]); end = heads[index + 1].start() if index + 1 < len(heads) else len(spine)
        section = spine[head.end():end]
        routes = ROUTE.findall(section); found.extend(routes)
        gate = re.search(r"^- \*\*GATE \(", section, re.M)
        route = ROUTE.search(section)
        if not gate or not route or route.start() > gate.start():
            errors.append(f'stage routes: stage {sid} route must precede its full gate')
        if sid >= len(DETAILS) or routes != [(DETAILS[sid], DETAILS[sid])]:
            errors.append(f'stage routes: stage {sid} needs its one exact on-entry/resume detail')
            continue
        text = detail_text(refs, sid)
        if not text:
            errors.append(f'stage routes: unreadable or empty {DETAILS[sid]}')
        elif re.findall(r'^## (\d+) — (.+)$', text, re.M) != [(str(sid), head[2])]:
            errors.append(f'stage routes: {DETAILS[sid]} does not name its matching stage')
        elif re.search(r'^- \*\*GATE \(', text, re.M):
            errors.append(f'stage routes: {DETAILS[sid]} duplicates the spine gate')
    if len(ROUTE.findall(spine)) != len(found) or len(found) != len(DETAILS):
        errors.append('stage routes: route count or location differs from the default stage set')
    return errors
