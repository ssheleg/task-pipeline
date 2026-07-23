# templates

Skeletons task-pipeline seeds into a host project. Only the **brief** is owned by
this plugin (it is the stage-0 intake artifact); the spec and plan skeletons come
from the `superpowers` skills, and the `docs/ux/*` skeletons from `super-ux`.

| Template | Seeded to | Stage |
|---|---|---|
| `brief.md` | `docs/superpowers/specs/YYYY-MM-DD-<topic>-brief.md` | 0 — intake grill |

Seeding rule (per the ssheleg canon): create a template copy **only when the
target is absent**; never overwrite an existing brief.
