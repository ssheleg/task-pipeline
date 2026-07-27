# CONTEXT.md — format

The project's living glossary. The stage-0 grill writes to it **inline**, as each
term is resolved. Seeded at the repo root (`CONTEXT.md`) for a single-context repo.

> Adapted from Matt Pocock's `grill-with-docs` (MIT — see the repo LICENSE →
> *Third-party*).

## Structure

```md
# {Context Name}

{One or two sentences: what this context is and why it exists.}

## Language

**Order**:
A confirmed request from a Customer for goods or services.
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account

## Relationships

- An **Order** produces one or more **Invoices**
- An **Invoice** belongs to exactly one **Customer**

## Example dialogue

> **Dev:** "When a **Customer** places an **Order**, do we create the **Invoice** immediately?"
> **Domain expert:** "No — an **Invoice** is only generated once a **Fulfillment** is confirmed."

## Flagged ambiguities

- "account" was used to mean both **Customer** and **User** — resolved: these are
  distinct concepts.
```

## Rules

- **Be opinionated.** Several words for one concept → pick the best, list the rest
  as aliases to avoid.
- **Flag conflicts explicitly.** An ambiguous term goes under *Flagged ambiguities*
  with its resolution.
- **Keep definitions tight.** One sentence. Define what it IS, not what it does.
- **Show relationships.** Bold the term names; express cardinality where obvious.
- **Only project-specific terms.** General programming concepts (timeouts, error
  types, utility patterns) don't belong, however heavily the project uses them.
  Before adding: is this unique to this context, or just programming?
- **Group under subheadings** when natural clusters emerge; a flat list is fine
  when the terms are one cohesive area.
- **Write an example dialogue** — a dev and a domain expert using the terms
  naturally, which is what exposes the boundaries between related concepts.

## Single vs multi-context repos

**Single context (most repos):** one `CONTEXT.md` at the root.

**Multiple contexts:** a `CONTEXT-MAP.md` at the root lists them, where they live,
and how they relate:

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md) — manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced`; Fulfillment consumes it to start picking
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched`; Billing consumes it to invoice
- **Ordering ↔ Billing**: shared types for `CustomerId` and `Money`
```

Which structure applies is inferred: `CONTEXT-MAP.md` exists → read it to find the
contexts; only a root `CONTEXT.md` → single context; neither → create the root file
lazily, when the first term is resolved.
