# Foundation and Phase A status on 28 November 2026

**Foundation closed its four scoped engineering deliverables on 25 November (4/4, 100%). Phase A has 18 of 28 signed engineering milestones (64.29%).** Phase A's formal blind study and independent replication both remain `NOT_RUN`. The two percentages have different denominators. Neither measures model accuracy.

## Foundation

| D05 section 3 deliverable | What the project accepted |
| --- | --- |
| A00, source inventory | A dated baseline, source index and explicit unknowns for the approved scope. Broader usage and redistribution rights for the 32-source inventory remain unresolved. |
| L2 execution admission | For one fixed local run, reviewers checked source identity, launch arguments and the isolated configuration before launch. Exit, resource and cleanup records were reconciled afterward. |
| L2 implementation and validation | Six runtime modules were integrated. All 32 files in the product snapshot matched the tested Linux staging snapshot byte for byte. Historical staging records show **64/64** original acceptance cases and **42/42** additional synthetic regression cases passing. The file comparison added no second run of that suite. |
| A01, contract and evidence ledger | On 25 November one local synthetic test injected a lost acknowledgement after a successful ledger commit. The ledger entered `UNKNOWN`, subsequent reservation was refused, and the stored ledger bytes remained unchanged. The original test ran once and exited successfully. |

The closure applies to the approved source set and local environment. Full G0 and G1 remain open. The historical Windows host investigation remains blocked. Physical power loss and uncontrolled concurrent writers are outside the observed test conditions.

## Phase A

The project counts four sign-off milestones in each of seven work packages. The denominator stays at 28 when a test fails or a new asset is acquired.

| Work package | Signed | Evidence and next unmet condition |
| --- | ---: | --- |
| A02, data and splits | 2/4 | Six development packs contain 16 previously disclosed cards. Their fingerprints and 120 pair comparisons were checked. Formal data still need an independent custodian's record of rights, prior exposure and family-level splits. |
| A03, comparison runner | 4/4 | The E0 preview reconstructed five archived commands and prompts. E1 exercised controlled observations, rejection and replay. E2 and E3 exercised planning and delivery with zero dispatch to a model or observation backend. |
| A04, Unified Insight Process | 4/4 | Assumption challenge, relation search and thought-experiment planning were each switched on or off on the same disclosed card at a fixed intervention point. Six submissions reached the same scoring procedure and tied. Planner stopping states and the effect of exploration feedback remain open research questions. |
| A05-D, scoring contract | 4/4 | The owner adopted scoring rules with explicit applicability across the six development packs. Formal study thresholds and power belong to A06. |
| A05-I, independent review | 3/4 | Two isolated local reviewer endpoints each received six disclosed items. Seven controls passed and 77 decisions could be replayed. Independent human ratings, disagreement resolution and formal calibration remain outstanding. |
| A06, blind evaluation | 1/4 | The owner accepted a method for counting development families and assessing power for two primary comparisons. Three first responses from the B0, B1 and full UIP policies on one development card are sealed. Accepted scores are **0/3** and verifiable policy pairs **0/2**. Formal blind evaluation remains `NOT_RUN`. |
| A07, independent replication | 0/4 | The protocol calls for an independent replicator and a separate set of sealed, unexposed families. Replication remains `NOT_RUN`. |
| **Total** | **18/28** | **64.29%.** Two more signed milestones would reach 20/28 (71.43%), the first attainable mark at or above 70%. |

## Why the latest reviewer result added no milestone

On 28 November the R12 calibration passed **35/35 offline controls**. One generated synthetic ballot then failed the judgment check. Four designated AI reviewers examined the aggregate result and recommended retaining the failure and calibrating a replacement on a fresh, pre-sealed synthetic case. The three sealed research responses still need trustworthy scores.

The project acquired Qwen2.5-3B-Instruct Q4_K_M as a candidate reviewer for noncommercial research. The 2,104,932,768-byte file matched the publisher's SHA-256, and independent static inspection checked all **435/435** tensor shapes and byte ranges. Model loading, inference and reviewer calibration with this asset remain pending. The project distributes no model weights here. [Publisher's pinned model file](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/blob/7dabda4d13d513e3e842b20f0d435c732f172cbe/qwen2.5-3b-instruct-q4_k_m.gguf) · [License at the same revision](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/blob/7dabda4d13d513e3e842b20f0d435c732f172cbe/LICENSE)

## What can advance the study

1. Bind the candidate reviewer to its own version and resource limits, then calibrate it on a fresh sealed synthetic case. The next A06 milestone requires three trustworthy scores, two reproducible pairs and unconditional acceptance of the same result by both designated AI reviewers.
2. In parallel, secure an independent custodian's split receipt, complete human reviewer staffing, and freeze agreement thresholds before the first human rating.
3. Run the formal blind study under its own authorization, then replicate it independently. The historical development Pilot remains available. PIM showed lower verified success and higher accounted cost than both baselines in that setting.

This update summarizes existing private project records. The public showcase covers an earlier subset. Readers can inspect the aggregate provenance and the older snapshots through the [evidence guide](evidence-and-reproducibility.md) and the [20 November report](development-status-2026-11-20.md). No research experiment was rerun for this documentation update.
