# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Calculate Phius Blind Transmittance."""

try:
    from ph_gh_component_io import validators
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))


class GHCompo_CalcPhiusShadeTransmittance(object):
    transmittance = validators.FloatPercentage("transmittance")

    def __init__(self, _transmittance, _inside):
        # type: (float, bool) -> None
        print(_transmittance)
        self.transmittance = _transmittance or 0.85
        self.inside = _inside

    def run(self):
        # type: () -> tuple[float, float]
        """Calculate the effective reduction factor according to Phius Guidebook v3.1, Appendix N-8"""

        if self.inside is False:
            transmittance_eff = 0.3 + (0.7 * self.transmittance)
        else:
            transmittance_eff = 1 - (1 - self.transmittance) * (1 - 0.6)

        reflectance = 1.0 - transmittance_eff

        return (transmittance_eff, reflectance)
