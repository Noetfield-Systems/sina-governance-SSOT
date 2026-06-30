#!/usr/bin/env python3
import hashlib
import subprocess
import sys
from pathlib import Path


EXPECTED_HEAD = "5ab5530cacb35f51d20edfa619a04f8ef2bc8782"
EXPECTED_SHA256 = "1ba4a793dba183388afd244ea21e850cad879c78824f78603e961070ae9b3af4"
SSOT_PATH = Path("ssot/strategy-ssot-v6-split.md")


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


remote = subprocess.run(
    ["git", "ls-remote", "origin", "HEAD"],
    check=False,
    text=True,
    capture_output=True,
)

if remote.returncode != 0:
    fail(remote.stderr.strip() or "git ls-remote origin HEAD failed")

remote_head = remote.stdout.strip().split()[0] if remote.stdout.strip() else ""
if remote_head != EXPECTED_HEAD:
    fail(f"remote HEAD expected {EXPECTED_HEAD}, got {remote_head or '<empty>'}")

actual_sha256 = hashlib.sha256(SSOT_PATH.read_bytes()).hexdigest()
if actual_sha256 != EXPECTED_SHA256:
    fail(f"SSOT SHA256 expected {EXPECTED_SHA256}, got {actual_sha256}")

print("REMOTE_CHECK_ADVISORY: MATCH")
