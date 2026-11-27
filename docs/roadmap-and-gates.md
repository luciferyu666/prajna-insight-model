# Roadmap, milestones and gates

Updated 28 November 2026. Current scope and completion counts appear in the [dated status report](development-status-2026-11-28.md).

## Gate semantics

| Term | Meaning |
| --- | --- |
| Entry gate | Prerequisites for starting a specific work package |
| Exit gate | Evidence required to accept the package's output |
| Execution authorization | A separate owner decision bound to version, scope, environment, commands, resources and limits |

An exit gate must not become a circular prerequisite for the work needed to satisfy it. For example, G1 acceptance follows the foundation/verifier/adapter work that it evaluates; it does not authorize their execution in advance.

G0-P0-STATIC covered source preparation. Full G0 and G1 remain open. The 25 November closeout accepted D05 section 3 within its fixed local scope after reconciling the run's authorization, configuration, results and cleanup.

## Current D05 priorities

| Priority | Next evidence needed |
| --- | --- |
| A06 development scoring | Qualify a version-bound independent reviewer on a fresh sealed synthetic ballot. Obtain three trustworthy scores, two reproducible policy pairs and sign-off by both designated AI reviewers. |
| A02 and A05-I custody and human calibration | Obtain a rights-backed split and exposure record, staff the second human reviewer and freeze thresholds before ratings begin. Keep both initial ratings independently sealed for adjudication. |
| A06 formal blind evaluation | Complete study design and admission for sealed, unexposed families, including resource limits, missing-data handling and statistical power. |
| A07 independent replication | Have a separate replicator repeat the accepted protocol on another sealed family set and report discrepancies. |
| Subsequent stages | Phase B post-training and Phase C training from random initialization each require their own gate, rights and resource decisions. |

**Phase A stands at 18/28 (64.29%).** A03, A04 and A05-D have owner sign-off within their engineering scopes. Their results support the next evaluation steps. Formal blind evaluation and replication remain `NOT_RUN`.

## Earlier engineering milestones

The ENG and IW identifiers below belong to earlier plans. The current D05 sign-offs and reporting denominator are in the [28 November package table](development-status-2026-11-28.md).

| Priority / milestone | Existing starting point | Required next work | Completion evidence |
| --- | --- | --- | --- |
| P0 — Foundation readiness and governance | Source inventory and case-specific execution admission accepted within the D05 closure | Keep broader source rights and historical host constraints visible for any new use | Independent evidence and a decision for the proposed scope |
| P0 — Foundation behavior | Six integrated cores, historical staging results and a separately accepted local lost-acknowledgement test | Carry forward version and environment limits | The D05 engineering closeout accepted four scoped deliverables on 25 November |
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

The scoped Foundation closeout leaves the historical Windows diagnostics on their own track. The blocked host investigation and earlier SCORE01 Linux result retain their individual evidence and limits.

For the portable/native branch, preserve the 279-identity obligations, the 140-process matrix, required N01/C1 cases, three full regressions and independent full verification according to the applicable version. Do not silently substitute platform coverage. A formal platform-applicability decision is needed for any change to those obligations.

Older IW-12–IW-16 research directions remain relevant to hypotheses, experiments and evaluation, but their mapping to ENG-A07–A10 is functional rather than a claim that either set is complete. Older IW-08–IW-10 attribution/gating work needs controlled cost-matched comparisons.

## Required handoff at each milestone

Record the version, authority, inputs and dependencies, exact acceptance cases, environment, commands, output locations, resource ownership, finite retry allowance, actual results, residual unknowns and next owner. Preserve failed and unknown outcomes.

If dispatch is requested without a trustworthy start or rejection receipt, record the dispatch request/identity and uncertainty; do not retry automatically. Add a later receipt as a new event. Budget anomalies remain incidents and cannot be erased by retrospectively granting more budget.

Public release requires a separate rights/privacy review, an exact release snapshot, reproducible commands and honest evidence availability. It does not follow automatically from a technical gate.
