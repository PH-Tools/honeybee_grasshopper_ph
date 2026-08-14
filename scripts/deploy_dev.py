#!/usr/bin/env python3
"""Mirror the maintained Rhino worker package into Ladybug Tools."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path


PACKAGE_NAME = "honeybee_ph_rhino"
TARGET_ENV_VAR = "HBPH_LBT_SITE_PACKAGES"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _default_site_packages() -> Path:
    configured_target = os.environ.get(TARGET_ENV_VAR)
    if configured_target:
        return Path(configured_target).expanduser()

    lib_root = Path.home() / "ladybug_tools" / "python" / "lib"
    candidates = sorted(lib_root.glob("python*/site-packages"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise RuntimeError(
            "Ladybug Tools site-packages was not found under '{}'. Set {} to its exact path.".format(
                lib_root, TARGET_ENV_VAR
            )
        )
    raise RuntimeError(
        "Multiple Ladybug Tools site-packages directories were found: {}. Set {} to the intended path.".format(
            ", ".join(str(path) for path in candidates), TARGET_ENV_VAR
        )
    )


def _validated_target(site_packages: Path, source: Path) -> Path:
    site_packages = site_packages.expanduser().resolve()
    if not site_packages.is_dir() or site_packages.name != "site-packages":
        raise RuntimeError("Deploy target must be an existing site-packages directory: '{}'".format(site_packages))

    target = site_packages / PACKAGE_NAME
    if target.resolve() == source.resolve():
        raise RuntimeError("Deploy source and target resolve to the same directory: '{}'".format(source))
    return target


def deploy(site_packages: Path) -> tuple[Path, int]:
    source = _repo_root() / PACKAGE_NAME
    if not source.is_dir():
        raise RuntimeError("Worker source directory was not found: '{}'".format(source))

    target = _validated_target(site_packages, source)
    file_count = sum(1 for path in source.rglob("*") if path.is_file() and "__pycache__" not in path.parts)

    staging_root = Path(tempfile.mkdtemp(prefix=".hbph-deploy-", dir=str(target.parent)))
    staged_package = staging_root / PACKAGE_NAME
    backup = target.parent / ".{}.deploy-backup".format(PACKAGE_NAME)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")

    try:
        shutil.copytree(str(source), str(staged_package), ignore=ignore)
        if backup.exists():
            shutil.rmtree(str(backup))
        if target.exists():
            target.rename(backup)
        try:
            staged_package.rename(target)
        except Exception:
            if backup.exists() and not target.exists():
                backup.rename(target)
            raise
        if backup.exists():
            shutil.rmtree(str(backup))
    finally:
        if staging_root.exists():
            shutil.rmtree(str(staging_root))

    return target, file_count


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        help="Exact site-packages directory. Defaults to $HOME/ladybug_tools/python/lib/python*/site-packages.",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress the success message.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        target, file_count = deploy(args.target or _default_site_packages())
    except Exception as error:
        print("Honeybee-PH dev deploy failed: {}".format(error), file=sys.stderr)
        return 1

    if not args.quiet:
        print("Deployed {} files to '{}'".format(file_count, target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
