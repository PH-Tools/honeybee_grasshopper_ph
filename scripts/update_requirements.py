#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update version pins in requirements.txt.

Reads the current requirements.txt, updates any packages whose versions
are provided via CLI flags, and writes the file back.

Usage:
    python scripts/update_requirements.py \
        --honeybee-ph=1.33.0 \
        --phx=1.57.0 \
        --ph-units=1.5.29

Only the flags you pass will be updated; others are left unchanged.
"""

import argparse
import re
import sys
from pathlib import Path

REQUIREMENTS_PATH = Path(__file__).resolve().parent.parent / "requirements.txt"

# Maps CLI flag name -> PyPI package name as it appears in requirements.txt
KNOWN_PACKAGES = {
    "honeybee_ph": "honeybee-ph",
    "phx": "PHX",
    "ph_units": "PH-units",
    "honeybee_ref": "honeybee-ref",
    "honeybee_core": "honeybee-core",
    "honeybee_energy": "honeybee-energy",
    "ladybug_rhino": "ladybug-rhino",
}


def main():
    parser = argparse.ArgumentParser(description="Update requirements.txt version pins")
    parser.add_argument("--honeybee-ph", dest="honeybee_ph")
    parser.add_argument("--phx", dest="phx")
    parser.add_argument("--ph-units", dest="ph_units")
    parser.add_argument("--honeybee-ref", dest="honeybee_ref")
    parser.add_argument("--honeybee-core", dest="honeybee_core")
    parser.add_argument("--honeybee-energy", dest="honeybee_energy")
    parser.add_argument("--ladybug-rhino", dest="ladybug_rhino")
    parser.add_argument("--requirements-path", dest="requirements_path")
    args = parser.parse_args()

    req_path = Path(args.requirements_path) if args.requirements_path else REQUIREMENTS_PATH
    if not req_path.exists():
        print("ERROR: requirements.txt not found: {}".format(req_path))
        sys.exit(1)

    # Collect updates
    updates = {}
    for flag_name in KNOWN_PACKAGES:
        val = getattr(args, flag_name, None)
        if val is not None:
            updates[flag_name] = val

    if not updates:
        print("No version updates specified. Nothing to do.")
        return

    print("Updating: {}".format(req_path))

    lines = req_path.read_text().splitlines()
    new_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue

        updated = False
        for flag_name, pypi_name in KNOWN_PACKAGES.items():
            if flag_name not in updates:
                continue
            # Match package name (case-insensitive) followed by a version specifier
            pattern = re.compile(
                r"^" + re.escape(pypi_name) + r"\s*([><=!~]+)",
                re.IGNORECASE,
            )
            if pattern.match(stripped):
                new_line = "{}>={}" .format(pypi_name, updates[flag_name])
                new_lines.append(new_line)
                print("  {} -> {}".format(stripped, new_line))
                updated = True
                break

        if not updated:
            new_lines.append(line)

    req_path.write_text("\n".join(new_lines) + "\n")
    print("requirements.txt updated successfully.")


if __name__ == "__main__":
    main()
