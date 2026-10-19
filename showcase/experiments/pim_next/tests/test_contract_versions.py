"""TEST_VECTOR boundaries only; no human, bank or provider evidence."""
import copy
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import re
import unittest

from experiments.pim_next.pim_next.contracts import (
    AnswerEnvelope, ReferenceSpec, ValidationError,
)
from experiments.pim_next.pim_next.contract_versions import (
    ContractProposal, load_contract_proposal, propose_contract,
)
from experiments.pim_next.pim_next.reference import adjudicate_answer


WIRE = {
    "schema_version", "status", "original_problem_utf8", "parent_contract_utf8",
    "proposed_contract_utf8", "original_problem_sha256", "parent_sha256",
    "proposed_sha256", "case_id", "parent_version", "proposed_version",
    "reason", "evidence_refs", "proposal_sha256",
}


def declaration(version="v1", c=("a",), v=("a",), rule="ONE_WITNESS"):
    return {"case_id": "tv.case", "version": version, "omega": ["a", "b"],
            "acceptance_rule": rule, "C_v": list(c),
            "V_v": None if v is None else list(v)}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")


def inputs():
    return {"original_problem_bytes": "TEST_VECTOR: 保留\r\n original. ".encode(),
            "parent_contract_bytes": encoded(declaration()),
            "proposed_contract_bytes": encoded(declaration("v2", ("b",), ("b",))),
            "reason": " Synthetic alternative; not approved. ",
            "evidence_refs": ("synthetic:TV01", "opaque:not-fetched")}


