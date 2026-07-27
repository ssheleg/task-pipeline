# ADR — format

Architecture Decision Records live in `docs/adr/` with sequential numbering
(`0001-slug.md`, `0002-slug.md`, …). Scan for the highest existing number and
increment. Create the directory **lazily** — only when the first ADR is needed.

> Adapted from Matt Pocock's `grill-with-docs` (MIT — see the repo LICENSE →
> *Third-party*).

## Template

```md
# {Short title of the decision}

{1–3 sentences: what the context was, what was decided, and why.}
```

That's it. An ADR can be a single paragraph. The value is recording *that* a
decision was made and *why* — not filling out sections.

## Optional sections

Only when they add genuine value; most ADRs need none.

- **Status** frontmatter (`proposed | accepted | deprecated | superseded by
  ADR-NNNN`) — useful once decisions start getting revisited.
- **Considered options** — only when the rejected alternatives are worth
  remembering.
- **Consequences** — only when non-obvious downstream effects need calling out.

## When to write one

All three must hold:

1. **Hard to reverse** — changing your mind later carries real cost.
2. **Surprising without context** — a future reader will look at the code and
   wonder "why on earth did they do it this way?"
3. **A real trade-off** — genuine alternatives existed and one was picked for
   specific reasons.

Easy to reverse → skip it, you'll just reverse it. Not surprising → nobody will
wonder. No real alternative → there's nothing to record beyond "we did the obvious
thing."

### What qualifies

- **Architectural shape.** "We're using a monorepo." "The write model is
  event-sourced; the read model projects into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via
  domain events, not synchronous HTTP."
- **Technology choices carrying lock-in.** Database, message bus, auth provider,
  deployment target — not every library, just the ones that would take a quarter to
  swap out.
- **Boundary and scope decisions.** "Customer data is owned by the Customer
  context; others reference it by ID only." The explicit no's are as valuable as
  the yes's.
- **Deliberate deviations from the obvious path.** "Manual SQL instead of an ORM
  because X." Anything a reasonable reader would assume the opposite of — this is
  what stops the next engineer from "fixing" something deliberate.
- **Constraints invisible in the code.** "No AWS, for compliance." "Sub-200ms
  responses, per the partner API contract."
- **Rejected alternatives whose rejection is non-obvious.** Considered GraphQL,
  picked REST for subtle reasons → record it, or someone re-proposes GraphQL in six
  months.
