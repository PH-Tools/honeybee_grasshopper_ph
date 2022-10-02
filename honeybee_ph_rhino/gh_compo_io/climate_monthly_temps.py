# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH Climate Monthly Temps."""

try:
    from typing import List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph import site
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_utils import units
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

class GHCompo_MonthlyTemps(object):

    def __init__(self, _IGH, _air_temps, _dewpoints, _sky_temps, _ground_temps):
        # type: (gh_io.IGH, List[float], List[float], List[float], List[float]) -> None
        self.IGH = _IGH
        self.air_temps = _air_temps
        self.dewpoints = _dewpoints
        self.sky_temps = _sky_temps
        self.ground_temps = _ground_temps

    def _validate(self, _input_list):
        # type: (List[float]) -> List[float]
        """Validate that the input data is the right shape."""
        if not _input_list:
            return [0.0]*12

        if len(_input_list) != 12:
            msg = "Error: Monthly data should be a collection of 12 numeric items.\n"\
                  "Got a {} of length: {}?".format(type(_input_list), len(_input_list))
            raise Exception(msg)

        return _input_list

    def _build_data(self, _input_list):
        # type: (List[float]) -> List[float]
        """Clean and convert the input data (if needed)."""
        _ = []
        for t in self._validate(_input_list):
            input_value, input_units = units.parse_input(str(t))
            result = units.convert(input_value, input_units or "C", "C")
            _.append(result)
        return _

    @property
    def air_temps(self):
        # type: () -> List[float]
        return self._air_temps

    @air_temps.setter
    def air_temps(self, _air_temps):
        # type: (List[float]) -> None
        self._air_temps = self._build_data(_air_temps)

    @property
    def dewpoints(self):
        return self._dewpoints

    @dewpoints.setter
    def dewpoints(self, _dewpoints):
        # type: (List[float]) -> None
        self._dewpoints = self._build_data(_dewpoints)

    @property
    def sky_temps(self):
        return self._sky_temps

    @sky_temps.setter
    def sky_temps(self, _sky_temps):
        # type: (List[float]) -> None
        self._sky_temps = self._build_data(_sky_temps)

    @property
    def ground_temps(self):
        return self._ground_temps

    @ground_temps.setter
    def ground_temps(self, _ground_temps):
        # type: (List[float]) -> None
        self._ground_temps = self._build_data(_ground_temps)

    def run(self):
        # type: () -> site.Climate_MonthlyTempCollection
        return site.Climate_MonthlyTempCollection(
            _air=site.Climate_MonthlyValueSet(self.air_temps),
            _dewpoint=site.Climate_MonthlyValueSet(self.dewpoints),
            _sky=site.Climate_MonthlyValueSet(self.sky_temps),
            _ground=site.Climate_MonthlyValueSet(self.ground_temps),
        )

