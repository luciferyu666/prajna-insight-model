# Contributing - Local Candidate Draft

This document prepares a contribution path for a private local PIM Showcase candidate. It does not establish a public repository, an active issue tracker, permission to redistribute the package or a software license. Use only an already authorized channel until those gates are cleared.

## Start with the actual scope

Read the [quick start](docs/quickstart.md), [evidence guide](docs/research-evidence.md) and [limitations](docs/limitations.md). This slice demonstrates finite contract/reference checks and proposal-only contract versioning. It is not a foundation LLM, the complete CPCR/CAIG solver or a validated human-intent system.

The cases are synthetic TEST_VECTOR_ONLY. Expected FAIL, UNKNOWN and PROPOSED fields are useful results, not values to replace with PASS. A successful demonstration exit does not establish budget-compliant task success.

## Prepare a small, reproducible report

If you already have an authorized copy and a compatible Python installation, the existing JSON demonstration command is:

```console
python -B -X utf8 -m examples.run_showcase --case all --format json
```

Run from the candidate root, without adding a private research checkout to the import path. This document adds no test run. Historical GH02 evidence remains 79 PASS and 13 compiled files on its 23-file snapshot; later documentation checks are different evidence. Full-candidate GH04, Linux and CI verification remain pending.

For a report, record the exact authorized package/version or manifest digest, OS and Python version, command and working directory, exit status, expected and actual behavior, and a minimal synthetic reproduction. Mark unavailable fields UNKNOWN rather than filling them with a guessed value. Identify which output fields you checked and which remain uncertain.

Keep the original local diagnostic in an authorized private location. Before sharing, remove credentials, identifying paths and private research material, and describe any redaction. Do not include reference answers, private Pilot/Rerun records, original research traces, author responses or validation/held-out data. See [support guidance](SUPPORT.md).

## Propose one bounded change

Suitable future tasks include clarifying an output explanation, checking an internal documentation link or adding a synthetic boundary test under a separately approved work package. Agree on the target files, expected behavior, evidence, tests and finite retry budget before implementation.

Do not change a verifier or expected value merely to obtain a green result. Preserve a fixed parent contract; a new proposal remains PROPOSED until a separate authorized adoption mechanism exists. Do not introduce a provider call, API key, model download, dependency, private fixture or research experiment as an incidental fix.

If a change needs code, tests or configuration, follow the applicable written-design, planning, test and independent-review gates. Do not imply that this contribution guide authorizes such work or a Git operation.

## Prepare review evidence

Use the [pull-request template](.github/PULL_REQUEST_TEMPLATE.md) as a local review aid. An actual repository/PR workflow is a later authorized step. State exactly what changed, the reproduced problem, actual validation commands and outcomes, failure/unknown results, preservation evidence, and remaining limits. Mark checks not performed as NOT_RUN.

Keep scientific claims within the tested finite domain. No general Specification Fidelity, optimal CAIG, state sufficiency/Markov property, Atomic Snapshot Commit, External Audit Journal or cross-method performance superiority is established by this candidate.

Disclose AI assistance and material third-party sources. Missing provenance is PARTIAL or UNKNOWN. A report or code contribution does not automatically confer paper authorship. Rights, a specific contribution/license policy and public distribution approval remain human decisions; this draft does not ask contributors to accept an unapproved license.
