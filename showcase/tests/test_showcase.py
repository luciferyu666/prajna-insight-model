"""Real offline facade contracts; synthetic fixtures are not human validation."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import stat
from types import SimpleNamespace
import unittest
from unittest import mock


class ShowcaseTests(unittest.TestCase):
    def demo(self):
        from examples import run_showcase
        return run_showcase

    def invoke(self, module, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = module.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_wrong_contract_preserves_contract_pass_and_reference_fail(self):
        d = self.demo()
        r = d.run_case("wrong_contract")["adjudication"]
        self.assertEqual((r["I_contract"], r["L_ref"], r["C_claims"]), (1, "FAIL", "FAIL"))
        self.assertEqual((r["original_contract_status"], r["original_verifier_status"]), ("PASS", "PASS"))
        self.assertEqual((r["intent_confirmation"], r["evidence_scope"], r["budget_status"]),
                         ("UNKNOWN", "TEST_VECTOR_ONLY", "NOT_EVALUATED"))

    def test_conditional_domain_does_not_confirm_intent_or_switch_contract(self):
        d = self.demo()
        r = d.run_case("conditional_domain")["adjudication"]
        self.assertEqual((r["I_contract"], r["L_ref"], r["C_claims"]), (0, "PASS", "PASS"))
        self.assertEqual((r["original_contract_status"], r["original_verifier_status"]), ("FAIL", "FAIL"))
        self.assertEqual((r["coverage"]["theta"], r["coverage"]["soundness"],
                          r["coverage"]["completeness"]), ("FULL", "PASS", "PASS"))
        self.assertEqual(r["intent_confirmation"], "UNKNOWN")

    def test_unknown_verifier_never_becomes_contract_success(self):
        d = self.demo()
        r = d.run_case("unknown_verifier")["adjudication"]
        self.assertEqual((r["I_contract"], r["original_contract_status"],
                          r["original_verifier_status"], r["L_ref"]), (0, "PASS", "UNKNOWN", "PASS"))

    def test_proposal_roundtrip_preserves_original_parent_and_bytes(self):
        d = self.demo()
        source = d._load_fixture("proposal_only")
        r = d.run_case("proposal_only")
        self.assertEqual(set(r), {"case", "kind", "proposal", "parent_before", "parent_after", "parent_unchanged"})
        self.assertEqual(r["proposal"]["status"], "PROPOSED")
        self.assertTrue(r["parent_unchanged"])
        self.assertEqual(r["parent_before"], r["parent_after"])
        self.assertEqual(r["parent_before"]["L_ref"], "FAIL")
        for field, digest in (("original_problem_utf8", "original_problem_sha256"),
                              ("parent_contract_utf8", "parent_sha256"),
                              ("proposed_contract_utf8", "proposed_sha256")):
            self.assertEqual(r["proposal"][field], source[field])
            self.assertEqual(r["proposal"][digest], hashlib.sha256(source[field].encode("utf-8")).hexdigest())
        loaded = d.contract_versions.load_contract_proposal(r["proposal"])
        self.assertEqual(loaded.as_dict(), r["proposal"])

    def test_outputs_are_deterministic_and_json_safe(self):
        d = self.demo()
        a, b = d.run_all(), d.run_all()
        self.assertEqual(a, b)
        self.assertEqual(json.loads(json.dumps(a, allow_nan=False)), a)
        self.assertEqual([r["case"] for r in a], list(d.CASES))
        self.assertNotIn("timestamp", json.dumps(a))
        self.assertNotIn("worker_pid", json.dumps(a))

    def test_facade_calls_original_adjudication_and_proposal_apis(self):
        d = self.demo()
        with mock.patch.object(d.reference, "adjudicate_answer", wraps=d.reference.adjudicate_answer) as adjudicate, \
             mock.patch.object(d.contracts, "load_reference", wraps=d.contracts.load_reference) as load_ref, \
             mock.patch.object(d.contracts, "load_answer", wraps=d.contracts.load_answer) as load_ans, \
             mock.patch.object(d.contract_versions, "propose_contract", wraps=d.contract_versions.propose_contract) as propose, \
             mock.patch.object(d.contract_versions, "load_contract_proposal", wraps=d.contract_versions.load_contract_proposal) as loader:
            result = d.run_all()
        # The real loader revalidates through propose_contract, hence two real calls.
        self.assertEqual((adjudicate.call_count, load_ref.call_count, load_ans.call_count,
                          propose.call_count, loader.call_count), (5, 4, 4, 2, 1))
        self.assertEqual(result[0]["adjudication"]["L_ref"], "FAIL")
        self.assertEqual(result[3]["proposal"]["status"], "PROPOSED")

    def test_unknown_case_is_rejected_before_file_access(self):
        d = self.demo()
        with mock.patch.object(Path, "open", side_effect=AssertionError("unexpected open")) as opened, \
             mock.patch.object(Path, "lstat", side_effect=AssertionError("unexpected metadata")) as metadata:
            for bad in ("../wrong_contract", "other", "", None, True):
                with self.subTest(bad=bad), self.assertRaises(d.contracts.ValidationError):
                    d.run_case(bad)
            opened.assert_not_called()
            metadata.assert_not_called()
        for mode, flags in ((stat.S_IFLNK, 0), (stat.S_IFREG, 0x400), (stat.S_IFDIR, 0)):
            with self.subTest(mode=mode, flags=flags), \
                 mock.patch.object(Path, "lstat", return_value=SimpleNamespace(st_mode=mode, st_file_attributes=flags)), \
                 mock.patch.object(Path, "open", side_effect=AssertionError("unsafe open")) as opened, \
                 self.assertRaises(d.contracts.ValidationError):
                d._load_fixture("wrong_contract")
            opened.assert_not_called()

    def test_duplicate_nonfinite_and_malformed_fixture_json_are_rejected(self):
        d = self.demo()
        valid = d._load_fixture("wrong_contract")
        text = json.dumps(valid)
        duplicate = (text[:-1] + ', "schema_version": "pim.showcase.fixture.v1"}').encode("utf-8")
        with self.assertRaisesRegex(d.contracts.ValidationError, "^DUPLICATE_JSON_KEY$"):
            d._decode_fixture(duplicate)
        value = copy.deepcopy(valid)
        value["response"]["notes"] = "__NONFINITE__"
        template = json.dumps(value)
        for number in ("NaN", "Infinity", "1e9999"):
            raw = template.replace('"__NONFINITE__"', number).encode("utf-8")
            with self.subTest(number=number), self.assertRaisesRegex(
                    d.contracts.ValidationError, "^NONFINITE_JSON_NUMBER$"):
                d._decode_fixture(raw)
        with self.assertRaisesRegex(d.contracts.ValidationError, "^MALFORMED_JSON$"):
            d._decode_fixture(text[:-1].encode("utf-8"))

    def test_fixture_byte_bounds_utf8_and_bom_are_rejected(self):
        d = self.demo()
        valid = json.dumps(d._load_fixture("wrong_contract")).encode("utf-8")
        maximum = valid + b" " * (131072 - len(valid))
        self.assertEqual(d._decode_fixture(maximum), d._decode_fixture(valid))
        for raw in (b"", maximum + b" ", valid.decode("utf-8")):
            with self.subTest(kind=type(raw).__name__), self.assertRaisesRegex(
                    d.contracts.ValidationError, "^FIXTURE_BOUNDS$"):
                d._decode_fixture(raw)
        for raw in (b"\xff" + valid, b"\xef\xbb\xbf" + valid):
            with self.subTest(prefix=raw[:3]), self.assertRaisesRegex(
                    d.contracts.ValidationError, "^FIXTURE_ENCODING$"):
                d._decode_fixture(raw)

    def test_fixture_shape_cannot_request_adoption_or_success(self):
        d = self.demo()
        source = d._load_fixture("proposal_only")
        for extra in ({"adopt": True}, {"status": "APPROVED"}, {"verifier_success": True},
                      {"evidence_refs": "synthetic:bad"}, {"parent_contract_utf8": 7}):
            bad = dict(source, **extra)
            with self.subTest(extra=extra), self.assertRaises(d.contracts.ValidationError):
                d._decode_fixture(json.dumps(bad).encode("utf-8"))

    def test_forged_human_reference_marker_is_rejected(self):
        d = self.demo()
        source = d._load_fixture("wrong_contract")
        for status in ("HUMAN_CONFIRMED", "APPROVED", "PENDING_HUMAN_CONFIRMATION"):
            bad = copy.deepcopy(source)
            bad["reference"]["approval_source"]["status"] = status
            with self.subTest(status=status), mock.patch.object(d, "_load_fixture", return_value=bad), \
                 self.assertRaises(d.contracts.ValidationError):
                d.run_case("wrong_contract")
        for change in ({"source_ref": None}, {"source_ref": "human:unverified"}):
            bad = copy.deepcopy(source)
            bad["reference"]["approval_source"].update(change)
            with mock.patch.object(d, "_load_fixture", return_value=bad), self.assertRaises(d.contracts.ValidationError):
                d.run_case("wrong_contract")
        bad = copy.deepcopy(source)
        bad["reference"]["confirmation_required"] = False
        with mock.patch.object(d, "_load_fixture", return_value=bad), self.assertRaises(d.contracts.ValidationError):
            d.run_case("wrong_contract")

    def test_cli_json_all_and_single_have_actual_result_rows(self):
        d = self.demo()
        for case, expected in (("all", d.run_all()), ("unknown_verifier", [d.run_case("unknown_verifier")])):
            code, out, err = self.invoke(d, ["--case", case, "--format", "json"])
            self.assertEqual((code, err), (0, ""))
            self.assertEqual(json.loads(out), {"schema_version": "pim.showcase.run.v1", "results": expected})

    def test_cli_text_exposes_scope_unknown_and_proposed(self):
        d = self.demo()
        code, out, err = self.invoke(d, [])
        self.assertEqual((code, err), (0, ""))
        for token in (*d.CASES, "TEST_VECTOR_ONLY", "UNKNOWN", "PROPOSED", "NOT_EVALUATED", "FAIL"):
            self.assertIn(token, out)

    def test_cli_bad_arguments_have_exit_two_and_no_stdout(self):
        d = self.demo()
        for args in (["--case", "../secret"], ["--format", "xml"], ["--adopt"], ["--case"]):
            code, out, err = self.invoke(d, args)
            self.assertEqual((code, out), (2, ""))
            self.assertTrue(err)

    def test_cli_fixture_failure_is_atomic_and_returns_one(self):
        d = self.demo()
        original = d._load_fixture
        def with_bad_second(name):
            if name == "conditional_domain":
                return d._decode_fixture(b'{"kind": "ADJUDICATION", "forged": true}')
            return original(name)
        with mock.patch.object(d, "_load_fixture", side_effect=with_bad_second):
            code, out, err = self.invoke(d, ["--case", "all", "--format", "json"])
        self.assertEqual((code, out), (1, ""))
        self.assertIn("SHOWCASE_ERROR", err)

    def test_running_all_preserves_fixture_source_bytes(self):
        d = self.demo()
        paths = [d._fixture_path(name) for name in d.CASES]
        before = {p.name: p.read_bytes() for p in paths}
        d.run_all()
        self.assertEqual({p.name: p.read_bytes() for p in paths}, before)


if __name__ == "__main__":
    unittest.main()

