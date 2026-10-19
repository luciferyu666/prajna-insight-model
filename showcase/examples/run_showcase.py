"""Offline synthetic illustrations over original finite APIs; no solver or provider."""
from __future__ import annotations

import argparse
from dataclasses import fields
import hashlib
import json
from pathlib import Path
import stat
import sys

from experiments.pim_next.pim_next import contracts, reference, contract_versions

CASES = ("wrong_contract", "conditional_domain", "unknown_verifier", "proposal_only")
_LIMIT = 131072
_ADJ_FIELDS = frozenset(("schema_version", "kind", "reference", "contract", "response"))
_PROP_FIELDS = frozenset(("schema_version", "kind", "reference", "response",
                         "original_problem_utf8", "parent_contract_utf8",
                         "proposed_contract_utf8", "reason", "evidence_refs"))


def _shape(raw):
    if type(raw) is not dict or raw.get("schema_version") != "pim.showcase.fixture.v1":
        raise contracts.ValidationError("FIXTURE_VERSION")
    kind = raw.get("kind")
    expected = _ADJ_FIELDS if kind == "ADJUDICATION" else _PROP_FIELDS if kind == "PROPOSAL" else None
    if expected is None or set(raw) != expected:
        raise contracts.ValidationError("FIXTURE_FIELDS")
    if kind == "PROPOSAL" and (any(type(raw[key]) is not str for key in (
            "original_problem_utf8", "parent_contract_utf8", "proposed_contract_utf8", "reason"))
            or type(raw["evidence_refs"]) is not list):
        raise contracts.ValidationError("FIXTURE_TYPES")
    return raw


def _decode_fixture(raw: bytes):
    if type(raw) is not bytes or not 1 <= len(raw) <= _LIMIT:
        raise contracts.ValidationError("FIXTURE_BOUNDS")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise contracts.ValidationError("FIXTURE_ENCODING") from exc
    if text.startswith("\ufeff"):
        raise contracts.ValidationError("FIXTURE_ENCODING")
    return _shape(contracts.strict_json_loads(text))


def _fixture_path(name):
    if type(name) is not str or name not in CASES:
        raise contracts.ValidationError("FIXTURE_NAME")
    return Path(__file__).absolute().parent / "fixtures" / (name + ".json")


def _load_fixture(name):
    path = _fixture_path(name)
    for entry in (path, *path.parents):
        info = entry.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise contracts.ValidationError("FIXTURE_PATH")
        if entry == path and not stat.S_ISREG(info.st_mode):
            raise contracts.ValidationError("FIXTURE_PATH")
        if entry != path and not stat.S_ISDIR(info.st_mode):
            raise contracts.ValidationError("FIXTURE_PATH")
    with path.open("rb") as stream:
        raw = stream.read(_LIMIT + 1)
    return _decode_fixture(raw)


def _serialize(result):
    data = {f.name: getattr(result, f.name) for f in fields(contracts.AdjudicationResult)}
    data["coverage"] = dict(result.coverage)
    data["reason_codes"] = list(result.reason_codes)
    return data


def run_case(case_name: str) -> dict:
    raw = _shape(_load_fixture(case_name))
    case = contracts.load_reference(raw["reference"])
    source = case.approval_source
    if (source["status"] != "TEST_VECTOR" or not isinstance(source["source_ref"], str)
            or not source["source_ref"].startswith("synthetic:") or case.confirmation_required is not True):
        raise contracts.ValidationError("FIXTURE_SCOPE")
    response = contracts.load_answer(raw["response"])
    if raw["kind"] == "ADJUDICATION":
        result = reference.adjudicate_answer(case, raw["contract"], response, {})
        return {"case": case_name, "kind": "ADJUDICATION", "adjudication": _serialize(result)}

    if raw["original_problem_utf8"] != case.original_text:
        raise contracts.ValidationError("FIXTURE_ORIGINAL")
    original = raw["original_problem_utf8"].encode("utf-8", errors="strict")
    parent = raw["parent_contract_utf8"].encode("utf-8", errors="strict")
    proposed = raw["proposed_contract_utf8"].encode("utf-8", errors="strict")
    declaration = contracts.strict_json_loads(parent.decode("utf-8"))
    before = _serialize(reference.adjudicate_answer(case, declaration, response, {}))
    digest = hashlib.sha256(parent).hexdigest()
    proposal = contract_versions.propose_contract(
        original_problem_bytes=original, parent_contract_bytes=parent,
        proposed_contract_bytes=proposed, reason=raw["reason"],
        evidence_refs=tuple(raw["evidence_refs"]))
    wire = proposal.as_dict()
    checked = contract_versions.load_contract_proposal(wire)
    after = _serialize(reference.adjudicate_answer(case, declaration, response, {}))
    unchanged = (before == after and checked.parent_contract_bytes == parent
                 and wire["parent_sha256"] == digest and checked.as_dict() == wire)
    if not unchanged:
        raise contracts.ValidationError("PARENT_PRESERVATION")
    return {"case": case_name, "kind": "PROPOSAL", "proposal": wire,
            "parent_before": before, "parent_after": after, "parent_unchanged": unchanged}


def run_all() -> list[dict]:
    return [run_case(name) for name in CASES]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Offline synthetic PIM API tour; no human intent validation.")
    parser.add_argument("--case", choices=(*CASES, "all"), default="all")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)
    try:
        rows = run_all() if args.case == "all" else [run_case(args.case)]
        payload = {"schema_version": "pim.showcase.run.v1", "results": rows}
        if args.format == "json":
            output = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        else:
            output = ("PIM offline showcase: synthetic evidence; execution is not Task PASS.\n"
                      + json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False))
    except (contracts.ValidationError, OSError, UnicodeError, ValueError) as exc:
        detail = str(exc) if isinstance(exc, contracts.ValidationError) else type(exc).__name__
        print("SHOWCASE_ERROR: " + detail, file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

