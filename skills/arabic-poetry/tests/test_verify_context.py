"""Replacement checks must honor the supplied poem position in either mode."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCANNER = Path(__file__).resolve().parents[1] / 'scripts' / 'scan.py'


class VerifyContextTests(unittest.TestCase):
    def verify(self, poem, line, candidate, *flags):
        """Execute the public CLI against a temporary poem file."""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'poem.txt'
            source.write_text(poem, encoding='utf-8')
            result = subprocess.run([sys.executable, str(SCANNER), 'verify',
                                     '--poem', str(source), '--line', str(line),
                                     *flags, candidate], text=True, capture_output=True, check=True)
        return result.stdout

    def test_free_verse_honors_explicit_repeat_check(self):
        line = 'فَاعِلُنْ فَاعِلُنْ'
        out = self.verify(line + '\n' + line, 2, line, '--meter', 'mutadarak', '--free')
        self.assertIn('إيطاء', out)
        self.assertNotIn('✓ موزون', out)
        self.assertIn('مرفوض للتكرار', out)

    def test_later_verse_does_not_gain_opening_tasri(self):
        half = 'فَعُولُنْ مَفَاعِيلُنْ فَعُولُنْ مَفَاعِيلُنْ'
        normal = half.rsplit(' ', 1)[0] + ' مَفَاعِلُنْ'
        poem = normal + ' * ' + normal + '\n' + normal + ' * ' + normal
        out = self.verify(poem, 2, half + ' * ' + half, '--meter', 'tawil')
        self.assertNotIn('✓ موزون', out)
        self.assertIn('✗', out)

    def test_line_number_counts_blank_source_rows(self):
        line = 'فَعُولُنْ فَعُولُنْ فَعُولُنْ فَعُولُنْ'
        out = self.verify('\n' + line + '\n', 2, line, '--meter', 'mutaqarib')
        self.assertNotIn('إيطاء', out)
        self.assertIn('✓ موزون', out)


if __name__ == '__main__':
    unittest.main()
