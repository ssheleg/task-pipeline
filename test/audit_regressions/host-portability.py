#!/usr/bin/env python3
"""Portable skill installs have no sibling skill or plugin agent directory.

Copies only each actual skill payload to a temporary custom path, then validates
required procedure closure and executes the project collector offline. No provider.
"""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / 'plugins/task-pipeline'


def check_payloads(root):
    pipeline = root / 'task-pipeline'
    project = root / 'project-audit'
    for tier in ('unit', 'seam', 'product', 'visual'):
        body = (pipeline / 'assets' / ('verifier-' + tier + '.md')).read_text()
        canonical = (PLUGIN / 'agents' / ('verifier-' + tier + '.md')).read_text().split('---', 2)[2].lstrip()
        assert body == canonical, 'portable verifier body drift: ' + tier
    md = (project / 'SKILL.md').read_text()
    assert '../task-pipeline/' not in md, 'project-audit still requires sibling install'
    method = (project / 'references/portable-method.md').read_text()
    assert all('L' + str(i) in method for i in range(8)), 'portable ladder incomplete'
    for heading in ('## Evidence and missing capabilities', '## Rotate the reading', '## Proposed rows and priority'):
        assert heading in method, 'portable method loses contract section: ' + heading
    for skill in (pipeline, project):
        docs = [skill / 'SKILL.md']
        docs += list((skill / 'assets').glob('verifier-*.md'))
        docs += list((skill / 'references').glob('portable-method.md'))
        if skill == pipeline:
            docs += [skill / 'references/certification.md']
        for f in docs:
            for link in re.findall(r'\]\(([^\s)]+)\)', f.read_text()):
                path = link.split('#')[0]
                if not path or ':' in path:
                    continue
                target = (f.parent / path).resolve()
                assert target.is_relative_to(skill.resolve()) and target.exists(), (f, path)


def main():
    with tempfile.TemporaryDirectory(prefix='portable skills ') as tmp:
        root = Path(tmp)
        for name in ('task-pipeline', 'project-audit'):
            shutil.copytree(PLUGIN / 'skills' / name, root / name)
        check_payloads(root)
        # A planted missing procedure must fail before any collector evidence exists.
        missing = root / 'task-pipeline/assets/verifier-unit.md'
        saved = missing.read_bytes()
        missing.unlink()
        try:
            check_payloads(root)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError('missing portable verifier was accepted')
        missing.write_bytes(saved)
        project = root / 'fixture-project'
        project.mkdir()
        subprocess.run(['git', 'init', '-q', str(project)], check=True)
        (project / 'README.md').write_text('# Frozen offline fixture\nNo deployment or provider receipt.\n')
        subprocess.run(['git', '-C', str(project), 'add', 'README.md'], check=True)
        subprocess.run(['git', '-C', str(project), '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.com', 'commit', '-qm', 'fixture'], check=True)
        result = subprocess.run([sys.executable, str(root / 'project-audit/scripts/audit.py'), '--root', str(project), '--out', str(root / 'report.json'), '--report', '--no-open', '--offline'], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        report = json.loads(next((root / 'report.json').glob('*-audit.json')).read_text())
        assert isinstance(report, dict) and report, 'empty collector report'
        assert len(list((root / 'report.json').glob('*-audit.html'))) == 1, result.stdout
        # No sibling task-pipeline in project-audit's installation parent.
        isolated = root / 'project-only' / 'project-audit'
        shutil.copytree(root / 'project-audit', isolated)
        result = subprocess.run([sys.executable, str(isolated / 'scripts/audit.py'), '--root', str(project), '--out', str(root / 'alone.json'), '--report', '--no-open', '--offline'], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        assert json.loads(next((root / 'alone.json').glob('*-audit.json')).read_text()) and len(list((root / 'alone.json').glob('*-audit.html'))) == 1
        result = subprocess.run([sys.executable, str(isolated / 'scripts/audit.py'), '--root', str(project), '--out', str(root / 'json-only'), '--offline'], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        assert len(list((root / 'json-only').glob('*-audit.json'))) == 1
        assert not list((root / 'json-only').glob('*.html')), 'default unexpectedly created HTML'
    print('PASS: isolated payload closure, missing-procedure negative, offline JSON+HTML with no companion')


if __name__ == '__main__':
    main()
