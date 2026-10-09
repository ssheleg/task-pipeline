# Portable project-audit method

Read before phase 4 or pricing proposed findings. This is the standalone floor;
no sibling skill, plugin agent or network fetch is required. The full pipeline's
references explain the same ladder in delivery contexts, but are optional here.

## Walk the ladder and its seams

For one discovered capability at a time, record an artifact or an explicit gap
at each rung. Never invent a missing brief or claim an unexecuted test passed.

| Rung | Required evidence |
|---|---|
| L0 | Requirement and named check |
| L1 | Recorded decision, ADR or accepted context term |
| L2 | Design/specification covering the requirement |
| L3 | Exact contract/schema and caller-visible failure behavior |
| L4 | Task and its written acceptance criterion |
| L5 | Actual committed implementation |
| L6 | Executed assertion and its output, with source/artifact identity |
| L7 | Reachable user surface: screen, CLI, scenario or runbook |

Walk L0→L1→L2→L3→L4→L5→L6→L7, then L7→L0. Ask whether each
preceding statement actually reached its dependent artifact; findings are ordered
by the broken seam, not by the file. The last seam checks the original outcome,
not merely whether the implementation followed its task.
For Figma-enabled UI, compare spec→recorded frame→actual surface and ensure every
frame belongs to the project's recorded file set. If visual intent was specified,
compare the director record with the approved render/contact sheet. No browser,
design tool or approval receipt means that comparison remains unverified.

## Evidence and missing capabilities

Every finding states the mechanism, reproduction or counterexample, exposure,
observed incidence and impact uncertainty separately. Missing, blind, UNKNOWN and
NOT_RUN are not zero and are not PASS. Quote the command and observed output or
source location; an empty output must be distinguished from a broken invocation.
Check output shape before believing a silent detector. Every check relied on must
fire against a planted defect: plant it in an isolated fixture, observe rejection,
remove it, then observe the clean result. Record that proof; disclosure alone is
not detector acceptance. A check without this proof remains unverified and the
dependent audit conclusion incomplete or UNKNOWN, never clean. Scope a runtime conclusion to the artifact/version actually
observed; source presence is not installation, deployment or provider acceptance.
When two copies disagree, establish which one is actually selected and consumed
before choosing the direction of a fix. Do not discard either side as stale by taste.

The collector's JSON and HTML are evidence about probes it executed. Add the
manual seam findings and limitations to the human report; do not claim the
collector performed judgment it cannot make. No network or credentials: use the
available committed evidence and label the missing production probes blind.

## Rotate the reading

After the seam pass, choose a different axis rather than repeating effort:

1. Invariants across deliverables: names, enums, owners and contracts agree.
2. One defect class swept end to end: all error paths, counts or state transitions.
3. Code graph against the documented modules, when graph evidence exists.
4. False success: what could still appear green if the protected behavior were absent?
5. Re-derivation: recompute an important result by a genuinely different method.

Record new product findings versus corrections to the audit itself. If the latter
dominate, rotate the axis. A repeated defect class deserves a proposed executable
guard, with a planted defect proving detection; do not edit the project during an
audit. Uncheckable claims remain disclosed, never removed to improve a score.

## Proposed rows and priority

Use the project's board header and column names, never positional assumptions.
Each proposed row names the finding, evidence, affected surface, owner, acceptance
check and dependencies. Preserve the project formula exactly. If no board formula
exists, disclose this default for findings: `Sev × Blast + age_bonus`, with Sev and
Blast each 1–3 and explicitly judged; age_bonus is 1 after 14 days and 2 after 30.
Compute using the recorded finding date and audit date. Do not invent an age,
severity or blast where unknown. Effort does not rank an audit finding.
When product work and findings compete, defer to the project's prioritisation
contract and operator's named task; this audit does not silently choose another job.
Accepted waivers remain decisions with a measured revisit condition, not open debt
that accumulates priority. Findings are proposals until accepted through the owning
project process. The audit changes no application, deployment or shared board.

At opening, measure the work-list from its owning register. At closing, remeasure
it from current state and print both counts and the actual changes beside them;
never reuse the opening list as the closing truth. A missing register or inaccessible
measurement is UNKNOWN and leaves that conclusion incomplete, not an invented zero.

Close when discovered capabilities and required rungs are accounted for and every
relied-on check has demonstrated detection of a planted defect. Unavailable proof
is explicitly incomplete, with the dependent conclusions unverified. Always write
the JSON sidecar. Produce and inspect HTML only when `--report` was requested;
record `--no-open` when used. Without `--report`, JSON-only delivery is complete
when the other conditions hold. The sidecar and requested human report name exactly
what was and was not verified, including the opening/closing work-list comparison.
