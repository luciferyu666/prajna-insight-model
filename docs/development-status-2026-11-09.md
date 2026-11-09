# Development status — 2026-11-09

This is a dated documentation snapshot, not a test run or an acceptance decision. It replaces the root README's October 14 progress summary. The [evidence guide](evidence-and-reproducibility.md) defines source IDs and disclosure limits.

## Reading the statuses

- **Historical bounded verification:** an existing result for a fixed version, environment, and case set. It is not a fresh November 9 execution.
- **Source prepared / static review:** files and descriptions have been inspected; runtime behavior is not established.
- **NOT_RUN:** required execution has not occurred for that version.
- **BLOCKED:** a necessary prerequisite or authorization remains unresolved.
- **Planned / no whole-package acceptance evidence:** a research direction or partial work, not a completed capability.

A finished subpackage does not close its parent. Counts from overlapping regressions, subtests, static checks, episodes, and research records must not be added into one success total.

## November 9 P0 work

| Package | Delivered | Remaining / status | Evidence |
| --- | --- | --- | --- |
| ENG-A00: project inventory | Version/directory/environment inventory and namespace check | Bounded inventory complete; complete environment admission, permissions and G0 remain unproven | E01 |
| FIX-R00: preservation | Named-file hashes, metadata comparison and preservation report | Bounded preservation evidence; not whole-disk immutability, comprehensive ACL certification or an off-site backup | E01 |
| FIX-R01: environment/blocker diagnosis | Historical failure, safety restriction and unknown-environment branches separated | No new reproduction or safety clearance | E01 |
| FIX-R02: historical R04/G2 gaps | Failure locations, unexecuted obligations and exhausted repair budget identified | Repair and full engineering acceptance remain outstanding | E01 |
| FIX-R04: test/evidence inventory | Version-specific historical tests and outstanding schedules reconciled | Inventory complete; no test was executed by that audit | E01 |
| ENG-A01: task contracts | Foundation schema and acceptance-test source preparation | Runtime contracts/types are not implemented in the new core | E02 |
| ENG-A02: test data and separation | Synthetic public/restricted fixture structure, family manifest and test sources | Loader/registry enforcement is not dynamically verified; these are not adopted research gold answers | E02 |
| ENG-A03: evidence ledger | Event-schema and acceptance-test source preparation | Runtime ledger, ordering/failure behavior and durability remain untested | E02 |
| FIX-R03: budget control | Budget-schema and acceptance-test source preparation | Runtime accounting/admission and incident handling remain untested; no real resource enforcement established | E02 |

The approved **G0-P0-STATIC/L1** scope is narrower than full G0. The four-package Foundation preparation is not implementation acceptance of ENG-A01/A02/A03/FIX-R03.

### Foundation L1 exact boundary

The completed source-preparation stage contains **26 sources**: six schemas, five test files, fourteen fixture/manifest files, and a README. Seven audit files and one implementation plan remain private.

The source-text review outcome is **ACCEPTABLE_WITH_LIMITS**, with a final stage of **SOURCE_PREPARED_DYNAMIC_NOT_RUN**. Two designated AI conversations reviewed supplied source text; this was not independent runtime execution or human scientific validation.

| New acceptance-test area | Defined cases | Execution |
| --- | ---: | --- |
| Constraints | 12 | NOT_RUN |
| Registry / data separation | 14 | NOT_RUN |
| Evidence ledger | 16 | NOT_RUN |
| Budget gate | 16 | NOT_RUN |
| Foundation flow | 6 | NOT_RUN |
| **Total** | **64** | **NOT_RUN** |

The six intended Runtime Core files—`__init__.py`, `types.py`, `contracts.py`, `registry.py`, `ledger.py`, and `budget.py`—have **not been created** in the new Foundation namespace.

The L1 record reports 73 Node-only static observations. These are **not product tests** and are unrelated to SCORE01's historical 73-test result. JSON syntax checks are not JSON Schema validation. Python parsing/import/collection, actual behavior, filesystem durability and failure paths remain untested. **G0/G1 are not passed. L2 is NOT_AUTHORIZED.**

## Earlier engineering packages

The following rows summarize preserved private records unless a public source is explicitly linked.

