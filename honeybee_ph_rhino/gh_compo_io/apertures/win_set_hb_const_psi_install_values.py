# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set HB-Construction Psi-Installs."""

from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from System import Object

try:
    from honeybee_energy.construction.window import WindowConstruction
    from honeybee_energy.construction.windowshade import WindowConstructionShade
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction.window import PhWindowFrame
    from honeybee_energy_ph.properties.construction.window import WindowConstructionPhProperties
    from honeybee_energy_ph.properties.construction.windowshade import WindowConstructionShadePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


def _get_ph_properties(_construction):
    # type: (WindowConstruction | WindowConstructionShade) -> WindowConstructionPhProperties | WindowConstructionShadePhProperties
    """Return the PH-properties object from a WindowConstruction or WindowConstructionShade."""

    if isinstance(_construction, WindowConstructionShade):
        return getattr(_construction.window_construction.properties, "ph")  # type: WindowConstructionShadePhProperties
    elif isinstance(_construction, WindowConstruction):
        return getattr(_construction.properties, "ph")  # type: WindowConstructionPhProperties
    else:
        raise ValueError("Unsupported construction type: {}".format(type(_construction)))


def _parse_single_psi_value(_raw_input):
    # type: (str) -> float
    """Parse a single user-provided psi-install string and return the value in W/mK."""

    input_value, input_unit = parse_input(_raw_input)
    if not input_value:
        raise ValueError("Failed to parse Psi-Install input: '{}'".format(_raw_input))

    input_unit = input_unit or "W/MK"
    result = convert(input_value, input_unit, "W/mK")
    if result is None:
        raise ValueError("Failed to convert Psi-Install input {} {} to W/mK".format(input_value, input_unit))

    print("Converting: {} {} -> {:.4f} W/mK".format(input_value, input_unit, result))
    return result


def _parse_psi_install_tree(_input):
    # type: (DataTree[str]) -> DataTree[float]
    """Convert a DataTree of user-provided psi-install strings to W/mK values."""

    output_ = DataTree[float]()
    for branch_idx, branch in enumerate(_input.Branches):
        for raw_value in branch:
            output_.Add(_parse_single_psi_value(raw_value), GH_Path(branch_idx))
    return output_


def _get_psi_value_from_tree(_tree, _branch_idx, _element_idx):
    # type: (DataTree[float], int, int) -> float
    """Get the psi-install value for a given branch/element index, with fallbacks.

    Falls back to branch-0 if the branch index is out of range,
    and to element-0 if the element index is out of range.
    """

    try:
        branch = _tree.Branches[_branch_idx]
    except ValueError:
        try:
            branch = _tree.Branches[0]
        except ValueError:
            raise ValueError("No Psi-Install values were provided?")

    try:
        return branch[_element_idx]
    except ValueError:
        try:
            return branch[0]
        except ValueError:
            raise ValueError("No Psi-Install values on branch {}?".format(_branch_idx))


def _apply_psi_values_to_frame(_ph_frame, _psi_tree, _branch_idx):
    # type: (PhWindowFrame, DataTree[float], int) -> PhWindowFrame
    """Duplicate a PhWindowFrame and apply psi-install values to each element."""

    dup_frame = _ph_frame.duplicate()  # type: PhWindowFrame
    for element_idx, element in enumerate(dup_frame.elements):
        psi_value = _get_psi_value_from_tree(_psi_tree, _branch_idx, element_idx)
        element.psi_install = psi_value
        print("  element {}: {} << Psi-{} W/mk".format(element_idx, element, psi_value))
    return dup_frame


def _update_single_construction(_construction, _psi_tree, _branch_idx):
    # type: (WindowConstruction | WindowConstructionShade, DataTree[float], int) -> WindowConstruction | WindowConstructionShade | None
    """Duplicate a construction and apply psi-install values to its PH frame. Returns None if no PH frame."""

    dup = _construction.duplicate()
    ph_props = _get_ph_properties(dup)

    if not ph_props.ph_frame:
        print("Construction '{}' has no PH frame -- skipping.".format(dup.identifier))
        return None

    ph_props.ph_frame = _apply_psi_values_to_frame(ph_props.ph_frame, _psi_tree, _branch_idx)
    return dup


class GHCompo_SetWindowConstructionPsiInstallValues(object):
    """Interface to collect and clean user-inputs."""

    def __init__(self, _IGH, _psi_install_values, _constructions, *args, **kwargs):
        # type: (gh_io.IGH, DataTree[str], DataTree, *list, **dict) -> None
        self.IGH = _IGH
        self.psi_values = _parse_psi_install_tree(_psi_install_values)
        self._constructions = _constructions

    @property
    def ready(self):
        # type: () -> bool
        if len(self._constructions.Branches) == 0:
            return False
        if len(self.psi_values.Branches) == 0:
            return False
        return True

    def run(self):
        # type: () -> DataTree
        if not self.ready:
            return self._constructions

        output_ = DataTree[Object]()
        for branch_idx, constructions in enumerate(self._constructions.Branches):
            results = []
            for construction in constructions:
                print("Processing branch {} construction: {}".format(branch_idx, construction.identifier))
                updated = _update_single_construction(construction, self.psi_values, branch_idx)
                if updated is not None:
                    results.append(updated)
            output_.AddRange(results, GH_Path(branch_idx))

        return output_
