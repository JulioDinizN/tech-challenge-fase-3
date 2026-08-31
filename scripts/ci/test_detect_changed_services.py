from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("detect_changed_services.py")
SPEC = importlib.util.spec_from_file_location("detect_changed_services", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

CATALOG = [
    {
        "name": "auth-service",
        "path": "services/auth-service",
        "language": "go",
        "runtime_version": "1.27.x",
    },
    {
        "name": "flag-service",
        "path": "services/flag-service",
        "language": "python",
        "runtime_version": "3.11",
    },
]


class SelectServicesTests(unittest.TestCase):
    def test_unknown_history_runs_every_service(self):
        self.assertEqual(MODULE.select_services(CATALOG, None), CATALOG)

    def test_service_change_selects_only_that_service(self):
        selected = MODULE.select_services(CATALOG, ["services/auth-service/main.go"])
        self.assertEqual([item["name"] for item in selected], ["auth-service"])

    def test_shared_ci_change_selects_every_service(self):
        selected = MODULE.select_services(CATALOG, [".ci/python-tools.txt"])
        self.assertEqual(selected, CATALOG)

    def test_documentation_change_selects_no_service(self):
        self.assertEqual(MODULE.select_services(CATALOG, ["docs/architecture.md"]), [])


if __name__ == "__main__":
    unittest.main()
