# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH Location"""

try:
    from typing import Optional, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph import site
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_Location(object):
    display_name = ghio_validators.HBName("display_name")
    site_elevation = ghio_validators.UnitM("site_elevation", default=0.0)
    latitude = ghio_validators.Float("latitude", default=40.6)
    longitude = ghio_validators.Float("longitude", default=-73.8)
    _allowable_climate_zones = {
        1: "Not defined",
        11: "US 1",
        12: "US 2",
        13: "US 3",
        14: "US 4",
        141: "US 4C",
        15: "US 5",
        16: "US 6",
        17: "US 7",
        18: "US 8",
    }

    def __init__(
        self,
        _IGH,
        _display_name,
        _latitude,
        _longitude,
        _site_elevation,
        _climate_zone,
        _hours_from_UTC,
    ):
        # type: (gh_io.IGH, Optional[str], Optional[float], Optional[float], Optional[float], Optional[int], Optional[int]) -> None
        self.IGH = _IGH
        self.display_name = _display_name or "New York"
        self.latitude = _latitude or 40.6
        self.longitude = _longitude or -73.8
        self.site_elevation = _site_elevation or None
        self.climate_zone = self.clean_climate_zone(_climate_zone or 1)
        self.hours_from_UTC = _hours_from_UTC or -4

    def clean_climate_zone(self, _cz_input):
        # type: (Union[str, int]) -> int
        """Check the input climate zone and return the number."""

        cz_number = gh_io.input_to_int(str(_cz_input))
        if not cz_number:
            return 1

        if cz_number not in self._allowable_climate_zones.keys():
            msg = "Climate zone number must be one of the following:\n"
            msg += ", ".join(["'{}-{}'".format(k, v) for k, v in self._allowable_climate_zones.items()])
            self.IGH.error(msg)
            return 1

        return cz_number

    def run(self):
        # type: () -> site.Location
        hbph_obj = site.Location(
            self.latitude,
            self.longitude,
            self.site_elevation,
            self.climate_zone,
            self.hours_from_UTC,
        )
        hbph_obj.display_name = self.display_name

        return hbph_obj
