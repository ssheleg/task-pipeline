# shared-mechanism: sshlg-skills/member-gates-v1
# diverges: none
# Extraction scope: board-only extraction; identifiers allow a lowercase hyphen suffix for AW-0906-desc/refusal.
# Source: agent-stack 792e3f6cb2e46517f0187066db55edc63ae7d12c:test/member_gates.py.
"""Bounded ID-table grammar: explicit declarations, no implicit continuation.

This does not parse arbitrary Markdown. Headers start with ID; each table has an
immediate width-matching separator. References belong in prose, not duplicate rows.
"""
from pathlib import Path
import re


def cells(line):
    """Markdown pipes escaped by an odd number of backslashes are cell content."""
    result, start, escapes = [], 0, 0
    for index, char in enumerate(line):
        if char == '|' and escapes % 2 == 0:
            result.append(line[start:index].strip())
            start = index + 1
        escapes = escapes + 1 if char == '\\' else 0
    result.append(line[start:].strip())
    return result[1:-1] if not result[0] and not result[-1] else result


def label(value):
    value = value.strip().strip('*` ')
    link = re.fullmatch(r'\[([^\]]+)\]\([^)]*\)', value)
    return (link.group(1) if link else value).strip('*` ')


def board_errors(text):
    errors, seen, width, declares, count, fenced = [], {}, None, False, 0, False
    pending = None
    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        row = cells(line) if line.startswith('|') else []
        separator = bool(row) and all(re.fullmatch(r':?-{3,}:?', c) for c in row)
        if pending is not None:
            if separator and len(row) == width and line.endswith('|'):
                pending = None
                continue
            errors.append(f'{pending}: board header needs an immediate matching separator')
            pending = None
        if line.startswith(('```', '~~~')):
            fenced = not fenced
            width = None
            continue
        if fenced:
            continue
        if not line.startswith('|'):
            width = None
            continue
        first = label(row[0]) if row else ''
        if first.lower() == 'row':
            errors.append(f'{number}: board Row header unsupported; use ID for declarations')
            width = None
            continue
        if first.lower() == 'id':
            width, declares, pending = len(row), True, number
            continue
        if separator:
            if width is not None:
                errors.append(f'{number}: board misplaced separator')
            continue
        identifier = re.fullmatch(r'[A-Z]{1,4}-\d+(?:[a-z]|-[a-z]+)?', first)
        if width is None:
            if identifier:
                errors.append(f'{number}: board row without ID header: {first}')
            continue
        if len(row) != width or not line.endswith('|'):
            errors.append(f'{number}: board row width: {first} has {len(row)} cells; header declares {width}')
        if not identifier:
            errors.append(f'{number}: board invalid ID: {first!r}')
            continue
        if declares:
            count += 1
            if first in seen:
                errors.append(f'{number}: board duplicate ID {first}; first at {seen[first]}')
            seen[first] = number
    if pending is not None:
        errors.append(f'{pending}: board header needs an immediate matching separator')
    if not count:
        errors.append('board has no declared rows')
    return errors



def check(root, fail):
    relative = 'docs/evidence/backlog.md'
    try:
        text = (Path(root) / relative).read_text(encoding='utf-8')
    except OSError as exc:
        fail(f'{relative}: board missing or unreadable: {exc.__class__.__name__}')
        return
    except UnicodeError:
        fail(f'{relative}: board unreadable: invalid UTF-8')
        return
    for error in board_errors(text):
        fail(f'{relative}: {error}')
