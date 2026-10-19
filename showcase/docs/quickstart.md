# Quick Start - A Small Offline PIM Showcase

This guide is for a local candidate supplied through an authorized channel. Public redistribution rights and a software license are not cleared. There is no public release or installation service supplied by this guide.

## Prerequisites and working directory

Use an existing compatible Python installation. Recorded runtime evidence is Windows with Python 3.12.14. Linux and other environments have not been validated by the recorded runs.

Run from the root of the candidate copy: the directory containing README.md, examples and experiments. Do not run from inside examples, and do not add a private research checkout to PYTHONPATH to work around an import error. This slice needs no API key, provider account, model download, package installation or research Worker.

## Run the four built-in cases

```console
python -B -X utf8 -m examples.run_showcase --case all --format json
python -B -X utf8 -m examples.run_showcase --case all --format text
```

These are the two existing documented commands. The recorded standalone run used JSON. Text mode was exercised inside the GH02 test process, not in a second standalone run. A new run of this extended documented candidate is still a future GH04 check.

## Read the result without promoting its meaning

The following are selected fields from recorded synthetic demonstrations, not a full output transcript:

| Case | What to inspect |
|---|---|
| wrong_contract | Contract and finite verifier declarations PASS and I_contract=1, while the supplied finite reference L_ref and claims C_claims FAIL. |
| conditional_domain | Finite real/complex branches and declared-domain claims PASS, while the fixed original contract and verifier FAIL and I_contract=0. |
| unknown_verifier | Original constraint PASS and verifier UNKNOWN; I_contract=0. A supplied finite reference may PASS separately. |
| proposal_only | A real 14-field proposal envelope is PROPOSED. Its source bytes/digests and loader round-trip are checked; parent_before equals parent_after. It is not adopted. |

Every case is TEST_VECTOR_ONLY, intent_confirmation UNKNOWN and budget_status NOT_EVALUATED. These examples do not establish benchmark VSR, human intent confirmation or budget-compliant task success.

Exit0 means the demonstration completed, including expected FAIL or UNKNOWN values. Bad arguments exit2. Fixture, I/O or validation errors exit1 with diagnostics on stderr and no partial stdout. A PASS in one result field must not erase a FAIL or UNKNOWN in another.

## If the command fails

Check the current directory and completeness of the candidate first. Keep the command, environment, exit status and original diagnostic. Do not fix a missing file by copying private reports, human answers or research traces into the candidate. Do not change a verifier, fill in a success value or treat an unknown result as a defect to hide.

Discuss a synthetic reproduction with the package owner through an already authorized channel. This candidate does not establish a public issue tracker or support address. Never include credentials or private research materials in a report.

## Evidence and next reading

A five-minute introduction is a readability goal, not a measured external-user result. The historical GH02 record covers 79 PASS and 13 compiled Python files on a 23-file snapshot. Subsequent native documentation checks do not constitute a new Python runtime regression of the extended candidate.

Read the [existing walkthrough](demo-walkthrough.md), [architecture](architecture.md), [limitations](limitations.md) and [evidence guide](research-evidence.md).
