# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Monthly Shade Factor."""

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


class GHCompo_SetWindowMonthlyShadeFactor(object):
    def __init__(self, _IGH, _apertures, _factors, *args, **kwargs):
        # type: (gh_io.IGH, list[Aperture], list[float], list, dict) -> None
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
        # type: () -> list[Aperture]
        apertures_ = []
        for i, aperture in enumerate(self.apertures):
            new_ap = aperture.duplicate()
            f = self.get_factor(i)
            ap_prop_ph = getattr(new_ap.properties, "ph", None)  # type: AperturePhProperties | None
            if not ap_prop_ph:
                raise ValueError(
                    "Aperture {} does not have PH properties. Cannot set monthly shading factor.".format(
                        new_ap.display_name
                    )
                )
            ap_prop_ph.default_monthly_shading_correction_factor = f
            apertures_.append(new_ap)

        return apertures_
