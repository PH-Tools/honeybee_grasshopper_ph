# Honeybee-PH: Build & Release Workflow

This document describes how to build, version, and release updates across
the Honeybee-PH plugin ecosystem.

---

## Repository Map

| Repo | Purpose | Published to | Auto-version? |
|------|---------|-------------|---------------|
| [PH_units](https://github.com/PH-Tools/PH_units) | Unit conversion library | PyPI (`PH-units`) | Yes |
| [honeybee_ph](https://github.com/PH-Tools/honeybee_ph) | Core Passive House plugin for Honeybee | PyPI (`honeybee-ph`) | Yes |
| [PHX](https://github.com/PH-Tools/PHX) | PHPP/WUFI export engine | PyPI (`PHX`) | Yes |
| [honeybee_ref](https://github.com/PH-Tools/honeybee_ref) | Reference/document tracking extension | PyPI (`honeybee-ref`) | Yes |
| [PH_GH_Component_IO](https://github.com/PH-Tools/PH_GH_Component_IO) | GH component I/O utility | GitHub (auto-tag) | Yes |
| [honeybee_grasshopper_ph](https://github.com/PH-Tools/honeybee_grasshopper_ph) | Grasshopper components + installer | GitHub Releases | Orchestrator |
| [honeybee_grasshopper_ph_plus](https://github.com/PH-Tools/honeybee_grasshopper_ph_plus) | Additional GH components | GitHub Releases | Orchestrator |

### Dependency Chain

```
PH_units  (standalone)
    |
honeybee_ph  (depends on PH_units)
    |
PHX  (depends on honeybee_ph, PH_units)

honeybee_ref  (standalone, depends only on honeybee-energy)

PH_GH_Component_IO  (standalone GH utility library)

honeybee_grasshopper_ph      (depends on all of the above at runtime)
honeybee_grasshopper_ph_plus (depends on all of the above at runtime)
```

---

## How Versioning Works

All repos use [bump-my-version](https://github.com/callowayproject/bump-my-version)
with a consistent pattern:

### PyPI Libraries (PH_units, honeybee_ph, PHX, honeybee_ref)

**On every push to `main`:**
1. Tests run automatically
2. Version is bumped (patch by default) and a new git tag is created
3. Package is built and published to PyPI via OIDC trusted publishing

**To control the bump level:**
- Direct push to `main` → always bumps **patch** (e.g., 1.5.28 → 1.5.29)
- Merge a PR with label `bump:minor` → bumps **minor** (e.g., 1.5.28 → 1.6.0)
- Merge a PR with label `bump:major` → bumps **major** (e.g., 1.5.28 → 2.0.0)
- Merge a PR with no label → bumps **patch**

The bump commit message includes `[skip ci]` so it doesn't trigger another CI run.

### Grasshopper Repos

These are versioned by the **release orchestrator** (see below), not on every push.
The `RELEASE_VERSION` string in `_component_info_.py` is updated automatically.

---

## Daily Development Workflow

### Making a quick bug fix to a PyPI library

1. Fix the bug in (e.g.) `PHX`
2. Push directly to `main`
3. CI runs tests, bumps patch, deploys to PyPI → **done**

### Making a change to PH_GH_Component_IO

1. Edit code, push to `main`
2. CI runs tests, bumps patch, creates a git tag → **done** (no PyPI publish — distributed via GitHub download)

### Adding a new feature (with PR)

1. Create a feature branch: `git checkout -b feat/my-feature`
2. Make your changes, push, open a PR
3. Add the `bump:minor` label to the PR
4. Merge → CI bumps minor version, deploys to PyPI → **done**

### Working on Grasshopper components

1. Edit worker classes in `honeybee_ph_rhino/gh_compo_io/`
2. If needed, edit GHPython components in Grasshopper
3. Run the `__HBPH__Util_Update_GHCompos.py` script from Grasshopper to export
   `.ghuser` and `.py` files to the repo
4. Push to `main`
5. Tests run, but **no version bump or release happens** (that's the orchestrator's job)

---

## Releasing a User-Facing Update

When you're ready to publish a new version that users can install:

### Step 1: Ensure all library changes are published

Check that any library changes (PHX, honeybee_ph, etc.) have been pushed
and their CI has completed successfully. You can verify on PyPI that the
latest versions are live.

### Step 2: Run the Release Orchestrator

1. Go to **[honeybee_grasshopper_ph → Actions → "Release Honeybee-PH"](https://github.com/PH-Tools/honeybee_grasshopper_ph/actions/workflows/release.yml)**
2. Click **"Run workflow"**
3. Select the bump level (patch / minor / major)
4. Click **"Run workflow"**

The orchestrator will automatically:
- Fetch the latest versions of all PH-Tools packages from PyPI
- Update `requirements.txt` with those versions
- Bump `RELEASE_VERSION` in `_component_info_.py`
- Update the `hbph_installer.ghx` with current version pins
- Commit everything, create a git tag, and publish a GitHub Release

### Step 3: Release PH-Plus (if needed)

If you also updated `honeybee_grasshopper_ph_plus`:

1. Go to **[honeybee_grasshopper_ph_plus → Actions → "Release Honeybee-PH+"](https://github.com/PH-Tools/honeybee_grasshopper_ph_plus/actions/workflows/release.yml)**
2. Click **"Run workflow"**, select bump level, run it

### That's it!

Users running the installer will now get the latest versions of everything.

---

## One-Time Setup (per repo)

These steps need to be done once when migrating to the new system:

### For PyPI libraries

1. **Configure OIDC Trusted Publishing on PyPI:**
   - Go to pypi.org → your package → Settings → Publishing
   - Add a new "GitHub Actions" trusted publisher
   - Set: Owner = `PH-Tools`, Repository = `<repo-name>`, Workflow = `ci.yml`, Environment = `pypi`

2. **Create a GitHub Environment:**
   - Go to repo Settings → Environments → New environment → name it `pypi`

3. **Create GitHub Labels:**
   - Create labels `bump:minor` and `bump:major` in the repo

4. **Delete old files** (after verifying new CI works):
   - `setup.py`
   - `setup.cfg`
   - `deploy.sh`
   - `.releaserc.json`
   - `MANIFEST.in`
   - `.github/workflows/ci.yaml` (replaced by `ci.yml`)

### For Grasshopper repos

1. **Delete old workflow** (honeybee_grasshopper_ph only):
   - `.github/workflows/hugo.yml` can stay (docs deployment)
   - Delete `.github/workflows/ci.yaml` if it existed

---

## File Reference

### PyPI library repos — key files

```
pyproject.toml           # Single source of truth: build config, metadata,
                         # version, tool config, bump-my-version config
.github/workflows/ci.yml # Test → bump → build → publish to PyPI
```

### honeybee_grasshopper_ph — key files

```
pyproject.toml                           # bump-my-version config + code quality tools
honeybee_ph_rhino/_component_info_.py    # RELEASE_VERSION (auto-bumped by orchestrator)
requirements.txt                         # Version pins (auto-updated by orchestrator)
hbph_installer.ghx                       # Installer (auto-updated by orchestrator)
scripts/update_requirements.py           # Helper: updates requirements.txt
scripts/update_installer_ghx.py          # Helper: updates .ghx version pins
.github/workflows/tests.yml             # Run tests on every push
.github/workflows/release.yml           # Release orchestrator (manual trigger)
```

### honeybee_grasshopper_ph_plus — key files

```
pyproject.toml                                # bump-my-version config
honeybee_ph_plus_rhino/_component_info_.py    # RELEASE_VERSION
.github/workflows/tests.yml                  # Run tests on every push
.github/workflows/release.yml                # Release (manual or dispatched)
```

---

## Troubleshooting

**CI fails on "Publish to PyPI":**
Check that OIDC trusted publishing is configured on PyPI and that the
`pypi` GitHub environment exists in the repo settings.

**Version not bumping correctly:**
Run `bump-my-version show current_version` locally to verify the config.
Check that `[tool.bumpversion]` in `pyproject.toml` matches the actual
version string in the source file.

**Installer not updating:**
Run `python3 scripts/update_installer_ghx.py --honeybee-ph=X.Y.Z` locally
to test. The script looks for a Panel with NickName "requirements" in the
GHX XML.

**Infinite CI loop:**
The bump commit includes `[skip ci]` in the message. If CI is still
triggering, check that the commit message format in `pyproject.toml`
includes `[skip ci]`.
