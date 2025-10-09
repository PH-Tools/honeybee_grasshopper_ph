# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create PH Glazing."""

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph.properties.aperture import AperturePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


class GHCompo_SetApertureInstallDepth(object):
    """Interface to collect and clean user-inputs."""

    def __init__(self, _IGH, _apertures, _install_depth):
        # type: (gh_io.IGH, list[Aperture], str | None) -> None
        self.IGH = _IGH
        self._apertures = _apertures
        self._install_depth = self.calc_install_depth(_install_depth or "4 in.")

    def calc_install_depth(self, _install_depth):
        # type: (str) -> int | float
        """Calculate the install depth of the window glazing, considering Rhino unit-types."""

        # -- If the user supplied an input unit, just use that
        input_value, input_unit = parse_input(_install_depth)

        # -- otherwise use the Rhino document unit system as the input unit
        if not input_unit:
            input_unit = self.IGH.get_rhino_unit_system_name()

        # -- convert the input value to Meters, always
        install_depth = convert(input_value, input_unit, "M")

        if install_depth is None:
            raise ValueError("Failed to parse install depth input {}?".format(_install_depth))
        else:
            print("Converting: {} {} -> {:.4f} M".format(input_value, input_unit, install_depth))
            return install_depth

    def run(self):
        # type: () -> list[Aperture]
        apertures_ = []
        for aperture in self._apertures:
            dup_ap = aperture.duplicate()
            dup_ap_prop_ph = getattr(dup_ap.properties, "ph", None)  # type: AperturePhProperties | None
            if not dup_ap_prop_ph:
                raise ValueError(
                    "Aperture {} does not have PH properties. Cannot set install depth.".format(dup_ap.display_name)
                )
            dup_ap_prop_ph.install_depth = self._install_depth
            apertures_.append(dup_ap)
        return apertures_
