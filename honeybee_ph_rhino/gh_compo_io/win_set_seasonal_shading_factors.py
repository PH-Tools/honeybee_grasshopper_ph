# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Seasonal Shading Factors."""

try:
    from typing import Dict, List
except ImportError:
    pass  # IronPython 2.7

try:
    from itertools import izip_longest as zip_longest  # type: ignore # Python-2
except ImportError:
    from itertools import zip_longest

    # Python 3

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph.properties.aperture import AperturePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_SetWindowSeasonalShadingFactors(object):
    def __init__(
        self, _IGH, _hb_apertures, _winter_factors, _summer_factors, *args, **kwargs
    ):
        # type: (gh_io.IGH, List[Aperture], List[float], List[float], List, Dict) -> None
        self.IGH = _IGH
        self.hb_apertures = _hb_apertures
        self.winter_factors = _winter_factors
        self.summer_factors = _summer_factors

    def clean_factor(self, factor):
        # type: (float) -> float
        """Ensure the factor is between 0.0 and 1.0"""
        if factor < 0.0:
            print("Factor cannot be less than 0.0. Setting it to 0.0.")
            return 0.0
        elif factor > 1.0:
            new_factor = factor / 100
            print(
                "Factor {} is greater than 1.0. Setting to: {:.2f}".format(
                    factor, new_factor
                )
            )
            return self.clean_factor(new_factor)
        else:
            return factor

    def run(self):
        # type: () -> List[Aperture]
        apertures_ = []
        for ap, w_factor, s_factor in zip_longest(
            self.hb_apertures, self.winter_factors, self.summer_factors
        ):
            new_ap = ap.duplicate()
            new_ap_ph_prop = (
                new_ap.properties.ph # type: ignore
            )  # type: AperturePhProperties 

            if w_factor is not None:
                new_ap_ph_prop.winter_shading_factor = self.clean_factor(w_factor)
                print(
                    "Setting aperture {} winter factor to: {:.2f}".format(
                        new_ap.display_name, w_factor
                    )
                )

            if s_factor is not None:
                new_ap_ph_prop.summer_shading_factor = self.clean_factor(s_factor)
                print(
                    "Setting aperture {} summer factor to: {:.2f}".format(
                        new_ap.display_name, s_factor
                    )
                )

            apertures_.append(new_ap)
        return apertures_
