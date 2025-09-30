# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH Climate Peak Load."""

try:
    from honeybee_ph import site
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreatePeakLoad(object):
    display_name = ghio_validators.HBName("display_name")
    temp = ghio_validators.UnitDegreeC("temp", default=0.0)
    rad_north = ghio_validators.UnitKWH_M2("rad_north", default=0.0)
    rad_east = ghio_validators.UnitKWH_M2("rad_east", default=0.0)
    rad_south = ghio_validators.UnitKWH_M2("rad_south", default=0.0)
    rad_west = ghio_validators.UnitKWH_M2("rad_west", default=0.0)
    rad_global = ghio_validators.UnitKWH_M2("rad_global", default=0.0)
    dewpoint_temp = ghio_validators.UnitDegreeC("dewpoint_temp")
    ground_temp = ghio_validators.UnitDegreeC("ground_temp")
    sky_temp = ghio_validators.UnitDegreeC("sky_temp")

    def __init__(
        self,
        _IGH,
        _display_name,
        _temp,
        _rad_north,
        _rad_east,
        _rad_south,
        _rad_west,
        _rad_global,
        _dewpoint_temp,
        _ground_temp,
        _sky_temp,
    ):
        # type: (gh_io.IGH, str, float, float, float, float, float, float, float | None, float | None, float | None) -> None
        self.IGH = _IGH
        self.display_name = _display_name
        self.temp = _temp
        self.rad_north = _rad_north
        self.rad_east = _rad_east
        self.rad_south = _rad_south
        self.rad_west = _rad_west
        self.rad_global = _rad_global
        self.dewpoint_temp = _dewpoint_temp
        self.ground_temp = _ground_temp
        self.sky_temp = _sky_temp

    def run(self):
        # type: () -> site.Climate_PeakLoadValueSet
        hbph_obj = site.Climate_PeakLoadValueSet(
            self.temp,
            self.rad_north,
            self.rad_east,
            self.rad_south,
            self.rad_west,
            self.rad_global,
            self.dewpoint_temp,
            self.ground_temp,
            self.sky_temp,
        )
        hbph_obj.display_name = self.display_name

        return hbph_obj
