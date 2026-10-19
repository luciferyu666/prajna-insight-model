"""Synthetic structural examples only; no study bank or human approval."""
import ast
import copy
from dataclasses import FrozenInstanceError
import hashlib
import importlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from experiments.pim_next.pim_next.contracts import (
    ValidationError, load_answer, public_payload,
)
from experiments.pim_next.pim_next.reference import adjudicate_answer
from experiments.pim_next.pim_next.reference_bank import (
    ReferenceBank, load_reference_bank,
)

FAMILIES = ("DOMAIN", "UNITS", "ENDPOINT", "QUANTIFIER",
            "OPTIMALITY_TIES", "ALLOWED_OPERATIONS")


def encode(raw):
    return json.dumps(raw, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def bank_fixture():
    manifest = {
        "schema_version": "pim-next.reference-bank.v1", "bank_id": "bank-draft-v1",
        "reference_revision": "draft-v1", "evidence_kind": "DRAFT_REFERENCE_BANK",
        "review_status": "PENDING_HUMAN_CONFIRMATION", "entries": [],
    }
    payloads = {}
    for family in FAMILIES:
        for index, split in enumerate(("calibration", "development", "development")):
            latent = family.lower() + "-" + str(index)
            for kind in ("EXPLICIT", "AMBIGUOUS"):
                case_id = latent + "-" + kind.lower()
                raw = {
                    "case_id": case_id, "latent_id": latent, "family_id": family,
                    "presentation_kind": kind,
                    "original_text": "Synthetic " + kind + " " + latent,
                    "omega": ["a", "b", "c"], "theta_options": ["left", "right"],
                    "theta_star": "left",
                    "q_by_theta": {"left": ["a", "b"], "right": ["b", "c"]},
                    "question_slots": ["domain"],
                    "confirmation_required": kind == "AMBIGUOUS",
                    "reference_revision": "draft-v1",
                    "approval_source": {"status": "PENDING_HUMAN_CONFIRMATION",
                                        "source_ref": None},
                }
                path = split + "/" + case_id + ".json"
                payloads[path] = encode(raw)
                manifest["entries"].append({
                    "case_id": case_id, "latent_id": latent, "family_id": family,
                    "split": split, "presentation_kind": kind, "path": path,
                    "sha256": hashlib.sha256(payloads[path]).hexdigest(),
                })
    return manifest, payloads


def replace_bytes(manifest, payloads, index, value):
    entry = manifest["entries"][index]
    payloads[entry["path"]] = value
    entry["sha256"] = hashlib.sha256(value).hexdigest()


def change_case(manifest, payloads, index, **changes):
    raw = json.loads(payloads[manifest["entries"][index]["path"]])
    raw.update(changes)
    replace_bytes(manifest, payloads, index, encode(raw))


def move_split(manifest, payloads, index, split):
    entry = manifest["entries"][index]
    value = payloads.pop(entry["path"])
    entry["split"] = split
    entry["path"] = split + "/" + entry["case_id"] + ".json"
    payloads[entry["path"]] = value


class ReferenceBankTests(unittest.TestCase):
    def deny(self, manifest, payloads, code):
        with self.assertRaises(ValidationError) as caught:
            load_reference_bank(manifest, payloads)
        self.assertEqual(str(caught.exception), code)
        return caught.exception

    def test_valid_bank_counts_order_binding_and_determinism(self):
        manifest, payloads = bank_fixture()
        before = copy.deepcopy((manifest, payloads))
        bank = load_reference_bank(manifest, payloads)
        self.assertIsNotNone(bank)
        self.assertEqual(before, (manifest, payloads))
        self.assertEqual((bank.bank_id, bank.reference_revision), ("bank-draft-v1", "draft-v1"))
        self.assertEqual(bank.readiness, "PENDING_HUMAN_REFERENCE_REVIEW")
        self.assertEqual(len(bank.cases), 36)
        self.assertEqual(len({case.latent_id for case in bank.cases}), 18)
        self.assertEqual({case.family_id for case in bank.cases}, set(FAMILIES))
        for case, entry in zip(bank.cases, manifest["entries"]):
            self.assertEqual((case.case_id, case.latent_id, case.family_id,
                              case.presentation_kind, case.reference_revision),
                             (entry["case_id"], entry["latent_id"], entry["family_id"],
                              entry["presentation_kind"], manifest["reference_revision"]))
            self.assertEqual(bank.case_to_split[case.case_id], entry["split"])
        for split, count in (("calibration", 12), ("development", 24)):
            selected = tuple(case for case, entry in zip(bank.cases, manifest["entries"])
                             if entry["split"] == split)
            self.assertEqual(bank.public_cases(split), tuple(public_payload(c) for c in selected))
            self.assertEqual(len(bank.public_cases(split)), count)
        self.assertEqual(bank, load_reference_bank(manifest, payloads))
        manifest["entries"].reverse()
        self.assertEqual(tuple(c.case_id for c in load_reference_bank(manifest, payloads).cases),
                         tuple(e["case_id"] for e in manifest["entries"]))

    def test_exact_top_fields_ids_and_scope(self):
        for change, code in (({"extra": True}, "BANK_FIELDS"),
                             ({"bank_id": True}, "BANK_ID"),
                             ({"bank_id": "x\n"}, "BANK_ID"),
                             ({"reference_revision": 1}, "BANK_REVISION"),
                             ({"reference_revision": "x" * 65}, "BANK_REVISION"),
                             ({"schema_version": 1}, "BANK_SCOPE"),
                             ({"evidence_kind": "TEST_VECTOR"}, "BANK_SCOPE"),
                             ({"review_status": "APPROVED"}, "BANK_SCOPE")):
            manifest, payloads = bank_fixture()
            manifest.update(change)
            with self.subTest(change=change):
                self.deny(manifest, payloads, code)
        manifest, payloads = bank_fixture()
        del manifest["bank_id"]
        self.deny(manifest, payloads, "BANK_FIELDS")
        for manifest in ([], None, True):
            self.deny(manifest, {}, "BANK_FIELDS")

    def test_entry_shape_types_and_layout(self):
        for field, value in (("case_id", True), ("latent_id", 3), ("family_id", "UNKNOWN"),
                             ("split", "main"), ("presentation_kind", "explicit"),
                             ("sha256", "A" * 64), ("sha256", "0" * 63)):
            manifest, payloads = bank_fixture()
            manifest["entries"][0][field] = value
            with self.subTest(field=field, value=value):
                self.deny(manifest, payloads, "BANK_ENTRY_VALUE")
        for value in ([], None, {"extra": 1}):
            manifest, payloads = bank_fixture()
            manifest["entries"][0] = value
            self.deny(manifest, payloads, "BANK_ENTRY_FIELDS")
        manifest, payloads = bank_fixture()
        del manifest["entries"][0]["path"]
        self.deny(manifest, payloads, "BANK_ENTRY_FIELDS")
        for entries in (None, (), [], [None] * 35, [None] * 37):
            manifest, payloads = bank_fixture()
            manifest["entries"] = entries
            self.deny(manifest, payloads, "BANK_LAYOUT")
        manifest, payloads = bank_fixture()
        manifest["entries"][1] = dict(manifest["entries"][0])
        self.deny(manifest, payloads, "BANK_LAYOUT")

    def test_unsafe_and_noncanonical_paths(self):
        for path in (True, "/absolute.json", "https://example.invalid/a.json",
                     "//server/share/a.json", "\\\\?\\C:\\a.json", "calibration\\a.json",
                     "calibration/../a.json", "calibration/a.json:stream",
                     "calibration/a.JSON", "development/domain-0-explicit.json",
                     "calibration/other.json"):
            manifest, payloads = bank_fixture()
            manifest["entries"][0]["path"] = path
            with self.subTest(path=path):
                self.deny(manifest, payloads, "BANK_PATH")
        for case_id in ("NUL", "CON.txt", "COM1", "LPT9", "a:stream"):
            manifest, payloads = bank_fixture()
            entry = manifest["entries"][0]
            entry["case_id"] = case_id
            entry["path"] = "calibration/" + case_id + ".json"
            self.deny(manifest, payloads, "BANK_PATH")

    def test_payload_boundary_has_no_user_mapping_hooks(self):
        class Trap(dict):
            def __iter__(self):
                raise AssertionError("untrusted mapping hook")
        manifest, payloads = bank_fixture()
        self.deny(manifest, Trap(payloads), "BANK_PAYLOAD_KEYS")
        for mode in ("missing", "extra", "wrong_key"):
            manifest, payloads = bank_fixture()
            key = next(iter(payloads))
            if mode == "missing":
                payloads.pop(key)
            elif mode == "extra":
                payloads["extra.json"] = b"{}"
            else:
                payloads[1] = payloads.pop(key)
            self.deny(manifest, payloads, "BANK_PAYLOAD_KEYS")
        for value in ("{}", bytearray(b"{}"), memoryview(b"{}"), None, True):
            manifest, payloads = bank_fixture()
            payloads[next(iter(payloads))] = value
            self.deny(manifest, payloads, "BANK_PAYLOAD_TYPE")

    def test_byte_bounds_hash_and_utf8_precede_reference_parse(self):
        for value in (b"", b" " * 131073):
            manifest, payloads = bank_fixture()
            replace_bytes(manifest, payloads, 0, value)
            self.deny(manifest, payloads, "BANK_BYTE_BOUND")
        manifest, payloads = bank_fixture()
        for index in range(36):
            replace_bytes(manifest, payloads, index, b" " * 30000)
        self.deny(manifest, payloads, "BANK_BYTE_BOUND")
        manifest, payloads = bank_fixture()
        key = next(iter(payloads))
        payloads[key] += b" "
        self.deny(manifest, payloads, "BANK_HASH")
        manifest, payloads = bank_fixture()
        replace_bytes(manifest, payloads, 0, b"\xff")
        self.assertIsInstance(self.deny(manifest, payloads, "BANK_ENCODING").__cause__,
                              UnicodeDecodeError)
        manifest, payloads = bank_fixture()
        raw = payloads[next(iter(payloads))]
        replace_bytes(manifest, payloads, 0, raw + b" " * (131072 - len(raw)))
        self.assertEqual(len(load_reference_bank(manifest, payloads).cases), 36)

    def test_actual_strict_json_errors_and_reference_errors_propagate(self):
        for raw, code in ((b"{", "MALFORMED_JSON"),
                          (b'{"x":1,"x":2}', "DUPLICATE_JSON_KEY"),
                          (b'{"x":NaN}', "NONFINITE_JSON_NUMBER"),
                          (b'{"x":1e9999}', "NONFINITE_JSON_NUMBER")):
            manifest, payloads = bank_fixture()
            replace_bytes(manifest, payloads, 0, raw)
            error = self.deny(manifest, payloads, code)
            if code == "MALFORMED_JSON":
                self.assertIsNotNone(error.__cause__)
        for changes, code in (({"omega": "a"}, "WIRE_ARRAY"),
                              ({"omega": ["a"] * 513}, "IDS_TYPE_OR_BOUND"),
                              ({"theta_options": ["a", "b", "c", "d", "e"]}, "IDS_TYPE_OR_BOUND"),
                              ({"question_slots": ["s"] * 9}, "IDS_TYPE_OR_BOUND"),
                              ({"confirmation_required": 1}, "THETA_STAR_OR_CONFIRMATION_TYPE"),
                              ({"q_by_theta": {"left": ["a"]}}, "INCOMPLETE_THETA_DOMAIN"),
                              ({"q_by_theta": {"left": ["outside"], "right": []}}, "REFERENCE_OUT_OF_DOMAIN")):
            manifest, payloads = bank_fixture()
            change_case(manifest, payloads, 0, **changes)
            self.deny(manifest, payloads, code)

    def test_case_binding_and_draft_only_source(self):
        for field, value in (("case_id", "other"), ("latent_id", "other"),
                             ("family_id", "UNITS"), ("presentation_kind", "AMBIGUOUS"),
                             ("reference_revision", "other")):
            manifest, payloads = bank_fixture()
            change_case(manifest, payloads, 0, **{field: value})
            self.deny(manifest, payloads, "BANK_CASE_BINDING")
        for source in ({"status": "TEST_VECTOR", "source_ref": None},
                       {"status": "PENDING_HUMAN_CONFIRMATION", "source_ref": "copied:claim"}):
            manifest, payloads = bank_fixture()
            change_case(manifest, payloads, 0, approval_source=source)
            self.deny(manifest, payloads, "BANK_DRAFT_REQUIRED")
        manifest, payloads = bank_fixture()
        change_case(manifest, payloads, 0,
                    approval_source={"status": "APPROVED", "source_ref": None})
        self.deny(manifest, payloads, "ENUM")

    def test_pair_semantics_order_text_and_confirmation(self):
        for change in ({"omega": ["c", "b", "a"]},
                       {"theta_options": ["right", "left"]}, {"theta_star": "right"},
                       {"q_by_theta": {"left": ["b", "a"], "right": ["b", "c"]}},
                       {"question_slots": ["other"]}, {"confirmation_required": True}):
            manifest, payloads = bank_fixture()
            change_case(manifest, payloads, 0, **change)
            self.deny(manifest, payloads, "BANK_PAIR")
        manifest, payloads = bank_fixture()
        first = json.loads(payloads[manifest["entries"][0]["path"]])
        change_case(manifest, payloads, 1, original_text=first["original_text"])
        self.deny(manifest, payloads, "BANK_PAIR")
        manifest, payloads = bank_fixture()
        change_case(manifest, payloads, 1, confirmation_required=False)
        self.deny(manifest, payloads, "BANK_PAIR")

    def test_pair_members_family_and_split_counts(self):
        # Keeping 36 entries exposes one-member and three-member latent groups.
        manifest, payloads = bank_fixture()
        latent = manifest["entries"][0]["latent_id"]
        manifest["entries"][2]["latent_id"] = latent
        change_case(manifest, payloads, 2, latent_id=latent)
        self.deny(manifest, payloads, "BANK_PAIR")
        manifest, payloads = bank_fixture()
        manifest["entries"][1]["presentation_kind"] = "EXPLICIT"
        change_case(manifest, payloads, 1, presentation_kind="EXPLICIT")
        self.deny(manifest, payloads, "BANK_PAIR")
        manifest, payloads = bank_fixture()
        manifest["entries"][1]["family_id"] = "UNITS"
        change_case(manifest, payloads, 1, family_id="UNITS")
        self.deny(manifest, payloads, "BANK_PAIR")
        manifest, payloads = bank_fixture()
        move_split(manifest, payloads, 1, "development")
        self.deny(manifest, payloads, "BANK_SPLIT")
        manifest, payloads = bank_fixture()
        for index in (2, 3):
            move_split(manifest, payloads, index, "calibration")
        self.deny(manifest, payloads, "BANK_SPLIT")
        manifest, payloads = bank_fixture()
        for index in range(6):
            manifest["entries"][index]["family_id"] = "UNITS"
            change_case(manifest, payloads, index, family_id="UNITS")
        self.deny(manifest, payloads, "BANK_SPLIT")

    def test_projection_and_snapshot_isolation_constructor_limit(self):
        manifest, payloads = bank_fixture()
        bank = load_reference_bank(manifest, payloads)
        projected = bank.public_cases("calibration")
        self.assertEqual(set(projected[0]),
                         {"case_id", "original_text", "question_slots", "answer_format"})
        projected[0]["question_slots"].append("changed")
        projected[0]["answer_format"]["actions"].clear()
        self.assertEqual(bank.public_cases("calibration")[0], public_payload(bank.cases[0]))
        manifest["bank_id"] = "changed"
        manifest["entries"][0]["split"] = "development"
        payloads.clear()
        self.assertEqual(bank.bank_id, "bank-draft-v1")
        self.assertEqual(bank.case_to_split[bank.cases[0].case_id], "calibration")
        with self.assertRaises(FrozenInstanceError):
            bank.bank_id = "changed"
        with self.assertRaises(TypeError):
            bank.case_to_split[bank.cases[0].case_id] = "development"
        with self.assertRaises(TypeError):
            bank.cases[0].approval_source["status"] = "APPROVED"
        for split in ("main", True, None, []):
            with self.assertRaisesRegex(ValidationError, "^BANK_UNKNOWN_SPLIT$"):
                bank.public_cases(split)
        # Direct construction produces a snapshot, not validation/authentication evidence.
        direct = ReferenceBank("arbitrary", "arbitrary", (), {})
        self.assertEqual(direct.readiness, "PENDING_HUMAN_REFERENCE_REVIEW")
        self.assertFalse(hasattr(direct, "approved"))
        self.assertFalse(hasattr(direct, "study_ready"))

    def test_real_t01_pending_adjudication_stays_unknown(self):
        manifest, payloads = bank_fixture()
        bank = load_reference_bank(manifest, payloads)
        for case in bank.cases:
            self.assertEqual(dict(case.approval_source),
                             {"status": "PENDING_HUMAN_CONFIRMATION", "source_ref": None})
        case = bank.cases[0]
        answer = load_answer({"action": "ANSWER", "answers": ["a", "b"],
                              "conditional_branches": {}, "question_slot": None, "notes": ""})
        declaration = {"case_id": case.case_id, "version": "synthetic-v1",
                       "omega": list(case.omega), "acceptance_rule": "ALL_SOLUTIONS",
                       "C_v": ["a", "b"], "V_v": ["a", "b"]}
        result = adjudicate_answer(case, declaration, answer, {})
        self.assertEqual((result.I_contract, result.L_ref, result.C_claims,
                          result.intent_confirmation), (1, "UNKNOWN", "UNKNOWN", "UNKNOWN"))
        self.assertEqual(result.evidence_scope, "PENDING_HUMAN_REFERENCE")
        self.assertIn("HUMAN_REFERENCE_PENDING", result.reason_codes)

    def test_module_has_no_effectful_imports_or_loader_calls(self):
        module = importlib.import_module("experiments.pim_next.pim_next.reference_bank")
        source = Path(module.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module)
        self.assertLessEqual(imports, {"__future__", "dataclasses", "hashlib", "re",
                                      "types", "typing", "contracts"})
        forbidden = {"open", "exec", "eval", "compile", "__import__", "input"}
        self.assertFalse(any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                             and node.func.id in forbidden for node in ast.walk(tree)))
        manifest, payloads = bank_fixture()
        with patch("builtins.open", side_effect=AssertionError("file IO")), \
                patch("socket.socket", side_effect=AssertionError("network")), \
                patch("subprocess.Popen", side_effect=AssertionError("child")), \
                patch("os.system", side_effect=AssertionError("shell")):
            importlib.reload(module)
            self.assertEqual(len(module.load_reference_bank(manifest, payloads).cases), 36)

    def test_local_schema_matches_wire_and_has_no_refs(self):
        path = Path(__file__).resolve().parents[1] / "schemas/reference-bank.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        manifest, _ = bank_fixture()
        self.assertEqual(set(schema["required"]), set(manifest))
        self.assertEqual(set(schema["properties"]), set(manifest))
        self.assertFalse(schema["additionalProperties"])
        entries = schema["properties"]["entries"]
        self.assertEqual((entries["minItems"], entries["maxItems"]), (36, 36))
        entry = entries["items"]
        self.assertEqual(set(entry["required"]), set(manifest["entries"][0]))
        self.assertEqual(set(entry["properties"]), set(manifest["entries"][0]))
        self.assertFalse(entry["additionalProperties"])
        self.assertEqual(entry["properties"]["family_id"]["enum"], list(FAMILIES))
        def visit(value):
            if isinstance(value, dict):
                self.assertNotIn("$ref", value)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        visit(schema)


if __name__ == "__main__":
    unittest.main()