class ContractProposalTests(unittest.TestCase):
    def rejected(self, changes, category=None):
        for maker in (propose_contract, ContractProposal):
            with self.subTest(maker=maker.__name__, changes=repr(changes)[:100]):
                with self.assertRaises(ValidationError) as caught:
                    maker(**dict(inputs(), **changes))
                if category is not None:
                    self.assertEqual(str(caught.exception), category)

    def test_valid_exact_bytes_and_fourteen_fields(self):
        data = inputs()
        wire = propose_contract(**data).as_dict()
        self.assertEqual(set(wire), WIRE)
        self.assertEqual(wire["status"], "PROPOSED")
        self.assertEqual(wire["schema_version"], "pim-next.contract-proposal.v1")
        for input_key, wire_key in (
                ("original_problem_bytes", "original_problem_utf8"),
                ("parent_contract_bytes", "parent_contract_utf8"),
                ("proposed_contract_bytes", "proposed_contract_utf8")):
            self.assertEqual(wire[wire_key].encode("utf-8"), data[input_key])
        self.assertEqual(wire["reason"], data["reason"])
        self.assertEqual(wire["evidence_refs"], list(data["evidence_refs"]))
        self.assertEqual((wire["case_id"], wire["parent_version"],
                          wire["proposed_version"]), ("tv.case", "v1", "v2"))

    def test_deterministic_roundtrip(self):
        first = propose_contract(**inputs())
        self.assertEqual(first, ContractProposal(**inputs()))
        self.assertEqual(first.as_dict(), propose_contract(**inputs()).as_dict())
        wire = json.loads(json.dumps(first.as_dict(), ensure_ascii=False))
        self.assertEqual(load_contract_proposal(wire), first)

    def test_independent_source_and_envelope_digests(self):
        data = inputs()
        wire = propose_contract(**data).as_dict()
        for source, digest in (("original_problem_bytes", "original_problem_sha256"),
                               ("parent_contract_bytes", "parent_sha256"),
                               ("proposed_contract_bytes", "proposed_sha256")):
            self.assertEqual(wire[digest], hashlib.sha256(data[source]).hexdigest())
        payload = dict(wire)
        actual = payload.pop("proposal_sha256")
        independent = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                 separators=(",", ":"), allow_nan=False).encode("utf-8")
        self.assertEqual(actual, hashlib.sha256(independent).hexdigest())

    def test_byte_formatting_reason_and_reference_order_are_bound(self):
        baseline = propose_contract(**inputs()).as_dict()
        for changes, changed_digest in (
                ({"parent_contract_bytes": b"\n" + inputs()["parent_contract_bytes"]}, "parent_sha256"),
                ({"original_problem_bytes": b"Another TEST_VECTOR"}, "original_problem_sha256"),
                ({"reason": "Another reason"}, None),
                ({"evidence_refs": tuple(reversed(inputs()["evidence_refs"]))}, None)):
            wire = propose_contract(**dict(inputs(), **changes)).as_dict()
            self.assertNotEqual(wire["proposal_sha256"], baseline["proposal_sha256"])
            if changed_digest:
                self.assertNotEqual(wire[changed_digest], baseline[changed_digest])

    def test_frozen_and_fresh_export(self):
        proposal = propose_contract(**inputs())
        with self.assertRaises(FrozenInstanceError):
            proposal.reason = "changed"
        with self.assertRaises(FrozenInstanceError):
            del proposal.evidence_refs
        wire = proposal.as_dict()
        wire["evidence_refs"].append("changed")
        wire["status"] = "APPROVED"
        self.assertEqual(proposal.as_dict()["evidence_refs"], list(inputs()["evidence_refs"]))
        self.assertEqual(proposal.as_dict()["status"], "PROPOSED")
        self.assertFalse(hasattr(proposal, "__dict__"))

    def test_direct_constructor_cannot_accept_state_or_digests(self):
        for key in ("status", "proposal_sha256", "parent_sha256", "case_id"):
            with self.subTest(key=key), self.assertRaises(TypeError):
                ContractProposal(**dict(inputs(), **{key: "APPROVED"}))

    def test_exact_bytes_types_bounds_and_original_blank(self):
        for key, maximum in (("original_problem_bytes", 65536),
                             ("parent_contract_bytes", 131072),
                             ("proposed_contract_bytes", 131072)):
            for bad in ("text", bytearray(b"x"), memoryview(b"x"), None, True):
                self.rejected({key: bad}, "INPUT_BYTES")
            for bad in (b"", b"x" * (maximum + 1)):
                self.rejected({key: bad}, "INPUT_BOUNDS")
        self.rejected({"original_problem_bytes": b" \r\n\t"}, "INPUT_BLANK")
        valid = inputs()
        valid["original_problem_bytes"] = b"x" * 65536
        for key in ("parent_contract_bytes", "proposed_contract_bytes"):
            valid[key] += b" " * (131072 - len(valid[key]))
        self.assertEqual(len(propose_contract(**valid).original_problem_bytes), 65536)

    def test_invalid_utf8_bom_and_surrogate_bytes_all_sources(self):
        for key in ("original_problem_bytes", "parent_contract_bytes", "proposed_contract_bytes"):
            for bad in (b"\xff", b"\xef\xbb\xbf{}", b"\xed\xa0\x80"):
                self.rejected({key: bad}, "INPUT_ENCODING")

    def test_strict_json_both_declarations(self):
        for key in ("parent_contract_bytes", "proposed_contract_bytes"):
            for raw, category in ((b'{"x":1,"x":2}', "DUPLICATE_JSON_KEY"),
                                  (b'{"x":NaN}', "NONFINITE_JSON_NUMBER"),
                                  (b'{"x":Infinity}', "NONFINITE_JSON_NUMBER"),
                                  (b'{"x":1e9999}', "NONFINITE_JSON_NUMBER"),
                                  (b"{", "MALFORMED_JSON")):
                self.rejected({key: raw}, category)

    def test_exact_declaration_fields_and_container_types_both_sides(self):
        for key in ("parent_contract_bytes", "proposed_contract_bytes"):
            for bad in (None, [], True, 5, "object"):
                self.rejected({key: encoded(bad)}, "DECLARATION_FIELDS")
            for change in ({"extra": 1}, {"C_v": None}, {"C_v": "a"},
                           {"V_v": {}}, {"omega": None}, {"omega": "a"},
                           {"acceptance_rule": True}, {"acceptance_rule": "PASS"}):
                raw = declaration("v2" if key.startswith("proposed") else "v1")
                raw.update(change)
                self.rejected({key: encoded(raw)})
            for omitted in declaration():
                raw = declaration()
                del raw[omitted]
                self.rejected({key: encoded(raw)}, "DECLARATION_FIELDS")

    def test_ids_bounds_duplicates_and_complete_domain_both_sides(self):
        for key in ("parent_contract_bytes", "proposed_contract_bytes"):
            for field in ("case_id", "version", "omega", "C_v", "V_v"):
                for bad in (True, 1, "", " a", "a/b", "a" * 65, "\ud800"):
                    raw = declaration()
                    raw[field] = [bad] if field in ("omega", "C_v", "V_v") else bad
                    source = json.dumps(raw, ensure_ascii=True).encode()
                    self.rejected({key: source}, "DECLARATION_ID")
            for field in ("omega", "C_v", "V_v"):
                for bad in (["a", "a"], [str(i) for i in range(513)]):
                    raw = declaration()
                    raw[field] = bad
                    self.rejected({key: encoded(raw)})
            for field in ("C_v", "V_v"):
                raw = declaration()
                raw[field] = ["outside"]
                self.rejected({key: encoded(raw)}, "DECLARATION_DOMAIN")
            self.rejected({key: encoded(dict(declaration(), omega=[]))}, "DECLARATION_LIST")

    def test_maximum_domain_and_identifier_are_accepted(self):
        domain = ["id" + str(i) for i in range(512)]
        parent = dict(declaration(), case_id="a" * 64, omega=domain, C_v=domain, V_v=domain)
        candidate = dict(parent, version="b" * 64, C_v=[])
        proposal = propose_contract(**dict(inputs(), parent_contract_bytes=encoded(parent),
                                           proposed_contract_bytes=encoded(candidate)))
        self.assertEqual(proposal.as_dict()["case_id"], "a" * 64)

    def test_case_ordered_domain_mode_and_version_mismatches(self):
        for change in ({"case_id": "other"}, {"omega": ["b", "a"]},
                       {"omega": ["a", "b", "c"]}, {"acceptance_rule": "ALL_SOLUTIONS"}):
            candidate = dict(declaration("v2", ("b",), ("b",)), **change)
            self.rejected({"proposed_contract_bytes": encoded(candidate)}, "DECLARATION_MISMATCH")
        self.rejected({"proposed_contract_bytes": encoded(declaration("v1", ("b",), ("b",)))},
                      "DECLARATION_VERSION")

    def test_version_only_and_set_reordering_are_noops(self):
        self.rejected({"proposed_contract_bytes": encoded(declaration("v2"))}, "DECLARATION_NOOP")
        parent = declaration(c=("a", "b"), v=("a", "b"))
        candidate = declaration("v2", ("b", "a"), ("b", "a"))
        self.rejected({"parent_contract_bytes": encoded(parent),
                       "proposed_contract_bytes": encoded(candidate)}, "DECLARATION_NOOP")

    def test_empty_unknown_and_each_set_change_are_distinct(self):
        pairs = ((declaration(v=None), declaration("v2", v=())),
                 (declaration(c=(), v=()), declaration("v2", c=(), v=None)),
                 (declaration(), declaration("v2", c=("b",))),
                 (declaration(), declaration("v2", v=("b",))))
        for parent, candidate in pairs:
            proposal = propose_contract(**dict(inputs(), parent_contract_bytes=encoded(parent),
                                               proposed_contract_bytes=encoded(candidate)))
            self.assertEqual(json.loads(proposal.as_dict()["proposed_contract_utf8"]), candidate)

    def test_metadata_bounds_types_and_unique_references(self):
        for reason in (None, True, [], "", " \n", "x" * 4097):
            self.rejected({"reason": reason}, "METADATA_TEXT")
        for refs in (None, [], ["x"], "x", (), ("x", "x"), tuple(str(i) for i in range(17))):
            self.rejected({"evidence_refs": refs}, "EVIDENCE_REFS")
        for ref in (None, True, [], "", " \n", "x" * 2049):
            self.rejected({"evidence_refs": (ref,)}, "METADATA_TEXT")
        proposal = propose_contract(**dict(inputs(), reason="r" * 4096,
                                           evidence_refs=tuple(str(i) + "x" * 2046 for i in range(16))))
        self.assertEqual(len(proposal.evidence_refs), 16)

    def test_unicode_surrogate_metadata_and_wire_rejected(self):
        self.rejected({"reason": "\ud800"}, "METADATA_ENCODING")
        self.rejected({"evidence_refs": ("\ud800",)}, "METADATA_ENCODING")
        for key in ("original_problem_utf8", "parent_contract_utf8", "proposed_contract_utf8"):
            wire = propose_contract(**inputs()).as_dict()
            wire[key] = "\ud800"
            with self.assertRaisesRegex(ValidationError, "^INPUT_ENCODING$"):
                load_contract_proposal(wire)

    def test_wire_exact_fields_types_and_forged_status(self):
        base = propose_contract(**inputs()).as_dict()
        for bad in (None, [], "wire", True):
            with self.assertRaisesRegex(ValidationError, "^WIRE_FIELDS$"):
                load_contract_proposal(bad)
        for key in WIRE:
            missing = dict(base)
            del missing[key]
            with self.subTest(missing=key), self.assertRaises(ValidationError):
                load_contract_proposal(missing)
            wrong = dict(base, **{key: True})
            with self.subTest(wrong=key), self.assertRaises(ValidationError):
                load_contract_proposal(wrong)
        for change in ({"actor": "human"}, {"approval_token": "synthetic"},
                       {"evidence_refs": ("synthetic:TV01",)},
                       {"schema_version": "pim-next.contract-proposal.v2"}):
            with self.assertRaises(ValidationError):
                load_contract_proposal(dict(base, **change))
        for status in ("APPROVED", "ACTIVE", "HUMAN_CONFIRMED"):
            with self.assertRaisesRegex(ValidationError, "^WIRE_STATUS$"):
                load_contract_proposal(dict(base, status=status))

    def test_wire_tamper_every_bound_field(self):
        base = propose_contract(**inputs()).as_dict()
        mutations = {
            "original_problem_utf8": base["original_problem_utf8"] + "!",
            "parent_contract_utf8": base["parent_contract_utf8"] + " ",
            "proposed_contract_utf8": base["proposed_contract_utf8"] + " ",
            "original_problem_sha256": "0" * 64, "parent_sha256": "0" * 64,
            "proposed_sha256": "0" * 64, "case_id": "other", "parent_version": "other",
            "proposed_version": "other", "reason": "Altered reason",
            "evidence_refs": list(reversed(base["evidence_refs"])), "proposal_sha256": "0" * 64,
        }
        for key, value in mutations.items():
            with self.subTest(key=key), self.assertRaisesRegex(ValidationError, "^WIRE_BINDING$"):
                load_contract_proposal(dict(base, **{key: value}))

    def test_loader_runs_semantics_even_with_recomputed_envelope(self):
        for candidate in (declaration("v1", ("b",), ("b",)), declaration("v2"),
                          dict(declaration("v2", ("b",), ("b",)), omega=["b", "a"])):
            wire = propose_contract(**inputs()).as_dict()
            wire["proposed_contract_utf8"] = encoded(candidate).decode()
            wire["proposed_sha256"] = hashlib.sha256(encoded(candidate)).hexdigest()
            wire["proposed_version"] = candidate["version"]
            payload = {k: v for k, v in wire.items() if k != "proposal_sha256"}
            wire["proposal_sha256"] = hashlib.sha256(json.dumps(
                payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
                allow_nan=False).encode()).hexdigest()
            with self.assertRaises(ValidationError):
                load_contract_proposal(wire)

    def test_real_t01_integration_original_is_not_replaced(self):
        case = ReferenceSpec(
            case_id="tv.case", latent_id="tv.latent", family_id="tv.family",
            presentation_kind="EXPLICIT", original_text="TEST_VECTOR only",
            omega=("a", "b"), theta_options=("one",), theta_star="one",
            q_by_theta={"one": ("a",)}, question_slots=(), confirmation_required=False,
            reference_revision="tv.r1",
            approval_source={"status": "TEST_VECTOR", "source_ref": "synthetic:proposal"})
        for rule in ("ONE_WITNESS", "ALL_SOLUTIONS"):
            parent = declaration(rule=rule)
            candidate = declaration("v2", ("b",), ("b",), rule)
            preserved = copy.deepcopy(parent)
            answer = AnswerEnvelope("ANSWER", ("b",), {}, None, "TEST_VECTOR")
            before = adjudicate_answer(case, parent, answer, {})
            proposal = propose_contract(**dict(inputs(), parent_contract_bytes=encoded(parent),
                                               proposed_contract_bytes=encoded(candidate)))
            wire = proposal.as_dict()
            alternative = adjudicate_answer(case, json.loads(wire["proposed_contract_utf8"]), answer, {})
            after = adjudicate_answer(case, json.loads(wire["parent_contract_utf8"]), answer, {})
            self.assertEqual(parent, preserved)
            self.assertEqual(before, after)
            self.assertEqual((after.I_contract, alternative.I_contract), (0, 1))
            self.assertEqual(alternative.evidence_scope, "TEST_VECTOR_ONLY")
            self.assertEqual(alternative.intent_confirmation, "UNKNOWN")
            self.assertEqual(wire["status"], "PROPOSED")

    def test_schema_declarations_and_representative_wire_shape(self):
        path = Path(__file__).resolve().parents[1] / "schemas" / "contract-proposal.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        props = schema["properties"]
        self.assertEqual(set(schema["required"]), WIRE)
        self.assertEqual(len(schema["required"]), 14)
        self.assertEqual(set(props), WIRE)
        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(props["status"]["const"], "PROPOSED")
        self.assertEqual(props["schema_version"]["const"], "pim-next.contract-proposal.v1")
        for key in ("original_problem_sha256", "parent_sha256", "proposed_sha256", "proposal_sha256"):
            self.assertEqual(props[key]["pattern"], "^[a-f0-9]{64}$")
        for key in ("case_id", "parent_version", "proposed_version"):
            self.assertEqual(props[key]["pattern"], "^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$")
        for key, maximum in (("original_problem_utf8", 65536), ("parent_contract_utf8", 131072),
                             ("proposed_contract_utf8", 131072), ("reason", 4096)):
            self.assertEqual((props[key]["minLength"], props[key]["maxLength"]), (1, maximum))
        refs = props["evidence_refs"]
        self.assertEqual((refs["minItems"], refs["maxItems"], refs["uniqueItems"]), (1, 16, True))
        self.assertEqual((refs["items"]["minLength"], refs["items"]["maxLength"]), (1, 2048))
        wire = propose_contract(**inputs()).as_dict()
        # Deliberately scoped assertions, not a generic Schema implementation.
        for key in WIRE - {"evidence_refs"}:
            self.assertIs(type(wire[key]), str)
            self.assertEqual(props[key]["type"], "string")
            if "pattern" in props[key]:
                self.assertIsNotNone(re.fullmatch(props[key]["pattern"], wire[key]))
            if "minLength" in props[key]:
                self.assertLessEqual(props[key]["minLength"], len(wire[key]))
                self.assertLessEqual(len(wire[key]), props[key]["maxLength"])
        self.assertEqual(refs["type"], "array")
        self.assertEqual(refs["items"]["type"], "string")
        self.assertEqual(len(set(wire["evidence_refs"])), len(wire["evidence_refs"]))
        for ref in wire["evidence_refs"]:
            self.assertIs(type(ref), str)
            self.assertLessEqual(1, len(ref))
            self.assertLessEqual(len(ref), 2048)


if __name__ == "__main__":
    unittest.main()
