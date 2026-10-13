#!/usr/bin/env python3
"""Owner-only local-tag-aware release admission. No authority is granted here."""
import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import time
import uuid

COMMAND = ['npm', 'run', 'test:all']
HOOK = 'plugins/task-pipeline/hooks/release-gate.sh'
LIMIT = 1024 * 1024


class Refusal(RuntimeError):
    pass


def need(value, message):
    if not value:
        raise Refusal(message)


def read_file(path):
    info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_size <= LIMIT,
         'regular bounded input required: ' + str(path))
    return path.read_bytes()


def private(path, directory=False):
    info = path.lstat()
    need((stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)) and
         info.st_uid == os.geteuid() and not (info.st_mode & 0o077),
         'private owned ' + ('directory' if directory else 'file') + ' required: ' + str(path))


def digest_file(path):
    need(stat.S_ISREG(path.lstat().st_mode), 'regular log required')
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda: stream.read(65536), b''):
            h.update(part)
    return h.hexdigest()


def write_json(path, data):
    pending = path.with_name(path.name + '.new-' + uuid.uuid4().hex)
    fd = os.open(pending, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as out:
        json.dump(data, out, indent=2); out.write('\n'); out.flush(); os.fsync(out.fileno())
    os.replace(pending, path)


class Candidate:
    def __init__(self, root, tag):
        self.root = Path(root).resolve()
        need(re.fullmatch(r'v\d+\.\d+\.\d+', tag), 'exact release version required')
        self.tag = tag
        self.gitdir = self.root / '.git'
        need(self.gitdir.is_dir() and not self.gitdir.is_symlink(), 'standalone clone required')
        common = Path(self.git('rev-parse', '--git-common-dir'))
        common = (self.root / common).resolve()
        need(common == self.gitdir.resolve(), 'shared Git directory refused')
        self.area = self.gitdir / 'sshlg-release-candidates'
        self.area.mkdir(mode=0o700, exist_ok=True)
        private(self.area, directory=True)
        self.directory = self.area / tag
        if self.directory.exists() or self.directory.is_symlink():
            private(self.directory, directory=True)
        else:
            self.directory.mkdir(mode=0o700)
        self.record = self.directory / 'candidate.json'
        self.log = self.directory / 'suite.log'

    def git(self, *args, root=None, check=True):
        r = subprocess.run(['git', *args], cwd=root or self.root, text=True,
                           capture_output=True, timeout=60)
        if check:
            need(r.returncode == 0, 'git operation failed: ' + ' '.join(args[:2]) + ': ' + r.stderr.strip())
        return r.stdout.strip() if check else r

    @contextmanager
    def lock(self):
        path = self.area / 'operation.lock'
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            raise Refusal('operation lock exists; inspect owner before recovery')
        try:
            with os.fdopen(fd, 'w') as out: out.write(str(os.getpid()))
            yield
        finally:
            path.unlink()

    def destination(self):
        fetch = self.git('remote', 'get-url', '--all', 'origin').splitlines()
        push = self.git('remote', 'get-url', '--push', '--all', 'origin').splitlines()
        need(len(fetch) == 1 and push == fetch, 'one identical effective fetch/push destination required')
        # An already resolved URL can itself match another rewrite when used
        # literally. Resolve fetch rewrites through Git and conservatively refuse
        # matching push-only prefixes (explicit origin.pushurl would mask these).
        need(self.git('ls-remote', '--get-url', fetch[0]) == fetch[0],
             'literal bound destination would be rewritten')
        rewrites = self.git('config', '--null', '--get-regexp', r'^url\..*\.pushinsteadof$', check=False)
        need(rewrites.returncode in (0, 1), 'cannot inspect push URL rewrites')
        for record in rewrites.stdout.split('\0'):
            if not record: continue
            key, separator, prefix = record.partition('\n')
            need(separator and not fetch[0].startswith(prefix),
                 'literal bound destination would be rewritten')
        return fetch[0]

    def source(self):
        need(self.git('rev-parse', '--is-shallow-repository') == 'false', 'full history required')
        need(not self.git('status', '--porcelain'), 'clean source required')
        package = json.loads(read_file(self.root / 'package.json'))
        need(package.get('name') == 'task-pipeline-skill', 'owner repository required')
        version = self.tag[1:]
        need(package.get('version') == version, 'package version mismatch')
        need(package.get('scripts', {}).get('test:all'), 'complete owner suite missing')
        for path, key in [('.claude-plugin/marketplace.json', 'marketplace'),
                          ('plugins/task-pipeline/.claude-plugin/plugin.json', 'plugin')]:
            value = json.loads(read_file(self.root / path))
            actual = value['plugins'][0]['version'] if key == 'marketplace' else value['version']
            need(actual == version, 'manifest version mismatch: ' + path)
        changelog = read_file(self.root / 'CHANGELOG.md').decode()
        first = re.search(r'^## \[?v?(\d+\.\d+\.\d+)', changelog, re.M)
        need(first and first[1] == version, 'changelog version mismatch')
        card = read_file(self.root / 'SKILL-CARD.md').decode().replace('**', '')
        need(re.search(r'\|\s*Version\s*\|\s*`?v?' + re.escape(version) + r'`?\s*\|', card), 'card version mismatch')
        helper = self.root / 'scripts/release_candidate.py'
        self.git('ls-files', '--error-unmatch', 'scripts/release_candidate.py')
        need(read_file(helper) == read_file(Path(__file__).resolve()), 'executing helper differs from tracked candidate source')
        return dict(commit=self.git('rev-parse', 'HEAD'), tree=self.git('rev-parse', 'HEAD^{tree}'),
                    origin=self.destination(),
                    suite_sha256=hashlib.sha256(read_file(self.root / 'package.json')).hexdigest(),
                    helper_sha256=hashlib.sha256(read_file(Path(__file__).resolve())).hexdigest(),
                    hook_sha256=hashlib.sha256(read_file(self.root / HOOK)).hexdigest())

    def remote(self):
        destination = self.destination()
        lines = self.git('ls-remote', '--symref', destination, 'HEAD').splitlines()
        branches = [s.split()[1] for s in lines if s.startswith('ref: refs/heads/')]
        need(len(branches) == 1, 'actual default branch unavailable')
        branch = branches[0]
        self.git('fetch', '--no-tags', destination, branch)
        need(self.git('merge-base', '--is-ancestor', 'HEAD', 'FETCH_HEAD', check=False).returncode == 0,
             'HEAD not reachable from remote default')
        refs = self.git('ls-remote', destination, 'refs/tags/' + self.tag)
        need(not refs, 'remote tag exists; published refs are immutable')
        return branch

    def context(self, root, source):
        if root is None:
            return None
        root = Path(root).resolve()
        need(root.is_dir(), 'context root unavailable')
        need(self.git('rev-parse', 'HEAD', root=root) == source['commit'], 'context source mismatch')
        need(self.git('remote', 'get-url', 'origin', root=root) == source['origin'], 'unrelated context origin')
        need(not self.git('status', '--porcelain', root=root), 'context tracked source changed')
        context_dir = root / '.task-pipeline'
        need(stat.S_ISDIR(context_dir.lstat().st_mode), 'regular project context directory required')
        ledger = read_file(context_dir / 'run.md').decode()
        headers = re.findall(r'^Run:\s*(.+)$', ledger, re.M)
        need(headers and headers[-1].strip(), 'current run identity unavailable')
        profile = read_file(root / 'pipeline.json')
        need(isinstance(json.loads(profile), dict), 'context profile unavailable')
        return dict(root=str(root), run=headers[-1], profile_sha256=hashlib.sha256(profile).hexdigest())

    def observe_hook(self, context, command):
        need(context is not None, 'publish unavailable: no bound actual project context')
        payload = json.dumps({'tool_input': {'command': shlex.join(command)}})
        env = dict(os.environ, CLAUDE_PROJECT_DIR=context['root'])
        r = subprocess.run(['bash', str(self.root / HOOK)], input=payload, text=True,
                           capture_output=True, cwd=context['root'], env=env, timeout=30)
        return dict(exit=r.returncode, stdout=r.stdout, stderr=r.stderr,
                    command=command, native_interception=False, authority_verified=False)

    def load(self):
        private(self.record)
        data = json.loads(read_file(self.record))
        need(isinstance(data, dict) and data.get('schema') == 1 and data.get('tag') == self.tag,
             'invalid candidate receipt')
        return data

    def verify(self, data):
        need(data['source'] == self.source(), 'source identity changed')
        need(self.git('cat-file', '-t', 'refs/tags/' + self.tag) == 'tag', 'annotated candidate required')
        need(self.git('rev-parse', 'refs/tags/' + self.tag) == data['object'], 'tag object changed')
        need(self.git('rev-parse', self.tag + '^{}') == data['source']['commit'], 'tag peel changed')
        if data['context']:
            need(self.context(data['context']['root'], data['source']) == data['context'],
                 'bound project/run context changed')

    def prepare(self, context_root=None):
        with self.lock():
            need(not self.record.exists() and not self.record.is_symlink(), 'candidate already recorded; no automatic replacement')
            source = self.source(); branch = self.remote()
            self.git('fetch', '--tags', source['origin'])
            need(self.git('show-ref', '--verify', 'refs/tags/' + self.tag, check=False).returncode != 0,
                 'unowned local tag already exists')
            context = self.context(context_root, source)
            data = dict(schema=1, tag=self.tag, source=source, default_branch=branch,
                        owner_nonce=uuid.uuid4().hex, context=context, state='PREPARING',
                        external_authority='NOT_VERIFIED_BY_HELPER', mechanical_evidence=None,
                        hook_observation=None)
            write_json(self.record, data)
            if context:
                observation = self.observe_hook(context, ['git', 'tag', '-a', self.tag, '-m', 'candidate'])
                data['hook_observation'] = observation; write_json(self.record, data)
                need(observation['exit'] == 0, 'existing hook refused local preparation')
            self.git('tag', '-a', self.tag, '-m', 'Owned release candidate ' + data['owner_nonce'], source['commit'])
            data.update(state='PREPARED', object=self.git('rev-parse', 'refs/tags/' + self.tag))
            write_json(self.record, data)
            return data

    def _run_suite(self, stream):
        p = subprocess.Popen(COMMAND, cwd=self.root, stdout=stream, stderr=subprocess.STDOUT,
                             start_new_session=True)
        reason = None
        previous_term = signal.getsignal(signal.SIGTERM)
        def terminated(signum, frame):
            raise SystemExit('terminated')
        signal.signal(signal.SIGTERM, terminated)
        try:
            while p.poll() is None:
                if shutil.disk_usage(self.root).free < 400 * 1024**2:
                    reason = 'disk-stopped'; break
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            reason = 'interrupted'
        finally:
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGTERM)
                try: p.wait(timeout=10)
                except subprocess.TimeoutExpired: os.killpg(p.pid, signal.SIGKILL); p.wait()
            signal.signal(signal.SIGTERM, previous_term)
        return p.returncode, reason

    def check(self):
        with self.lock():
            data = self.load(); self.verify(data)
            need(self.remote() == data['default_branch'], 'remote default branch changed')
            need(not self.log.exists() and not self.log.is_symlink(), 'suite log already exists; retain prior evidence')
            data.update(state='CHECKING', mechanical_evidence=dict(command=COMMAND, started=time.time()))
            write_json(self.record, data)
            fd = os.open(self.log, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'wb') as stream:
                code, reason = self._run_suite(stream)
            unlooked = []; initial_unlooked = []; structural_pass = False
            with self.log.open('r', encoding='utf-8', errors='replace') as stream:
                for line in stream:
                    if 'unlooked:' in line:
                        unlooked.append(line.strip())
                        if not structural_pass: initial_unlooked.append(line.strip())
                    if line.strip() == 'PASS: task-pipeline structure valid': structural_pass = True
            looked = structural_pass and not any('release stamps:' in line for line in initial_unlooked)
            evidence = data['mechanical_evidence']
            evidence.update(exit=code, interruption=reason, ended=time.time(),
                            log_sha256=digest_file(self.log), unlooked=unlooked, initial_unlooked=initial_unlooked,
                            release_gap_looked=looked)
            data['state'] = 'CHECK_PASSED' if code == 0 and reason is None and looked else 'CHECK_FAILED'
            write_json(self.record, data)
            self.verify(data)
            need(data['state'] == 'CHECK_PASSED', 'complete tagged gate did not pass; evidence preserved')
            return data

    def publish(self):
        with self.lock():
            data = self.load(); self.verify(data)
            evidence = data.get('mechanical_evidence') or {}
            need(data['state'] == 'CHECK_PASSED' and evidence.get('command') == COMMAND and
                 evidence.get('exit') == 0 and evidence.get('release_gap_looked') is True and
                 evidence.get('interruption') is None and evidence.get('ended'), 'successful complete receipt required')
            private(self.log)
            need(digest_file(self.log) == evidence.get('log_sha256'), 'suite output changed')
            need(self.remote() == data['default_branch'], 'remote default branch changed')
            command = ['git', 'push', data['source']['origin'], data['object'] + ':refs/tags/' + self.tag]
            observation = self.observe_hook(data['context'], command)
            data['hook_observation'] = observation; write_json(self.record, data)
            need(observation['exit'] == 0, 'existing release hook refused publication')
            self.verify(data)
            data['state'] = 'PUBLISHING'; write_json(self.record, data)
            try:
                r = self.git(*command[1:], check=False)
                data.update(state='PUSH_UNCONFIRMED', push=dict(exit=r.returncode, stdout=r.stdout, stderr=r.stderr))
                if r.returncode == 0:
                    remote = self.git('ls-remote', data['source']['origin'], 'refs/tags/' + self.tag, 'refs/tags/' + self.tag + '^{}')
                    refs = dict((line.split()[1], line.split()[0]) for line in remote.splitlines())
                    data['remote_readback'] = refs
                    if refs.get('refs/tags/' + self.tag) == data['object'] and refs.get('refs/tags/' + self.tag + '^{}') == data['source']['commit']:
                        data['state'] = 'PUBLISHED'
            except (subprocess.TimeoutExpired, Refusal, OSError, ValueError):
                data.update(state='PUSH_OUTCOME_UNKNOWN')
            write_json(self.record, data)
            need(data['state'] == 'PUBLISHED', 'push not confirmed; reconcile remote read-only before any retry')
            return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['prepare', 'check', 'publish'])
    parser.add_argument('--tag', required=True)
    parser.add_argument('--context-root', help='prepare only: exact same-source actual project/run context')
    args = parser.parse_args()
    try:
        need(args.operation == 'prepare' or args.context_root is None, 'context is bound only at preparation')
        candidate = Candidate(Path.cwd(), args.tag)
        result = candidate.prepare(args.context_root) if args.operation == 'prepare' else getattr(candidate, args.operation)()
        print(json.dumps(dict(state=result['state'], tag=args.tag,
                              receipt=str(candidate.record), external_authority='NOT_VERIFIED_BY_HELPER')))
        return 0
    except (Refusal, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print('REFUSED: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
