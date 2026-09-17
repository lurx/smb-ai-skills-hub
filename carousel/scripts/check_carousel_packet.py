#!/usr/bin/env python3
"""Validate a carousel handoff packet.

Self-contained adaptation of dangogit/content-skills' gate (MIT); the shared
contracts helpers are inlined so the skill installs as a single folder.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FIELD_RE = re.compile(r"^\s*(?:[-*]\s*)?([A-Za-z][A-Za-z0-9 /_-]*):\s*(.*?)\s*$")
PLACEHOLDER_RE = re.compile(
    r"^(?:<[^>]+>|tbd|todo|replace me|pending|unknown|unverified)$",
    re.IGNORECASE,
)

REQUIRED = (
    "Objective",
    "Audience",
    "Promise",
    "Story role",
    "Proof",
    "Slides",
    "Visual blueprint",
    "Image rights",
    "Pixel QA",
    "Next action",
)


def normalize_label(label: str) -> str:
    return " ".join(label.casefold().split())


def check_packet(text: str) -> list[str]:
    fields: dict[str, str] = {}
    counts: dict[str, int] = {}
    for line in text.splitlines():
        match = FIELD_RE.match(line)
        if match:
            key = normalize_label(match.group(1))
            fields[key] = match.group(2).strip()
            counts[key] = counts.get(key, 0) + 1

    errors: list[str] = []
    for label in REQUIRED:
        key = normalize_label(label)
        if key not in fields:
            errors.append(f"missing field: {label}")
        elif not fields[key]:
            errors.append(f"empty field: {label}")
        elif PLACEHOLDER_RE.fullmatch(fields[key]):
            errors.append(f"placeholder field: {label}")
        if counts.get(key, 0) > 1:
            errors.append(f"duplicate field: {label}")

    pixel_qa = fields.get("pixel qa", "").casefold().strip()
    if pixel_qa and pixel_qa not in {"passed", "verified"}:
        errors.append(f"invalid Pixel QA: {fields.get('pixel qa', '')}")
    if "—" in text:
        errors.append("contains an em dash")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    errors = check_packet(args.packet.read_text(encoding="utf-8"))
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    if errors:
        return 1
    print("PASS: carousel handoff contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
