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
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.properties.aperture import ApertureEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction.window import PhWindowFrame
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


def get_ph_frame(self):
    # type: (Aperture) -> PhWindowFrame | None
    """Get the PH frame type from an Aperture."""

    ap_prop_energy = getattr(self, "properties", None)
    if not ap_prop_energy:
        return None
    if ap_prop_energy and ap_prop_energy.energy.construction and ap_prop_energy.energy.construction.properties:
        return ap_prop_energy.energy.construction.properties.ph.ph_frame
    return None


def set_ph_frame(aperture, ph_frame):
    # type: (Aperture, PhWindowFrame) -> Aperture
    """Set the PH frame type on an Aperture."""

    dup_ap_prop_energy = getattr(aperture.properties, "energy", None)  # type: ApertureEnergyProperties | None
    if not dup_ap_prop_energy:
        raise ValueError("Aperture {} has no Energy properties?".format(aperture.display_name))
    dup_ap_const_prop = getattr(dup_ap_prop_energy.construction, "properties", None)
    if not dup_ap_const_prop:
        raise ValueError(
            "Aperture Construction {} has no Energy construction?".format(dup_ap_prop_energy.construction.display_name)
        )
    dup_ap_const_prop.ph.ph_frame = ph_frame

    return aperture


class GHCompo_SetAperturePsiInstallValues(object):
    """Interface to collect and clean user-inputs."""

    def __init__(self, _IGH, _psi_install_values, _apertures, *args, **kwargs):
        # type: (gh_io.IGH, DataTree[str], DataTree[Aperture], list, dict) -> None
        self.IGH = _IGH
        self.psi_install_values_w_mk = self.set_psi_install_values_w_mk(_psi_install_values)
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

    def set_psi_install_values_w_mk(self, _input):
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

                dup_ap = ap.duplicate()  # type: Aperture
                ph_frame = get_ph_frame(dup_ap)
                if not ph_frame:
                    print("Aperture {} has no PH frame?".format(dup_ap.display_name))
                    continue

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
