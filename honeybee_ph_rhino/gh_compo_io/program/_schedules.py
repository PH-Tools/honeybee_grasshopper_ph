# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: Utility to load Program Schedules from Standards Library."""

import os

try:
    from honeybee_energy.lib.schedules import schedule_by_identifier
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_ph_standards.schedules._load_schedules import load_schedules_from_json_file
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_standards:\n\t{}".format(e))


class SchedulesCollection(object):
    """Convenience class to hold all the schedules for a single-family home."""

    def __init__(self, root_directory):
        # type: (str) -> None
        self.all_appliances = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_appliances.json"))
        self.all_lighting = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_lighting.json"))
        self.all_mel = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_electric_equipment.json"))
        self.all_occupancy = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_occupancy.json"))
        self.all_lighting = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_lighting.json"))
        self.all_mel = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_electric_equipment.json"))
        self.all_setpoint = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_setpoint.json"))
        self.all_hot_water = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_hot_water.json"))

    def get_schedule(self, _schedule_name):
        # type: (str) -> ScheduleRuleset
        return getattr(self, _schedule_name, schedule_by_identifier("Always On"))  # type: ignore

    def __getitem__(self, key):
        # type: (str) -> ScheduleRuleset
        return self.get_schedule(key)

    @property
    def PhPhiusLightingInterior(self):
        # type: () -> ScheduleRuleset
        return self.all_lighting["hbph_sfh_Lighting"]

    @property
    def PhPhiusMEL(self):
        # type: () -> ScheduleRuleset
        return self.all_mel["hbph_sfh_MEL"]

    @property
    def PhFreezer(self):
        # type: () -> ScheduleRuleset
        return self.all_appliances["hbph_sfh_Refrigerator"]

    @property
    def PhFridgeFreezer(self):
        # type: () -> ScheduleRuleset
        return self.all_appliances["hbph_sfh_Refrigerator"]

    @property
    def PhRefrigerator(self):
        # type: () -> ScheduleRuleset
        return self.all_appliances["hbph_sfh_Refrigerator"]

    @property
    def PhClothesWasher(self):
        # type: () -> ScheduleRuleset
        return self.all_appliances["hbph_sfh_Clotheswasher"]

    @property
    def PhClothesDryer(self):
        # type: () -> ScheduleRuleset
        return self.all_appliances["hbph_sfh_Clothesdryer"]

    @property
    def PhDishwasher(self):
        # type: () -> ScheduleRuleset
        return self.all_appliances["hbph_sfh_Dishwasher"]

    @property
    def PhCooktop(self):
        # type: () -> ScheduleRuleset
        return self.all_appliances["hbph_sfh_Cooktop"]

    @property
    def occupancy_presence(self):
        # type: () -> ScheduleRuleset
        return self.all_occupancy["hbph_sfh_Occupant_Presence"]

    @property
    def occupancy_activity(self):
        # type: () -> ScheduleRuleset
        return self.all_occupancy["hbph_sfh_Occupant_Activity"]

    @property
    def lighting(self):
        # type: () -> ScheduleRuleset
        return self.all_lighting["hbph_sfh_Lighting"]

    @property
    def mel(self):
        # type: () -> ScheduleRuleset
        return self.all_mel["hbph_sfh_MEL"]

    @property
    def heating_setpoint(self):
        # type: () -> ScheduleRuleset
        return self.all_setpoint["hbph_sfh_Heating_Setpoint"]

    @property
    def cooling_setpoint(self):
        # type: () -> ScheduleRuleset
        return self.all_setpoint["hbph_sfh_Cooling_Setpoint"]

    @property
    def hot_water(self):
        # type: () -> ScheduleRuleset
        return self.all_hot_water["hbph_sfh_Combined_HotWater"]
