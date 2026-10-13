<sub>ssheleg skills — task-pipeline · agent-sync · evidence-docs</sub>

# FW07 R07: retire every declared plant copy

The future 1.95.0 candidate at
[7d18df5](https://github.com/ssheleg/task-pipeline/commit/7d18df5464fad6fdbaa77a91d48580ebbe3f5d9a)
still cleaned only the first `cp -R .` target in each plant. The coordinator found
second-copy residue during a separate 1.94.1 run. This correction does not edit
that active clone or delete its public scratch paths.

## Bounded contract and source

The implementation lives in [test/negatives.py](../../../../test/negatives.py):
`copy_dirs_of` discovers all admitted copy declarations; `run_plant` retires them
in `finally`; both negative and property branches use that helper. The original
`copy_dir_of` and first-copy no-op verdict are retained. An unchanged primary
copy stays BROKEN even if a secondary copy changed; an unchanged secondary does
not turn a real primary mutation into BROKEN.

The caller controls the test corpus. Cleanup admission recognizes the current
corpus's standalone `rm -rf PATH && cp -R . PATH` and bare-copy spelling, plus
its optional removal of that same target's `.git`. Paths must be literal,
normalized descendants of `/tmp`. Comments, quoted/multiline strings and
recognized Python/cat heredoc payloads do not grant cleanup authority. Unsupported
copy declarations and unsupported/unterminated heredocs refuse before execution.
This is a bounded corpus grammar, **not a general shell parser**; scripts that
construct paths dynamically, nested shell programs, and adversarial shell syntax
need separately designed admission.

Before a sweep deletes anything, all declared paths and existing components are
checked: owned directories only, no descendant symlinks, dot/traversal components
or shell expansions. The platform's `/tmp` alias remains supported. Independent
cleanup failures are collected after attempting the remaining admitted copies;
an incomplete sweep cannot report success. This does not prove safety against
an arbitrary concurrent external filesystem writer. The shared family scratch
lock remains the cooperation boundary; old runners and direct plant execution
are still outside it.

## Reproduction and checks

[checks.json](checks.json) binds source hashes and measured commands.
[baseline.log](baseline.log) preserves the first observation: all eight actual
runner controls failed on the unmodified candidate. The portable
[baseline replay](baseline-replay.py) rebuilds only the old runner and its lock
helper from Git, then runs those same eight controls from the final fixture.
Its [result](baseline-replay.log) confirms all eight expected failures and owned
fixture removal; a successful replay command means the expected red was observed.

The [focused test](../../../../test/audit_regressions/plant_copy_cleanup.py)
runs the actual runner over tiny synthetic repositories in unique owned `/tmp`
namespaces, mocking only corpus admission, the public lock and error injection.
[focused.log](focused.log): 18 tests, exit 0. They cover both runner branches,
child/observation exceptions, primary verdict preservation, data-only decoys,
continuations, unsafe paths, symlinks and cleanup errors. The corpus inspection
reads all 454 plant files without executing them; it finds 443 admitted copy
declarations. Only plants 157 and 158 have two. Quoted declarations inside 087,
238 and 331 are excluded. [runner.log](runner.log): existing 42 checks, exit 0.
The audit regression is discovered by the existing `test:audit-regressions` glob.

```sh
python3 -B test/audit_regressions/plant_copy_cleanup.py
python3 -B test/runner_test.py
python3 -B docs/evidence/runs/2026-10-13-fw07-copy-cleanup/baseline-replay.py
```

Initial follow-up checks also found an overly broad refusal of ordinary file
copies and the existing property-196 post-copy `.git` removal; the final grammar
admits the complete current corpus. Those were intermediate implementation
failures, not passing candidate runs. No public plant, provider call, native host,
aggregate suite, tag or release was run by this packet.

## Handoff

Owned branch: `fix/fw07-all-plant-copies`, isolated from the composed PR127 and the
active release clone. Next: independent peer review of the parser and cleanup
boundary, then coordinator-controlled composition and complete owner validation
in the serial slot. Do not interpret these focused controls as a complete owner
gate. Abrupt termination/SIGKILL and the runner's separate snapshot lifecycle
remain outside this exception-finally correction; no universal zero-residue claim
is made.

---

**Made with [ssheleg skills](https://github.com/ssheleg/sshlg-skills)**

- [`task-pipeline`](https://github.com/ssheleg/task-pipeline) — bounded runner correction
- [`agent-sync`](https://github.com/ssheleg/agent-sync) — isolated ownership
- [`evidence-docs`](https://github.com/ssheleg/task-pipeline) — baseline and focused receipts
