"""Synthetic finite counterexamples only; no human or provider experiment."""
import contextlib
import copy
from dataclasses import FrozenInstanceError
import io
import json
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from experiments.pim_next.pim_next.contracts import (
    AnswerEnvelope, ProviderResult, ReferenceSpec, ValidationError,
    load_answer, load_case_pack, load_provider_result, load_reference,
    public_payload, strict_json_loads,
)
from experiments.pim_next.pim_next.reference import adjudicate_answer
from experiments.pim_next.scripts.validate_case_pack import main


def case_raw():
    return {
        "case_id": "tv.case", "latent_id": "tv.latent", "family_id": "tv.family",
        "presentation_kind": "AMBIGUOUS", "original_text": "Public finite example.",
        "omega": ["a", "b", "c"], "theta_options": ["left", "right"],
        "theta_star": "left", "q_by_theta": {"left": ["a", "b"], "right": ["b", "c"]},
        "question_slots": ["domain"], "confirmation_required": False,
        "reference_revision": "tv.r1",
        "approval_source": {"status": "TEST_VECTOR", "source_ref": "synthetic:TV01"},
    }


def envelope(action="ANSWER", answers=("b",), branches=None, slot=None):
    return load_answer({"action": action, "answers": list(answers),
                        "conditional_branches": {} if branches is None else branches,
                        "question_slot": slot, "notes": ""})


def contract(rule="ONE_WITNESS", c=("a", "b", "c"), v=("a", "b", "c")):
    return {"case_id": "tv.case", "version": "tv.v1", "omega": ["a", "b", "c"],
            "acceptance_rule": rule, "C_v": list(c),
            "V_v": None if v is None else list(v)}


