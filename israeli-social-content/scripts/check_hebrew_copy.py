#!/usr/bin/env python3
"""Fast mechanical checks for Hebrew social copy."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FORBIDDEN = (
    "share with someone who needs this",
    "שתפו עם מישהו שצריך את זה",
)

SAFE_INLINE_AI = re.compile(
    r"<bdi\b[^>]*\bdir=[\"']ltr[\"'][^>]*>\s*AI\s*</bdi>|`AI`",
    flags=re.IGNORECASE,
)


def check_copy(text: str) -> list[str]:
    errors: list[str] = []
    if "—" in text:
        errors.append("contains an em dash")
    lower = text.casefold()
    for phrase in FORBIDDEN:
        if phrase.casefold() in lower:
            errors.append(f"uses generic share CTA: {phrase}")
    for line_no, line in enumerate(text.splitlines(), 1):
        unsafe_line = SAFE_INLINE_AI.sub("", line)
        if re.search(r"[\u0590-\u05ff]", unsafe_line) and re.search(r"\bAI\b", unsafe_line):
            errors.append(f"line {line_no} mixes inline AI with Hebrew")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("copy", type=Path)
    args = parser.parse_args()
    text = args.copy.read_text(encoding="utf-8")
    errors = check_copy(text)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: Israeli copy mechanics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
