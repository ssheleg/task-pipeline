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

/**
 * Ask the family launcher to write the routing block, for this member only.
 *
 * Delegated rather than reimplemented, for three reasons. The block describes
 * what the machine actually has, so a lone member rendering the whole thing
 * would produce a table for routers nobody installed. `--member` limits this to
 * the `task-pipeline` section and leaves everyone else's alone, which is what
 * lets the bundle and a single installer both write. And the launcher is the
 * only writer that copies the operator's global instruction file before touching
 * it — that file has no version control behind it, and two defects in this
 * family's history destroyed it.
 *
 * `--no-install` keeps this from silently downloading a package the user did not
 * ask for. When the launcher is absent, print the one command instead of
 * failing: an installer that ends in an error because an OPTIONAL follow-up is
 * missing reads as a failed install.
 */
function offerRouters() {
  const { spawnSync } = require('child_process');
  const r = spawnSync(
    'npx',
    ['--no-install', 'sshlg-skills', 'routers', '--member', 'task-pipeline'],
    { stdio: 'inherit', shell: process.platform === 'win32' }
  );
  if (r.status !== 0) {
    console.log(
      '\nTo have this skill apply by default in every project, add the\n' +
      "family's routing block to your agent's global instructions:\n\n" +
      '  npx --yes sshlg-skills routers --member task-pipeline\n'
    );
  }
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

  // One channel per agent. This installer writes a PLAIN copy to
  // ~/.claude/skills/<id>, and while the Claude Code PLUGIN channel is active that
  // copy SHADOWS the plugin — silently serving whatever version was copied, forever.
  // The family launcher (sshlg-skills) prunes exactly these copies for that reason,
  // so creating one without saying so undoes the thing it is paired with.
  const pluginDirs = [
    path.join(home, '.claude', 'plugins', 'marketplaces', 'task-pipeline'),
    path.join(home, '.claude', 'plugins', 'cache', 'task-pipeline'),
  ];
  if (!force && pluginDirs.some((d) => fs.existsSync(d))) {
    console.error(`refusing: task-pipeline is already installed as a Claude Code PLUGIN.

A plain copy in ~/.claude/skills/ shadows the plugin and keeps serving the version
it was copied from — the failure this family prunes for. Prefer the plugin:

  claude plugin marketplace update task-pipeline
  claude plugin update task-pipeline@task-pipeline

Rerun with --force if you deliberately want the plain copy instead.`);
    return 3;
  }

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
  offerRouters();
  return 0;
}

process.exit(main(process.argv));
