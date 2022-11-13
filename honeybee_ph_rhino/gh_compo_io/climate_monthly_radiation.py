# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH Climate Monthly Radiation."""

try:
    from typing import List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph import site
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError('\nFailed to import ph_units:\n\t{}'.format(e))

class GHCompo_CreateMonthlyRadiation(object):
    """Interface for "HBPH - PH Climate Monthly Radiation" Component."""

    def __init__(self, _IGH, _north, _east, _south, _west, _glob):
        # type: (gh_io.IGH, List[float], List[float], List[float], List[float], List[float]) -> None
        self.IGH = _IGH
        self.north = _north
        self.east = _east
        self.south = _south
        self.west = _west
        self.glob = _glob

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
            input_value, input_units = parse_input(str(t))
            result = convert(input_value, input_units or "KWH/M2", "KWH/M2")
            _.append(result)
        return _

    @property
    def north(self):
        return self._north

    @north.setter
    def north(self, _north):
        # type: (List[float]) -> None
        self._north = self._build_data(_north)

    @property
    def east(self):
        return self._east

    @east.setter
    def east(self, _east):
        # type: (List[float]) -> None
        self._east = self._build_data(_east)

    @property
    def south(self):
        return self._south

    @south.setter
    def south(self, _south):
        # type: (List[float]) -> None
        self._south = self._build_data(_south)

    @property
    def west(self):
        return self._west

    @west.setter
    def west(self, _west):
        # type: (List[float]) -> None
        self._west = self._build_data(_west)

    @property
    def glob(self):
        return self._glob

    @glob.setter
    def glob(self, _glob):
        # type: (List[float]) -> None
        self._glob = self._build_data(_glob)

    def run(self):
        # type: () -> site.Climate_MonthlyRadiationCollection
        return site.Climate_MonthlyRadiationCollection(
            _north=site.Climate_MonthlyValueSet(self.north),
            _east=site.Climate_MonthlyValueSet(self.east),
            _south=site.Climate_MonthlyValueSet(self.south),
            _west=site.Climate_MonthlyValueSet(self.west),
            _glob=site.Climate_MonthlyValueSet(self.glob),
        )

