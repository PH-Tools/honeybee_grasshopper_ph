# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Phius Certification."""

try:
    from typing import Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph import phius
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

class GHCompo_PhiusCertification(object):

    def __init__(self, _IGH, building_category_type_, building_use_type_, building_status_, building_type_, _PHIUS_annual_heating_demand_kWh_m2, _PHIUS_annual_cooling_demand_kWh_m2, _PHIUS_peak_heating_load_W_m2, _PHIUS_peak_cooling_load_W_m2,):
        # type: (gh_io.IGH, Optional[int], Optional[int], Optional[int], Optional[int], float, float, float, float) -> None
        self.IGH = _IGH
        self.building_category_type = gh_io.input_to_int(building_category_type_)
        self.building_use_type = gh_io.input_to_int(building_use_type_)
        self.building_status = gh_io.input_to_int(building_status_)
        self.building_type = gh_io.input_to_int(building_type_)
        self.PHIUS_annual_heating_demand_kWh_m2 = _PHIUS_annual_heating_demand_kWh_m2 or 15.0
        self.PHIUS_annual_cooling_demand_kWh_m2 = _PHIUS_annual_cooling_demand_kWh_m2 or 15.0
        self.PHIUS_peak_heating_load_W_m2 = _PHIUS_peak_heating_load_W_m2 or 10.0
        self.PHIUS_peak_cooling_load_W_m2 = _PHIUS_peak_cooling_load_W_m2 or 10.0

    def run(self):
        # type: () -> phius.PhiusCertification
        certification_ = phius.PhiusCertification()

        certification_.building_category_type = self.building_category_type
        certification_.building_use_type = self.building_use_type
        certification_.building_status = self.building_status
        certification_.building_type = self.building_type

        certification_.PHIUS2021_heating_demand = self.PHIUS_annual_heating_demand_kWh_m2
        certification_.PHIUS2021_cooling_demand = self.PHIUS_annual_cooling_demand_kWh_m2
        certification_.PHIUS2021_heating_load = self.PHIUS_peak_heating_load_W_m2
        certification_.PHIUS2021_cooling_load = self.PHIUS_peak_cooling_load_W_m2
        
        return certification_