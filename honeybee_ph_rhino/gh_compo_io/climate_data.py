# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH Climate Data."""

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


class GHCompo_ClimateData(object):
    display_name = ghio_validators.HBName("display_name")
    station_elevation = ghio_validators.UnitM("station_elevation", default=0.0)
    daily_temp_swing = ghio_validators.UnitDeltaC("daily_temp_swing", default=8.0)
    average_wind_speed = ghio_validators.UnitMeterPerSecond("average_wind_speed", default=4.0)

    def __init__(
        self,
        _IGH,
        _display_name,
        _station_elevation,
        _daily_temp_swing,
        _average_wind_speed,
        _monthly_temps,
        _monthly_radiation,
        _peak_heat_load_1,
        _peak_heat_load_2,
        _peak_cooling_load_1,
        _peak_cooling_load_2,
    ):
        # type: (gh_io.IGH, Optional[str], Optional[float], Optional[float], Optional[float], Optional[site.Climate_MonthlyTempCollection], Optional[site.Climate_MonthlyRadiationCollection],site.Climate_PeakLoadValueSet, Optional[site.Climate_PeakLoadValueSet], Optional[site.Climate_PeakLoadValueSet], Optional[site.Climate_PeakLoadValueSet]) -> None
        self.IGH = _IGH
        self.display_name = _display_name or "_unnamed_climate_"
        self.station_elevation = _station_elevation or 0.0
        self.daily_temp_swing = _daily_temp_swing or 8.0
        self.average_wind_speed = _average_wind_speed or 4.0
        self.monthly_temps = _monthly_temps or site.Climate_MonthlyTempCollection()
        self.monthly_radiation = _monthly_radiation or site.Climate_MonthlyRadiationCollection()
        self.heat_load_1 = _peak_heat_load_1 or site.Climate_PeakLoadValueSet()
        self.heat_load_2 = _peak_heat_load_2 or site.Climate_PeakLoadValueSet()
        self.cooling_load_1 = _peak_cooling_load_1 or site.Climate_PeakLoadValueSet()
        self.cooling_load_2 = _peak_cooling_load_2 or site.Climate_PeakLoadValueSet()

    def run(self):
        # type: () -> site.Climate

        peak_loads = site.Climate_PeakLoadCollection(
            self.heat_load_1, self.heat_load_2, self.cooling_load_1, self.cooling_load_2
        )

        hbph_climate = site.Climate(
            _display_name=self.display_name,
            _station_elevation=self.station_elevation,
            _daily_temp_swing=self.daily_temp_swing,
            _average_wind_speed=self.average_wind_speed,
            _monthly_temps=self.monthly_temps,
            _monthly_radiation=self.monthly_radiation,
            _peak_loads=peak_loads,
        )

        return hbph_climate
