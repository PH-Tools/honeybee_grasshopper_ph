# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Aperture Psi-Installs.

Sets per-edge 'Install Type' assignments on the Aperture's PH-properties
(AperturePhProperties.install_types). The window construction is NEVER touched or
duplicated: per-window install conditions are aperture-instance data, resolved
against the construction's frame-element defaults downstream
(honeybee_ph_utils.aperture_psi_install). See honeybee_grasshopper_ph issue #59
for why per-aperture construction duplication must never come back.

`_install_types` accepts either of two shapes, because there are two ways to say
which Install Types belong to which Aperture:

  * a DATATREE, matched by branch index - one branch of up to four items per
    branch of Apertures, and every Aperture in a branch gets the same four. This
    is the hand-painting case: one install condition over a set of windows.
  * a KEYED COLLECTION - anything dict-like (`.get(key, default)` + `.keys()`)
    whose keys are Aperture display-names and whose values are the ordered list
    [top, right, bottom, left]. Matched per-Aperture by name, so the Aperture
    tree can be grafted or flattened however the user likes. This is the bulk
    case: a generator upstream already knows exactly which edges belong to which
    window. `honeybee_ph_plus_rhino`'s PH-Navigator getter emits one of these,
    though nothing here knows or cares about that - a plain dict works too.

Key matching exists because branch-index matching cannot express per-window
values against a FLAT list of Apertures: every Aperture would land in branch 0
and silently receive the first window's four Install Types.
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
    from honeybee_ph.properties.aperture import AperturePsiInstalls
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

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

# -- Input order follows PhWindowFrame element order: top / right / bottom / left
SIDES = AperturePsiInstalls.SIDES


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
    try:
        psi_install_w_mk = parse_psi_install_w_mk(_input)
    except Exception as e:
        # -- Most often a keyed collection that `as_keyed_lookup` did not recognise
        # -- (it needs both `.get()` and `.keys()`), which otherwise surfaces as a
        # -- bare float() TypeError from deep inside the parser.
        raise ValueError(
            "Cannot read '{}' as an Install Type or a psi-install value. Supply "
            "'PhApertureInstallType' objects, numbers / unit-strings, or a single "
            "dict-like collection keyed by Aperture name.\n\t{}".format(_input, e)
        )
    return build_install_type(None, psi_install_w_mk, "user-input")


def as_keyed_lookup(_tree):
    # type: (DataTree) -> object | None
    """Return the keyed collection `_install_types` carries, or None for a plain tree.

    Grasshopper hands a single collection object in as a one-item tree, so the two
    input shapes are told apart by what is actually inside: exactly one item, and
    that item dict-like. A `PhApertureInstallType`, a number and a unit-string all
    fail that test, so the branch-index path is never taken by surprise.
    """
    items = [item for branch in _tree.Branches for item in branch]
    if len(items) != 1:
        return None

    collection = items[0]
    if hasattr(collection, "get") and hasattr(collection, "keys"):
        return collection
    return None


def get_tree_item(_tree, _branch_idx, _item_idx):
    # type: (DataTree, int, int) -> object | None
    """Get a tree item with fallbacks: branch->first-branch, item->LAST-item.

    Returns None if the tree is empty (meaning: inherit from the construction).
    NOTE: unlike the first-item fallback used by some sibling components, the item
    fallback here is deliberately the LAST item: with t/r/b/l inputs, a single value
    applies to all four edges, and a partial list extends its final value.
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

        Side order is always top / right / bottom / left. A missing or empty entry
        leaves that edge as None (= inherit the construction frame default).
        """
        if not self.ready:
            return self._apertures

        lookup = as_keyed_lookup(self._install_types)
        if lookup is not None:
            return self._run_keyed(lookup)
        return self._run_by_branch()

    def _run_by_branch(self):
        # type: () -> DataTree
        """Match by branch index: every Aperture in a branch gets the same four."""
        output_ = DataTree[Object]()
        for branch_idx, apertures in enumerate(self._apertures.Branches):
            # -- Coerce the branch's inputs ONCE: all apertures on a branch share the
            # -- same four Install Type objects (shared named types, like constructions).
            install_types_by_side = []  # type: list[PhApertureInstallType | None]
            for side_idx, side in enumerate(SIDES):
                install_type = as_install_type(get_tree_item(self._install_types, branch_idx, side_idx))
                install_types_by_side.append(install_type)
                if install_type is not None:
                    print(
                        "Branch {}: {} << '{}' (Psi={:.4f} W/mK)".format(
                            branch_idx, side, install_type.display_name, install_type.psi_install
                        )
                    )

            dup_aps = []  # type: list[Aperture]
            for ap in apertures:
                dup_aps.append(self._assign(ap, install_types_by_side))

            output_.AddRange(dup_aps, GH_Path(branch_idx))

        return output_

    def _run_keyed(self, _lookup):
        # type: (object) -> DataTree
        """Match each Aperture to the collection by its display-name.

        Immune to tree topology, so the input paths are preserved as-is rather than
        renumbered. An Aperture whose name is not in the collection is passed through
        untouched - leaving its slots None means 'inherit the construction default',
        which is the honest answer when the collection said nothing about it.
        """
        output_ = DataTree[Object]()
        unmatched = []  # type: list[str]

        for branch_idx, apertures in enumerate(self._apertures.Branches):
            dup_aps = []  # type: list[Aperture]
            for ap in apertures:
                install_types = _lookup.get(ap.display_name, None)
                if install_types is None or len(install_types) != len(SIDES):
                    # -- A short list would be truncated silently by zip(), leaving
                    # -- some edges assigned and some inherited. Refuse it instead.
                    unmatched.append(ap.display_name)
                    dup_aps.append(ap)
                    continue
                dup_aps.append(self._assign(ap, [as_install_type(i) for i in install_types]))

            output_.AddRange(dup_aps, self._apertures.Paths[branch_idx])

        self._warn_unmatched(unmatched)
        return output_

    def _assign(self, _aperture, _install_types_by_side):
        # type: (Aperture, list[PhApertureInstallType | None]) -> Aperture
        """Return a duplicate of the Aperture with its four Install Type slots set."""
        dup_ap = _aperture.duplicate()  # type: Aperture
        ph_prop = dup_ap.properties.ph
        for side_idx, side in enumerate(SIDES):
            setattr(ph_prop.install_types, side, _install_types_by_side[side_idx])
        return dup_ap

    def _warn_unmatched(self, _unmatched):
        # type: (list[str]) -> None
        """Surface any Apertures the collection had nothing usable for."""
        if not _unmatched:
            print("All Apertures matched an Install-Type set.")
            return

        self.IGH.warning(
            "{} Aperture(s) did not match a usable entry in the Install-Type collection "
            "and were left to inherit their construction's frame defaults: {}".format(
                len(_unmatched), ", ".join(sorted(set(_unmatched)))
            )
        )