class ReferenceTests(unittest.TestCase):
    def score(self, response, declaration=None, raw=None, confirmation=None):
        return adjudicate_answer(load_reference(case_raw() if raw is None else raw),
                                 contract() if declaration is None else declaration,
                                 response, {} if confirmation is None else confirmation)

    def test_tv01_correct_answer_under_wrong_contract_fails_reference(self):
        result = self.score(envelope(answers=("c",)), contract(c=("c",), v=("c",)))
        self.assertEqual((result.I_contract, result.L_ref, result.C_claims), (1, "FAIL", "FAIL"))

    def test_tv02_true_conditional_branches_do_not_confirm_intent(self):
        raw = case_raw()
        raw["confirmation_required"] = True
        result = self.score(envelope("CONDITIONAL", (), {"left": ["a"], "right": ["c"]}),
                            contract(c=("a",), v=("a",)), raw,
                            {"evidence_kind": "TEST_VECTOR", "theta": "left"})
        self.assertEqual((result.I_contract, result.L_ref, result.C_claims), (0, "PASS", "PASS"))
        self.assertEqual(result.intent_confirmation, "UNKNOWN")
        self.assertEqual(result.evidence_scope, "TEST_VECTOR_ONLY")
        self.assertEqual(result.coverage["theta"], "FULL")

    def test_tv03_common_answer_can_avoid_clarification(self):
        result = self.score(envelope(answers=("b",)))
        self.assertEqual((result.I_contract, result.L_ref, result.C_claims), (1, "PASS", "PASS"))
        self.assertEqual(result.availability, "ANSWER")
        self.assertEqual(result.coverage["completeness"], "FAIL")
        self.assertEqual(result.intent_confirmation, "UNKNOWN")

    def test_tv04_no_observation_does_not_fabricate_verifier(self):
        result = self.score(None)
        self.assertEqual(result.I_contract, 0)
        self.assertEqual((result.availability, result.original_verifier_status),
                         ("NO_OBSERVATION", "NOT_RUN"))
        self.assertEqual(result.L_ref, "UNKNOWN")

    def test_tv05_unknown_and_no_answer_have_distinct_reasons(self):
        result = self.score(envelope(answers=()))
        self.assertEqual((result.availability, result.original_verifier_status), ("NO_ANSWER", "NOT_RUN"))
        self.assertEqual(result.I_contract, 0)
        self.assertNotEqual(result.reason_codes, self.score(None).reason_codes)

    def test_tv06_original_verifier_unknown_is_not_success(self):
        result = self.score(envelope(), contract(v=None))
        self.assertEqual((result.I_contract, result.original_contract_status,
                          result.original_verifier_status, result.L_ref), (0, "PASS", "UNKNOWN", "PASS"))

    def test_tv07_all_solutions_omission_fails(self):
        result = self.score(envelope(answers=("a",)), contract("ALL_SOLUTIONS", ("a", "b"), ("a", "b")))
        self.assertEqual((result.I_contract, result.L_ref, result.C_claims), (0, "FAIL", "FAIL"))
        self.assertEqual((result.coverage["soundness"], result.coverage["completeness"]), ("PASS", "FAIL"))

    def test_tv08_out_of_domain_claim_is_not_dropped(self):
        answer = envelope(answers=("outside",))
        result = self.score(answer)
        self.assertEqual(answer.answers, ("outside",))
        self.assertEqual((result.I_contract, result.L_ref, result.C_claims), (0, "FAIL", "FAIL"))
        self.assertIn("ANSWER_OUT_OF_DOMAIN", result.reason_codes)

    def test_tv09_false_and_unknown_conditional_claims_fail(self):
        for branches in ({"left": ["c"]}, {"unknown": ["b"]}):
            with self.subTest(branches=branches):
                result = self.score(envelope("CONDITIONAL", (), branches))
                self.assertEqual(result.C_claims, "FAIL")
        result = self.score(envelope("CONDITIONAL", (), {"right": ["c"]}))
        self.assertEqual((result.C_claims, result.L_ref, result.coverage["theta"]),
                         ("PASS", "UNKNOWN", "PARTIAL"))

    def test_tv10_pending_reference_and_forged_human_markers(self):
        raw = case_raw()
        raw["approval_source"]["status"] = "PENDING_HUMAN_CONFIRMATION"
        result = self.score(envelope(), raw=raw)
        self.assertEqual((result.I_contract, result.L_ref, result.C_claims), (1, "UNKNOWN", "UNKNOWN"))
        self.assertEqual((result.evidence_scope, result.intent_confirmation),
                         ("PENDING_HUMAN_REFERENCE", "UNKNOWN"))
        for status in ("HUMAN_CONFIRMED", "APPROVED"):
            raw["approval_source"]["status"] = status
            with self.assertRaises(ValidationError):
                load_reference(raw)
        with self.assertRaises(ValidationError):
            self.score(envelope(), confirmation={"status": "HUMAN_CONFIRMED"})

    def test_tv11_malformed_json_and_reference_domain_rejected(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":1e9999}', "{"):
            with self.subTest(text=text), self.assertRaises(ValidationError):
                strict_json_loads(text)
        for change in ({"q_by_theta": {"left": ["a"]}}, {"theta_star": "unknown"},
                       {"omega": ["a", "a"]}, {"q_by_theta": {"left": ["outside"], "right": []}},
                       {"omega": list(map(str, range(513)))},
                       {"theta_options": ["a", "b", "c", "d", "e"]},
                       {"question_slots": list(map(str, range(9)))},
                       {"confirmation_required": 1}, {"omega": "a"},
                       {"q_by_theta": {"left": ["a", "a"], "right": []}},
                       {"theta_options": ["left", "left"]}, {"omega": [" a"]}):
            raw = case_raw()
            raw.update(change)
            with self.subTest(change=change), self.assertRaises(ValidationError):
                load_reference(raw)

    def test_tv12_reference_fields_never_enter_public_payload(self):
        raw = case_raw()
        projected = public_payload(load_reference(raw))
        self.assertEqual(set(projected), {"case_id", "original_text", "question_slots", "answer_format"})
        for field in ("omega", "theta_star", "theta_options", "q_by_theta",
                      "approval_source", "latent_id", "family_id", "reference_revision"):
            self.assertNotIn(field, projected)
        projected["question_slots"].append("changed")
        self.assertEqual(load_reference(raw).question_slots, ("domain",))

    def test_true_partial_conditional_stays_true_without_full_fidelity(self):
        result = self.score(envelope("CONDITIONAL", (), {"left": ["a"]}),
                            contract(c=("c",), v=("c",)))
        self.assertEqual((result.I_contract, result.C_claims, result.L_ref), (0, "PASS", "PASS"))
        self.assertEqual(result.coverage["theta"], "PARTIAL")
        self.assertEqual(result.coverage["completeness"], "FAIL")

    def test_independent_original_contract_and_verifier_sets(self):
        for c, v, original, verifier in ((("b",), ("a",), "PASS", "FAIL"),
                                          (("a",), ("b",), "FAIL", "PASS")):
            result = self.score(envelope(), contract(c=c, v=v))
            self.assertEqual((result.I_contract, result.original_contract_status,
                              result.original_verifier_status), (0, original, verifier))

    def test_all_solutions_exact_and_empty_no_solution(self):
        result = self.score(envelope(answers=("b", "a")),
                            contract("ALL_SOLUTIONS", ("a", "b"), ("b", "a")))
        self.assertEqual((result.I_contract, result.L_ref), (1, "PASS"))
        raw = case_raw()
        raw["q_by_theta"] = {"left": [], "right": []}
        result = self.score(envelope(answers=()), contract("ALL_SOLUTIONS", (), ()), raw)
        self.assertEqual((result.I_contract, result.L_ref, result.availability), (1, "PASS", "ANSWER"))
        result = self.score(envelope(answers=()), contract("ALL_SOLUTIONS", ("a",), ("a",)))
        self.assertEqual((result.I_contract, result.L_ref), (0, "FAIL"))

    def test_duplicate_answers_fail_without_normalization(self):
        answer = envelope(answers=("b", "b"))
        result = self.score(answer)
        self.assertEqual(answer.answers, ("b", "b"))
        self.assertEqual((result.I_contract, result.C_claims, result.L_ref), (0, "FAIL", "FAIL"))
        self.assertIn("DUPLICATE_ANSWER_ID", result.reason_codes)

    def test_clarify_slot_and_abstain_are_separate(self):
        for response, available in ((envelope("CLARIFY", (), slot="domain"), "CLARIFY"),
                                    (envelope("CLARIFY", (), slot="secret"), "INVALID_CLARIFICATION"),
                                    (envelope("ABSTAIN", ()), "ABSTAIN")):
            result = self.score(response)
            self.assertEqual(result.availability, available)
            self.assertEqual(result.I_contract, 0)
            self.assertEqual(result.original_verifier_status, "NOT_RUN")

    def test_strict_answer_fields_types_and_bounds(self):
        base = {"action": "ANSWER", "answers": ["b"], "conditional_branches": {},
                "question_slot": None, "notes": ""}
        for change in ({"verifier_success": True}, {"domain_coverage": "partial"},
                       {"answers": "b"}, {"answers": [1]}, {"answers": [" b"]},
                       {"conditional_branches": []}, {"action": "PASS"},
                       {"question_slot": "domain"}, {"notes": "x" * 4097},
                       {"answers": ["a"] * 513}):
            raw = dict(base)
            raw.update(change)
            with self.subTest(change=list(change)), self.assertRaises(ValidationError):
                load_answer(raw)
        for action in ("CONDITIONAL", "CLARIFY", "ABSTAIN"):
            raw = dict(base, action=action)
            with self.assertRaises(ValidationError):
                load_answer(raw)
        raw = dict(base)
        del raw["notes"]
        with self.assertRaises(ValidationError):
            load_answer(raw)

    def test_immutable_snapshots_and_direct_construction_validation(self):
        raw = case_raw()
        case = load_reference(raw)
        raw["omega"].append("d")
        raw["q_by_theta"]["left"].clear()
        raw["approval_source"]["status"] = "APPROVED"
        self.assertEqual((case.omega, case.q_by_theta["left"], case.approval_source["status"]),
                         (("a", "b", "c"), ("a", "b"), "TEST_VECTOR"))
        with self.assertRaises(TypeError):
            case.q_by_theta["left"] = ()
        with self.assertRaises(FrozenInstanceError):
            case.theta_star = "right"
        with self.assertRaises(ValidationError):
            ReferenceSpec(**dict(case_raw(), confirmation_required="yes"))
        branches = {"left": ["a"]}
        answer = envelope("CONDITIONAL", (), branches)
        branches["left"].append("c")
        self.assertEqual(answer.conditional_branches["left"], ("a",))
        result = self.score(answer)
        with self.assertRaises(TypeError):
            result.coverage["theta"] = "FULL"

    def test_contract_cannot_mutate_domain_or_claim_verifier_pass(self):
        for change in ({"omega": ["a", "b"]}, {"case_id": "other"},
                       {"verifier_success": True}, {"V_v": "PASS"},
                       {"C_v": ["outside"]}, {"C_v": ["b", "b"]},
                       {"acceptance_rule": "partial"}, {"version": ""}):
            declaration = contract()
            declaration.update(change)
            with self.subTest(change=change), self.assertRaises(ValidationError):
                self.score(envelope(), declaration)

    def test_provider_no_observation_and_observed_no_answer_distinct(self):
        base = {"status": "NOT_RUN", "envelope": None, "request_id": None, "usage": None,
                "transport_error": None, "evidence_kind": "NOT_RUN"}
        unobserved = load_provider_result(base)
        observed = load_provider_result(dict(base, status="NO_ANSWER", evidence_kind="TEST_VECTOR"))
        self.assertNotEqual(unobserved.status, observed.status)
        self.assertNotEqual(unobserved.evidence_kind, observed.evidence_kind)
        for change in ({"request_id": "fake"}, {"status": "NO_ANSWER"},
                       {"usage": {"input_tokens": 1}}, {"envelope": {}}):
            with self.assertRaises(ValidationError):
                load_provider_result(dict(base, **change))
        ok = dict(base, status="OK", evidence_kind="TEST_VECTOR",
                  envelope={"action": "ANSWER", "answers": ["b"], "conditional_branches": {},
                            "question_slot": None, "notes": ""},
                  usage={"input_tokens": 2})
        loaded = load_provider_result(ok)
        ok["usage"]["input_tokens"] = 99
        self.assertEqual(loaded.usage["input_tokens"], 2)
        for usage in ({"input_tokens": True}, {"input_tokens": float("nan")}, {"usd": 1}):
            with self.assertRaises(ValidationError):
                load_provider_result(dict(ok, usage=usage))
        with self.assertRaises(ValidationError):
            ProviderResult("OK", None, None, None, None, "RAW_PROVIDER")

    def test_pack_duplicate_case_latent_and_pending_reference_rejected(self):
        first = case_raw()
        second = copy.deepcopy(first)
        for modify in ({}, {"case_id": "other"}, {"latent_id": "other"}):
            second = dict(copy.deepcopy(first), **modify)
            with self.assertRaises(ValidationError):
                load_case_pack({"evidence_kind": "TEST_VECTOR", "cases": [first, second]})
        for pack in ({"evidence_kind": "RAW_PROVIDER", "cases": [first]},
                     {"evidence_kind": "TEST_VECTOR", "cases": []},
                     {"evidence_kind": "TEST_VECTOR", "cases": [first] * 65}):
            with self.assertRaises(ValidationError):
                load_case_pack(pack)
        first["approval_source"]["status"] = "PENDING_HUMAN_CONFIRMATION"
        with self.assertRaises(ValidationError):
            load_case_pack({"evidence_kind": "TEST_VECTOR", "cases": [first]})

    def test_cli_in_process_valid_invalid_and_bounded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "case-pack.json"
            for payload, expected in ((json.dumps({"evidence_kind": "TEST_VECTOR",
                                                  "cases": [case_raw()]}).encode(), 0),
                                      (b'{"bad":true}', 2), (b"\xff", 2),
                                      (b" " * 1048577, 2)):
                path.write_bytes(payload)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = main(["--case-pack", str(path), "--mode", "test-vector"])
                self.assertEqual(code, expected)
                self.assertEqual(json.loads(output.getvalue())["evidence_scope"], "TEST_VECTOR_ONLY")

    def test_schema_fields_and_explicit_limit_contract(self):
        schema_root = Path(__file__).resolve().parents[1] / "schemas"
        case_schema = strict_json_loads((schema_root / "case.schema.json").read_text(encoding="utf-8"))
        answer_schema = strict_json_loads((schema_root / "answer.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(set(case_schema["required"]), set(case_raw()))
        self.assertFalse(case_schema["additionalProperties"])
        self.assertEqual(case_schema["properties"]["omega"]["maxItems"], 512)
        self.assertEqual(case_schema["properties"]["theta_options"]["maxItems"], 4)
        self.assertEqual(case_schema["properties"]["question_slots"]["maxItems"], 8)
        self.assertEqual(set(answer_schema["required"]),
                         {"action", "answers", "conditional_branches", "question_slot", "notes"})
        self.assertFalse(answer_schema["additionalProperties"])
        self.assertEqual(answer_schema["properties"]["action"]["enum"],
                         ["ANSWER", "CONDITIONAL", "CLARIFY", "ABSTAIN"])


    def test_cli_rejects_unsafe_windows_path_syntax_before_open(self):
        denied = (
            r"\\server\share\pack.json", "//server/share/pack.json",
            r"\\?\C:\pack.json", r"\\.\pipe\pim", "NUL", "NUL.json",
            r"C:\work\CON.txt", r"C:\work\CON .txt", r"C:\work\COM1.json",
            r"C:\work\LPT9.json", r"C:\pack.json:stream",
            "../pack.json", r"sub\..\pack.json",
            "bad\x00.json", "bad\n.json", "pack.json.", "pack.json ",
        )
        for name in denied:
            with self.subTest(path=name), \
                    mock.patch.object(Path, "open", side_effect=OSError("denied sentinel")) as opened, \
                    mock.patch.object(Path, "lstat", side_effect=OSError("metadata sentinel")) as metadata, \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["--case-pack", name, "--mode", "test-vector"]), 2)
                opened.assert_not_called()
                metadata.assert_not_called()

    def test_cli_rejects_remote_or_unknown_drive_before_metadata_and_open(self):
        for drive_type in (0, 1, 4):
            with self.subTest(drive_type=drive_type), \
                    mock.patch("ctypes.WinDLL") as library, \
                    mock.patch.object(Path, "open", side_effect=OSError("denied sentinel")) as opened, \
                    mock.patch.object(Path, "lstat", side_effect=OSError("metadata sentinel")) as metadata, \
                    contextlib.redirect_stdout(io.StringIO()):
                library.return_value.GetDriveTypeW.return_value = drive_type
                self.assertEqual(main(["--case-pack", r"C:\pim_fixture\pack.json",
                                       "--mode", "test-vector"]), 2)
                opened.assert_not_called()
                metadata.assert_not_called()

    def test_cli_rejects_reparse_symlink_nonregular_or_unknown_metadata_before_open(self):
        target = Path(r"C:\pim_fixture\pack.json")
        for unsafe_kind in ("reparse", "symlink", "nonregular", "unknown"):
            def metadata_for(path):
                if unsafe_kind == "unknown":
                    raise OSError("unknown metadata")
                if unsafe_kind == "reparse":
                    return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
                if unsafe_kind == "symlink":
                    return SimpleNamespace(st_mode=stat.S_IFLNK, st_file_attributes=0)
                mode = stat.S_IFIFO if path == target else stat.S_IFDIR
                return SimpleNamespace(st_mode=mode, st_file_attributes=0)

            with self.subTest(unsafe_kind=unsafe_kind), \
                    mock.patch("ctypes.WinDLL") as library, \
                    mock.patch.object(Path, "lstat", autospec=True, side_effect=metadata_for), \
                    mock.patch.object(Path, "open", side_effect=OSError("denied sentinel")) as opened, \
                    contextlib.redirect_stdout(io.StringIO()):
                library.return_value.GetDriveTypeW.return_value = 3
                self.assertEqual(main(["--case-pack", str(target), "--mode", "test-vector"]), 2)
                opened.assert_not_called()


if __name__ == "__main__":
    unittest.main()
