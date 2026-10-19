"""Pure finite contract proposals; no approval, activation or IO."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from .contracts import ValidationError, strict_json_loads


_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}\Z")
_DECLARATION_FIELDS = frozenset(("case_id", "version", "omega", "acceptance_rule", "C_v", "V_v"))
_WIRE_FIELDS = frozenset((
    "schema_version", "status", "original_problem_utf8", "parent_contract_utf8",
    "proposed_contract_utf8", "original_problem_sha256", "parent_sha256",
    "proposed_sha256", "case_id", "parent_version", "proposed_version",
    "reason", "evidence_refs", "proposal_sha256",
))


def _source(raw: bytes, maximum: int, *, original: bool = False) -> str:
    if type(raw) is not bytes:
        raise ValidationError("INPUT_BYTES")
    if not 1 <= len(raw) <= maximum:
        raise ValidationError("INPUT_BOUNDS")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ValidationError("INPUT_ENCODING") from exc
    if text.startswith("\ufeff"):
        raise ValidationError("INPUT_ENCODING")
    if original and not text.strip():
        raise ValidationError("INPUT_BLANK")
    return text


def _identifier(value) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise ValidationError("DECLARATION_ID")
    return value


def _id_list(value, *, nonempty: bool = False) -> tuple[str, ...]:
    if type(value) is not list or len(value) > 512 or (nonempty and not value):
        raise ValidationError("DECLARATION_LIST")
    result = tuple(_identifier(item) for item in value)
    if len(set(result)) != len(result):
        raise ValidationError("DECLARATION_DUPLICATE")
    return result


def _declaration(text: str) -> dict:
    raw = strict_json_loads(text)
    if type(raw) is not dict or set(raw) != _DECLARATION_FIELDS:
        raise ValidationError("DECLARATION_FIELDS")
    _identifier(raw["case_id"])
    _identifier(raw["version"])
    omega = _id_list(raw["omega"], nonempty=True)
    if type(raw["acceptance_rule"]) is not str or raw["acceptance_rule"] not in (
            "ONE_WITNESS", "ALL_SOLUTIONS"):
        raise ValidationError("DECLARATION_RULE")
    c = _id_list(raw["C_v"])
    v = None if raw["V_v"] is None else _id_list(raw["V_v"])
    if not set(c) <= set(omega) or (v is not None and not set(v) <= set(omega)):
        raise ValidationError("DECLARATION_DOMAIN")
    return raw


def _metadata(value, maximum: int) -> str:
    if type(value) is not str or not value.strip() or len(value) > maximum:
        raise ValidationError("METADATA_TEXT")
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ValidationError("METADATA_ENCODING") from exc
    return value


def _sets(raw: dict):
    return (frozenset(raw["C_v"]),
            None if raw["V_v"] is None else frozenset(raw["V_v"]))


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class ContractProposal:
    original_problem_bytes: bytes
    parent_contract_bytes: bytes
    proposed_contract_bytes: bytes
    reason: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self):
        _source(self.original_problem_bytes, 65536, original=True)
        parent = _declaration(_source(self.parent_contract_bytes, 131072))
        proposed = _declaration(_source(self.proposed_contract_bytes, 131072))
        if any(parent[key] != proposed[key] for key in ("case_id", "omega", "acceptance_rule")):
            raise ValidationError("DECLARATION_MISMATCH")
        if parent["version"] == proposed["version"]:
            raise ValidationError("DECLARATION_VERSION")
        if _sets(parent) == _sets(proposed):
            raise ValidationError("DECLARATION_NOOP")
        _metadata(self.reason, 4096)
        if type(self.evidence_refs) is not tuple or not 1 <= len(self.evidence_refs) <= 16:
            raise ValidationError("EVIDENCE_REFS")
        for ref in self.evidence_refs:
            _metadata(ref, 2048)
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValidationError("EVIDENCE_REFS")

    def as_dict(self) -> dict:
        parent_text = self.parent_contract_bytes.decode("utf-8")
        proposed_text = self.proposed_contract_bytes.decode("utf-8")
        parent = strict_json_loads(parent_text)
        proposed = strict_json_loads(proposed_text)
        wire = {
            "schema_version": "pim-next.contract-proposal.v1", "status": "PROPOSED",
            "original_problem_utf8": self.original_problem_bytes.decode("utf-8"),
            "parent_contract_utf8": parent_text, "proposed_contract_utf8": proposed_text,
            "original_problem_sha256": _digest(self.original_problem_bytes),
            "parent_sha256": _digest(self.parent_contract_bytes),
            "proposed_sha256": _digest(self.proposed_contract_bytes),
            "case_id": parent["case_id"], "parent_version": parent["version"],
            "proposed_version": proposed["version"], "reason": self.reason,
            "evidence_refs": list(self.evidence_refs),
        }
        canonical = json.dumps(wire, sort_keys=True, ensure_ascii=False,
                               separators=(",", ":"), allow_nan=False).encode("utf-8")
        wire["proposal_sha256"] = _digest(canonical)
        return wire


def propose_contract(*, original_problem_bytes: bytes, parent_contract_bytes: bytes,
                     proposed_contract_bytes: bytes, reason: str,
                     evidence_refs: tuple[str, ...]) -> ContractProposal:
    return ContractProposal(original_problem_bytes=original_problem_bytes,
                            parent_contract_bytes=parent_contract_bytes,
                            proposed_contract_bytes=proposed_contract_bytes,
                            reason=reason, evidence_refs=evidence_refs)


def load_contract_proposal(raw: dict) -> ContractProposal:
    if type(raw) is not dict or set(raw) != _WIRE_FIELDS:
        raise ValidationError("WIRE_FIELDS")
    if any(type(raw[key]) is not str for key in _WIRE_FIELDS - {"evidence_refs"}):
        raise ValidationError("WIRE_TYPE")
    if type(raw["evidence_refs"]) is not list:
        raise ValidationError("WIRE_TYPE")
    if raw["status"] != "PROPOSED":
        raise ValidationError("WIRE_STATUS")
    try:
        original = raw["original_problem_utf8"].encode("utf-8", errors="strict")
        parent = raw["parent_contract_utf8"].encode("utf-8", errors="strict")
        proposed = raw["proposed_contract_utf8"].encode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ValidationError("INPUT_ENCODING") from exc
    proposal = propose_contract(original_problem_bytes=original, parent_contract_bytes=parent,
                                proposed_contract_bytes=proposed, reason=raw["reason"],
                                evidence_refs=tuple(raw["evidence_refs"]))
    if raw != proposal.as_dict():
        raise ValidationError("WIRE_BINDING")
    return proposal
