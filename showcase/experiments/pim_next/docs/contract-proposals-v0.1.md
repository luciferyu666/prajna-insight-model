# Pure Contract Proposals v0.1

This boundary creates PROPOSED-only in-memory values. It does not confirm intent, approve or activate contracts, replace an original verifier, score answers, fetch evidence, write files or dispatch work. All examples and tests are synthetic TEST_VECTOR evidence.

## API

Import ContractProposal, propose_contract and load_contract_proposal directly from experiments.pim_next.pim_next.contract_versions. The constructor and factory take the same five keyword-only inputs: original_problem_bytes, parent_contract_bytes, proposed_contract_bytes, reason and evidence_refs. No public constructor argument accepts status or derived digests. as_dict() returns a fresh mutable JSON-compatible dict; load_contract_proposal(raw) validates and recomputes an exact wire object.

The frozen slotted value retains only exact bytes, a string and a tuple of strings. Its normal Python API is deeply immutable; returned containers cannot mutate it. This is not protection against hostile code deliberately bypassing Python object protections, nor immutable storage.

## Exact inputs and finite declarations

Original bytes have length1–65536, valid strict UTF-8 without BOM, and nonblank text. Each declaration has length1–131072 bytes, valid strict UTF-8 without BOM, and exactly one strict JSON object. Mutable bytearray/memoryview, duplicate JSON keys, nonfinite numbers, invalid UTF-8 and non-object declarations reject. Source bytes are retained without trimming, normalization, newline conversion or reserialization.

Declarations contain exactly case_id, version, omega, acceptance_rule, C_v and V_v. IDs match [A-Za-z0-9][A-Za-z0-9_.:-]{0,63}. omega is an ordered list of1–512 unique IDs. C_v is a list of0–512 unique IDs contained in omega. V_v is null or such a list. Null means unknown; an empty set is valid and distinct from unknown. acceptance_rule is ONE_WITNESS or ALL_SOLUTIONS.

Parent and candidate must have identical case_id, ordered omega and acceptance_rule, different versions, and different C_v or V_v set meanings. Version-only and set-order-only changes reject. No subset, equivalence, intent fidelity or semantic preservation relation is inferred. Candidate acceptance never changes the original declaration's result.

reason is a nonblank, strict UTF-8 encodable string of at most4096 characters. evidence_refs is a tuple of1–16 unique nonblank, strict UTF-8 encodable strings, each at most2048 characters. References are opaque supplied pointers; they are never opened, authenticated or treated as approval. Do not supply private human data or credentials.

## Wire format and integrity

The exact14 fields are schema_version, status, original_problem_utf8, parent_contract_utf8, proposed_contract_utf8, original_problem_sha256, parent_sha256, proposed_sha256, case_id, parent_version, proposed_version, reason, evidence_refs and proposal_sha256. schema_version is pim-next.contract-proposal.v1 and status is PROPOSED. evidence_refs exports as a fresh JSON list. All retained text roundtrips to its original bytes.

Each source digest is lowercase SHA-256 over the exact bytes. proposal_sha256 is SHA-256 over UTF-8 JSON of the other13 fields with sorted keys, ensure_ascii=false, compact comma/colon separators and allow_nan=false. Reason and reference order are bound. Formatting-only source changes produce different hashes without proving semantic difference or falsification.

Loading reconstructs and validates inputs and compares every supplied derived field and digest against recomputation. Unknown fields, forged status and stale/tampered bindings reject. Rehashing a changed proposal creates different content; a hash is not a signature, trusted provenance, proof of human authorship, atomic commit or immutable audit. Binding original bytes does not prove correct extraction or fidelity.

## Failures and validation limits

Invalid data raise T01 ValidationError. Categories are INPUT_BYTES, INPUT_BOUNDS, INPUT_ENCODING, INPUT_BLANK; DECLARATION_FIELDS, DECLARATION_ID, DECLARATION_LIST, DECLARATION_DUPLICATE, DECLARATION_DOMAIN, DECLARATION_RULE, DECLARATION_MISMATCH, DECLARATION_VERSION, DECLARATION_NOOP; METADATA_TEXT, METADATA_ENCODING, EVIDENCE_REFS; WIRE_FIELDS, WIRE_TYPE, WIRE_STATUS and WIRE_BINDING. Strict JSON categories DUPLICATE_JSON_KEY, NONFINITE_JSON_NUMBER and MALFORMED_JSON propagate. Unsupported call keywords are ordinary Python TypeError, not accepted proposal fields.

The Schema declares wire shape and character bounds. Runtime additionally enforces byte bounds, strict encodability, nonblank metadata, finite-declaration semantics and hash integrity. Tests inspect specific Schema declarations and representative generated-wire shape; no generic JSON Schema validation engine is provided.

Synthetic tests include real T01 scoring of parent and candidate independently. A candidate can accept a synthetic answer rejected by its parent while the parent's I_contract remains unchanged. This demonstrates boundary compatibility only, not adoption or a research outcome. Actual test and process results live in the IW-04 audit evidence; this document does not assert a passing test count.

## Remaining boundaries

Human/reference review, trusted confirmation, activation, persistence, race-safe updates and UI/CLI require separately approved designs. No general fidelity, calibrated belief, Markov/sufficient state, optimal policy, causal benefit, zero leakage or atomic snapshot theorem is established. IW-03 and IW-04 whole packages remain incomplete. R04/T00/WP04 remain BLOCKED; historical root cause UNDETERMINED; M01/M02/full human review PENDING; P15/TMLR submission BLOCKED, eligibility NEEDS_EDITOR_CLARIFICATION, publication NOT_SUBMITTED. Historical B0/B1/PIM VSR79.07%/79.81%/60.37% and costs923.79/796.90/1294.22 are unchanged.
