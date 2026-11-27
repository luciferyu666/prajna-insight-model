# Evidence availability and reproducibility

Updated 28 November 2026. See the [current status](development-status-2026-11-28.md) for Foundation closure and Phase A. The [19 November](development-status-2026-11-19.md) and [20 November](development-status-2026-11-20.md) reports preserve the earlier observations.

This documentation update reviewed the public repository and existing local project records. It ran no product tests, model experiments or native diagnostics. It publishes a sanitized progress summary, not private source packages or raw audit evidence.

## Evidence levels

1. **Public source:** readers can inspect the linked fixed repository snapshot.
2. **Private historical execution evidence:** the publisher inspected local stored results/receipts; the underlying run is historical and access is restricted.
3. **Private source-review evidence:** documents, hashes or source text were inspected; no runtime acceptance is inferred.
4. **Plan:** intended behavior and acceptance criteria, not observed results.

These labels describe availability and scope, not increasing scientific certainty. Private evidence claims are **project-reported engineering results**, not independently reproducible from this public repository. A hash can bind bytes but cannot establish correctness, identity or permission.

## Public reference snapshot

The historical public reference used before the November 19 update is [commit 8dfbcf4](https://github.com/luciferyu666/prajna-insight-model/tree/8dfbcf4f6eb34f214cf2e1ef090bf94dd68a18f6).

| ID | Public source | Supports / limit |
| --- | --- | --- |
| P01 | [Root README at the fixed snapshot](https://github.com/luciferyu666/prajna-insight-model/blob/8dfbcf4f6eb34f214cf2e1ef090bf94dd68a18f6/README.md) | Previously published Pilot summary and research scope; not raw Pilot data |
| P02 | [Showcase evidence guide](https://github.com/luciferyu666/prajna-insight-model/blob/8dfbcf4f6eb34f214cf2e1ef090bf94dd68a18f6/showcase/docs/research-evidence.md), [source tree](https://github.com/luciferyu666/prajna-insight-model/tree/8dfbcf4f6eb34f214cf2e1ef090bf94dd68a18f6/showcase) | Inspectable 33-file historical slice; earlier 63/79-test packaging claims remain historical private-evidence summaries |
| P03 | [Film guide](https://github.com/luciferyu666/prajna-insight-model/blob/8dfbcf4f6eb34f214cf2e1ef090bf94dd68a18f6/docs/research-film.md) | v0.2 explanatory media and its stated research limits; not an execution demonstration |

The original showcase files remain unchanged by this synchronization. Their old pending-release language is retained as historical context, not silently rewritten into retroactive acceptance.

## Private evidence register used for this update

The IDs below identify inspected project records. They are not download links or a claim that private evidence has been released. Exact local paths and SHA-256 bindings are retained in the private synchronization record; personal responses, restricted answers, operational identifiers and raw logs are excluded.

| ID | Record / version | Evidence class and supported scope |
| --- | --- | --- |
| E01 | November 9 P0 Final Report and Historical Test Catalog | Historical-receipt/diagnostic synthesis: ENG-A00, FIX-R00/R01/R02/R04 inventory; runtime failures and unrun obligations |
| E02 | P0-FOUNDATION01 Source-v01 final Stage Decision and Source Manifest, November 9 | Source review: 26 sources, 64 NOT_RUN cases, six absent modules, L2 unauthorized. File hashes were checked against the final manifest for the November 9 update |
| E03 | IW-00 Attempt-01 Final Decision | Historical report: 19-test bounded offline governance acceptance |
| E04 | IW-00-ALIGN01 Attempt-01 Delivery Index | Static candidate: 36 test definitions unexecuted |
| E05 | IW-02 Control-Candidate-v02 Stage Decision | Static source-only acceptance; control plugin and dynamic checks absent |
| E06 | IW-03-HR01 Final Review Decision and Final Validation Receipt | Bounded review/documentation: 36 cases, 18 pairs, 19 actual messages; not reference adoption |
| E07 | SCORE01 ENV-DYNAMIC01 Acceptance, Receipts and stored Raw Run Log, November 1 | Historical fixed-container result: 73 product/regression tests, 17 controls, 111 subtests; raw-log hash matches its receipt |
| E08 | IW-04-T05 Attempt-04 Final Decision | Historical review-packet acceptance; 148-test suite includes previous component regressions |
| E09 | IW-04-CONFIRM-01 Attempt-01 Final Decision | Historical engineering and private single-session operational demo, under explicit trust assumptions |
| E10 | IW-05-MVP01 Attempt-01 Final Decision | Historical 180-method verification and 18 scripted episodes; no model efficacy study |
| E11 | November 3 development inventory | Dated synthesis for remaining IW-06–IW-16 scope and research limits |
| E12 | November 9 work-package crosswalk and approved four-package design | Planning: new ENG/FIX identities, Phase A dependencies and later conditional research |
| E13 | November 19 local Foundation integration, test and closure-review records | Project-reported private evidence: 64 original and 42 additional synthetic cases passed on fixed Linux staging; product snapshot matched but was not separately tested. Raw source, fixtures, receipts and audit records are not publicly available. |

## Later evidence and public verification limits

| Record | What the project checked | What a reader can verify here |
| --- | --- | --- |
| 25 November Foundation closeout | Four scoped engineering exits, the separately executed synthetic ledger test, independently checked launch and cleanup receipts, and the historical staging matrix | The dated result and its scope. The selected public showcase cannot replay the private Foundation runs. |
| 26–27 November Phase A sign-offs | Disclosed data inventories, owner-adopted runner and UIP work, scoring rules, local reviewer delivery controls and the accepted A06 statistical method | The seven-package accounting and milestones in the [status report](development-status-2026-11-28.md). Raw responses and evaluation materials remain private. |
| 28 November reviewer calibration | 35 offline controls passed. One synthetic model ballot failed the judgment check. No research response received an accepted score. | The aggregate negative result and remaining acceptance conditions. |
| 28 November candidate acquisition | File digest and tensor layout checked for the 3B candidate reviewer | The vendor's pinned file and license are linked in the [status report](development-status-2026-11-28.md). Reviewer fitness still requires a prospective calibration. |

The 20 November follow-up recorded the direct ledger test as unrun at that cutoff. The later test has its own execution record.

E02 records the November 9 stage and its 64 NOT_RUN cases and absent modules at that time; E13 is later, bounded evidence and does not retroactively change E02. Later scoped records supersede earlier pending notes only for that particular result. For example, E07 supports the later SCORE01 test result; it does not reconcile the older environment-image mismatch, adopt references, close full IW-03 or pass the new Foundation tests.

## How to inspect or reproduce responsibly

Use the [showcase quick start](../showcase/docs/quickstart.md) for its own source layout and commands. Pin a commit, record the actual interpreter/dependencies, and report exact test identities and output. Those commands do not reproduce private Pilot, SCORE01, TA1 or Foundation evidence.

A complete public research reproduction package would require separately cleared data and software rights, a fixed source/data manifest, environment and dependency identity, commands, expected outputs, analysis and failure records, and appropriate independent checking. Those materials are not all available here. Local private paths must not be represented as publicly accessible citations.

No repository-wide software license is currently selected. Do not infer redistribution rights from visibility, and do not upload restricted answers or private records to fill a reproducibility gap.

## Scientific and engineering limits

- Historical Development Pilot: lower observed PIM VSR and higher mean accounted cost than B0/B1. This is not a confirmatory general ranking or a causal verdict on reframing.
- Gate cost share does not establish the success-rate effect of removing CAIG. A controlled ablation is needed.
- Non-significance is not equivalence. Tasks/seeds within families are dependent; paired reruns are consistency evidence, not extra independent samples.
- A hidden curated branch is not necessarily the unique meaning of an ambiguous task. Clarification, branch completeness and reference hit are separate outcomes.
- Empty solution sets, no answer, ABSTAIN and UNKNOWN must remain distinct.
- Scripted episodes and synthetic fixtures are not evidence of general language understanding, physical fidelity or scientific discovery.
- Byte hashes, replay and local transaction evidence do not establish immutable external storage, oracle correctness or external scientific replication.
- Missing release/handle evidence remains UNKNOWN; it proves neither zero leakage nor a leak.
- Separate AI review contexts do not substitute for independent human scientific or security review.

The current documentation reflects these limits. It does not grant runtime, deployment, scientific, publication or release approval.
