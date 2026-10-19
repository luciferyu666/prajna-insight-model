# PIM Showcase — Finite Contract Checks and Proposal-Only Versioning

A small synthetic executable slice associated with Prajna Insight Model research. It demonstrates existing finite-reference checks and proposal-only contract versioning.

**Private local candidate. Public redistribution rights and a software license have not been cleared.** This is not a pretrained/foundation LLM or a full CPCR/CAIG research execution.

## Quick Start

Use an existing compatible Python installation from the root of your local candidate copy. Recorded runtime evidence is Windows/Python 3.12.14; no installation or API key is needed for this slice.

```console
python -B -X utf8 -m examples.run_showcase --case all --format json
python -B -X utf8 -m examples.run_showcase --case all --format text
```

JSON has a recorded standalone execution. Text mode was exercised inside the GH02 test process, not a second standalone run. A five-minute introduction is a readability goal, not a measured external-user result.

## What to inspect

These selected fields summarize the recorded GH02 output; they are not a full raw transcript.

| Case | Observed distinction |
|---|---|
| wrong_contract | Contract and finite verifier declarations PASS, I_contract=1; supplied finite reference L_ref and claims C_claims FAIL. |
| conditional_domain | Real/complex finite branches and declared-domain claims PASS; the fixed original contract and verifier FAIL, I_contract=0. Human intent remains UNKNOWN. |
| unknown_verifier | Original constraint PASS, verifier UNKNOWN, I_contract=0; the supplied finite reference can PASS independently. |
| proposal_only | A real 14-field envelope is PROPOSED. Source bytes/digests and loader round-trip are checked; parent_before equals parent_after. No adoption. |

Every case is TEST_VECTOR_ONLY, intent_confirmation UNKNOWN and budget_status NOT_EVALUATED. These are not benchmark VSR or budget-compliant task-success results.

Exit0 means the demonstration ran, including expected FAIL/UNKNOWN. Bad arguments exit2; fixture/IO/validation errors exit1 with stderr diagnostics and no partial stdout.

## Evidence and platform

PRIVATE_LOCAL_EVIDENCE: GH02 Attempt-01 recorded 79 PASS and 13 compiled Python files on the 23-file pre-documentation snapshot. That is historical evidence, not fresh runtime validation of the 27-file documented candidate. No Linux, CI, public-release or external-user result is claimed. GH04 remains the future full-candidate/release verification gate.

The standalone JSON and in-process capture match as documents; their raw streams differ only in the final LF/CRLF. Hashes identify observed bytes; they do not enforce immutable storage.

## Read next

- [Existing walkthrough](docs/demo-walkthrough.md)
- [Actual offline architecture](docs/architecture.md)
- [Research and distribution limitations](docs/limitations.md)
- [AI assistance and provenance](docs/ai-assistance.md)

For local review, inspect or discuss a synthetic case with the package owner. No public issue tracker or support channel is established by this candidate. Do not send secrets, private research traces or human reference answers.

