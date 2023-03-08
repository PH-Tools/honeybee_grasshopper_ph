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
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

class GHCompo_SetApertureInstallDepth(object):
    """Interface to collect and clean PhWindowGlazing user-inputs."""

    _install_depth = ghio_validators.UnitM("_install_depth")

    def __init__(self, _IGH, _apertures, _install_depth):
        # type: (gh_io.IGH, List[Aperture], Optional[str]) -> None
        self.IGH = _IGH
        self._apertures = _apertures
        self._install_depth = _install_depth or 0.106

    def run(self):
        # type: () -> List[Aperture]
        apertures_ = []
        for aperture in self._apertures:
            dup_ap = aperture.duplicate()
            dup_ap.properties.ph.install_depth = self._install_depth
            apertures_.append(dup_ap)
        return apertures_