'use strict';
/**
 * `migrate-artifacts` — move a project's paperwork off the legacy root, on request.
 *
 * **Nothing calls this on its own.** The resolver supports `docs/superpowers/`
 * indefinitely and no run warns about it, so a project that never runs this command is
 * not behind. This exists because `task-pipeline` is published: without it, a project
 * that WANTS the new name has to do the move by hand and guess what else to touch.
 *
 * What it does, and the line it does not cross:
 *
 * - **It moves the directory.** That part is mechanical and safe to automate.
 * - **It does not rewrite your prose.** Files elsewhere in the project that name the
 *   old path are LISTED, never edited. A command that rewrote arbitrary documents in
 *   somebody's repository would be deciding, for them, which mentions were a path in
 *   use and which were a path being discussed — the exact distinction a mechanical
 *   replace cannot make, and one this pipeline got wrong in its own sweep before
 *   shipping this file.
 * - **A partial state is a state, not a fault.** Where both roots exist it moves what
 *   does not collide and names what does. Nothing is ever overwritten.
 * - **A configured root is refused, not overridden.** `paths.artifacts` is the
 *   operator saying where the paperwork goes; moving it would contradict the config
 *   the resolver is about to read.
 *
 * The backup is a mechanism, not a habit: a copy that cannot be taken CANCELS the
 * move. Copies land under `.task-pipeline/backups/`, and a name already taken in the
 * same second gets a suffix — two backups inside one second were one backup once, and
 * the second overwrote the first.
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const { resolve, LEGACY, KNOWN } = require('./artifact-root.js');

const NEW = KNOWN[0];

/** Every file under `dir`, repo-relative, posix-separated. */
function walk(dir, base, out) {
  out = out || [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) walk(full, base, out);
    else out.push(path.relative(base, full).split(path.sep).join('/'));
  }
  return out;
}

