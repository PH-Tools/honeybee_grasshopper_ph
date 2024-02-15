# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH Location"""

try:
    from typing import Optional
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
        # type: (gh_io.IGH, str, float, float, Optional[float], int, int) -> None
        self.IGH = _IGH
        self.display_name = _display_name or "New York"
        self.latitude = _latitude
        self.longitude = _longitude
        self.site_elevation = _site_elevation or None
        self.climate_zone = _climate_zone or 1
        self.hours_from_UTC = _hours_from_UTC or -4

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
