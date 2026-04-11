# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Summer Ventilation."""


from honeybee_ph_utils.input_tools import input_to_int
from honeybee_ph_rhino import gh_io
from honeybee_ph_rhino.gh_compo_io import ghio_validators


try:
    from honeybee_ph.bldg_segment import PhVentilationSummerBypassMode, SummerVentilation, PhSummerVentilationExtractSystemControl
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))


class GHCompo_CreateSummerVentilation(object):
    daytime_extract_system_fan_power_wh_m3 = ghio_validators.UnitWH_M3("daytime_extract_system_fan_power_wh_m3")
    nighttime_minimum_indoor_temp_C = ghio_validators.UnitDegreeC("nighttime_minimum_indoor_temp_C")
    nighttime_extract_system_fan_power_wh_m3 = ghio_validators.UnitWH_M3("nighttime_extract_system_fan_power_wh_m3")
    nighttime_extract_system_heat_fraction = ghio_validators.FloatPercentage("nighttime_extract_system_heat_fraction")
    
    def __init__(self, 
                 _IGH,     
                 _ventilation_system_ach,
                _ventilation_system_summer_bypass_mode,
                _daytime_extract_system_ach,
                _daytime_extract_system_fan_power_wh_m3,
                _daytime_window_ach,
                _nighttime_extract_system_ach,
                _nighttime_extract_system_fan_power_wh_m3, 
                _nighttime_extract_system_heat_fraction,
                _nighttime_extract_system_control,
                _nighttime_window_ach,
                _nighttime_minimum_indoor_temp_C,
                *args, 
                **kwargs 
            ):
        self.IGH = _IGH
        self.ventilation_system_ach = _ventilation_system_ach
        self.ventilation_system_summer_bypass_mode = _ventilation_system_summer_bypass_mode or "4"
        self.daytime_extract_system_ach = _daytime_extract_system_ach or 0.0
        self.daytime_extract_system_fan_power_wh_m3 = _daytime_extract_system_fan_power_wh_m3 or 0.65
        self.daytime_window_ach = _daytime_window_ach or 0.0
        self.nighttime_extract_system_ach = _nighttime_extract_system_ach or 0.0
        self.nighttime_extract_system_fan_power_wh_m3 = _nighttime_extract_system_fan_power_wh_m3 or 0.65
        self.nighttime_extract_system_heat_fraction = _nighttime_extract_system_heat_fraction or 0.0
        self.nighttime_extract_system_control = _nighttime_extract_system_control or "1"
        self.nighttime_window_ach = _nighttime_window_ach or 0.0
        self.nighttime_minimum_indoor_temp_C = _nighttime_minimum_indoor_temp_C or 22.0
    
    @property
    def ventilation_system_summer_bypass_mode(self):
        # type: () -> PhVentilationSummerBypassMode
        return self._ventilation_system_summer_bypass_mode

    @ventilation_system_summer_bypass_mode.setter
    def ventilation_system_summer_bypass_mode(self, _input):
        # type: (str) -> None
        self._ventilation_system_summer_bypass_mode = PhVentilationSummerBypassMode(input_to_int(_input) or 4)
        return None

    @property
    def nighttime_extract_system_control(self):
        # type: () -> PhSummerVentilationExtractSystemControl
        return self._nighttime_extract_system_control

    @nighttime_extract_system_control.setter
    def nighttime_extract_system_control(self, _input):
        # type: (str) -> None
        self._nighttime_extract_system_control = PhSummerVentilationExtractSystemControl(input_to_int(_input) or 1)
        return None

    def run(self):
        # type: () -> SummerVentilation
        obj = SummerVentilation(
            self.ventilation_system_ach,
            self.ventilation_system_summer_bypass_mode.value,
            self.daytime_extract_system_ach,
            self.daytime_extract_system_fan_power_wh_m3,
            self.daytime_window_ach,
            self.nighttime_extract_system_ach,
            self.nighttime_extract_system_fan_power_wh_m3,
            self.nighttime_extract_system_heat_fraction,
            self.nighttime_extract_system_control.value,
            self.nighttime_window_ach,
            self.nighttime_minimum_indoor_temp_C
        )
        return obj
