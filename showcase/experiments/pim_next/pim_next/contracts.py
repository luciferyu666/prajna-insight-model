"""Strict immutable finite contracts; no IO or provider operations."""
from __future__ import annotations

from dataclasses import dataclass, fields
import json
import math
import re
from types import MappingProxyType
from typing import Mapping

_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}\Z")


class ValidationError(ValueError):
    pass


def _object(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ValidationError("OBJECT_FIELDS")
    return value


def _text(value, maximum=4096, nonempty=False):
    if type(value) is not str or len(value) > maximum or (nonempty and not value):
        raise ValidationError("TEXT")
    return value


def _id(value):
    if type(value) is not str or not _ID.fullmatch(value):
        raise ValidationError("CANONICAL_ID")
    return value


def _enum(value, options):
    if type(value) is not str or value not in options:
        raise ValidationError("ENUM")
    return value


def _ids(value, maximum, unique=True, nonempty=False):
    if type(value) not in (list, tuple) or len(value) > maximum:
        raise ValidationError("IDS_TYPE_OR_BOUND")
    result = tuple(_id(item) for item in value)
    if (nonempty and not result) or (unique and len(set(result)) != len(result)):
        raise ValidationError("IDS_EMPTY_OR_DUPLICATE")
    return result


def _mapping(value):
    if not isinstance(value, Mapping):
        raise ValidationError("MAPPING")
    return dict(value)


@dataclass(frozen=True)
class ReferenceSpec:
    case_id: str
    latent_id: str
    family_id: str
    presentation_kind: str
    original_text: str
    omega: tuple[str, ...]
    theta_options: tuple[str, ...]
    theta_star: str
    q_by_theta: Mapping[str, tuple[str, ...]]
    question_slots: tuple[str, ...]
    confirmation_required: bool
    reference_revision: str
    approval_source: Mapping[str, object]

    def __post_init__(self):
        for name in ("case_id", "latent_id", "family_id", "reference_revision"):
            _id(getattr(self, name))
        _enum(self.presentation_kind, ("EXPLICIT", "AMBIGUOUS"))
        _text(self.original_text, 16384, True)
        omega = _ids(self.omega, 512, nonempty=True)
        theta = _ids(self.theta_options, 4, nonempty=True)
        slots = _ids(self.question_slots, 8)
        if _id(self.theta_star) not in theta or type(self.confirmation_required) is not bool:
            raise ValidationError("THETA_STAR_OR_CONFIRMATION_TYPE")
        source = _object(_mapping(self.approval_source), ("status", "source_ref"))
        _enum(source["status"], ("TEST_VECTOR", "PENDING_HUMAN_CONFIRMATION"))
        if source["source_ref"] is not None:
            _text(source["source_ref"], 4096, True)
        q = _mapping(self.q_by_theta)
        if set(q) != set(theta):
            raise ValidationError("INCOMPLETE_THETA_DOMAIN")
        q = {key: _ids(q[key], 512) for key in theta}
        if any(not set(value) <= set(omega) for value in q.values()):
            raise ValidationError("REFERENCE_OUT_OF_DOMAIN")
        for name, value in (("omega", omega), ("theta_options", theta),
                            ("question_slots", slots),
                            ("q_by_theta", MappingProxyType(q)),
                            ("approval_source", MappingProxyType(source))):
            object.__setattr__(self, name, value)


@dataclass(frozen=True)
class AnswerEnvelope:
    action: str
    answers: tuple[str, ...]
    conditional_branches: Mapping[str, tuple[str, ...]]
    question_slot: str | None
    notes: str

    def __post_init__(self):
        _enum(self.action, ("ANSWER", "CONDITIONAL", "CLARIFY", "ABSTAIN"))
        answers = _ids(self.answers, 512, unique=False)
        branches = _mapping(self.conditional_branches)
        if len(branches) > 4:
            raise ValidationError("BRANCH_BOUND")
        branches = {_id(key): _ids(value, 512, unique=False)
                    for key, value in branches.items()}
        if self.question_slot is not None:
            _id(self.question_slot)
        _text(self.notes)
        if self.action == "ANSWER" and (branches or self.question_slot is not None):
            raise ValidationError("ACTION_MIXTURE")
        if self.action == "CONDITIONAL" and (
                answers or not branches or self.question_slot is not None):
            raise ValidationError("ACTION_MIXTURE")
        if self.action == "CLARIFY" and (
                answers or branches or self.question_slot is None):
            raise ValidationError("ACTION_MIXTURE")
        if self.action == "ABSTAIN" and (
                answers or branches or self.question_slot is not None):
            raise ValidationError("ACTION_MIXTURE")
        object.__setattr__(self, "answers", answers)
        object.__setattr__(self, "conditional_branches", MappingProxyType(branches))


@dataclass(frozen=True)
class ProviderResult:
    status: str
    envelope: AnswerEnvelope | None
    request_id: str | None
    usage: Mapping[str, int] | None
    transport_error: str | None
    evidence_kind: str

    def __post_init__(self):
        _enum(self.status, ("OK", "NO_ANSWER", "ERROR", "NOT_RUN"))
        _enum(self.evidence_kind, ("RAW_PROVIDER", "TEST_VECTOR", "NOT_RUN"))
        if self.envelope is not None and type(self.envelope) is not AnswerEnvelope:
            raise ValidationError("ENVELOPE_TYPE")
        if self.request_id is not None:
            _text(self.request_id, 256, True)
        usage = None if self.usage is None else _mapping(self.usage)
        if usage is not None:
            if not set(usage) <= {"input_tokens", "output_tokens", "total_tokens"}:
                raise ValidationError("USAGE_FIELDS")
            if any(type(v) is not int or v < 0 or v > 10**12 for v in usage.values()):
                raise ValidationError("USAGE_VALUE")
        if self.transport_error is not None:
            _text(self.transport_error, 4096, True)
        if self.status == "NOT_RUN":
            if (self.evidence_kind != "NOT_RUN" or any(value is not None for value in
                    (self.envelope, self.request_id, usage, self.transport_error))):
                raise ValidationError("NOT_RUN_OBSERVATION")
        else:
            if self.evidence_kind == "NOT_RUN":
                raise ValidationError("OBSERVATION_EVIDENCE")
            if self.status == "OK" and (self.envelope is None or self.transport_error is not None):
                raise ValidationError("OK_SHAPE")
            if self.status == "NO_ANSWER" and (self.envelope is not None or self.transport_error is not None):
                raise ValidationError("NO_ANSWER_SHAPE")
            if self.status == "ERROR" and (self.envelope is not None or self.transport_error is None):
                raise ValidationError("ERROR_SHAPE")
        object.__setattr__(self, "usage", None if usage is None else MappingProxyType(usage))


@dataclass(frozen=True)
class AdjudicationResult:
    I_contract: int
    L_ref: str
    C_claims: str
    coverage: Mapping[str, str]
    intent_confirmation: str
    availability: str
    reason_codes: tuple[str, ...]
    original_contract_status: str
    original_verifier_status: str
    evidence_scope: str
    budget_status: str = "NOT_EVALUATED"

    def __post_init__(self):
        object.__setattr__(self, "coverage", MappingProxyType(dict(self.coverage)))
        object.__setattr__(self, "reason_codes", tuple(self.reason_codes))


def _wire_arrays(raw, names):
    for name in names:
        if type(raw[name]) is not list:
            raise ValidationError("WIRE_ARRAY")


def load_reference(raw: dict) -> ReferenceSpec:
    raw = _object(raw, (field.name for field in fields(ReferenceSpec)))
    _wire_arrays(raw, ("omega", "theta_options", "question_slots"))
    if type(raw["q_by_theta"]) is not dict or type(raw["approval_source"]) is not dict:
        raise ValidationError("WIRE_OBJECT")
    if any(type(v) is not list for v in raw["q_by_theta"].values()):
        raise ValidationError("WIRE_ARRAY")
    return ReferenceSpec(**raw)


def load_answer(raw: dict) -> AnswerEnvelope:
    raw = _object(raw, (field.name for field in fields(AnswerEnvelope)))
    _wire_arrays(raw, ("answers",))
    if type(raw["conditional_branches"]) is not dict:
        raise ValidationError("WIRE_OBJECT")
    if any(type(v) is not list for v in raw["conditional_branches"].values()):
        raise ValidationError("WIRE_ARRAY")
    return AnswerEnvelope(**raw)


def load_provider_result(raw: dict) -> ProviderResult:
    raw = dict(_object(raw, (field.name for field in fields(ProviderResult))))
    if raw["envelope"] is not None:
        raw["envelope"] = load_answer(raw["envelope"])
    if raw["usage"] is not None and type(raw["usage"]) is not dict:
        raise ValidationError("WIRE_OBJECT")
    return ProviderResult(**raw)


def strict_json_loads(text: str):
    _text(text, 1048576, True)

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValidationError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result

    def constant(value):
        raise ValidationError("NONFINITE_JSON_NUMBER")

    def number(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValidationError("NONFINITE_JSON_NUMBER")
        return parsed

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=constant,
                          parse_float=number)
    except ValidationError:
        raise
    except (ValueError, RecursionError) as exc:
        raise ValidationError("MALFORMED_JSON") from exc


def public_payload(case: ReferenceSpec) -> dict:
    if type(case) is not ReferenceSpec:
        raise ValidationError("REFERENCE_TYPE")
    return {
        "case_id": case.case_id,
        "original_text": case.original_text,
        "question_slots": list(case.question_slots),
        "answer_format": {
            "actions": ["ANSWER", "CONDITIONAL", "CLARIFY", "ABSTAIN"],
            "fields": ["action", "answers", "conditional_branches", "question_slot", "notes"],
        },
    }


def load_case_pack(raw: dict) -> tuple[ReferenceSpec, ...]:
    raw = _object(raw, ("evidence_kind", "cases"))
    if raw["evidence_kind"] != "TEST_VECTOR":
        raise ValidationError("TEST_VECTOR_PACK_REQUIRED")
    if type(raw["cases"]) is not list or not 1 <= len(raw["cases"]) <= 64:
        raise ValidationError("PACK_BOUND")
    cases = tuple(load_reference(value) for value in raw["cases"])
    if any(case.approval_source["status"] != "TEST_VECTOR" for case in cases):
        raise ValidationError("PACK_REFERENCE_SCOPE")
    if len({case.case_id for case in cases}) != len(cases):
        raise ValidationError("DUPLICATE_CASE")
    if len({case.latent_id for case in cases}) != len(cases):
        raise ValidationError("DUPLICATE_LATENT")
    return cases
