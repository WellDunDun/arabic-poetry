#!/usr/bin/env python3
"""Check an explicit عروض transcription and its annotated feet, not its meter."""

import argparse
import json
import sys
import unicodedata
from pathlib import Path

SHORT = "َُِ"
SUKUN = "ْ"
LONG = {"ا": "َ", "ى": "َ", "و": "ُ", "ي": "ِ"}


def compact(text):
    return "".join(unicodedata.normalize("NFC", text).split())


def sound_pattern(text):
    text = compact(text)
    bits, previous, index = [], None, 0
    while index < len(text):
        letter = text[index]
        if not ("\u0621" <= letter <= "\u063a" or "\u0641" <= letter <= "\u064a"):
            raise ValueError(f"Unexpected character at position {index + 1}: {letter!r}")
        if letter in "آة":
            raise ValueError(f"Expand {letter!r} for the intended pronunciation first")
        mark = text[index + 1] if index + 1 < len(text) else ""
        if mark and mark in SHORT + SUKUN:
            if letter in "اى" and mark in SHORT:
                raise ValueError("Use an explicit hamza for a moving alif")
            bits.append("0" if mark == SUKUN else "1")
            previous = mark
            index += 2
        elif letter in LONG and previous == LONG[letter]:
            bits.append("0")
            previous = SUKUN
            index += 1
        else:
            raise ValueError(
                f"Missing or unexpanded vocalization at position {index + 1}: {letter!r}. "
                "Expand shadda, tanwin and unwritten sounds; mark consonants explicitly."
            )
    if not bits:
        raise ValueError("The transcription is empty")
    return "".join(bits)


def check(document):
    if not isinstance(document, dict) or not isinstance(document.get("arudi"), str):
        raise ValueError("Expected an object with an arudi string and a feet array")
    feet = document.get("feet")
    if not isinstance(feet, list) or not feet:
        raise ValueError("feet must be a nonempty array")
    for foot in feet:
        if not isinstance(foot, dict) or not isinstance(foot.get("text"), str):
            raise ValueError("Each foot needs a text string and a binary pattern")
        pattern = foot.get("pattern")
        if not isinstance(pattern, str) or not pattern or set(pattern) - {"0", "1"}:
            raise ValueError("Each foot pattern must contain only 0 and 1")
    actual = sound_pattern(document["arudi"])
    problems, rows = [], []
    if compact("".join(foot["text"] for foot in feet)) != compact(document["arudi"]):
        problems.append("Foot text does not cover the transcription exactly and in order")
    for index, foot in enumerate(feet, 1):
        calculated = sound_pattern(foot["text"])
        rows.append({"foot": index, "text": foot["text"], "actual": calculated,
                     "claimed": foot["pattern"]})
        if calculated != foot["pattern"]:
            problems.append(f"Foot {index}: calculated {calculated}, claimed {foot['pattern']}")
    if "".join(foot["pattern"] for foot in feet) != actual:
        problems.append("Concatenated foot patterns do not match the whole sound sequence")
    return {"ok": not problems, "actual": actual, "feet": rows, "problems": problems,
            "scope": "Transcription arithmetic only; pronunciation and meter legality need review"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSON file, or - for stdin")
    args = parser.parse_args()
    try:
        source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = check(json.loads(source))
    except (OSError, ValueError) as error:
        result = {"ok": False, "error": str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
