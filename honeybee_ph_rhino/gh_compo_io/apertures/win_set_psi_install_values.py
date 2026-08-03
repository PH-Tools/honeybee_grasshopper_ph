# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Aperture Psi-Installs."""


from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from System import Object

try:
    from itertools import izip_longest  # type: ignore
except ImportError:
    from itertools import zip_longest as izip_longest

try:
    from honeybee.aperture import Aperture
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.construction.window import WindowConstruction
    from honeybee_energy.construction.windowshade import WindowConstructionShade
    from honeybee_energy.properties.aperture import ApertureEnergyProperties
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
    """Return the PH properties for a regular or shaded window construction."""

    if isinstance(_construction, WindowConstructionShade):
        return getattr(_construction.window_construction.properties, "ph")
    if isinstance(_construction, WindowConstruction):
        return getattr(_construction.properties, "ph")
    raise ValueError("Unsupported construction type: {}".format(type(_construction)))


def get_ph_frame(_aperture):
    # type: (Aperture) -> PhWindowFrame | None
    """Get the PH frame type from an Aperture."""

    ap_prop_energy = getattr(_aperture.properties, "energy", None)  # type: ApertureEnergyProperties | None
    if not ap_prop_energy:
        raise ValueError("Aperture {} has no properties.energy ?".format(_aperture.display_name))
    return _get_ph_properties(ap_prop_energy.construction).ph_frame


def set_ph_frame(_aperture, _ph_frame):
    # type: (Aperture, PhWindowFrame) -> Aperture
    """Set the PH frame type on an Aperture."""

    ap_prop_energy = getattr(_aperture.properties, "energy", None)  # type: ApertureEnergyProperties | None
    if not ap_prop_energy:
        raise ValueError("Aperture {} has no properties.energy ?".format(_aperture.display_name))

    _get_ph_properties(ap_prop_energy.construction).ph_frame = _ph_frame
    return _aperture


def duplicate_aperture_construction(_aperture):
    # type: (Aperture) -> Aperture
    """Give an aperture its own window construction and identifier."""

    ap_prop_energy = getattr(_aperture.properties, "energy", None)  # type: ApertureEnergyProperties | None
    if not ap_prop_energy:
        raise ValueError("Aperture {} has no properties.energy ?".format(_aperture.display_name))

    construction = ap_prop_energy.construction
    aperture_suffix = _aperture.identifier

    if isinstance(construction, WindowConstructionShade):
        dup_construction = construction.duplicate()  # type: WindowConstructionShade
        dup_window_construction = construction.window_construction.duplicate()  # type: WindowConstruction
        dup_window_construction.identifier = clean_and_id_ep_string(
            "{}_{}".format(construction.window_construction.identifier, aperture_suffix)
        )
        dup_window_construction.lock()
        # WindowConstructionShade.duplicate() retains the nested construction,
        # and Honeybee exposes no public setter for replacing it.
        dup_construction._window_construction = dup_window_construction
    elif isinstance(construction, WindowConstruction):
        dup_construction = construction.duplicate()  # type: WindowConstruction
    else:
        raise ValueError(
            "Aperture {} construction is an unsupported type: {}?".format(_aperture.display_name, type(construction))
        )

    dup_construction.identifier = clean_and_id_ep_string("{}_{}".format(construction.identifier, aperture_suffix))
    ap_prop_energy.construction = dup_construction
    return _aperture


class GHCompo_SetAperturePsiInstallValues(object):
    """Interface to collect and clean user-inputs."""

    def __init__(self, _IGH, _psi_install_values, _apertures, *args, **kwargs):
        # type: (gh_io.IGH, DataTree[str], DataTree[Aperture], list, dict) -> None
        self.IGH = _IGH
        self.psi_install_values_w_mk = self._set_psi_install_values_w_mk(_psi_install_values)
        self._apertures = _apertures

    @property
    def ready(self):
        # type: () -> bool
        """Check if the component has the minimum required inputs to run."""

        if len(self._apertures.Branches) == 0:
            return False
        if len(self.psi_install_values_w_mk.Branches) == 0:
            return False
        return True

    def _set_psi_install_values_w_mk(self, _input):
        # type: (DataTree[str]) -> DataTree[float]
        """Convert the input psi-install values to W/mK, considering User-provded unit-types."""

        output_ = DataTree[float]()
        for branch_idx, psi_install_branch in enumerate(_input.Branches):
            parse_inputs = [parse_input(val) for val in psi_install_branch]
            for element_idx, (input_value, input_unit) in enumerate(parse_inputs):
                if not input_value:
                    raise ValueError("Failed to parse Psi-Install input {}?".format(psi_install_branch[element_idx]))

                # -- If the user supplied an input unit, just use that
                if not input_unit:
                    input_unit = "W/MK"

                # -- convert the input value to W/mK, always
                psi_install_value_w_mk = convert(input_value, input_unit, "W/mK")
                if psi_install_value_w_mk is None:
                    raise ValueError(
                        "Failed to convert Psi-Install input {} {} to W/mK?".format(input_value, input_unit)
                    )
                else:
                    print("Converting: {} {} -> {:.4f} W/mK".format(input_value, input_unit, psi_install_value_w_mk))
                    output_.Add(psi_install_value_w_mk, GH_Path(branch_idx))
        return output_

    def get_psi_install_value(self, branch_idx, element_idx):
        # type: (int, int) -> float
        """Get the right psi-install value for a given frame element, with fallbacks."""

        # -- Get the branch of psi-install values to use, defaulting to the first branch if the index is out of range
        try:
            psi_install_branch = self.psi_install_values_w_mk.Branches[branch_idx]
        except ValueError:
            try:
                psi_install_branch = self.psi_install_values_w_mk.Branches[0]
            except ValueError:
                raise ValueError("No Psi-Install values were provided?")

        # -- Get the psi-install value to use, defaulting to the last value in the branch if the index is out of range
        try:
            psi_install_value = psi_install_branch[element_idx]
        except ValueError:
            try:
                psi_install_value = psi_install_branch[0]
            except ValueError:
                raise ValueError("No Psi-Install values were provided on branch {}?".format(branch_idx))

        return psi_install_value

    def run(self):
        # type: () -> DataTree
        """Run the component and return the output apertures with updated Psi-Install values."""

        if not self.ready:
            return self._apertures

        output_ = DataTree[Object]()
        for branch_idx, apertures in enumerate(self._apertures.Branches):
            dup_aps = []  # type: list[Aperture]
            for ap in apertures:
                print("Processing aperture: {}".format(ap.display_name))

                ph_frame = get_ph_frame(ap)
                if not ph_frame:
                    print("Aperture {} has no PH frame?".format(ap.display_name))
                    continue

                dup_ap = ap.duplicate()  # type: Aperture
                duplicate_aperture_construction(dup_ap)

                # -- Get and apply the right Psi-Install values to the frame elements
                dup_ph_frame = ph_frame.duplicate()  # type: PhWindowFrame
                for element_idx, element in enumerate(dup_ph_frame.elements):
                    psi_install_value_w_mk = self.get_psi_install_value(branch_idx, element_idx)
                    element.psi_install = psi_install_value_w_mk
                    print("element {}: {} << Psi-{} W/mk".format(element_idx, element, psi_install_value_w_mk))

                # -- Assign the updated frame back to the aperture
                dup_ap_with_ph_frame = set_ph_frame(dup_ap, dup_ph_frame)
                dup_aps.append(dup_ap_with_ph_frame)

            output_.AddRange(dup_aps, GH_Path(branch_idx))

        return output_
