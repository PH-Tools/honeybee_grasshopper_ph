# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Aperture Psi-Installs.

Sets per-edge 'Install Type' assignments on the Aperture's PH-properties
(AperturePhProperties.install_types). The window construction is NEVER touched or
duplicated: per-window install conditions are aperture-instance data, resolved
against the construction's frame-element defaults downstream
(honeybee_ph_utils.aperture_psi_install). See honeybee_grasshopper_ph issue #59
for why per-aperture construction duplication must never come back.
"""

from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from System import Object

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction.window import PhApertureInstallType
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

try:
    from honeybee_ph_rhino.gh_compo_io.apertures.win_create_install_type import (
        build_install_type,
        parse_psi_install_w_mk,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

# -- Input order follows PhWindowFrame element order (and AperturePsiInstalls.SIDES)
SIDES = ("top", "right", "bottom", "left")


def as_install_type(_input):
    # type: (PhApertureInstallType | str | float | None) -> PhApertureInstallType | None
    """Coerce a component input to a PhApertureInstallType (or None to inherit).

    Accepts a PhApertureInstallType directly, or a bare number / unit-string which is
    wrapped in an anonymous Install Type with a content-keyed identifier (no uuids -
    repeated values dedupe downstream).
    """
    if _input is None or _input == "":
        return None
    if isinstance(_input, PhApertureInstallType):
        return _input
    psi_install_w_mk = parse_psi_install_w_mk(_input)
    return build_install_type(None, psi_install_w_mk, "user-input")


def get_tree_item(_tree, _branch_idx, _item_idx):
    # type: (DataTree, int, int) -> object | None
    """Get a tree item with the standard fallbacks: branch->first-branch, item->last-item.

    Returns None if the tree is empty (meaning: inherit from the construction).
    """
    if len(_tree.Branches) == 0:
        return None

    try:
        branch = _tree.Branches[_branch_idx]
    except Exception:
        branch = _tree.Branches[0]

    if len(branch) == 0:
        return None

    try:
        return branch[_item_idx]
    except Exception:
        return branch[len(branch) - 1]


class GHCompo_SetAperturePsiInstallValues(object):
    """Interface to collect and clean user-inputs."""

    def __init__(self, _IGH, _install_types, _apertures, *args, **kwargs):
        # type: (gh_io.IGH, DataTree, DataTree[Aperture], list, dict) -> None
        self.IGH = _IGH
        self._install_types = _install_types
        self._apertures = _apertures

    @property
    def ready(self):
        # type: () -> bool
        """Check if the component has the minimum required inputs to run."""
        if len(self._apertures.Branches) == 0:
            return False
        if len(self._install_types.Branches) == 0:
            return False
        return True

    def run(self):
        # type: () -> DataTree
        """Return duplicated Apertures with their per-edge Install Types assigned.

        Input order per-branch is top / right / bottom / left. A missing or empty
        input leaves that edge as None (= inherit the construction frame default).
        """
        if not self.ready:
            return self._apertures

        output_ = DataTree[Object]()
        for branch_idx, apertures in enumerate(self._apertures.Branches):
            dup_aps = []  # type: list[Aperture]
            for ap in apertures:
                dup_ap = ap.duplicate()  # type: Aperture
                ph_prop = dup_ap.properties.ph

                for side_idx, side in enumerate(SIDES):
                    install_type = as_install_type(get_tree_item(self._install_types, branch_idx, side_idx))
                    setattr(ph_prop.install_types, side, install_type)
                    if install_type is not None:
                        print(
                            "{}: {} << '{}' (Psi={:.4f} W/mK)".format(
                                dup_ap.display_name, side, install_type.display_name, install_type.psi_install
                            )
                        )

                dup_aps.append(dup_ap)

            output_.AddRange(dup_aps, GH_Path(branch_idx))

        return output_
