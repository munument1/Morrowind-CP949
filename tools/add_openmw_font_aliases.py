#!/usr/bin/env python3
"""Add OpenMW Import-Wizard-compatible FNT aliases without touching TEX files.

This script does not contain or generate font binaries. It only copies existing
FNT files supplied by the user/package author and verifies byte identity.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

ALIASES = {
    "MysticCards.fnt": "magic_cards_regular.fnt",
    "DemonicLetters.fnt": "daedric_font.fnt",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(
        description=(
            "Create OpenMW bitmap-font filename aliases for both the default "
            "MysticCards/DemonicLetters config and Morrowind.ini Import Wizard "
            "magic_cards_regular/daedric_font config."
        )
    )
    ap.add_argument("fonts_dir", type=Path, help="Directory containing the existing .fnt/.tex files")
    ap.add_argument("--check", action="store_true", help="Verify aliases only; do not create or replace files")
    args = ap.parse_args()

    fonts_dir = args.fonts_dir.resolve()
    if not fonts_dir.is_dir():
        raise SystemExit(f"Fonts directory not found: {fonts_dir}")

    failures = 0
    for source_name, alias_name in ALIASES.items():
        source = fonts_dir / source_name
        alias = fonts_dir / alias_name

        if not source.is_file():
            print(f"FAIL missing source: {source}")
            failures += 1
            continue

        if args.check:
            if not alias.is_file():
                print(f"FAIL missing alias:  {alias}")
                failures += 1
                continue
        else:
            shutil.copyfile(source, alias)

        src_hash = sha256(source)
        alias_hash = sha256(alias)
        if src_hash != alias_hash:
            print(f"FAIL byte mismatch: {source_name} != {alias_name}")
            failures += 1
            continue

        print(f"PASS {alias_name} == {source_name}  sha256={src_hash}")

    # TEX aliases are intentionally not created. OpenMW reads the internal font
    # name from the FNT header and opens Fonts/<internal-name>.tex.
    if failures:
        return 1

    print("PASS OpenMW font aliases ready; TEX aliases were not created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
