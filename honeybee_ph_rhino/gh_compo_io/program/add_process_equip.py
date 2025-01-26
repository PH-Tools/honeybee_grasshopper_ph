# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Process Equipment."""

import os

try:
    from typing import Type
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.config import folders
    from honeybee.room import Room
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.lib.schedules import schedule_by_identifier
    from honeybee_energy.load.process import Process
    from honeybee_energy.properties.room import RoomEnergyProperties
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.load import ph_equipment
    from honeybee_energy_ph.properties.load.process import ProcessPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_standards.schedules._load_schedules import load_schedules_from_json_file
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_standards:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
    from ph_gh_component_io.input_tools import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class SchedulesCollection(object):
    """Convenience class to hold all the schedules for a single-family home."""

    def __init__(self, root_directory):
        # type: (str) -> None
        self.all_appliances = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_appliances.json"))
        self.all_lighting = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_lighting.json"))
        self.all_mel = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_electric_equipment.json"))

    def get_schedule(self, _schedule_name):
        # type: (str) -> ScheduleRuleset
        return getattr(self, _schedule_name, schedule_by_identifier("Always On"))  # type: ignore

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


# ------------------------------------------------------------------------------
# -- Component Interface


class GHCompo_AddProcessEquip(object):
    ph_equip_types = {
        1: ph_equipment.PhDishwasher,
        2: ph_equipment.PhClothesWasher,
        3: ph_equipment.PhClothesDryer,
        4: ph_equipment.PhRefrigerator,
        5: ph_equipment.PhFreezer,
        6: ph_equipment.PhFridgeFreezer,
        7: ph_equipment.PhCooktop,
        13: ph_equipment.PhPhiusMEL,
        11: ph_equipment.PhCustomAnnualElectric,
        14: ph_equipment.PhPhiusLightingInterior,
        15: ph_equipment.PhPhiusLightingExterior,
        16: ph_equipment.PhPhiusLightingGarage,
        17: ph_equipment.PhCustomAnnualLighting,
        18: ph_equipment.PhCustomAnnualMEL,
    }  # type: dict[int, Type[ph_equipment.PhEquipment]]

    def __init__(self, _IGH, _equipment, _num_bedrooms, _num_occupants, _num_dwellings, _hb_rooms):
        # type: (gh_io.IGH, list[str | ph_equipment.PhEquipment], float, float, float, list[Room]) -> None
        self.schedules = SchedulesCollection(
            os.path.join(folders.python_package_path, "honeybee_ph_standards", "schedules")
        )
        self.IGH = _IGH
        self.equipment = _equipment
        self.num_bedrooms = _num_bedrooms
        self.num_occupants = _num_occupants
        self.num_dwellings = _num_dwellings
        self.hb_rooms = _hb_rooms

    @property
    def ready(self):
        # type: () -> bool
        if len(self.equipment) > 0 and len(self.hb_rooms) > 0:
            if all(
                [

                    self.num_bedrooms is not None,
                    self.num_occupants is not None,
                    self.num_dwellings is not None,
                ]
            ):
                return True
            else:
                msg = "Please input values for the _num_bedrooms, _num_occupants, and _num_dwellings."
                self.IGH.warning(msg)
                print(msg)
                return False
        return False

    @property
    def total_floor_area_ft2(self):
        return 1.0

    def run(self):
        # type: () -> list[Room] | None
        if not self.ready:
            return self.hb_rooms

        new_process_loads = []  # type: list[Process]
        for _input_ in self.equipment:
            if isinstance(_input_, str):
                input_type_num = input_to_int(_input_)
                if not input_type_num:
                    raise ValueError("Failed to convert input to integer: {}".format(_input_))

                # -- Create the PH-Equipment
                ph_equip_type = self.ph_equip_types[input_type_num]
                ph_equip = ph_equip_type.phius_default()
            else:
                # -- Input is a 'PhEquipment' object
                ph_equip_type = type(_input_)
                ph_equip = _input_

            # -- Create the HB-Process-Load
            schd = self.schedules.get_schedule(ph_equip_type.__name__)
            watts = ph_equip.annual_avg_wattage(
                _schedule=schd,
                _num_occupants=self.num_occupants,
                _num_units=self.num_dwellings,
                _floor_area_ft2=self.total_floor_area_ft2,
                _num_bedrooms=self.num_dwellings,
            )

            new_process = Process(
                identifier=clean_and_id_ep_string("HBPH_Process"),
                watts=watts,
                schedule=schd,
                fuel_type="Electricity",
                end_use_category="HBPH_Process",
                radiant_fraction=0,
                latent_fraction=0,
                lost_fraction=0,
            )

            # -- Add the PH-Equipment to the new Process Load
            new_process.display_name = ph_equip_type.__name__
            hbph_prop = getattr(new_process.properties, "ph")  # type: ProcessPhProperties
            hbph_prop.ph_equipment = ph_equip
            new_process_loads.append(new_process)

        hb_rooms_ = []  # type: list[Room]
        for r in self.hb_rooms:
            new_room = r.duplicate()  # type: Room
            hbe_prop = getattr(new_room.properties, "energy")  # type: RoomEnergyProperties
            for process_load in new_process_loads:
                hbe_prop.add_process_load(process_load)
                print("Added Process Load: '{}' to '{}'".format(process_load.display_name, new_room.display_name))
            hb_rooms_.append(new_room)

        return hb_rooms_
