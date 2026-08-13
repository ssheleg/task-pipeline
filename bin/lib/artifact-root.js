#!/usr/bin/env node
'use strict';
/**
 * Where this project's run artifacts live — the shipped answer.
 *
 * The same ordered rule as `test/artifact_root.py`, which serves the validator.
 * `test/artifact_root_test.py` runs both against
 * `test/fixtures/artifact-root-cases.json` and fails when they disagree, which is
 * what makes two implementations of one rule affordable at all.
 *
 *   1. `paths.artifacts` in `pipeline.json` wins outright. Any relative path.
 *   2. otherwise the first KNOWN name that exists AND CARRIES A REGISTER.
 *      `docs/evidence/` before `docs/superpowers/`, so a partial migration
 *      resolves forward and moving one file at a time never splits a project.
 *   3. otherwise `docs/evidence/`, the default for a project that has none.
 *
 * **Carrying a register is the whole difference between a root and a directory.**
 * A project may keep an unrelated `docs/evidence/`; adopting it on bare existence
 * would write a run's paperwork into somebody else's folder.
 *
 * **The answer is a record, not a string.** A bare path cannot say *this is the
 * legacy name*, *records also sit over there*, or *the default landed on an
 * occupied directory* — and a caller that cannot know those things writes blind.
 *
 * This file lives under `bin/` because that is what the package ships
 * (`package.json` → `files`), and `bin/task-pipeline.js` is its only caller.
 * Run directly it prints the record as JSON, which is how the Python test asks it.
 */

const fs = require('fs');
const path = require('path');

/** Ordered. The new name first, so a partial migration resolves forward. */
const KNOWN = ['docs/evidence', 'docs/superpowers'];

/** The name this pipeline used until 2026-08-13. Supported, not deprecated. */
const LEGACY = 'docs/superpowers';

/** What makes a directory a root rather than a directory. Any ONE of these. */
const REGISTERS = ['retro.md', 'backlog.md', 'verification.md',
                   'specs', 'plans', 'briefs', 'retro'];

/** Does this directory hold any artifact this pipeline recognises? */
function carriesRegister(dir) {
  let st;
  try { st = fs.statSync(dir); } catch (e) { return false; }
  if (!st.isDirectory()) return false;
  return REGISTERS.some((name) => fs.existsSync(path.join(dir, name)));
}

/**
 * `paths.artifacts` from `pipeline.json`, or `null`.
 *
 * An unreadable or malformed config yields `null` rather than throwing: the
 * resolver's job is to answer, and a project with a broken config still has a
 * directory layout. The config's own validity is the schema check's business.
 */
function configured(project) {
  let cfg;
  try {
    cfg = JSON.parse(fs.readFileSync(path.join(project, 'pipeline.json'), 'utf8'));
  } catch (e) {
    return null;
  }
  const value = cfg && cfg.paths && cfg.paths.artifacts;
  if (typeof value === 'string' && value.trim()) {
    return value.trim().replace(/\/+$/, '');
  }
  return null;
}

/**
 * `{root, reason, legacy, leftover, collision}` for a project directory.
 * `root` is relative to `project` and posix-separated.
 */
function resolve(project) {
  if (typeof project !== 'string' || !project) {
    // A resolver handed nothing must not answer as though it were handed a
    // project: standing instruction #1, in the one line where it is cheapest.
    throw new TypeError('resolve() needs a project directory');
  }

  let root = configured(project);
  let reason = root ? 'configured' : null;

  if (!root) {
    for (const name of KNOWN) {
      if (carriesRegister(path.join(project, name))) {
        root = name;
        reason = name === LEGACY ? 'legacy' : 'found';
        break;
      }
    }
  }

  if (!root) {
    root = KNOWN[0];
    reason = 'default';
  }

  // `leftover` answers "what else carries records here", a different question
  // from "which root won" — so it is computed the same way whatever chose the root.
  const leftover = KNOWN.find(
    (n) => n !== root && carriesRegister(path.join(project, n))
  ) || null;

  // The default landing on a directory that exists but is not a root: answer,
  // and say so, so the caller asks instead of writing into it.
  let collision = false;
  if (reason === 'default') {
    const dir = path.join(project, root);
    collision = fs.existsSync(dir) && !carriesRegister(dir);
  }

  return { root, reason, legacy: reason === 'legacy', leftover, collision };
}

module.exports = { resolve, carriesRegister, configured, KNOWN, LEGACY, REGISTERS };

if (require.main === module) {
  const target = process.argv[2] || process.cwd();
  process.stdout.write(JSON.stringify(resolve(target)) + '\n');
}
