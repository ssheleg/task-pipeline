#!/usr/bin/env node
/*
 * task-pipeline installer CLI.
 *
 * Installs the task-pipeline skill into ~/.claude/skills/task-pipeline and
 * the /task-pipeline slash command into ~/.claude/commands/ (same layout as
 * install.sh). Idempotent: existing installs are skipped unless --force.
 *
 * Zero dependencies, non-interactive. For other agents (Cursor, Codex, 70+)
 * use: npx skills add ssheleg/task-pipeline
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const ROOT = path.resolve(__dirname, '..');
const REPO = 'ssheleg/task-pipeline';

function usage() {
  console.log(`task-pipeline installer

Usage:
  npx task-pipeline-skill [--force]   install skill + /task-pipeline command
                                      into ~/.claude (skip existing unless --force)
  npx task-pipeline-skill --help

Other install paths:
  Claude Code plugin:  /plugin marketplace add ${REPO}
                       /plugin install task-pipeline@task-pipeline
  Any agent (70+):     npx skills add ${REPO}`);
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dest, entry.name);
    if (entry.isDirectory()) copyDir(s, d);
    else fs.copyFileSync(s, d);
  }
}

function installOne(label, src, dest, isDir, force) {
  if (fs.existsSync(dest) && !force) {
    console.log(`skip: ${label} already installed at ${dest} (rerun with --force to overwrite)`);
    return;
  }
  fs.rmSync(dest, { recursive: true, force: true });
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  if (isDir) copyDir(src, dest);
  else fs.copyFileSync(src, dest);
  console.log(`Installed ${label} -> ${dest}`);
}

function main(argv) {
  const args = argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    usage();
    return 0;
  }
  const force = args.includes('--force');
  const unknown = args.filter((a) => a !== '--force');
  if (unknown.length) {
    console.error(`unknown argument(s): ${unknown.join(' ')}`);
    usage();
    return 2;
  }

  const skillSrc = path.join(ROOT, 'plugins/task-pipeline/skills/task-pipeline');
  const cmdSrc = path.join(ROOT, 'plugins/task-pipeline/commands/task-pipeline.md');
  for (const [p, what] of [[skillSrc, 'skill sources'], [cmdSrc, 'command source']]) {
    if (!fs.existsSync(p)) {
      console.error(`error: ${what} missing at ${p} — corrupted package?`);
      return 1;
    }
  }

  const home = os.homedir(); // respects $HOME on POSIX — tests override via env
  installOne(
    'task-pipeline skill  ',
    skillSrc,
    path.join(home, '.claude', 'skills', 'task-pipeline'),
    true,
    force
  );
  installOne(
    '/task-pipeline command',
    cmdSrc,
    path.join(home, '.claude', 'commands', 'task-pipeline.md'),
    false,
    force
  );
  return 0;
}

process.exit(main(process.argv));
