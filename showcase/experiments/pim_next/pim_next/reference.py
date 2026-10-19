"""Independent exhaustive finite comparisons; no natural-language oracle."""
from __future__ import annotations

from .contracts import (
    AdjudicationResult, AnswerEnvelope, ReferenceSpec, ValidationError,
    _enum, _id, _ids, _object,
)


def _contract(case, declaration):
    raw = _object(declaration, ("case_id", "version", "omega", "acceptance_rule", "C_v", "V_v"))
    if _id(raw["case_id"]) != case.case_id:
        raise ValidationError("CONTRACT_CASE_MISMATCH")
    _id(raw["version"])
    if type(raw["omega"]) is not list or tuple(raw["omega"]) != case.omega:
        raise ValidationError("CONTRACT_DOMAIN_MISMATCH")
    rule = _enum(raw["acceptance_rule"], ("ONE_WITNESS", "ALL_SOLUTIONS"))
    for key in ("C_v", "V_v"):
        if raw[key] is not None and type(raw[key]) is not list:
            raise ValidationError("CONTRACT_SET_TYPE")
    if raw["C_v"] is None:
        raise ValidationError("CONTRACT_SET_REQUIRED")
    c = frozenset(_ids(raw["C_v"], 512))
    v = None if raw["V_v"] is None else frozenset(_ids(raw["V_v"], 512))
    if not c <= set(case.omega) or (v is not None and not v <= set(case.omega)):
        raise ValidationError("CONTRACT_OUT_OF_DOMAIN")
    return rule, c, v


def _valid_ids(values, omega):
    return len(values) == len(set(values)) and set(values) <= set(omega)


def _accept(values, target, rule, omega):
    if not _valid_ids(values, omega):
        return False
    value_set = set(values)
    if rule == "ONE_WITNESS":
        return bool(value_set) and value_set <= target
    return value_set == target


def _status(values, target, rule, omega):
    if target is None:
        return "UNKNOWN"
    return "PASS" if all(_accept(value, target, rule, omega) for value in values) else "FAIL"


def adjudicate_answer(case: ReferenceSpec, contract_version: dict,
                      response: AnswerEnvelope | None, confirmation: dict) -> AdjudicationResult:
    if type(case) is not ReferenceSpec:
        raise ValidationError("REFERENCE_TYPE")
    if response is not None and type(response) is not AnswerEnvelope:
        raise ValidationError("ENVELOPE_TYPE")
    rule, original_c, original_v = _contract(case, contract_version)
    if type(confirmation) is not dict:
        raise ValidationError("CONFIRMATION_TYPE")
    if confirmation:
        _object(confirmation, ("evidence_kind", "theta"))
        if confirmation["evidence_kind"] != "TEST_VECTOR" or _id(confirmation["theta"]) not in case.theta_options:
            raise ValidationError("UNSUPPORTED_CONFIRMATION")
    scope = ("TEST_VECTOR_ONLY" if case.approval_source["status"] == "TEST_VECTOR"
             else "PENDING_HUMAN_REFERENCE")
    coverage = {"scope": "ANSWER_CLAIM_SET", "domain": "FULL_DECLARED_FINITE_DOMAIN", "theta": "NONE",
                "soundness": "UNKNOWN", "completeness": "UNKNOWN"}

    def result(i=0, l="UNKNOWN", claims="UNKNOWN", available="ANSWER", reasons=(),
               original="NOT_RUN", verifier="NOT_RUN"):
        return AdjudicationResult(i, l, claims, coverage, "UNKNOWN", available,
                                  tuple(reasons), original, verifier, scope)

    if response is None:
        return result(available="NO_OBSERVATION", reasons=("NO_OBSERVATION",))
    if response.action == "ABSTAIN":
        return result(available="ABSTAIN", reasons=("ABSTAIN",))
    if response.action == "CLARIFY":
        valid = response.question_slot in case.question_slots
        return result(available="CLARIFY" if valid else "INVALID_CLARIFICATION",
                      reasons=("VALID_PUBLIC_SLOT" if valid else "INVALID_PUBLIC_SLOT",))
    if response.action == "ANSWER" and not response.answers and rule == "ONE_WITNESS":
        return result(available="NO_ANSWER", reasons=("NO_ANSWER",))

    if response.action == "ANSWER":
        pairs = [(case.theta_star, response.answers)]
        coverage["theta"] = "FULL" if len(case.theta_options) == 1 else "PARTIAL"
        star_values = response.answers
    else:
        pairs = list(response.conditional_branches.items())
        coverage["theta"] = ("FULL" if set(response.conditional_branches) == set(case.theta_options)
                             else "PARTIAL")
        star_values = response.conditional_branches.get(case.theta_star)
    unknown_branch = any(theta not in case.theta_options for theta, _ in pairs)
    values = [value for _, value in pairs]
    original = _status(values, original_c, rule, case.omega)
    verifier = _status(values, original_v, rule, case.omega)
    if unknown_branch:
        original = "FAIL"
        if original_v is not None:
            verifier = "FAIL"
    i = int(original == verifier == "PASS")
    reasons = []
    if unknown_branch:
        reasons.append("UNKNOWN_THETA_BRANCH")
    if any(len(value) != len(set(value)) for value in values):
        reasons.append("DUPLICATE_ANSWER_ID")
    if any(not set(value) <= set(case.omega) for value in values):
        reasons.append("ANSWER_OUT_OF_DOMAIN")
    if original == "FAIL":
        reasons.append("ORIGINAL_CONTRACT_REJECTED")
    if verifier != "PASS":
        reasons.append("ORIGINAL_VERIFIER_" + verifier)
    if coverage["theta"] == "PARTIAL":
        reasons.append("PARTIAL_THETA_COVERAGE")
    if scope == "PENDING_HUMAN_REFERENCE":
        reasons.append("HUMAN_REFERENCE_PENDING")
        return result(i, available=response.action, reasons=reasons, original=original, verifier=verifier)

    sound = not unknown_branch and all(
        _valid_ids(value, case.omega) and set(value) <= set(case.q_by_theta[theta])
        for theta, value in pairs)
    complete = not unknown_branch and all(
        set(case.q_by_theta[theta]) <= set(value) for theta, value in pairs)
    coverage["soundness"] = "PASS" if sound else "FAIL"
    coverage["completeness"] = "PASS" if complete else "FAIL"
    claims = "PASS" if not unknown_branch and all(
        _accept(value, set(case.q_by_theta[theta]), rule, case.omega)
        for theta, value in pairs) else "FAIL"
    if star_values is None:
        l = "UNKNOWN"
        reasons.append("THETA_STAR_NOT_COVERED")
    else:
        l = "PASS" if _accept(star_values, set(case.q_by_theta[case.theta_star]),
                              rule, case.omega) else "FAIL"
    if claims == "FAIL":
        reasons.append("REFERENCE_CLAIMS_REJECTED")
    if l == "FAIL":
        reasons.append("REFERENCE_ANSWER_REJECTED")
    reasons.append("TEST_VECTOR_FINITE_CHECK")
    if case.confirmation_required:
        reasons.append("HUMAN_INTENT_UNCONFIRMED")
    return result(i, l, claims, response.action, reasons, original, verifier)