| Package | Verified scope / existing result | Outstanding boundary | Evidence |
| --- | --- | --- | --- |
| IW-00 | Original six-file offline governance slice: historical 19/19 tests | Structural trusted-caller checks; CLI denies actual launch, no production authentication or OS isolation | E03 |
| IW-00-ALIGN01 | Governance registry candidate, 17 parent packages, static source review | 36 new test definitions NOT_RUN; no executable authority or parent-package PASS produced | E04 |
| IW-01 C01-R01 | Historical 20/20 pure/controlled tests plus bounded native observations | Limited resource receipts; two handle observations UNKNOWN; main Runtime not adopted | E01 |
| IW-01 portable core / PC09 | Isolated 85-file CoreStage, one baseline and seven audit files | Static integration only; 279 test identities require version-specific acceptance. First 89 = 66 contract + 23 observability; remaining 190 retain their obligations. PC09 NOT_RUN | E01 |
| IW-02 | Seven control-test/schema/fixture/document sources and four audit files in v02 | Formal control plugin absent; CONTROL_PRE, CONTROL_GREEN and PC09 NOT_RUN | E05 |
| IW-03 reference layer | Public historical finite loaders, reference checks and paired-manifest checks | Finite syntactic/semantic checks do not authenticate human intent or grant reference adoption | P02, E06 |
| IW-03-HR01 | 36 cases / 18 pairs reviewed through 19 actual human messages; bounded review documentation validated | Curated branches are not uniquely inferable intent. Original bank/adoption authority is unchanged | E06 |
| IW-03-SCORE01 | Historical **73/73** product/regression tests: 36 new + 37 selected regressions; 17 controls and 111 subtests separate | Bounded scoring alignment only; references NOT_ADOPTED. No general intent, efficacy, whole-IW-03 or new Foundation acceptance | E07 |
| IW-04-T01/T02/T03/T05 | Proposal, non-authorizing response statement, finite change preview and review-packet components. T05 historical 148/148 tests includes 24 new tests | Proposals and statements do not themselves authorize adoption; hash consistency is not identity or immutable storage | P02, E08 |
| IW-04-CONFIRM-01 | Private single-contract TA1 demonstration: 188-test engineering record and commit/query evidence; session ended | Bounded single-operator operational trust, not independent identity verification or permission for later contracts | E09 |
| IW-05-MVP01 | Scripted offline three-policy prototype: historical 180 tests (32 new + 148 regressions); six scenarios × three policies = 18 episodes / 94 events | No live LLM study. Clarification supplies scripted reference information; not a fair information-matched performance comparison | E10 |
| Public showcase GH01/GH02 and guides | 33 files are publicly inspectable. Historical packaging reports 63 tests on an earlier snapshot and 79 on its demo extension | Those historical counts do not certify every later file or constitute a new release test. Full research runtime/data are absent | P01–P02 |

SCORE01's later acceptance used a fixed Linux userspace/container validation route. Its earlier environment-inventory image-label discrepancy remains a separate unresolved historical item. The later result does not retroactively accept that environment or clear Windows safety restrictions.

### Remaining research packages

The existing roadmap defines the following work. Whole-package acceptance has not been established by the reviewed cutoff records (E11–E12).

| Package | Existing basis | Still needed |
| --- | --- | --- |
| IW-06: model transport and cost ledger | Historical operation accounting and interface planning | Actual provider integration with verified input/output and cost boundaries |
| IW-07: bounded API calibration | Evaluation planning | Authorized model experiments with fixed tasks, budgets and environment |
| IW-08: historical attribution | Descriptive cost/strategy analyses | Controlled causal comparisons; cost share alone is not removal benefit |
| IW-09: conservative CAIG | Historical rule-based gate | Calibrated candidate and controlled comparison; no optimality claim |
| IW-10: paired counterfactuals | Same-state comparison design | Actual matched alternative-action evidence |
| IW-11: snapshot / external journal | Semantic-projection replay | Snapshot/commit durability and independent external audit acceptance |
| IW-12: hypothesis / assumption / prediction contracts | Research contract design | Implemented and tested interfaces |
| IW-13: finite experiment environment and independent checker | Roadmap | Versioned environments, separate verification and empirical tests |
| IW-14: bounded abduction and counterexample revision | Roadmap | Controlled hypothesis-generation/revision evidence |
| IW-15: active experimentation loop | Roadmap | Cost-matched comparison with passive/random strategies |
| IW-16: preregistered evaluation and claim grading | Research principles | Family-aware evaluation, external checking and scientific validation |

New ENG-Axx/FIX-Rxx identifiers are a later implementation crosswalk; they are not aliases for every older IW package. The A01/A02/A03 policy names inside the older MVP are also different from ENG-A01/A02/A03 Foundation work.

## Outstanding failures and gates

| Item | Actual state at cutoff | Consequence |
| --- | --- | --- |
| Historical HOST H1 | **FAILED: five processes observed against hard limit four** | Limit remains four; no acceptance by relaxing it |
| Historical JSON-D01 | Preparation failed with evidence; diagnostic cases NOT_RUN | Original preparation 1/1 exhausted; no automatic retry or safety clearance |
| Native CORE integration | NOT_RUN; preserved stage contains a RED baseline | RED describes stored baseline source here, not a new executed RED test |
| Earlier 140-process acceptance matrix | 25 PASS, 1 FAIL, 114 NOT_RUN | Not 140 accepted tests; three full regressions and independent full remain unexecuted |
| Later CORE schedule | 153 planned schedules NOT_RUN | Different version/scope; do not add earlier executions to close it |
| G0 / G1 | Not passed | Foundation source review does not close either gate |
| Foundation L2 | NOT_AUTHORIZED | Requires a precise implementation/execution appendix and suitable environment |
| Independent scientific validation | Incomplete | Engineering results do not establish general reasoning or discovery capability |

This update preserves the reported failures and unknowns. It neither reopens old budgets nor modifies existing Gate decisions.
