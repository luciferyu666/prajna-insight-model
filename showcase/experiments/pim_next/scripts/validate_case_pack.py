"""Validate local Windows regular-file synthetic packs; never dispatch or approve."""
from __future__ import annotations

import argparse
import ctypes
import json
import ntpath
import os
from pathlib import Path
import re
import stat

from experiments.pim_next.pim_next.contracts import (
    ValidationError, load_case_pack, strict_json_loads,
)

_RESERVED = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
_RESERVED.update("COM" + suffix for suffix in "123456789\u00b9\u00b2\u00b3")
_RESERVED.update("LPT" + suffix for suffix in "123456789\u00b9\u00b2\u00b3")


def _local_regular_path(raw: str) -> Path:
    # Lexical rejection precedes all filesystem metadata and content access.
    if not raw or any(ord(char) < 32 for char in raw):
        raise ValidationError("UNSAFE_PATH_SYNTAX")
    normalized = raw.replace("\\", "/")
    if normalized.startswith("/") or any(char in raw for char in '<>"|?*'):
        raise ValidationError("NETWORK_OR_DEVICE_PATH")
    drive, tail = ntpath.splitdrive(raw)
    if drive and (not re.fullmatch(r"[A-Za-z]:", drive) or not tail.startswith(("\\", "/"))):
        raise ValidationError("UNSUPPORTED_DRIVE_PATH")
    if ":" in tail:
        raise ValidationError("ALTERNATE_STREAM_PATH")
    for component in tail.replace("\\", "/").split("/"):
        if not component:
            continue
        if component in (".", "..") or component.endswith((".", " ")):
            raise ValidationError("TRAVERSAL_OR_AMBIGUOUS_PATH")
        if component.split(".")[0].rstrip(" ").upper() in _RESERVED:
            raise ValidationError("RESERVED_DEVICE_PATH")
    if os.name != "nt":
        raise ValidationError("UNSUPPORTED_LOCALITY_PLATFORM")
    path = Path(os.path.abspath(raw))
    if not path.is_absolute() or not re.fullmatch(r"[A-Za-z]:", path.drive):
        raise ValidationError("UNKNOWN_LOCALITY")
    try:
        get_drive_type = ctypes.WinDLL("kernel32", use_last_error=True).GetDriveTypeW
        get_drive_type.argtypes = [ctypes.c_wchar_p]
        get_drive_type.restype = ctypes.c_uint
        drive_type = get_drive_type(path.drive + "\\")
    except (AttributeError, OSError) as exc:
        raise ValidationError("UNKNOWN_LOCALITY") from exc
    # Removable, fixed, optical and RAM disks are declared local by Windows.
    if drive_type not in (2, 3, 5, 6):
        raise ValidationError("REMOTE_OR_UNKNOWN_DRIVE")
    for candidate in (*reversed(path.parents), path):
        metadata = candidate.lstat()
        attributes = getattr(metadata, "st_file_attributes", None)
        if type(attributes) is not int:
            raise ValidationError("UNKNOWN_FILE_ATTRIBUTES")
        if stat.S_ISLNK(metadata.st_mode) or attributes & 0x400:
            raise ValidationError("SYMLINK_OR_REPARSE_PATH")
        if candidate == path:
            if not stat.S_ISREG(metadata.st_mode):
                raise ValidationError("NONREGULAR_PACK")
        elif not stat.S_ISDIR(metadata.st_mode):
            raise ValidationError("NONDIRECTORY_ANCESTOR")
    # Metadata can race a later open: this is not an OS sandbox or TOCTOU proof.
    return path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-pack", required=True)
    parser.add_argument("--mode", required=True, choices=("test-vector",))
    args = parser.parse_args(argv)
    try:
        path = _local_regular_path(args.case_pack)
        with path.open("rb") as handle:
            payload = handle.read(1048577)
        if len(payload) > 1048576:
            raise ValidationError("PACK_BYTE_BOUND")
        cases = load_case_pack(strict_json_loads(payload.decode("utf-8")))
    except (OSError, UnicodeError, ValidationError) as exc:
        print(json.dumps({"valid": False, "evidence_scope": "TEST_VECTOR_ONLY",
                          "error": type(exc).__name__}))
        return 2
    print(json.dumps({"valid": True, "case_count": len(cases),
                      "evidence_scope": "TEST_VECTOR_ONLY",
                      "human_reference_approval": "PENDING"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
