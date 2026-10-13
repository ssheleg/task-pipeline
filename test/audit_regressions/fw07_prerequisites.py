#!/usr/bin/env python3
"""Actual source-guard mutations for the accepted artifact-provider contract.

Runs the existing regression entry in a small owned source fixture. It does not
simulate a native host, prove arbitrary prose semantics or invoke provider tools.
"""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
TEST = Path('test/audit_regressions/fix-tp-02.01.py')
BASE = 'plugins/task-pipeline/skills/task-pipeline/'
PLANTS = (
    (BASE + 'references/stage-03-spec.md', 'Requires the **super-ux** skills.'),
    (BASE + 'references/spec.md', "If it isn’t installed on a UI task, give the install line and stop."),
    (BASE + 'SKILL.md', 'The stage-3 UX track requires super-ux, and the spec gate stops until it is installed.'),
    (BASE + 'references/doctrine-map.md', 'The single deliberate exception is the stage-3 UX track on a user-facing task.'),
    (BASE + 'references/companion-skills.md', '**Never gate any stage on an install** except the stage-3 UX track on a UI task.'),
    ('plugins/task-pipeline/commands/task-pipeline.md', 'None is a gate except the stage-3 UX track on a user-facing task.'),
    ('README.md', 'On a user-facing task the stage-3 UX track requires super-ux, and the spec gate stops until it is installed.'),
    ('README.md', '| [super-ux](https://github.com/ssheleg/super-ux) | the stage-3 UX track | only for user-facing tasks |'),
    ('HOW-IT-WORKS.md', 'A missing companion does not block — the single exception being the stage-3 UX track on user-facing work.'),
    ('SKILL-CARD.md', 'The one conditional requirement is super-ux for the stage-3 UX track on a user-facing task.'),
)


def main():
    count = 0
    spec = importlib.util.spec_from_file_location('prerequisite_contract', ROOT / TEST)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='fw07-prerequisites-') as folder:
        fixture = Path(folder)
        for rel in (*module.PREREQUISITE_HOMES, str(TEST)):
            target = fixture / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, target)
        def run():
            return subprocess.run([sys.executable, '-B', str(fixture / TEST)],
                                  cwd=fixture, capture_output=True, text=True)
        baseline = run()
        assert baseline.returncode == 0, baseline.stdout + baseline.stderr
        count += 1
        for rel, original in PLANTS:
            target = fixture / rel
            before = target.read_text()
            for phrase in (original, '\n  '.join(original.split())):
                try:
                    target.write_text(before + '\n\n' + phrase + '\n')
                    result = run()
                    assert result.returncode == 1, (rel, result.stdout, result.stderr)
                    assert 'package-install prerequisite survived: ' + rel in result.stdout, result.stdout
                    assert 'Traceback' not in result.stderr, result.stderr
                    count += 1
                finally:
                    target.write_text(before)
        # Each relocated entry must preserve the real artifact gate and named
        # unavailable-check disclosure; provider fallback is not a quality bypass.
        for name in ('stage-03-spec.md', 'spec.md'):
            target = fixture / (BASE + 'references/' + name)
            before = target.read_text()
            for obligation in ('Missing or invalid scenario artifacts stop the gate, regardless of provider.',
                               'Record each unavailable check by name as NOT_RUN',
                               'equivalent artifacts', 'inline fallback'):
                try:
                    assert obligation in before
                    target.write_text(before.replace(obligation, 'omitted obligation', 1))
                    result = run()
                    assert result.returncode == 1, (name, obligation, result.stdout)
                    assert 'stage entry preserves quality and tool uncertainty' in result.stdout
                    assert 'Traceback' not in result.stderr
                    count += 1
                finally:
                    target.write_text(before)
        # Ordinary reflow cannot be confused with removal of an obligation.
        for rel in module.PREREQUISITE_HOMES:
            target = fixture / rel
            target.write_text(target.read_text().replace(' ', '  '))
        reflow = run()
        assert reflow.returncode == 0, reflow.stdout + reflow.stderr
        count += 1
    print(f'PASS: FW07 prerequisite source controls — {count} (owned fixture removed)')


if __name__ == '__main__':
    main()
