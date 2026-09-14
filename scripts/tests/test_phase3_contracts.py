"""Regression checks for changes selection and the privileged publication boundary."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('detect', ROOT/'scripts/ci/detect_changed_services.py')
detect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detect)


class ChangeRegressionTests(unittest.TestCase):
    def test_deletion_and_cross_service_move_select_both_owners(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            def git(*args):
                return subprocess.check_output(['git', '-C', tmp, *args], text=True).strip()
            git('init', '-q')
            git('config', 'user.email', 'test@example.invalid')
            git('config', 'user.name', 'Test')
            a = repo/'services/auth-service/main.go'
            a.parent.mkdir(parents=True)
            a.write_text('package main\n')
            git('add', '.')
            git('commit', '-qm', 'base')
            base = git('rev-parse', 'HEAD')
            b = repo/'services/flag-service/moved.go'
            b.parent.mkdir(parents=True)
            a.rename(b)
            git('add', '-A')
            git('commit', '-qm', 'move')
            with patch.object(detect, 'REPO_ROOT', repo):
                files = detect.changed_files(base, 'HEAD')
            catalog = [{'path':'services/auth-service'}, {'path':'services/flag-service'}]
            self.assertEqual(detect.select_services(catalog, files), catalog)

    def test_validation_has_no_secrets_or_tolerated_scanners(self):
        workflow = (ROOT/'.github/workflows/_service-ci.yml').read_text()
        self.assertNotIn('secrets:', workflow)
        self.assertNotIn('continue-on-error', workflow)
        self.assertIn('SECURITY_EXIT_CODE: "1"', workflow)
        caller = (ROOT/'.github/workflows/services-ci.yml').read_text()
        validation = caller.split('  service-ci:')[1].split('  publish:')[0]
        self.assertNotIn('secrets:', validation)
        self.assertIn('needs: [changes, service-ci, publish, promote-gitops]', caller)


if __name__ == '__main__':
    unittest.main()
