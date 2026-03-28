#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update version numbers in the hbph_installer.ghx file.

This script parses the Grasshopper .ghx (XML) file and updates the
package version pins in the 'requirements' panel's UserText element.

Usage:
    python scripts/update_installer_ghx.py \
        --honeybee-ph=1.33.0 \
        --phx=1.57.0

Only the flags you pass will be updated; others are left unchanged.
"""

import argparse
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

    if not updates:
        print("No version updates specified. Nothing to do.")
        return

    print("Updating installer: {}".format(installer_path.name))
    for flag_name, version in updates.items():
        print("  {} -> {}".format(KNOWN_PACKAGES[flag_name], version))

    # Read the GHX file
    content = installer_path.read_text(encoding="utf-8-sig")

    # Find the requirements panel's UserText element.
    # Pattern: <item name="NickName" ...>requirements</item> followed later by <item name="UserText" ...>...</item>
    # We look for the UserText within the same <items> block as the requirements NickName.
    pattern = re.compile(
        r'(<item\s+name="NickName"[^>]*>requirements</item>'  # NickName = requirements
        r'.*?'  # ... other items in between ...
        r'<item\s+name="UserText"\s+type_name="gh_string"\s+type_code="10">)'  # UserText opening tag
        r'(.*?)'  # The actual version text content
        r'(</item>)',  # Closing tag
        re.DOTALL,
    )

    match = pattern.search(content)
    if not match:
        print("ERROR: Could not find 'requirements' panel UserText in installer file.")
        print("The installer .ghx format may have changed.")
        sys.exit(1)

    old_text = match.group(2)
    new_text = update_requirements_text(old_text, updates)

    if old_text == new_text:
        print("No changes needed — versions already up to date.")
        return

    print("\nBefore:\n  {}".format(old_text.replace("\n", "\n  ")))
    print("After:\n  {}".format(new_text.replace("\n", "\n  ")))

    # Replace in the full content
    new_content = content[: match.start(2)] + new_text + content[match.end(2) :]
    installer_path.write_text(new_content, encoding="utf-8-sig")
    print("\nInstaller updated successfully.")


if __name__ == "__main__":
    main()
