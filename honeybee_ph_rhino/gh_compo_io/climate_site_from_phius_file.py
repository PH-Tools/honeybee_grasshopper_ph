# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Create Site From Phius File."""

try:
    from typing import List, Union, Dict, Optional
except ImportError:
    pass # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from honeybee_ph import site
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph:\n\t{}'.format(e))


def remove_non_ascii(string):
    return ''.join(char for char in string if ord(char) < 128)


def clean_key(key):
    # type: (str) -> str
    """Utility function to clean the data key"""
    return remove_non_ascii(key.upper().lstrip().rstrip().replace(" ", "_"))


class MonthlyDataInputCollection(object):
    """A Collection of Monthly data."""

    def __init__(self):
        self.storage = {}
    
    def _clean_values(self, _input_value_list):
        # type: (List[str]) -> List[float]
        _ = []
        for i in _input_value_list:
            try:
                _.append(float(i))
            except:
                _.append(i)
        return _
    
    def __setitem__(self, key, value):
        # type: (str, List[str]) -> None
        self.storage[clean_key(key)] = self._clean_values(value)
        
    def __getitem__(self, key):
        return self.storage[key]
    
    def keys(self):
        return self.storage.keys()
    
    @property
    def air_temps(self):
        # type: () -> List[float]
        return self["TEMPERATURE_OUTDOOR"]
        
    @property
    def dewpoints(self):
        # type: () -> List[float]
        return self["DEWPOINT"]
        
    @property
    def sky_temps(self):
        # type: () -> List[float]
        return self["SKY_TEMPERATURE"]

    @property
    def north(self):
        # type: () -> List[float]
        return self["NORTH"]

    @property
    def east(self):
        # type: () -> List[float]
        return self["EAST"]

    @property
    def south(self):
        # type: () -> List[float]
        return self["SOUTH"]
        
    @property
    def west(self):
        # type: () -> List[float]
        return self["WEST"]

    @property
    def glob(self):
        # type: () -> List[float]
        return self["GLOBAL"]
    
    @property
    def location_data(self):
        # type: () -> List[float]
        return self["LOCATION_DATA"]
    
    @property
    def display_name(self):
        # type: () -> str
        return self.location_data[0]

    @property
    def station_elevation(self):
        # type: () -> float
        return self.location_data[6]

    @property
    def daily_temp_swing(self):
        # type: () -> float
        return self.location_data[10] or 8

    @property
    def average_wind_speed(self):
        # type: () -> float
        return 4
    
    @property
    def latitude(self):
        # type: () -> float
        return self.location_data[2]

    @property
    def longitude(self):
        # type: () -> float
        return self.location_data[4]

    def __str__(self):
        return "\n".join([
             ('air_temps: {}'.format(self.air_temps)),
             ('dewpoints: {}'.format(self.dewpoints)),
             ('sky_temps: {}'.format(self.sky_temps)),
             ('north: {}'.format(self.north)),
             ('east:: {}'.format(self.east)),
             ('south: {}'.format(self.south)),
             ('west: {}'.format(self.west)),
             ('global: {}'.format(self.glob)),
             ('location_data: {}'.format(self.location_data))
        ])
  
    
class PeakLoadValueSet(object):
    """The data for a single peak-load (heating, cooling)."""

    def __init__(self):
        self.storage = {} # type: Dict[str, float]
    
    def __setitem__(self, key, value):
        # type: (str, float) -> None
        self.storage[clean_key(key)] = value

    def __getitem__(self, key):
        # type: (str) -> float
        return self.storage[key]

    @property
    def air_temp(self):
        # type: () -> float
        return self["TEMPERATURE_OUTDOOR"]
        
    @property
    def dewpoint(self):
        # type: () -> Optional[float]
        try:
            return self["DEWPOINT"]
        except KeyError:
            return None
        
    @property
    def sky_temp(self):
        # type: () -> Optional[float]
        try:
            return self["SKY_TEMPERATURE"]
        except KeyError:
            return None

    @property
    def ground_temp(self):
    # type: () -> Optional[float]
        try:
            return self["GROUND_TEMPERATURE"]
        except KeyError:
            return None
        
    @property
    def north(self):
        # type: () -> float
        return self["NORTH"]

    @property
    def east(self):
        # type: () -> float
        return self["EAST"]

    @property
    def south(self):
        # type: () -> float
        return self["SOUTH"]
        
    @property
    def west(self):
        # type: () -> float
        return self["WEST"]

    @property
    def glob(self):
        # type: () -> float
        return self["GLOBAL"]
    

class PeakLoadInputCollection(object):
    """A collection of Peak Load Datasets (2 Heating, 2 Cooling)."""

    def __init__(self):
        self.peak_heat_load_1 = PeakLoadValueSet()
        self.peak_heat_load_2 = PeakLoadValueSet()
        self.peak_cooling_load_1 = PeakLoadValueSet()
        self.peak_cooling_load_2 = PeakLoadValueSet()


