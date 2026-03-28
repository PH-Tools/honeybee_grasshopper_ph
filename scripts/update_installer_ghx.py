#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update version numbers in the hbph_installer.ghx file.

This script parses the Grasshopper .ghx (XML) file and updates:
  1. The package version pins in the 'requirements' panel's UserText element.
  2. The Scribble label that displays the release date and version.

Usage:
    python scripts/update_installer_ghx.py \
        --honeybee-ph=1.33.0 \
        --phx=1.57.0 \
        --release-version=1.18.1

Only the flags you pass will be updated; others are left unchanged.
"""

import argparse
from datetime import datetime, timezone
import re
import sys
from pathlib import Path

# The installer file path relative to the repo root
INSTALLER_PATH = Path(__file__).resolve().parent.parent / "hbph_installer.ghx"

# Packages we know how to update in the installer.
# Maps CLI flag name -> PyPI package name as it appears in the GHX requirements panel.
KNOWN_PACKAGES = {
    "honeybee_ph": "honeybee-ph",
    "phx": "PHX",
    "ph_units": "PH-units",
    "honeybee_ref": "honeybee-ref",
    "ladybug_rhino": "ladybug-rhino",
    "plotly": "plotly",
}


def update_requirements_text(text, updates):
    # type: (str, dict[str, str]) -> str
    """Given the raw UserText string from the GHX panel, update version pins.

    Each line looks like:  honeybee-ph>=1.32.0
    We match by package name and replace the version.
    """
    # The GHX XML stores ">" as "&gt;" inside element text.
    # We need to preserve that encoding.
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            new_lines.append(line)
            continue

        # Normalize XML entities for comparison
        normalized = stripped.replace("&gt;", ">").replace("&lt;", "<")

        updated = False
        for flag_name, pypi_name in KNOWN_PACKAGES.items():
            if flag_name in updates and normalized.lower().startswith(pypi_name.lower()):
                new_lines.append("{}&gt;={}" .format(pypi_name, updates[flag_name]))
                updated = True
                break

        if not updated:
            new_lines.append(line)

    return "\n".join(new_lines)


def main():
    parser = argparse.ArgumentParser(description="Update installer .ghx version pins")
    parser.add_argument("--honeybee-ph", dest="honeybee_ph", help="honeybee-ph version")
    parser.add_argument("--phx", dest="phx", help="PHX version")
    parser.add_argument("--ph-units", dest="ph_units", help="PH-units version")
    parser.add_argument("--honeybee-ref", dest="honeybee_ref", help="honeybee-ref version")
    parser.add_argument("--ladybug-rhino", dest="ladybug_rhino", help="ladybug-rhino version")
    parser.add_argument("--plotly", dest="plotly", help="plotly version")
    parser.add_argument("--release-version", dest="release_version", help="Release version for the Scribble label (e.g. 1.18.1)")
    parser.add_argument("--installer-path", dest="installer_path", help="Path to .ghx file (default: auto)")
    args = parser.parse_args()

    installer_path = Path(args.installer_path) if args.installer_path else INSTALLER_PATH
    if not installer_path.exists():
        print("ERROR: Installer file not found: {}".format(installer_path))
        sys.exit(1)

    # Collect only the flags that were actually provided
    updates = {}
    for flag_name in KNOWN_PACKAGES:
        val = getattr(args, flag_name, None)
        if val is not None:
            updates[flag_name] = val

    if not updates and not args.release_version:
        print("No version updates specified. Nothing to do.")
        return

    print("Updating installer: {}".format(installer_path.name))
    for flag_name, version in updates.items():
        print("  {} -> {}".format(KNOWN_PACKAGES[flag_name], version))

    # Read the GHX file
    content = installer_path.read_text(encoding="utf-8-sig")
    new_content = content

    # ---------------------------------------------------------------
    # Update requirements panel (if package versions were provided)
    # ---------------------------------------------------------------
    if updates:
        pattern = re.compile(
            r'(<item\s+name="NickName"[^>]*>requirements</item>'
            r'.*?'
            r'<item\s+name="UserText"\s+type_name="gh_string"\s+type_code="10">)'
            r'(.*?)'
            r'(</item>)',
            re.DOTALL,
        )

        match = pattern.search(new_content)
        if not match:
            print("ERROR: Could not find 'requirements' panel UserText in installer file.")
            print("The installer .ghx format may have changed.")
            sys.exit(1)

        old_text = match.group(2)
        new_text = update_requirements_text(old_text, updates)

        if old_text == new_text:
            print("Requirements already up to date.")
        else:
            print("\nBefore:\n  {}".format(old_text.replace("\n", "\n  ")))
            print("After:\n  {}".format(new_text.replace("\n", "\n  ")))
            new_content = new_content[: match.start(2)] + new_text + new_content[match.end(2) :]

    # ---------------------------------------------------------------
    # Update the Scribble label with the release date and version
    # ---------------------------------------------------------------
    if args.release_version:
        today = datetime.now(timezone.utc).strftime("%b %d, %Y").upper()
        new_label = "{} [v{}]".format(today, args.release_version)

        # Match the Scribble's Text element. The label looks like: "MAR 28, 2025 [v1.18.0]"
        scribble_pattern = re.compile(
            r'(<item\s+name="NickName"[^>]*>Scribble</item>'
            r'.*?'
            r'<item\s+name="Text"\s+type_name="gh_string"\s+type_code="10">)'
            r'([^<]*)'
            r'(</item>)',
            re.DOTALL,
        )
        scribble_match = scribble_pattern.search(new_content)
        if scribble_match:
            old_label = scribble_match.group(2)
            print("\nScribble label: '{}' -> '{}'".format(old_label, new_label))
            new_content = (
                new_content[: scribble_match.start(2)]
                + new_label
                + new_content[scribble_match.end(2) :]
            )
        else:
            print("\nWARNING: Could not find Scribble label in installer file.")

    installer_path.write_text(new_content, encoding="utf-8-sig")
    print("\nInstaller updated successfully.")


if __name__ == "__main__":
    main()
