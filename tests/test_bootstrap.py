from __future__ import annotations

from crm.bootstrap import build_context
from tests.common import SandboxPathsTestCase


class BootstrapSmokeTests(SandboxPathsTestCase):
    def test_build_context_initializes_all_csv_files(self) -> None:
        build_context()
        expected = {
            "users.csv",
            "clients.csv",
            "properties.csv",
            "deals.csv",
            "appointments.csv",
            "tasks.csv",
            "interactions.csv",
            "audit_log.csv",
        }
        actual = {path.name for path in self.data_dir.glob("*.csv")}
        self.assertEqual(expected, actual)
