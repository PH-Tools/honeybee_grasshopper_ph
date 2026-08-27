# /// script
# requires-python = ">=3.11"
# ///
"""Detect window-type inflation from HB-PH v1.25.2 - v1.32.x (bug #59, downstream half).

Scans a directory tree for the three artifact kinds that can carry the inflated
window-type list and reports a verdict per file:

- ``.hbjson``  window-construction count > distinct display-name count, with
               identifiers matching the uuid arithmetic the bug produced
               (``<con_id>_<con_id>_<hex8>_<hex8>``).
- ``.xml``     WUFI-Passive models only (root ``<WUFIplusProject>``): any
               ``<WindowType>`` whose ``<Name>`` matches the uuid signature.
- ``.mwp``     WUFI-Passive project files (proprietary binary): ASCII string
               runs matching the uuid signature. Works because construction
               identifiers are stored as plain strings.

Post-fix WUFI exports legitimately carry ~2x the base type count (PHX per-edge
psi-install variant synthesis) - that is NOT the bug, and the name-signature
detector correctly ignores it.

Usage:
    uv run scan_inflated_window_types.py                 # scan ~/Dropbox
    uv run scan_inflated_window_types.py --root <dir>    # scan another tree
    uv run scan_inflated_window_types.py --all           # also list clean files

Exit code is 1 if any affected file was found, else 0.

See ``exported-models-inflated-window-types.md`` (this folder, or the archive)
for the defect history and the 2026-08-26 scoping result this reproduces.
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from pathlib import Path

# The bug ran clean_and_id_ep_string() twice per aperture, so affected
# identifiers end in two uuid4()[:8] hex chunks: ..._a1789218_49914505
UUID_SIGNATURE = re.compile(r"_[0-9a-f]{8}_[0-9a-f]{8}$")

# ASCII runs of printable characters, minimum 18 chars (the signature alone).
ASCII_RUN = re.compile(rb"[\x20-\x7e]{18,}")

DEFAULT_EXCLUDES = ("bldgtyp-00", ".dropbox.cache")

VERDICT_ORDER = ("AFFECTED", "clean", "unreadable", "skip")


def scan_hbjson(path: Path) -> tuple[str, str]:
    """Return (verdict, detail) for one .hbjson file."""
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return "unreadable", f"not parseable as JSON ({e.__class__.__name__})"
    constructions = (data.get("properties", {}).get("energy", {}) or {}).get("constructions") or []
    windows = [c for c in constructions if "Window" in c.get("type", "")]
    names = {c.get("display_name") or c.get("identifier") for c in windows}
    signature_hits = sum(1 for c in windows if UUID_SIGNATURE.search(c.get("identifier", "")))
    detail = f"win_constructions={len(windows)} distinct_names={len(names)} signature_ids={signature_hits}"
    if len(windows) > len(names) and signature_hits > len(names):
        return "AFFECTED", detail
    return "clean", detail


def scan_wufi_xml(path: Path) -> tuple[str, str]:
    """Return (verdict, detail) for one WUFI-Passive .xml file."""
    try:
        with path.open(encoding="utf-8", errors="replace") as f:
            head = f.read(2048)
            if "<WUFIplusProject>" not in head:
                return "skip", "not a WUFI-Passive model"
            text = head + f.read()
    except OSError as e:
        return "unreadable", str(e)
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        return "unreadable", f"XML parse error ({e})"
    window_types = root.findall(".//WindowType")
    signature_hits = sum(
        1 for wt in window_types if (name := wt.findtext("Name")) and UUID_SIGNATURE.search(name)
    )
    detail = f"window_types={len(window_types)} signature_names={signature_hits}"
    return ("AFFECTED" if signature_hits else "clean"), detail


def scan_mwp(path: Path) -> tuple[str, str]:
    """Return (verdict, detail) for one WUFI-Passive .mwp project file."""
    try:
        raw = path.read_bytes()
    except OSError as e:
        return "unreadable", str(e)
    signature_hits = sum(
        1 for run in ASCII_RUN.findall(raw) if UUID_SIGNATURE.search(run.decode("ascii"))
    )
    detail = f"signature_strings={signature_hits}"
    return ("AFFECTED" if signature_hits else "clean"), detail


SCANNERS = {".hbjson": scan_hbjson, ".xml": scan_wufi_xml, ".mwp": scan_mwp}


def iter_candidate_files(root: Path, excludes: list[str]) -> Iterator[Path]:
    """Yield scannable files under root, pruning excluded subtrees during the walk."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            d for d in dirnames
            if not any(pattern in os.path.join(dirpath, d) for pattern in excludes)
        ]
        for filename in filenames:
            path = Path(dirpath, filename)
            if path.suffix.lower() in SCANNERS and not any(p in str(path) for p in excludes):
                yield path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path.home() / "Dropbox", help="tree to scan")
    parser.add_argument("--all", action="store_true", help="also list clean and skipped files")
    parser.add_argument(
        "--exclude", action="append", default=list(DEFAULT_EXCLUDES),
        help="path substring to skip (repeatable); defaults: %(default)s",
    )
    args = parser.parse_args()

    results: dict[str, list[tuple[Path, str]]] = {}
    for path in sorted(iter_candidate_files(args.root, args.exclude)):
        verdict, detail = SCANNERS[path.suffix.lower()](path)
        results.setdefault(verdict, []).append((path, detail))

    for verdict in VERDICT_ORDER:
        if verdict != "AFFECTED" and not args.all:
            continue
        for path, detail in results.get(verdict, []):
            print(f"{verdict:9} {detail}  {path}")

    counts = {verdict: len(rows) for verdict, rows in results.items()}
    print(f"--- scanned {sum(counts.values())} files: {counts}", file=sys.stderr)
    return 1 if results.get("AFFECTED") else 0


if __name__ == "__main__":
    sys.exit(main())
