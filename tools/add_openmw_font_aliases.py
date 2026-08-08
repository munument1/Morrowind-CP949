#!/usr/bin/env python3
"""Add OpenMW Import-Wizard-compatible FNT aliases without touching TEX files.

This script does not contain or generate font binaries. It only copies existing
FNT files supplied by the user/package author and verifies byte identity plus the
FNT-internal texture basename used by OpenMW.
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


def fnt_internal_name(path: Path) -> str:
    """Read the 284-byte name buffer used by OpenMW's Morrowind FNT loader.

    FNT layout relevant here:
      float fontSize
      int   one
      int   one
      char  nameBuffer[284]

    Therefore nameBuffer starts at byte offset 12.
    """
    data = path.read_bytes()
    if len(data) < 12 + 284:
        raise ValueError(f"FNT too small: {path}")
    raw = data[12 : 12 + 284].split(b"\0", 1)[0]
    return raw.decode("ascii")


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

        expected_internal = source.stem
        try:
            internal = fnt_internal_name(source)
        except (ValueError, UnicodeDecodeError) as e:
            print(f"FAIL invalid FNT header: {source_name}: {e}")
            failures += 1
            continue

        if internal != expected_internal:
            print(
                f"FAIL unexpected internal FNT name: {source_name}: "
                f"{internal!r} != {expected_internal!r}"
            )
            failures += 1
            continue

        texture = fonts_dir / f"{internal}.tex"
        if not texture.is_file():
            print(f"FAIL missing internal texture: {texture}")
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

        alias_internal = fnt_internal_name(alias)
        if alias_internal != internal:
            print(
                f"FAIL alias internal name changed: {alias_name}: "
                f"{alias_internal!r} != {internal!r}"
            )
            failures += 1
            continue

        print(
            f"PASS {alias_name} == {source_name}  sha256={src_hash}  "
            f"internal={internal}  texture={texture.name}"
        )

    # TEX aliases are intentionally not created. OpenMW loads Fonts/<requested>.fnt,
    # then reads nameBuffer[284] from the FNT header and loads
    # Fonts/<internal-name>.tex.
    if failures:
        return 1

    print("PASS OpenMW font aliases ready; TEX aliases were not created.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
