"""Pure offline structural consistency checks under trusted caller observations.

An allowed result is neither actor authentication nor a dispatch token.
"""
from dataclasses import dataclass
import hashlib
import json
import re
from types import MappingProxyType
from typing import Mapping

SOURCE_PREFIX = "experiments/pim_next/"
EVIDENCE_PREFIX = "reports/development/pim-next/IW-00/Attempt-01/"
OUTPUT_PREFIX = EVIDENCE_PREFIX + "outputs/"
BUDGET_KEYS = frozenset(("python_pids", "worker_pids", "api_calls", "api_micro_usd", "retry_cycles"))
MANIFEST_KEYS = frozenset(("schema_version", "work_package_id", "source_revision", "runtime", "mode", "provider", "approval_id", "source_hashes", "roots", "budgets"))
APPROVAL_KEYS = frozenset(("approval_id", "status", "source", "revision", "content_sha256", "scope_hash"))
IDENTITY_KEYS = (APPROVAL_KEYS - {"status"}) | {"trusted_human"}
MODES = frozenset(("offline", "worker_diagnostic", "api_calibration", "api_pilot"))


@dataclass(frozen=True)
class LaunchGateResult:
    allowed: bool
    reason_codes: tuple[str, ...]
    scope_hash: str
    remaining_budget: Mapping[str, int]

    def as_dict(self) -> dict:
        return {"allowed": self.allowed, "reason_codes": list(self.reason_codes),
                "scope_hash": self.scope_hash, "remaining_budget": dict(self.remaining_budget)}


def _object(value, keys) -> bool:
    return type(value) is dict and set(value) == set(keys)


def _text(value) -> bool:
    return type(value) is str and bool(value)


def _digest(value) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _identifier(value) -> bool:
    return type(value) is str and re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value) is not None


def _path(value, prefix) -> bool:
    if type(value) is not str or not value.startswith(prefix) or len(value) <= len(prefix):
        return False
    for part in value.split("/"):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", part) or part in (".", "..") or part.endswith("."):
            return False
        lower = part.lower()
        stem = lower.split(".")[0]
        if stem in {"con", "prn", "aux", "nul"} or re.fullmatch(r"(?:com|lpt)[1-9]", stem):
            return False
        if "secret" in lower or "credential" in lower or lower.startswith(".env") or lower.endswith((".pem", ".key")):
            return False
    return True


def _sources(value) -> bool:
    return (type(value) is dict and 1 <= len(value) <= 128
            and all(_path(path, SOURCE_PREFIX) and _digest(digest) for path, digest in value.items())
            and len({path.casefold() for path in value}) == len(value))


def _budget(value) -> bool:
    return _object(value, BUDGET_KEYS) and all(type(item) is int and item >= 0 for item in value.values())


def _manifest(value) -> bool:
    if not _object(value, MANIFEST_KEYS):
        return False
    if not all(type(value[key]) is str for key in ("schema_version", "work_package_id", "source_revision", "runtime")):
        return False
    if (value["schema_version"] != "1" or value["work_package_id"] != "PIM-NEXT-IW-00"
            or value["source_revision"] != "IW-00-v1" or value["runtime"] != "bundled_python_3_12"):
        return False
    if (type(value["mode"]) is not str or value["mode"] not in MODES
            or not _text(value["provider"]) or not _identifier(value["approval_id"])
            or not _sources(value["source_hashes"])):
        return False
    roots, budgets = value["roots"], value["budgets"]
    return (_object(roots, ("cases", "tasks", "prompts", "output"))
            and all(_path(roots[key], SOURCE_PREFIX) for key in ("cases", "tasks", "prompts"))
            and _path(roots["output"], OUTPUT_PREFIX)
            and _object(budgets, ("caps", "used")) and _budget(budgets["caps"]) and _budget(budgets["used"]))


def _approval(value) -> bool:
    return (_object(value, APPROVAL_KEYS) and _identifier(value["approval_id"])
            and type(value["status"]) is str and value["status"] in {"APPROVED", "PENDING", "REJECTED", "TEST_VECTOR"}
            and all(_text(value[key]) for key in ("source", "revision"))
            and all(_digest(value[key]) for key in ("content_sha256", "scope_hash")))


