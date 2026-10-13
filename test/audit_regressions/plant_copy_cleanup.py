#!/usr/bin/env python3
"""Actual runner controls confined to newly owned /tmp namespaces; no public plants."""
import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import warnings
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import negatives as N


class CopyCleanup(unittest.TestCase):
    def setUp(self):
        self.owned = tempfile.TemporaryDirectory(prefix='tp-copy-cleanup-', dir='/tmp')
        self.addCleanup(self.owned.cleanup)
        self.box = Path(self.owned.name)
        self.repo = self.box / 'source'
        self.repo.mkdir()
        (self.repo / 'source.txt').write_text('original\n')
        self.first, self.second = self.box / 'first', self.box / 'second'
        self.foreign = self.box / 'foreign'
        self.foreign.mkdir()
        (self.foreign / 'keep').write_text('unrelated\n')

    def pair(self, path):
        return f'rm -rf {path} && cp -R . {path}\n'

    def run_script(self, script, *, prop=False, exception=False):
        name = ('Property check' if prop else 'Negative self-test') + ' (owned fixture)'
        rows = [('001-owned.sh', name, script)]
        real_run = subprocess.run
        def run(args, **kw):
            result = real_run(args, **kw)
            if exception and args[0] == 'bash':
                raise OSError('injected runner observation failure after child completion')
            return result
        out = io.StringIO()
        # ROOT is tiny and owned; lock mock prevents touching the public family lock.
        # Snapshot allocations are also confined to the owned fixture for cleanup.
        real_mkdtemp = tempfile.mkdtemp
        def allocate(*a, **kw):
            kw['dir'] = self.box
            return real_mkdtemp(*a, **kw)
        with patch.object(N, 'ROOT', str(self.repo)), \
             patch.object(N, 'scan', return_value=(rows, [])), \
             patch.object(N, 'MIN_EXPECTED', 0 if prop else 1), \
             patch.object(N, 'MIN_PROPS', 1 if prop else 0), \
             patch.object(N, 'acquire_scratch_lock', return_value=io.StringIO()), \
             patch.object(N.tempfile, 'mkdtemp', side_effect=allocate), \
             patch.object(N.subprocess, 'run', side_effect=run), \
             contextlib.redirect_stdout(out):
            try:
                code = N.main(['negatives.py'])
            except OSError as exc:
                code = type(exc).__name__
        return code, out.getvalue()

    def script(self, finish='echo OK: fixture', first_changed=True, second_changed=True):
        return (self.pair(self.first) +
                (f'echo planted >> {self.first}/source.txt\n' if first_changed else '') +
                self.pair(self.second) +
                (f'echo planted >> {self.second}/source.txt\n' if second_changed else '') + finish)

    def assert_copies_gone(self):
        self.assertFalse(self.first.exists(), 'first copy leaked')
        self.assertFalse(self.second.exists(), 'second copy leaked')
        self.assertEqual((self.foreign / 'keep').read_text(), 'unrelated\n')

    def test_all_copies_success(self):
        self.assertEqual(self.run_script(self.script())[0], 0)
        self.assert_copies_gone()

    def test_all_copies_shell_failure(self):
        self.assertEqual(self.run_script(self.script('exit 7'))[0], 1)
        self.assert_copies_gone()

    def test_all_copies_runner_exception(self):
        self.assertEqual(self.run_script(self.script(), exception=True)[0], 'OSError')
        self.assert_copies_gone()

    def test_property_copies_success(self):
        self.assertEqual(self.run_script(self.script(), prop=True)[0], 0)
        self.assert_copies_gone()

    def test_property_copies_exception(self):
        self.assertEqual(self.run_script(self.script(), prop=True, exception=True)[0], 'OSError')
        self.assert_copies_gone()

    def test_primary_unchanged_stays_broken_despite_secondary_change(self):
        code, out = self.run_script(self.script(first_changed=False))
        self.assertEqual(code, 1)
        self.assertIn('BROKEN', out)
        self.assert_copies_gone()

    def test_secondary_unchanged_does_not_change_primary_verdict(self):
        self.assertEqual(self.run_script(self.script(second_changed=False))[0], 0)
        self.assert_copies_gone()

    def test_heredoc_and_comment_are_not_cleanup_authority(self):
        payload = ("cat <<'DATA' >/dev/null\n" + self.pair(self.foreign) + 'DATA\n' +
                   '# ' + self.pair(self.foreign))
        self.assertEqual(self.run_script(self.script() + '\n' + payload)[0], 0)
        self.assert_copies_gone()

    def test_corpus_all_copy_declarations_admitted_without_execution(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', ResourceWarning)
            corpus, problems = N.scan()
        self.assertFalse(problems)
        found = {file: N.copy_dirs_of(script) for file, _, script in corpus}
        self.assertEqual(len(next(paths for file, paths in found.items()
                                  if file.startswith('157-'))), 2)
        self.assertEqual(len(next(paths for file, paths in found.items()
                                  if file.startswith('158-'))), 2)
        # Quoted declarations in Python payloads must not join cleanup.
        for prefix in ('087-', '238-', '331-'):
            self.assertEqual(len(next(paths for file, paths in found.items()
                                      if file.startswith(prefix))), 1)

    def test_unsafe_declarations_refuse_before_child(self):
        for target in ('/tmp', '/tmp/', '/tmp/../private', '/tmp/x/../y',
                       '/tmp/x//y', '/tmp/$NAME', '/tmp/x;echo', '/var/tmp/x',
                       '"/tmp/x"', '/tmp/x*'):
            with self.subTest(target=target):
                called = []
                with self.assertRaises(ValueError):
                    N.run_plant('cp -R . ' + target, called.append)
                self.assertEqual(called, [])
        with self.assertRaises(ValueError):
            N.copy_dirs_of(f'rm -rf {self.foreign} && cp -R . {self.first}')
        self.assertTrue((self.foreign / 'keep').exists())

    def test_comments_strings_and_heredocs_are_inert(self):
        for opener, closer in [("cat <<'DATA'", 'DATA'), ('cat <<DATA', 'DATA'),
                               ('cat <<"DATA"', 'DATA'), ("cat <<-'DATA'", '\tDATA')]:
            script = opener + '\n' + self.pair(self.foreign) + closer + '\n'
            script += '# ' + self.pair(self.foreign)
            script += 'echo "cp -R . ' + str(self.foreign) + '"\n'
            self.assertEqual(N.copy_dirs_of(script), [])
        with self.assertRaises(ValueError):
            N.copy_dirs_of("cat <<'DATA'\n" + self.pair(self.foreign))

    def test_multiline_quoted_declaration_is_not_cleanup_authority(self):
        for quote in ("'", '"'):
            script = 'echo ' + quote + '\n' + self.pair(self.foreign) + quote + '\n'
            self.assertEqual(N.copy_dirs_of(script), [])
        with self.assertRaises(ValueError):
            N.copy_dirs_of("bash <<'DATA'\n" + self.pair(self.foreign) + 'DATA\n')

    def test_continued_echo_is_not_cleanup_authority(self):
        script = 'echo ' + chr(92) + '\ncp -R . ' + str(self.foreign) + '\n'
        self.assertEqual(N.copy_dirs_of(script), [])

    def test_observation_failure_still_cleans_both(self):
        with patch.object(N, 'differs_from_repo', side_effect=OSError('injected diff failure')):
            self.assertEqual(self.run_script(self.script())[0], 'OSError')
        self.assert_copies_gone()

    def test_duplicate_declaration_cleanup_once(self):
        script = self.pair(self.first) + self.pair(self.first)
        self.assertEqual(N.copy_dirs_of(script), [str(self.first)])

    def test_symlink_target_and_ancestor_refused_without_deletion(self):
        for target in (self.first, self.first / 'child'):
            self.first.symlink_to(self.foreign, target_is_directory=True)
            try:
                with self.assertRaises(ValueError):
                    N.run_plant(self.pair(target), lambda _: self.fail('child ran'))
                self.assertEqual((self.foreign / 'keep').read_text(), 'unrelated\n')
                self.assertTrue(self.first.is_symlink())
            finally:
                self.first.unlink()

    def test_cleanup_error_is_not_silent_success(self):
        with patch.object(N.shutil, 'rmtree', side_effect=PermissionError('injected')):
            with self.assertRaises(OSError):
                N.sweep([str(self.first)])

    def test_cleanup_attempts_remaining_paths_after_one_failure(self):
        # Implementations must attempt the independent second copy even if the first
        # cleanup fails; the aggregate error still prevents a success claim.
        self.first.mkdir(); self.second.mkdir()
        real = N.shutil.rmtree
        def fail_first(path):
            if path == str(self.first):
                raise PermissionError('injected first cleanup failure')
            return real(path)
        with patch.object(N.shutil, 'rmtree', side_effect=fail_first):
            with self.assertRaises(OSError):
                N.sweep([str(self.first), str(self.second)])
        self.assertTrue(self.first.exists())
        self.assertFalse(self.second.exists())


if __name__ == '__main__':
    unittest.main()
