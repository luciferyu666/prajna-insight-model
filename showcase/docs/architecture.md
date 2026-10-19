# Actual Offline Architecture

This CLI demonstrates finite declarations and proposal-only versioning. It does not launch a model, a research Worker or an online verifier.

| Stage | Responsibility |
|---|---|
| Fixed synthetic fixture | One of four bundled cases; not arbitrary external input. |
| examples.run_showcase | Fixed case selection, guarded fixture reads, orchestration and deterministic presentation. |
| experiments.pim_next.pim_next.contracts | Real load_reference and load_answer calls over supplied finite declarations. |
| experiments.pim_next.pim_next.reference | Real adjudicate_answer calls using the loaded finite declarations. |
| experiments.pim_next.pim_next.contract_versions | Real propose_contract and load_contract_proposal calls; a proposal remains PROPOSED. |
| Output | Finite contract/verifier status, supplied-reference claims/coverage, unknown intent, unevaluated budgets, or an unadopted proposal. |

Existing contracts, governance and reference-bank helpers are retained original dependencies. This CLI does not claim to exercise every included helper.

## Separate acceptance questions

The demonstration's C_v and V_v are supplied finite declarations. Their adjudication is distinct from the original WP02 runtime's independent verifier. This slice does not execute legacy CPCR/CAIG, semantic replay or the research Worker.

Contract conformity and supplied finite-reference acceptance can disagree. Neither confirms a person's intended task. I_contract is a finite contract/verifier indicator, not an intent oracle or a budget-compliant success measure.

The conditional real/complex response does not replace the fixed original contract. Proposal creation preserves original/parent/proposed UTF-8 sources and digests; loader round-trip and unchanged parent adjudications do not authorize adoption.

## Defensive boundaries

Fixed paths, bounded reads and strict JSON reject selected malformed or out-of-scope inputs. These checks are not an OS sandbox or an exhaustive security proof.

Intent is UNKNOWN; budgets are NOT_EVALUATED. There is no durable commit, immutable snapshot, External Audit Journal or general semantic-fidelity guarantee.

See [limitations](limitations.md), [AI assistance](ai-assistance.md) and the [entry guide](../README.md).

