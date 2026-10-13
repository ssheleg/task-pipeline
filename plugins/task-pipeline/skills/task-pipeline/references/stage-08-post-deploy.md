# Stage 8 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 8 — Post-deploy
- Tail deploy logs / health-check per conventions. Confirm clean boot, no error
  spike, live subsystems healthy. **All three of the verification trio, not one of
  them** ([`deploy-targets.md`](deploy-targets.md) → *The verification trio*):
  deployment/process state, runtime logs, and a health-check request from outside.
  Where deploy happens in CI, verify the **deploy** job and not only the build —
  a green build beside a skipped deploy is the commonest way a run reports success
  while nothing shipped.
- **A deployed web target is opened, not curled.** A `200` proves the server
  answered; it says nothing about whether the page rendered, whether a bundle 404'd,
  or whether the console filled with errors on load — all three ship green past a
  health check. Where a browser channel is connected — `playwright` **or**
  `chrome-devtools`, either one ([`browser.md`](browser.md)) — load the deployed URL and read
  the console and the network log; quote what you read, not that you looked
  ([`companion-skills.md`](companion-skills.md)). Absent → say the check was an HTTP
  response only, which is the honest name for it.
- **Read the CI verdict for the deploy's own commit** ([`conventions.md`](conventions.md)
  → *The CI verdict*): the run's conclusion quoted, the **failing step's log quoted**
  on anything but `success`, and one of the three states stated — including **`no run
  found`**, out loud, because a project without CI is a legitimate state and not a
  green one.
- **A public surface a logged-out reader will see** can additionally be audited for
  search and answer-engine visibility with `seo-aeo-audit`
  ([`companion-skills.md`](companion-skills.md)) — recommended, never a gate;
  absent, visibility ships unaudited and the close-out says so.
