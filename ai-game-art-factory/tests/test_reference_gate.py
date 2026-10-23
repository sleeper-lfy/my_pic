"""The rejected interpolation/proxy pipeline cannot run as the normal default."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


class ReferenceGateTests(unittest.TestCase):
    def test_old_defaults_are_blocked_before_asset_generation(self):
        for command in ['structure','experiment']:
            with self.subTest(command=command):
                run=subprocess.run([sys.executable,str(ROOT/'scripts/factory.py'),command],capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0)
                self.assertIn('Legacy human-form baseline was rejected',run.stderr)
                self.assertNotIn('BUILT',run.stdout)

    def test_reference_help_names_supported_scopes(self):
        run=subprocess.run([sys.executable,str(ROOT/'scripts/factory.py'),'reference-baseline','--help'],capture_output=True,text=True)
        self.assertEqual(run.returncode,0)
        self.assertIn('anatomy,motion,all',run.stdout)


if __name__=='__main__':unittest.main()
