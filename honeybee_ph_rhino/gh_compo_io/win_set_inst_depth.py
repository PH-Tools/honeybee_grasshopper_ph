# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create PH Glazing."""

try:
    from typing import List, Optional
except ImportError:
    pass # IronPython 2.7

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_ph.properties.aperture import AperturePhProperties
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError('\nFailed to import ph_units:\n\t{}'.format(e))


class GHCompo_SetApertureInstallDepth(object):
    """Interface to collect and clean PhWindowGlazing user-inputs."""

    def __init__(self, _IGH, _apertures, _install_depth):
        # type: (gh_io.IGH, List[Aperture], Optional[str]) -> None
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

        if not install_depth:
            raise ValueError("Failed to parse install depth input {}?".format(_install_depth))
        else:
            print("Converting: {} {} -> {:.4f} M".format(input_value, input_unit, install_depth))
            return install_depth

    def run(self):
        # type: () -> List[Aperture]
        apertures_ = []
        for aperture in self._apertures:
            dup_ap = aperture.duplicate()
            dup_ap.properties.ph.install_depth = self._install_depth # type: ignore
            apertures_.append(dup_ap)
        return apertures_