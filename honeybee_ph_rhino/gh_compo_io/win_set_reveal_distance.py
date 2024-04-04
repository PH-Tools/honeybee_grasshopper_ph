# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create PH Glazing."""

try:
    from typing import Any, List, Optional, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph.properties.aperture import AperturePhProperties, ShadingDimensions
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


class GHCompo_SetApertureRevealDistance(object):
    """Interface to collect and clean user-inputs."""

    def __init__(self, _IGH, _reveal_distance, _apertures, *args, **kwargs):
        # type: (gh_io.IGH, Optional[str], List[Aperture], *Any, **Any) -> None
        self.IGH = _IGH
        self._reveal_distance = self.calc_reveal_distance(_reveal_distance)
        self._apertures = _apertures

    def calc_reveal_distance(self, _install_depth):
        # type: (Optional[str]) -> Optional[Union[int, float]]
        """Calculate the reveal distance of the window glazing, considering Rhino unit-types."""
        if not _install_depth:
            return None

        # -- If the user supplied an input unit, just use that
        input_value, input_unit = parse_input(_install_depth)

        # -- otherwise use the Rhino document unit system as the input unit
        if not input_unit:
            input_unit = self.IGH.get_rhino_unit_system_name()

        # -- convert the input value to Meters, always
        install_depth = convert(input_value, input_unit, "M")

        if not install_depth:
            raise ValueError("Failed to parse reveal-distance input {}?".format(_install_depth))
        else:
            print("Converting: {} {} -> {:.4f} M".format(input_value, input_unit, install_depth))
            return install_depth

    def run(self):
        # type: () -> List[Aperture]
        apertures_ = []
        for aperture in self._apertures:
            dup_ap = aperture.duplicate()
            ph_prop = dup_ap.properties.ph  # type: AperturePhProperties # type: ignore

            if self._reveal_distance:
                if not ph_prop.shading_dimensions:
                    ph_prop.shading_dimensions = ShadingDimensions()

                ph_prop.shading_dimensions.d_reveal = self._reveal_distance
                ph_prop.shading_dimensions.o_reveal = self._reveal_distance

            apertures_.append(dup_ap)

        return apertures_
