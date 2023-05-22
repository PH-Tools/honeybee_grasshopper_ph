# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Monthly Shade Factor."""

try:
    from typing import Dict, List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_SetWindowMonthlyShadeFactor(object):
    def __init__(self, _IGH, _apertures, _factors, *args, **kwargs):
        # type: (gh_io.IGH, List[Aperture], List[float], List, Dict) -> None
        self.IGH = _IGH
        self.apertures = _apertures
        self.factors = _factors

    def get_factor(self, i):
        # type: (int) -> float
        try:
            return self.factors[i]
        except IndexError:
            try:
                return self.factors[0]
            except IndexError:
                return 1.0

    def run(self):
        # type: () -> List[Aperture]
        apertures_ = []
        for i, aperture in enumerate(self.apertures):
            new_ap = aperture.duplicate()
            f = self.get_factor(i)
            new_ap.properties.ph.default_monthly_shading_correction_factor = f
            apertures_.append(new_ap)

        return apertures_
