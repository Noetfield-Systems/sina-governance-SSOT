#!/usr/bin/env python3
"""Validate a workflow-supplied P0-PGR packet path without shell interpretation."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def validate_packet_path(raw_path: str, *, root: Path = ROOT) -> str:
    if not raw_path or "\x00" in raw_path or "\n" in raw_path or "\r" in raw_path:
        raise ValueError("packet path must be one non-empty line")
    if "\\" in raw_path:
        raise ValueError("packet path must use repository-relative POSIX separators")

    relative = PurePosixPath(raw_path)
    if relative.is_absolute():
        raise ValueError("absolute packet paths are forbidden")
    if any(part in {"", ".", ".."} for part in raw_path.split("/")):
        raise ValueError("dot and parent path components are forbidden")
    if len(relative.parts) != 2 or relative.parts[0] != "p0-pgr":
        raise ValueError("packet path must match p0-pgr/*.json")
    if relative.suffix != ".json":
        raise ValueError("packet path must end in lowercase .json")

    packet_root = (root / "p0-pgr").resolve(strict=True)
    candidate = root.joinpath(*relative.parts)
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlink packet paths are forbidden")

    resolved = candidate.resolve(strict=True)
    try:
        resolved.relative_to(packet_root)
    except ValueError as exc:
        raise ValueError("packet path escapes p0-pgr/") from exc
    if not resolved.is_file():
        raise ValueError("packet path must identify a regular file")

    return resolved.relative_to(root.resolve(strict=True)).as_posix()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet")
    args = parser.parse_args()
    try:
        print(validate_packet_path(args.packet))
    except (OSError, ValueError) as exc:
        print(f"BLOCKED_INVALID_PACKET_PATH: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
