"""Auth surface receipts count as membrane proof only on PASS."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from living_system_chain_validate_v1 import check_membrane_or_external  # noqa: E402


class AuthMembraneReceiptTests(unittest.TestCase):
    def _check(self, status: str) -> str:
        receipt = ROOT / "receipts" / "auth-surface-probe-unit.json"
        payload = {"schema": "sg-auth-surface-probe-v1.1", "status": status}
        with patch(
            "living_system_chain_validate_v1._iter_recent_receipts",
            return_value=[(receipt, payload, None)],
        ):
            return check_membrane_or_external(None).status

    def test_pass_counts_as_membrane_proof(self) -> None:
        self.assertEqual(self._check("PASS"), "PASS")

    def test_warn_does_not_count_as_membrane_proof(self) -> None:
        self.assertNotEqual(self._check("WARN"), "PASS")


if __name__ == "__main__":
    unittest.main()
