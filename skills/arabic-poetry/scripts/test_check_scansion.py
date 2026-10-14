"""Behavior checks for explicit transcription arithmetic and complete coverage."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from check_scansion import check, sound_pattern


class ScansionChecks(unittest.TestCase):
    def test_source_backed_classical_patterns(self):
        samples = [
            ("قِفَا نَبْ كِ مِنْ ذِكْرَى حَبِيبِنْ وَمَنْزِلِي", "11010110101011010110110"),
            ("بِسِقْطِلْ لِوَى بَيْنَدْ دَخُولِ فَحَوْمَلِي", "1101011010101101110110"),
            ("هَزَجْنَا فِي أَغَانِيكُمْ", "11010101101010"),
            ("وَشَاقَتْنَا مَعَانِيكُمْ", "11010101101010"),
        ]
        for text, expected in samples:
            with self.subTest(text=text):
                self.assertEqual(sound_pattern(text), expected)

    def test_tanwin_readings_must_be_explicit(self):
        self.assertEqual(sound_pattern("وَحِيدَا"), "11010")
        self.assertEqual(sound_pattern("وَحِيدَنْ"), "11010")
        with self.assertRaises(ValueError):
            sound_pattern("وَحِيدًا")

    def test_incomplete_and_unexpanded_readings_are_rejected(self):
        for text in ["قفا نبك", "كُلُّ", "آمَنَ", "غُرْفَة", "قِفَا!", ""]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                sound_pattern(text)

    def test_complete_aligned_scan_passes(self):
        document = {"arudi": "هَزَجْنَا فِي أَغَانِيكُمْ", "feet": [
            {"text": "هَزَجْنَا فِي", "pattern": "1101010"},
            {"text": "أَغَانِيكُمْ", "pattern": "1101010"},
        ]}
        self.assertTrue(check(document)["ok"])

    def test_trailing_and_duplicated_sounds_cannot_pass_as_a_prefix(self):
        for arudi, texts in [
            ("أُنَادِي بِلَادِي", ["أُنَادِي"]),
            ("أُنَادِي", ["أُنَادِي", "أُنَادِي"]),
            ("أُنَادِي بِلَادِي", ["بِلَادِي", "أُنَادِي"]),
        ]:
            with self.subTest(arudi=arudi, texts=texts):
                result = check({"arudi": arudi, "feet": [
                    {"text": text, "pattern": "11010"} for text in texts]})
                self.assertFalse(result["ok"])

    def test_false_foot_pattern_is_rejected(self):
        result = check({"arudi": "فَعِلُنْ", "feet": [
            {"text": "فَعِلُنْ", "pattern": "11010"}]})
        self.assertFalse(result["ok"])
        self.assertEqual(result["actual"], "1110")

    def test_cli_malformed_input_returns_failure_json(self):
        command = [sys.executable, str(Path(__file__).with_name("check_scansion.py"))]
        for source in ["{", '{"arudi":"أُنَادِي","feet":[]}', "null"]:
            with self.subTest(source=source):
                result = subprocess.run(command, input=source, text=True, capture_output=True)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(json.loads(result.stdout)["ok"])

    def test_cli_file_and_stdin_return_the_same_success(self):
        source = json.dumps({"arudi": "أُنَادِي", "feet": [
            {"text": "أُنَادِي", "pattern": "11010"}]}, ensure_ascii=False)
        command = [sys.executable, str(Path(__file__).with_name("check_scansion.py"))]
        stdin_result = subprocess.run(command, input=source, text=True, capture_output=True)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "scan.json"
            path.write_text(source, encoding="utf-8")
            file_result = subprocess.run(command + [str(path)], text=True, capture_output=True)
        self.assertEqual(stdin_result.returncode, 0)
        self.assertEqual(file_result.returncode, 0)
        self.assertEqual(json.loads(stdin_result.stdout), json.loads(file_result.stdout))


if __name__ == "__main__":
    unittest.main()