class GHCompo_CreateSiteFromPhiusFile(object):
    """Interface for the GH Component"""

    def __init__(self, _IGH, _source_file_path):
        # type: (gh_io.IGH, str) -> None
        self.IGH = _IGH
        self.data = self._read_file(_source_file_path)
        self.monthly_data_collection = MonthlyDataInputCollection()
        self.peak_load_data_collection = PeakLoadInputCollection()

    def _read_file(self, _source_file_path):
        # type: (Optional[str]) -> List[str]
        """Read in the Phius Data file (TXT only) and return a list of the contents."""

        if not _source_file_path:
            msg = "Please supply a valid .TXT file path for the Phius data to read."
            self.IGH.warning(msg)
            return []

        extension = _source_file_path[-3:].upper()
        if extension != "TXT":
            msg = "Error: Input Phius data '.TXT' file path. Got file of type: '{}'?".format(extension)
            self.IGH.error(msg)
            return []
        
        return self.IGH.ghpythonlib_components.ReadFile(_source_file_path)

    def _create_input_data_collection(self):
        # type: () -> None

        """
        Generate a dict (self.input_data_collection) that looks like:

        {
            "Ambient Temp": [10, 14, 17, ... 4],
            "North": [10, 14, 17, ... 4], #<-- Radiation
            "East": [10, 14, 17, ... 4],
            "South": [10, 14, 17, ... 4],
            "West": [10, 14, 17, ... 4],
            "Global": [10, 14, 17, ... 4],
            "Dewpoint": [10, 14, 17, ... 4],
            "Sky Temperature": [10, 14, 17, ... 4],
        }
        """

        for line in self.data[2:10]:
            # -- Log the monthly data
            line = line.split("\t")
            self.monthly_data_collection[line[0]] = line[1:13]
        
        for line in self.data[2:8]:
            line = line.split("\t")
            # -- Log the peak load data
            self.peak_load_data_collection.peak_heat_load_1[line[0]] = float(line[13])
            self.peak_load_data_collection.peak_heat_load_2[line[0]] = float(line[14])
            self.peak_load_data_collection.peak_cooling_load_1[line[0]] = float(line[15])
            self.peak_load_data_collection.peak_cooling_load_2[line[0]] = float(line[15])

        # -- Log the header / location data
        self.monthly_data_collection["LOCATION_DATA"] = self.data[1].split("\t")

    def _create_location(self):
        # type: () -> site.Location
        
        return site.Location(
            latitude=self.monthly_data_collection.latitude,
            longitude=self.monthly_data_collection.longitude,
            site_elevation=self.monthly_data_collection.station_elevation,
            climate_zone=1,
            hours_from_UTC=-4,
        )

    def _create_monthly_temps(self):
        # type: () -> site.Climate_MonthlyTempCollection

        return site.Climate_MonthlyTempCollection(
                    _air=site.Climate_MonthlyValueSet(self.monthly_data_collection.air_temps),
                    _dewpoint=site.Climate_MonthlyValueSet(self.monthly_data_collection.dewpoints),
                    _sky=site.Climate_MonthlyValueSet(self.monthly_data_collection.sky_temps),
                )

    def _create_monthly_radiation(self):
        # type: () -> site.Climate_MonthlyRadiationCollection

        return site.Climate_MonthlyRadiationCollection(
                    _north=site.Climate_MonthlyValueSet(self.monthly_data_collection.north),
                    _east=site.Climate_MonthlyValueSet(self.monthly_data_collection.east),
                    _south=site.Climate_MonthlyValueSet(self.monthly_data_collection.south),
                    _west=site.Climate_MonthlyValueSet(self.monthly_data_collection.west),
                    _glob=site.Climate_MonthlyValueSet(self.monthly_data_collection.glob),
                )

    def _create_peak_load_value_set(self, _peak_load_data):
        # type: (PeakLoadValueSet) -> site.Climate_PeakLoadValueSet
        
        climate_peak_loads_ = site.Climate_PeakLoadValueSet(
                    _temp=_peak_load_data.air_temp,
                    _rad_north=_peak_load_data.north,
                    _rad_east=_peak_load_data.east,
                    _rad_south=_peak_load_data.south,
                    _rad_west=_peak_load_data.west,
                    _rad_global=_peak_load_data.glob,
                    _dewpoint_temp=_peak_load_data.dewpoint,
                    _sky_temp=_peak_load_data.sky_temp,
                    _ground_temp=_peak_load_data.ground_temp,
                )
        climate_peak_loads_.display_name = self.monthly_data_collection.display_name
        
        return climate_peak_loads_

    def _create_peak_loads(self):
        # type: () -> site.Climate_PeakLoadCollection

        climate_peak_loads_ = site.Climate_PeakLoadCollection(
            self._create_peak_load_value_set(self.peak_load_data_collection.peak_heat_load_1),
            self._create_peak_load_value_set(self.peak_load_data_collection.peak_heat_load_2),
            self._create_peak_load_value_set(self.peak_load_data_collection.peak_cooling_load_1),
            self._create_peak_load_value_set(self.peak_load_data_collection.peak_cooling_load_2),
        )
        return climate_peak_loads_

    def _create_climate_data(self):
        # type: () -> site.Climate
   
        climate_data_ = site.Climate(
                    _display_name = self.monthly_data_collection.display_name,
                    _station_elevation = self.monthly_data_collection.station_elevation,
                    _daily_temp_swing = self.monthly_data_collection.daily_temp_swing,
                    _average_wind_speed = self.monthly_data_collection.average_wind_speed,
                    _monthly_temps = self._create_monthly_temps(),
                    _monthly_radiation = self._create_monthly_radiation(),
                    _peak_loads = self._create_peak_loads(),
                )
        
        return climate_data_

    def run(self):
        # type: () -> Optional[site.Site]
        if not self.data:
            return None
            
        self._create_input_data_collection()
        
        ph_site = site.Site(
            self._create_location(),
            self._create_climate_data()
        )

        return ph_site