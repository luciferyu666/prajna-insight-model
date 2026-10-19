# PIM offline tour

This Windows/Python3.12 demonstration calls the existing finite-reference and proposal APIs. It is a small synthetic research slice, without a model, network, API key or installation step. Public redistribution rights and a software license are not yet cleared.

From this candidate directory, run:

```console
python -B -X utf8 -m examples.run_showcase --case all --format text
python -B -X utf8 -m examples.run_showcase --case all --format json
```

Use any one fixed name instead of all:

| Case | What to inspect |
|---|---|
| wrong_contract | Original contract and verifier accept one; the separately supplied finite reference requires two, so I_contract=1 but L_ref=FAIL. |
| conditional_domain | The real/complex branches match the supplied finite sets, while the single fixed original contract rejects the combined conditional response. No human has confirmed the domain. |
| unknown_verifier | The original constraint accepts a, but V_v is unavailable: original_verifier_status=UNKNOWN and I_contract=0. |
| proposal_only | A new declaration is PROPOSED; original UTF-8 sources/digests are preserved and the original parent is adjudicated unchanged before and after. |

Every case is TEST_VECTOR_ONLY. intent_confirmation stays UNKNOWN and budget_status is NOT_EVALUATED. A finite-reference PASS is not a proof of natural-language fidelity, real human intent, generalization or task success. Proposal creation does not approve or activate a contract.

Exit0 means the demonstration ran, including expected FAIL/UNKNOWN results. Invalid CLI arguments exit2; fixture/IO/validation failures exit1 with diagnostics on stderr and no partial result on stdout. JSON is deterministic; no private path, PID or timestamp is part of its result. Path checks are not an OS sandbox.

Optional test commands (for a reader; not additional executions claimed by this document):

```console
python -B -X utf8 -m unittest discover -s experiments/pim_next/tests -p "test_*.py"
python -B -X utf8 -m unittest discover -s tests -p "test_showcase.py"
```

The preserved Windows source slice has63 methods; this tour adds16. Historical private82-method evidence is a different scope. No Linux/CI/public-release or external-user success is claimed. Three minutes is a tour goal, not an observed independent usability result.

The historical development results remain negative: B0/B1/PIM VSR79.07%/79.81%/60.37%, mean costs923.79/796.90/1294.22. This demonstration changes none of those records or research limitations.

