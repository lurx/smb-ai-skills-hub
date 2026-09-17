#!/usr/bin/env python3
"""Vendor-side: regenerate standards/manifest.json after editing standards files.

Reads each standards/*.md header (version:) and emits the manifest the
ads-standards-update skill consumes. Changelog lines are prompted per changed
file (or pass --changelog "file=text" pairs).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

STANDARDS = Path(__file__).parent / "standards"
MANIFEST = STANDARDS / "manifest.json"


def parse_version(path: Path) -> str:
    head = path.read_text(encoding="utf-8")[:500]
    m = re.search(r"^version:\s*([\d.]+)\s*$", head, re.M)
    if not m:
        sys.exit(f"ERROR: {path.name} has no 'version:' header")
    return m.group(1)


def main() -> None:
    cli_changelogs = dict(
        arg.split("=", 1) for arg in sys.argv[2:] if "=" in arg
    ) if len(sys.argv) > 2 and sys.argv[1] == "--changelog" else {}

    old = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"files": {}}
    files = {}
    for path in sorted(STANDARDS.glob("*.md")):
        version = parse_version(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        prev = old["files"].get(path.name, {})
        changelog = prev.get("changelog", "")
        if prev.get("sha256") != digest:
            if path.name in cli_changelogs:
                changelog = cli_changelogs[path.name]
            else:
                changelog = input(f"changelog for {path.name} ({prev.get('version', 'new')} -> {version}): ")
        files[path.name] = {"version": version, "sha256": digest, "changelog": changelog}

    MANIFEST.write_text(
        json.dumps({"generated": True, "files": files}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"manifest.json written with {len(files)} files")


if __name__ == "__main__":
    main()
