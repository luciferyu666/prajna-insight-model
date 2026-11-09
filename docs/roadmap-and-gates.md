# Roadmap, milestones and gates

Planning cutoff: **2026-11-09**. This document records priorities and completion criteria, not new execution authorization. Status evidence is linked in the [dated report](development-status-2026-11-09.md).

## Gate semantics

| Term | Meaning |
| --- | --- |
| Entry gate | Prerequisites for starting a specific work package |
| Exit gate | Evidence required to accept the package's output |
| Execution authorization | A separate owner decision bound to version, scope, environment, commands, resources and limits |

An exit gate must not become a circular prerequisite for the work needed to satisfy it. For example, G1 acceptance follows the foundation/verifier/adapter work that it evaluates; it does not authorize their execution in advance.

G0-P0-STATIC is a bounded source-preparation permission. **Full G0 and G1 remain unpassed. Foundation L2 remains unauthorized.** A review, inventory, successful old test or remaining numerical budget does not create a new permission.

## Prioritized milestones

| Priority / milestone | Existing starting point | Required next work | Completion evidence |
| --- | --- | --- | --- |
| P0 — Foundation execution readiness | Approved four-package design; L1 source-text review complete | Prepare a precise L2 appendix covering actual environment, source closure, six missing runtime modules, commands, controlled writes, finite resource limits and stop conditions; resolve applicable G0 gaps | Owner-approved scope and environment admission; not a test PASS |
| P0 — Foundation behavior | 64 defined acceptance cases | After separate authorization, implement ENG-A01/A02/A03/FIX-R03 in the isolated namespace and execute the required failure-path and regression checks | Exact-case results, source preservation, failure evidence, budget reconciliation and independent review; no skipped obligations |
| P0 — Runtime/control readiness | Portable candidate and IW-02 v02 test/control sources | Complete the approved control-plugin path and environment appendix; first validate the 89-case PC09 scope | Fresh receipts on the exact candidate; remaining 190 and native/full-regression obligations stay open |
| P0 — Windows historical branch | Preserved H1/JSON/ACK and security records | Only if this branch is selected, complete precise safety review and bounded recovery authorization before diagnostics or repair | Necessary JSON/four-stage/HOST checks; H1 must satisfy four, not a raised limit |
| P1 — Independent verifier and offline adapter | Finite checks and older scripted prototypes available | ENG-A04/A05: establish public/restricted data boundaries, independent checking, explicit uncertainty and a controlled adapter | Package-specific behavior and negative-case evidence; G1 considered only after its complete criteria are met |
| P1 — Comparable baseline runner | Earlier Pilot and MVP limitations documented | ENG-A06: fixed baseline policies, equal resource accounting, controlled information access and fixed splits | Reproducible comparison protocol and run evidence; assess G2_A as an exit gate |
| P1 — UIP research loop | v0.3 conceptual design | ENG-A07/A08: structured hypotheses/counterexamples and permissioned experiments, with real ablations | Evidence that the implemented loop behaves as specified; no capability claim from an animation or schema |
| P1 — Evaluation and review | Historical negative results, reviewed finite cases and SCORE01 | ENG-A09/A10: blind/family-aware evaluation, uncertainty and cost analysis, replay and independent checking | Fixed protocol, traceable results and explicit claim limits before G_A_B review |
| Conditional Phase B | No accepted training result in this update | Consider derived-weight SFT/LoRA only after Phase A exit conditions and separate data/rights/compute authorization | Model-specific evaluation, provenance and Gate decision |
| Conditional Phase C | Future research | Consider from-scratch pretraining only after the later gates and separate resources are justified | Not scheduled or authorized by this roadmap |

No completion date, cloud budget, training run or deployment is implied by these priorities.

## Two independent engineering tracks

The new Foundation can be planned independently of the unresolved Windows diagnostics where its own prerequisites permit. Its tests cannot close Windows HOST/CORE. Conversely, a historical Windows blocker does not invalidate the separately scoped SCORE01 Linux result.

For the portable/native branch, preserve the 279-identity obligations, the 140-process matrix, required N01/C1 cases, three full regressions and independent full verification according to the applicable version. Do not silently substitute platform coverage. A formal platform-applicability decision is needed for any change to those obligations.

Older IW-12–IW-16 research directions remain relevant to hypotheses, experiments and evaluation, but their mapping to ENG-A07–A10 is functional rather than a claim that either set is complete. Older IW-08–IW-10 attribution/gating work needs controlled cost-matched comparisons.

## Required handoff at each milestone

Record the version, authority, inputs and dependencies, exact acceptance cases, environment, commands, output locations, resource ownership, finite retry allowance, actual results, residual unknowns and next owner. Preserve failed and unknown outcomes.

If dispatch is requested without a trustworthy start or rejection receipt, record the dispatch request/identity and uncertainty; do not retry automatically. Add a later receipt as a new event. Budget anomalies remain incidents and cannot be erased by retrospectively granting more budget.

Public release requires a separate rights/privacy review, an exact release snapshot, reproducible commands and honest evidence availability. It does not follow automatically from a technical gate.