def _identity(value) -> bool:
    return (value is None or (_object(value, IDENTITY_KEYS) and _identifier(value["approval_id"])
            and all(_text(value[key]) for key in ("source", "revision"))
            and all(_digest(value[key]) for key in ("content_sha256", "scope_hash"))
            and type(value["trusted_human"]) is bool))


def _observed(value) -> bool:
    return (_object(value, ("source_revision", "source_hashes", "used", "approval_identity"))
            and _text(value["source_revision"]) and _sources(value["source_hashes"])
            and _budget(value["used"]) and _identity(value["approval_identity"]))


def compute_scope_hash(manifest: dict) -> str:
    if not _manifest(manifest):
        raise ValueError("INVALID_MANIFEST")
    scope = dict(manifest)
    scope["budgets"] = {"caps": manifest["budgets"]["caps"]}
    try:
        serialized = json.dumps(scope, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    except ValueError as error:
        raise ValueError("INVALID_MANIFEST") from error
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def validate_launch(manifest: dict, observed_bindings: dict, approval_record: dict) -> LaunchGateResult:
    def result(reasons, scope_hash="", remaining=None):
        codes = tuple(sorted(set(reasons)))
        return LaunchGateResult(not codes, codes, scope_hash, MappingProxyType(dict(remaining or {})))

    if not _manifest(manifest):
        return result(("INVALID_MANIFEST",))
    try:
        scope_hash = compute_scope_hash(manifest)
    except ValueError:
        return result(("INVALID_MANIFEST",))
    if not _observed(observed_bindings):
        return result(("INVALID_OBSERVATIONS",), scope_hash)
    caps, declared_used, used = manifest["budgets"]["caps"], manifest["budgets"]["used"], observed_bindings["used"]
    remaining = {key: max(0, caps[key] - used[key]) for key in sorted(BUDGET_KEYS)}
    if not _approval(approval_record):
        return result(("INVALID_APPROVAL",), scope_hash, remaining)
    reasons = []
    if manifest["mode"] != "offline":
        reasons.append("MODE_NOT_ENABLED")
    if manifest["provider"] != "none":
        reasons.append("LIVE_PROVIDER_DENIED")
    if caps["python_pids"] > 9 or caps["retry_cycles"] > 2:
        reasons.append("BUDGET_CAP_EXCEEDED")
    if any(caps[key] or declared_used[key] or used[key] for key in ("worker_pids", "api_calls", "api_micro_usd")):
        reasons.append("OFFLINE_RESOURCE_DENIED")
    if any(used[key] > caps[key] or declared_used[key] > caps[key] for key in BUDGET_KEYS):
        reasons.append("BUDGET_EXCEEDED")
    if declared_used != used:
        reasons.append("USAGE_MISMATCH")
    if manifest["source_revision"] != observed_bindings["source_revision"]:
        reasons.append("SOURCE_REVISION_MISMATCH")
    if manifest["source_hashes"] != observed_bindings["source_hashes"]:
        reasons.append("SOURCE_HASH_MISMATCH")
    if approval_record["status"] != "APPROVED":
        reasons.append("APPROVAL_NOT_GRANTED")
    if approval_record["approval_id"] != manifest["approval_id"]:
        reasons.append("APPROVAL_ID_MISMATCH")
    if approval_record["scope_hash"] != scope_hash:
        reasons.append("SCOPE_MISMATCH")
    identity = observed_bindings["approval_identity"]
    if identity is None or not identity["trusted_human"]:
        reasons.append("TRUSTED_APPROVAL_REQUIRED")
    if identity is not None:
        if any(identity[key] != approval_record[key] for key in APPROVAL_KEYS - {"status"}):
            reasons.append("APPROVAL_BINDING_MISMATCH")
        if identity["scope_hash"] != scope_hash:
            reasons.append("SCOPE_MISMATCH")
    return result(reasons, scope_hash, remaining)
