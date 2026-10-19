"""Pure draft paired-reference validation; no IO, dispatch or approval proof."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re
from types import MappingProxyType
from typing import Mapping

from .contracts import (
    ReferenceSpec, ValidationError, load_reference, public_payload, strict_json_loads,
)

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}\Z")
_HASH = re.compile(r"[0-9a-f]{64}\Z")
_FAMILIES = ("DOMAIN", "UNITS", "ENDPOINT", "QUANTIFIER",
             "OPTIMALITY_TIES", "ALLOWED_OPERATIONS")
_SPLITS = ("calibration", "development")
_TOP = frozenset(("schema_version", "bank_id", "reference_revision", "evidence_kind",
                  "review_status", "entries"))
_ENTRY = frozenset(("case_id", "latent_id", "family_id", "split", "presentation_kind",
                    "path", "sha256"))
_DEVICES = frozenset(("CON", "PRN", "AUX", "NUL")) | frozenset(
    prefix + str(index) for prefix in ("COM", "LPT") for index in range(1, 10))
_PAIR_FIELDS = ("omega", "theta_options", "theta_star", "q_by_theta", "question_slots",
                "reference_revision", "approval_source")


def _require(condition, code):
    if not condition:
        raise ValidationError(code)


def _canonical_id(value):
    return type(value) is str and _ID.fullmatch(value) is not None


@dataclass(frozen=True)
class ReferenceBank:
    """Immutable snapshot; direct construction does not prove validation ran."""
    bank_id: str
    reference_revision: str
    cases: tuple[ReferenceSpec, ...]
    case_to_split: Mapping[str, str]
    readiness: str = field(default="PENDING_HUMAN_REFERENCE_REVIEW", init=False)

    def __post_init__(self):
        object.__setattr__(self, "cases", tuple(self.cases))
        object.__setattr__(self, "case_to_split", MappingProxyType(dict(self.case_to_split)))

    def public_cases(self, split: str) -> tuple[dict, ...]:
        _require(type(split) is str and split in _SPLITS, "BANK_UNKNOWN_SPLIT")
        return tuple(public_payload(case) for case in self.cases
                     if self.case_to_split[case.case_id] == split)


def _entries(manifest):
    values = manifest["entries"]
    _require(type(values) is list and len(values) == 36, "BANK_LAYOUT")
    ids, paths = set(), set()
    for entry in values:
        _require(type(entry) is dict and all(type(key) is str for key in entry)
                 and set(entry) == _ENTRY, "BANK_ENTRY_FIELDS")
        _require(all(_canonical_id(entry[key]) for key in ("case_id", "latent_id")),
                 "BANK_ENTRY_VALUE")
        _require(type(entry["family_id"]) is str and entry["family_id"] in _FAMILIES
                 and type(entry["split"]) is str and entry["split"] in _SPLITS
                 and type(entry["presentation_kind"]) is str
                 and entry["presentation_kind"] in ("EXPLICIT", "AMBIGUOUS")
                 and type(entry["sha256"]) is str and _HASH.fullmatch(entry["sha256"]) is not None,
                 "BANK_ENTRY_VALUE")
        case_id, path = entry["case_id"], entry["path"]
        _require(type(path) is str and path == entry["split"] + "/" + case_id + ".json"
                 and ":" not in path and case_id.split(".", 1)[0].upper() not in _DEVICES,
                 "BANK_PATH")
        _require(case_id not in ids and path not in paths, "BANK_LAYOUT")
        ids.add(case_id)
        paths.add(path)
    return values, paths


def _payloads(entries, paths, payloads):
    _require(type(payloads) is dict and all(type(key) is str for key in payloads)
             and set(payloads) == paths, "BANK_PAYLOAD_KEYS")
    _require(all(type(value) is bytes for value in payloads.values()), "BANK_PAYLOAD_TYPE")
    _require(all(1 <= len(value) <= 131072 for value in payloads.values())
             and sum(len(value) for value in payloads.values()) <= 1048576,
             "BANK_BYTE_BOUND")
    for entry in entries:
        _require(hashlib.sha256(payloads[entry["path"]]).hexdigest() == entry["sha256"],
                 "BANK_HASH")


def _cases(entries, revision, payloads):
    cases = []
    for entry in entries:
        try:
            text = payloads[entry["path"]].decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ValidationError("BANK_ENCODING") from exc
        # T01 parse/reference category codes and their existing causes propagate.
        case = load_reference(strict_json_loads(text))
        _require(all(getattr(case, key) == entry[key] for key in
                     ("case_id", "latent_id", "family_id", "presentation_kind"))
                 and case.reference_revision == revision, "BANK_CASE_BINDING")
        _require(case.approval_source["status"] == "PENDING_HUMAN_CONFIRMATION"
                 and case.approval_source["source_ref"] is None, "BANK_DRAFT_REQUIRED")
        cases.append(case)
    return tuple(cases)


def _pairs(cases, entries):
    groups = {}
    for case, entry in zip(cases, entries):
        groups.setdefault(case.latent_id, []).append((case, entry["split"]))
    _require(len(groups) == 18, "BANK_PAIR")
    counts = {family: {split: 0 for split in _SPLITS} for family in _FAMILIES}
    for members in groups.values():
        _require(len(members) == 2, "BANK_PAIR")
        (left, left_split), (right, right_split) = members
        _require(left.family_id == right.family_id
                 and {left.presentation_kind, right.presentation_kind} == {"EXPLICIT", "AMBIGUOUS"},
                 "BANK_PAIR")
        _require(left_split == right_split, "BANK_SPLIT")
        _require(all(getattr(left, key) == getattr(right, key) for key in _PAIR_FIELDS)
                 and left.original_text != right.original_text
                 and left.confirmation_required == (left.presentation_kind == "AMBIGUOUS")
                 and right.confirmation_required == (right.presentation_kind == "AMBIGUOUS"),
                 "BANK_PAIR")
        counts[left.family_id][left_split] += 1
    _require(all(value == {"calibration": 1, "development": 2}
                 for value in counts.values()), "BANK_SPLIT")


def load_reference_bank(manifest: dict, case_payloads: Mapping[str, bytes]) -> ReferenceBank:
    """Validate supplied draft bytes without opening paths or authenticating people."""
    _require(type(manifest) is dict and all(type(key) is str for key in manifest)
             and set(manifest) == _TOP, "BANK_FIELDS")
    _require(_canonical_id(manifest["bank_id"]), "BANK_ID")
    _require(_canonical_id(manifest["reference_revision"]), "BANK_REVISION")
    _require(type(manifest["schema_version"]) is str
             and manifest["schema_version"] == "pim-next.reference-bank.v1"
             and type(manifest["evidence_kind"]) is str
             and manifest["evidence_kind"] == "DRAFT_REFERENCE_BANK"
             and type(manifest["review_status"]) is str
             and manifest["review_status"] == "PENDING_HUMAN_CONFIRMATION", "BANK_SCOPE")
    entries, paths = _entries(manifest)
    _payloads(entries, paths, case_payloads)
    cases = _cases(entries, manifest["reference_revision"], case_payloads)
    _pairs(cases, entries)
    return ReferenceBank(manifest["bank_id"], manifest["reference_revision"], cases,
                         {entry["case_id"]: entry["split"] for entry in entries})
