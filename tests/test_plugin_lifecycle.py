import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class LifecycleExecution(unittest.TestCase):
    def test_optimized_python_cannot_report_success(self):
        harness = Path(__file__).with_name('plugin_lifecycle.py')
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / 'receipt.json'
            result = subprocess.run(
                [sys.executable, '-O', str(harness), '--output', str(receipt)],
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('PASS ', result.stdout)
            report = json.loads(receipt.read_text())
            self.assertFalse(report['passed'])
            self.assertIn('disable Python optimization', report['error'])
            self.assertNotIn('commands', report)


if __name__ == '__main__':
    unittest.main()
