from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class SandboxPathsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)
        self.data_dir = base / "data"
        self.log_dir = base / "logs"
        self.export_dir = base / "exports"
        self.backup_dir = base / "backups"
        self.patchers = [
            patch("crm.config.DATA_DIR", self.data_dir),
            patch("crm.config.LOG_DIR", self.log_dir),
            patch("crm.config.EXPORT_DIR", self.export_dir),
            patch("crm.config.BACKUP_DIR", self.backup_dir),
            patch("crm.utils.BACKUP_DIR", self.backup_dir),
            patch("crm.bootstrap.APP_LOG_FILE", str(self.log_dir / "app.log")),
            patch("crm.services.report_service.DATA_DIR", self.data_dir),
        ]
        for patcher in self.patchers:
            patcher.start()
        self.addCleanup(self._cleanup_patches)

    def _cleanup_patches(self) -> None:
        for patcher in reversed(self.patchers):
            patcher.stop()
        self.temp_dir.cleanup()
