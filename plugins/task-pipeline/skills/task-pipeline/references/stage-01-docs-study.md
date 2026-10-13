# Stage 1 detail

The full gate and freedom level remain in [stages.md](stages.md).

## 1 — Docs study
- **What:** ground every external library / API / SDK the task touches on the
  *current* docs, before locking any contract.
- **Invoke:** the `context7` MCP — `context7:resolve-library-id` → `context7:query-docs`,
  scoped by topic or the `context7-docs` skill. Web-search fallback for libs context7
  can't resolve.
