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

  npx task-pipeline-skill migrate-artifacts [--dry-run]
                                      move this project's paperwork from the legacy
                                      docs/superpowers/ to docs/evidence/. Optional:
                                      the legacy name is supported forever and no run
                                      warns about it. Moves the directory, LISTS every
                                      other file that names the old path, and edits
                                      none of them.

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

function verifyTree(src, staged, isDir) {
  if (!isDir) {
    if (!fs.readFileSync(src).equals(fs.readFileSync(staged))) {
      throw new Error(`staged ${path.basename(staged)} does not match its source`);
    }
    return;
  }
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(staged, entry.name);
    if (entry.isDirectory()) verifyTree(s, d, true);
    else if (!fs.readFileSync(s).equals(fs.readFileSync(d))) {
      throw new Error(`staged ${entry.name} does not match its source`);
    }
  }
}

/**
 * A TRANSACTIONAL install (FIX-UP-05.02): the writer contract from UP-05
 * applied to this member's installer. The old code deleted `dest` and THEN
 * copied into it, so a crash mid-copy left nothing (with --force) or a partial
 * tree. Now the payload is staged into a same-filesystem sibling and VERIFIED
 * first; only then is the old install moved aside (recoverable) and the staged
 * one renamed into place. A stage crash leaves the ACTIVE install untouched;
 * --force=false still skips, preserving the user's bytes.
 */
function installOne(label, src, dest, isDir, force) {
  if (fs.existsSync(dest) && !force) {
    console.log(`skip: ${label} already installed at ${dest} (rerun with --force to overwrite)`);
    return;
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  const staging = `${dest}.staging-${process.pid}`;   // same fs as dest
  const prev = `${dest}.prev-${process.pid}`;
  fs.rmSync(staging, { recursive: true, force: true });
  try {
    // 1. STAGE + VERIFY, before touching the active install.
    if (isDir) copyDir(src, staging);
    else { fs.mkdirSync(path.dirname(staging), { recursive: true }); fs.copyFileSync(src, staging); }
    verifyTree(src, staging, isDir);
    // 2. SWITCH: move the old aside (recoverable), rename staged into place.
    fs.rmSync(prev, { recursive: true, force: true });
    if (fs.existsSync(dest)) fs.renameSync(dest, prev);
    fs.renameSync(staging, dest);
    fs.rmSync(prev, { recursive: true, force: true });
    console.log(`Installed ${label} -> ${dest}`);
  } catch (err) {
    // Abort: leave the active install intact, remove the half-built staging.
    fs.rmSync(staging, { recursive: true, force: true });
    if (fs.existsSync(prev) && !fs.existsSync(dest)) fs.renameSync(prev, dest);
    throw new Error(`install aborted, previous install intact: ${err.message}`);
  }
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
/**
 * Say what this path does NOT install, and what runs instead.
 *
 * `agents/` is a Claude Code plugin capability; `install()` copies the skill directory
 * and the command and nothing else. That is the design — the brief chose plugin agents
 * with honest degradation — and it was silent, which is the part that is not. An
 * operator reading doctrine that names `task-pipeline:verifier` finds a name that
 * resolves to nothing and no explanation anywhere in what they ran.
 */
function discloseAgents() {
  const dir = path.join(ROOT, 'plugins', 'task-pipeline', 'agents');
  let files = [];
  try {
    files = fs.readdirSync(dir).filter((f) => f.endsWith('.md'));
  } catch (e) {
    return;               // no agents shipped: nothing to disclose
  }
  if (!files.length) return;
  console.log(
    `\nNot installed: plugins/task-pipeline/agents/ (${files.length} file(s)).\n` +
    '  Role agents are a Claude Code plugin capability; this path installs the skill\n' +
    '  and the command only. Every role still runs — on the main thread instead of in\n' +
    '  its own context, which costs context and speed, not doctrine.\n' +
    '  For the agent-backed version, install the plugin:\n' +
    `    claude plugin marketplace add ${REPO}\n` +
    '    claude plugin install task-pipeline@task-pipeline'
  );
}

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

/**
 * `migrate-artifacts` — the one verb this installer grew.
 *
 * Kept here rather than in a second binary because the package ships one `bin`, and a
 * project that wants the move should not have to learn a second command name. The work
 * itself is in `lib/migrate-artifacts.js`, which is pure up to the moment it copies.
 */
function migrateArtifacts(args) {
  const mig = require('./lib/migrate-artifacts.js');
  const project = process.cwd();
  const dry = args.includes('--dry-run');
  const unknown = args.filter((a) => a !== '--dry-run');
  if (unknown.length) {
    console.error(`unknown argument(s) for migrate-artifacts: ${unknown.join(' ')}`);
    return 2;
  }

  const p = mig.plan(project);
  console.log(mig.render(p));
  if (p.action === 'refused') return 3;
  if (p.action === 'nothing') return 0;
  if (dry) {
    console.log('\n--dry-run: nothing was written.');
    return 0;
  }

  let r;
  try {
    r = mig.apply(project, { stamp: new Date().toISOString().replace(/[:.]/g, '-') });
  } catch (e) {
    // A copy that cannot be taken cancels the move, and says so instead of
    // degrading to "moved anyway".
    console.error(`\nmove cancelled: ${e.message}`);
    return 1;
  }
  console.log(`\nbackup: ${r.backupDir}`);
  console.log(`moved:  ${r.moved} file(s)`);
  if (r.plan.collisions.length) {
    console.log(`kept:   ${r.plan.collisions.length} file(s) left in `
                + `${mig.LEGACY}/ — their targets already existed`);
  }
  if (r.plan.mentions.length) {
    console.log(`review: ${r.plan.mentions.length} file(s) still name ${mig.LEGACY}/ `
                + '— listed above, none edited');
  }
  return 0;
}

// The bundled HostContext resolver (FIX-UP-08.02) — one contract, a local
// copy per member because these installers run via `npx` with no shared lib.
// A host's config root is: an explicit root > the documented host env var >
// the platform default `~/<dir>`. Used verbatim (spaces preserved), never
// through a shell. Host EXISTENCE is a separate probe on the returned path.
const HOST_ENV = { claude: 'CLAUDE_CONFIG_DIR', codex: 'CODEX_HOME', gemini: 'GEMINI_CONFIG_DIR' };
const HOST_DIR = { claude: '.claude', codex: '.codex', gemini: '.gemini' };
function hostRoot(agent, home, env, explicit) {
  if (explicit) return explicit;
  const e = (env || process.env)[HOST_ENV[agent]];
  if (e) return e;
  return path.join(home, HOST_DIR[agent]);
}

function main(argv) {
  const args = argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    usage();
    return 0;
  }
  if (args[0] === 'migrate-artifacts') return migrateArtifacts(args.slice(1));

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
  const claude = hostRoot('claude', home, process.env);
  const pluginDirs = [
    path.join(claude, 'plugins', 'marketplaces', 'task-pipeline'),
    path.join(claude, 'plugins', 'cache', 'task-pipeline'),
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
    path.join(claude, 'skills', 'task-pipeline'),
    true,
    force
  );
  installOne(
    '/task-pipeline command',
    cmdSrc,
    path.join(claude, 'commands', 'task-pipeline.md'),
    false,
    force
  );
  discloseAgents();
  offerRouters();
  return 0;
}

if (require.main === module) {
  process.exit(main(process.argv));
}

module.exports = { installOne, copyDir, verifyTree, hostRoot };