/** Is this a git work tree? `git mv` keeps the history a rename would drop. */
function inGitWorkTree(project) {
  try {
    execFileSync('git', ['-C', project, 'rev-parse', '--is-inside-work-tree'],
                 { stdio: ['ignore', 'pipe', 'ignore'] });
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Which files elsewhere in the project still name the old path.
 *
 * Reported, never rewritten. Skips the artifact roots themselves — a brief written in
 * March describes where things were in March, and correcting it would falsify the
 * record it exists to be.
 */
function mentionsElsewhere(project) {
  const hits = [];
  const skipDirs = new Set(['.git', 'node_modules', 'graphify-out', 'dist', 'build']);
  const exts = ['.md', '.mdc', '.json', '.yml', '.yaml', '.sh', '.py', '.js', '.ts'];
  const walkAll = (dir) => {
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch (e) { return; }
    for (const e of entries) {
      const full = path.join(dir, e.name);
      const rel = path.relative(project, full).split(path.sep).join('/');
      if (e.isDirectory()) {
        if (skipDirs.has(e.name)) continue;
        if (rel === LEGACY || rel === NEW) continue;   // the records themselves
        walkAll(full);
      } else if (exts.includes(path.extname(e.name))) {
        let text;
        try { text = fs.readFileSync(full, 'utf8'); } catch (err) { continue; }
        const n = text.split(`${LEGACY}/`).length - 1;
        if (n) hits.push({ file: rel, count: n });
      }
    }
  };
  walkAll(project);
  return hits.sort((a, b) => b.count - a.count);
}

/**
 * What the move would do. Pure: reads the tree, writes nothing.
 *
 * `moves` are safe; `collisions` are files whose target already exists and which are
 * therefore left where they are. `mentions` is the list this command refuses to edit.
 */
function plan(project) {
  const info = resolve(project);
  const legacyAbs = path.join(project, LEGACY);

  if (info.reason === 'configured') {
    return { action: 'refused', info,
             why: `pipeline.json sets paths.artifacts to "${info.root}". Moving the `
                  + 'directory would contradict the config the resolver reads first. '
                  + 'Change or remove that key first if the move is what you want.' };
  }
  if (!fs.existsSync(legacyAbs)) {
    return { action: 'nothing', info,
             why: `no ${LEGACY}/ in this project — the root is already "${info.root}".` };
  }

  const files = walk(legacyAbs, legacyAbs);
  const moves = [];
  const collisions = [];
  for (const rel of files) {
    const target = path.join(project, NEW, rel);
    if (fs.existsSync(target)) collisions.push(`${NEW}/${rel}`);
    else moves.push({ from: `${LEGACY}/${rel}`, to: `${NEW}/${rel}` });
  }
  return { action: 'move', info, moves, collisions,
           mentions: mentionsElsewhere(project) };
}

/** A preview that shows what LEAVES, not only what arrives. */
function render(p) {
  const L = [];
  if (p.action === 'refused') { L.push(`refused: ${p.why}`); return L.join('\n'); }
  if (p.action === 'nothing') { L.push(`nothing to do: ${p.why}`); return L.join('\n'); }

  L.push(`artifact root: ${p.info.root}  (${p.info.reason})`);
  L.push('');
  L.push(`${p.moves.length} file(s) move:`);
  for (const m of p.moves) {
    L.push(`  - ${m.from}`);          // what leaves
    L.push(`  + ${m.to}`);            // and where it arrives
  }
  if (p.collisions.length) {
    L.push('');
    L.push(`${p.collisions.length} file(s) NOT moved — the target already exists and `
           + 'nothing here overwrites:');
    for (const c of p.collisions) L.push(`  ! ${c}`);
    L.push(`  ${LEGACY}/ stays in place for these.`);
  }
  if (p.mentions.length) {
    L.push('');
    L.push(`${p.mentions.length} file(s) elsewhere still name ${LEGACY}/ — `
           + 'LISTED, NOT EDITED:');
    for (const m of p.mentions) L.push(`  ? ${m.file}  (${m.count})`);
    L.push('  Some of those are paths in use and some are sentences about the old');
    L.push('  name. Only you can tell them apart, so this command will not try.');
  }
  return L.join('\n');
}

/** A copy that cannot be taken cancels the move. Returns the backup directory. */
function backup(project, stamp) {
  const dir = path.join(project, '.task-pipeline', 'backups');
  fs.mkdirSync(dir, { recursive: true });
  let target = path.join(dir, `artifacts-${stamp}`);
  let n = 1;
  // A stamp resolves to the second and an agent moves faster than that: a name
  // already taken gets a suffix rather than the previous copy's contents.
  while (fs.existsSync(target)) target = path.join(dir, `artifacts-${stamp}-${++n}`);
  fs.cpSync(path.join(project, LEGACY), target, { recursive: true });
  const copied = walk(target, target).length;
  const wanted = walk(path.join(project, LEGACY), path.join(project, LEGACY)).length;
  if (copied !== wanted) {
    throw new Error(`backup incomplete (${copied}/${wanted} files) — move cancelled`);
  }
  return target;
}

/** Do it. Returns `{plan, backupDir, moved}`. */
function apply(project, opts) {
  const o = opts || {};
  const p = plan(project);
  if (p.action !== 'move') return { plan: p, backupDir: null, moved: 0 };

  // Nothing movable is nothing to do — and a backup taken anyway would make every
  // repeat run change the tree it claims to leave alone. Found by the three-run
  // fixture, not by reading: the plan was right and the command that repeats was not,
  // which is standing instruction #2 arriving in the file that cites it.
  if (!p.moves.length) return { plan: p, backupDir: null, moved: 0 };

  const backupDir = backup(project, o.stamp || 'unstamped');
  const git = inGitWorkTree(project);
  let moved = 0;
  for (const m of p.moves) {
    const from = path.join(project, m.from);
    const to = path.join(project, m.to);
    fs.mkdirSync(path.dirname(to), { recursive: true });
    if (git) {
      try {
        execFileSync('git', ['-C', project, 'mv', m.from, m.to], { stdio: 'ignore' });
      } catch (e) {
        fs.renameSync(from, to);      // untracked files git mv refuses
      }
    } else {
      fs.renameSync(from, to);
    }
    moved += 1;
  }
  // The legacy directory goes only when nothing is left in it — a collision means
  // records still live there and removing it would delete them.
  pruneEmpty(path.join(project, LEGACY));
  return { plan: p, backupDir, moved };
}

/** Remove empty directories, deepest first. Never removes a directory with content. */
function pruneEmpty(dir) {
  if (!fs.existsSync(dir)) return;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.isDirectory()) pruneEmpty(path.join(dir, e.name));
  }
  if (!fs.readdirSync(dir).length) fs.rmdirSync(dir);
}

module.exports = { plan, render, apply, backup, mentionsElsewhere, NEW, LEGACY };
