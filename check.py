#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


EXPECTED_SHA256 = "1ba4a793dba183388afd244ea21e850cad879c78824f78603e961070ae9b3af4"
SSOT_PATH = Path("ssot/strategy-ssot-v6-split.md")


def run_git(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        check=False,
        text=True,
        capture_output=True,
    )


def git_stdout(args: list[str]) -> str:
    result = run_git(args)
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or f"git {' '.join(args)} failed"
        raise RuntimeError(error)
    return result.stdout.strip()


def remote_head(remote: str) -> str:
    output = git_stdout(["ls-remote", remote, "HEAD"])
    return output.split()[0] if output else ""


def ensure_commit_available(remote: str, commit: str) -> None:
    if run_git(["cat-file", "-e", f"{commit}^{{commit}}"]).returncode == 0:
        return

    result = run_git(["fetch", "--quiet", "--depth=1", remote, commit])
    if result.returncode != 0:
        error = result.stderr.strip() or result.stdout.strip() or f"unable to fetch {commit}"
        raise RuntimeError(error)


def remote_file_sha256(commit: str, path: Path) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path.as_posix()}"],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        error = result.stderr.decode(errors="replace").strip() or f"{path.as_posix()} missing at {commit}"
        raise RuntimeError(error)
    return hashlib.sha256(result.stdout).hexdigest()


def build_report(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    failures: list[str] = []
    report: dict[str, object] = {
        "status": "FAIL",
        "remote": args.remote,
        "ssot_path": SSOT_PATH.as_posix(),
        "expected_head": args.expected_head,
        "remote_head": None,
        "expected_sha256": args.expected_sha256,
        "remote_ssot_sha256": None,
        "failures": failures,
    }

    try:
        head = remote_head(args.remote)
        report["remote_head"] = head
        if not head:
            failures.append("remote HEAD is empty")
        elif head != args.expected_head:
            failures.append(f"remote HEAD expected {args.expected_head}, got {head}")

        if head:
            ensure_commit_available(args.remote, head)
            actual_sha256 = remote_file_sha256(head, SSOT_PATH)
            report["remote_ssot_sha256"] = actual_sha256
            if actual_sha256 != args.expected_sha256:
                failures.append(f"SSOT SHA256 expected {args.expected_sha256}, got {actual_sha256}")
    except Exception as exc:  # noqa: BLE001 - CLI reports all advisory check failures uniformly.
        failures.append(str(exc))

    if not failures:
        report["status"] = "MATCH"
        return report, 0
    return report, 1


def print_text(report: dict[str, object]) -> None:
    print(f"REMOTE_CHECK_ADVISORY: {report['status']}")
    print(f"remote: {report['remote']}")
    print(f"expected_head: {report['expected_head']}")
    print(f"remote_head: {report['remote_head']}")
    print(f"ssot_path: {report['ssot_path']}")
    print(f"expected_sha256: {report['expected_sha256']}")
    print(f"remote_ssot_sha256: {report['remote_ssot_sha256']}")
    failures = report["failures"]
    if failures:
        print("details:")
        for failure in failures:
            print(f"- {failure}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the remote advisory SSOT staging check.")
    parser.add_argument("--remote", default="origin", help="Git remote to inspect.")
    parser.add_argument(
        "--expected-head",
        default=git_stdout(["rev-parse", "HEAD"]),
        help="Expected remote HEAD commit. Defaults to local HEAD.",
    )
    parser.add_argument(
        "--expected-sha256",
        default=EXPECTED_SHA256,
        help="Expected SHA256 for the remote SSOT file.",
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report, exit_code = build_report(args)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
