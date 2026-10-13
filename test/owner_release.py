# shared-mechanism: sshlg-skills/member-release-v1
# diverges: none
# Extraction scope: release-only extraction; readable file failures include invalid UTF-8.
# Source: agent-stack 792e3f6cb2e46517f0187066db55edc63ae7d12c:test/member_gates.py.
"""Bounded release workflow contract; not an arbitrary YAML or shell parser."""
from pathlib import Path
import re
import shlex


def release_errors(text):
    """Require the live release job's checkout and unconditional refusing guard.

    Bounded to this family's two-space job/six-space step layout; comments or
    matching text in another job/step cannot satisfy this contract.
    """
    errors = []
    active = '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('#'))
    if re.search(r'^\s*(?:-\s*)?<<\s*:', active, re.M):
        return ['release ancestry guard merge keys require explicit review']
    if re.search(r'^\s*(?:-\s*)?[\'"][^\'"\n]+[\'"]\s*:', active, re.M):
        return ['release ancestry guard quoted mapping keys require explicit review']
    if len(re.findall(r'^jobs:', active, re.M)) != 1 or len(re.findall(r'^  release:', active, re.M)) != 1:
        return ['release ancestry guard job is missing or ambiguous']
    if re.search(r'^(?:defaults:|    defaults:)', active, re.M):
        return ['release ancestry guard defaults require explicit review']
    job = re.search(r'^  release:\s*\n(?P<body>.*?)(?=^  [\w-]+:|\Z)', active, re.M | re.S)
    if not job:
        return ['release job missing or unsupported layout']
    body = job.group('body')
    if len(re.findall(r'^    steps:', body, re.M)) != 1:
        return ['release ancestry guard steps are missing or ambiguous']
    if re.search(r'^    continue-on-error:\s*(?!false\s*(?:#.*)?$)\S', body, re.M):
        errors.append('release ancestry failure ignored at job scope')
    steps = re.split(r'(?=^      - )', body, flags=re.M)[1:]
    full, checkouts, guards = [], [], []
    for index, step in enumerate(steps):
        if re.search(r'^(?:      - |        )uses:\s*actions/checkout@', step, re.M):
            checkouts.append(index)
            options = re.findall(r'^        with:\s*\n((?:          [^\n]*\n?|\n)*)', step, re.M)
            depth = re.findall(r'^          fetch-depth:\s*(.*?)\s*(?:#.*)?$', options[0], re.M) if len(options) == 1 else []
            uses = re.findall(r'^(?:      - |        )uses:', step, re.M)
            if (len(uses) == 1 and len(re.findall(r'^        with:', step, re.M)) == 1
                and not re.search(r'^(?:      - |        )if:', step, re.M)
                and not re.search(r'^(?:      - |        )continue-on-error:\s*(?!false\s*(?:#.*)?$)\S', step, re.M)
                and len(depth) == 1 and depth[0].strip('\'"') == '0'):
                full.append(index)
        run = re.search(r'^        run:\s*\|[-+]?\s*\n((?:          [^\n]*\n?|\n)*)', step, re.M)
        if not run:
            continue
        shell = run.group(1)
        guard = re.search(r'^          if ! git merge-base --is-ancestor HEAD [\'"]origin/\$DEF[\'"]; then\s*\n(?P<failure>.*?)(?=^          fi\s*$)', shell, re.M | re.S)
        if not guard:
            continue
        guards.append(index)
        # This is the supported shell setup, not a substring hunt through arbitrary
        # programs. Unknown setup/control flow must be reviewed with new fixtures.
        prefix = [line.strip() for line in shell[:guard.start()].splitlines() if line.strip()]
        expected = ['set -eu', 'DEF="$(gh api "repos/$GITHUB_REPOSITORY" --jq .default_branch)"',
                    'git fetch --no-tags origin "$DEF"']
        if prefix != expected or len(re.findall(r'^(?:      - |        )run:', step, re.M)) != 1:
            errors.append('release ancestry guard has unsupported setup or duplicate run')
        commands = [line.strip() for line in guard.group('failure').replace('\\\n', '').splitlines() if line.strip()]
        try:
            refusal = shlex.split(commands[-1], comments=True) == ['exit', '1']
            for command in commands[:-1]:
                tokens = list(shlex.shlex(command, posix=True, punctuation_chars=';&|'))
                if not tokens or tokens[0] != 'echo' or any(t and set(t) <= set(';&|') for t in tokens) or '$(' in command or '`' in command:
                    refusal = False
        except (ValueError, IndexError):
            refusal = False
        if not refusal:
            errors.append('release ancestry guard refusal has unsupported control flow')
        shell_option = re.findall(r'^(?:      - |        )shell:\s*(.*?)\s*$', step, re.M)
        if shell_option and shell_option != ['bash']:
            errors.append('release ancestry guard shell requires explicit review')
        if not re.search(r'^\s+exit 1\s*(?:#.*)?$', guard.group('failure'), re.M):
            errors.append('release ancestry guard has no refusing exit')
        if re.search(r'^(?:      - |        )if:', step, re.M):
            errors.append('release ancestry step conditional')
        if re.search(r'^(?:      - |        )continue-on-error:\s*(?!false\s*(?:#.*)?$)\S', step, re.M):
            errors.append('release ancestry failure ignored at step scope')
    if not guards:
        errors.append('release ancestry guard missing from a live run block')
    before = [i for i in checkouts if guards and i < guards[0]]
    if not full or (guards and (not before or before[-1] not in full)):
        errors.append('release full-history checkout missing before ancestry guard')
    return errors


def check(root, fail):
    path = Path(root) / '.github/workflows/release.yml'
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as exc:
        fail(f'release workflow unreadable: {exc.__class__.__name__}')
        return
    for error in release_errors(text):
        fail(f'.github/workflows/release.yml: {error}')
