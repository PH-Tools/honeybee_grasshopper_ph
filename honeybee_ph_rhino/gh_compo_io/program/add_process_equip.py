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
    from honeybee_energy.load.process import Process
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.load import ph_equipment
    from honeybee_energy_ph.properties.load.process import ProcessPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
    from ph_gh_component_io.input_tools import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.converter import convert
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))

try:
    from honeybee_ph_rhino.gh_compo_io.program._schedules import SchedulesCollection
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

# ------------------------------------------------------------------------------
# -- Component Interface


def _get_room_floor_area_ft2(_hb_room, _IGH):
    # type: (Room, gh_io.IGH) -> float
    room_floor_area_ft2 = convert(_hb_room.floor_area, _IGH.get_rhino_areas_unit_name(), "FT2") or 0.0
    if not room_floor_area_ft2:
        _IGH.warning("Error: Room: '{}' has no floor surfaces?".format(_hb_room.display_name))
    print("Room Floor Area: '{}' = {} ft2".format(_hb_room.display_name, room_floor_area_ft2))
    return room_floor_area_ft2


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
        self._total_floor_area_ft2 = 0.0

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
        # type: () -> float
        """Get the total floor area of all the rooms in ft2."""
        if not self._total_floor_area_ft2:
            self._total_floor_area_ft2 = sum(_get_room_floor_area_ft2(rm, self.IGH) for rm in self.hb_rooms)
        return self._total_floor_area_ft2

    def get_default_ph_equipment_set(self, _type):
        # type: (str) -> list[ph_equipment.PhEquipment]
        """Get the default PhEquipment set for the type (PHIUS | PHI)."""
        if _type == "PHIUS":
            return [
                self.ph_equip_types[1].phius_default(),
                self.ph_equip_types[2].phius_default(),
                self.ph_equip_types[3].phius_default(),
                self.ph_equip_types[6].phius_default(),
                self.ph_equip_types[7].phius_default(),
                self.ph_equip_types[13].phius_default(),
                self.ph_equip_types[14].phius_default(),
                self.ph_equip_types[15].phius_default(),
            ]
        elif _type == "PHI":
            return [
                self.ph_equip_types[1].phi_default(),
                self.ph_equip_types[2].phi_default(),
                self.ph_equip_types[3].phi_default(),
                self.ph_equip_types[6].phi_default(),
                self.ph_equip_types[7].phi_default(),
            ]
        else:
            self.IGH.warning("Unkown default type: {}".format(_type))
            return []

    def gather_ph_equipment(self):
        # type: () -> list[ph_equipment.PhEquipment]
        """Figure out what the user input, gather the PhEquipment objects based on the input."""
        ph_equipment_ = []  # type: list[ph_equipment.PhEquipment]
        for _input_ in self.equipment:
            if isinstance(_input_, str):
                input_type_num = input_to_int(_input_)
                if not input_type_num:
                    raise ValueError("Failed to convert input to integer: {}".format(_input_))

                if input_type_num == 100:
                    # -- Phius Defaults
                    ph_equip = self.get_default_ph_equipment_set("PHIUS")
                elif input_type_num == 200:
                    # -- PHI Defaults
                    ph_equip = self.get_default_ph_equipment_set("PHI")
                else:
                    # -- Create a new PhEquipment for the type
                    ph_equip_type = self.ph_equip_types[input_type_num]
                    ph_equip = [ph_equip_type.phius_default()]
            else:
                # -- Input is already a PhEquipment object
                ph_equip = [_input_]
            ph_equipment_.extend(ph_equip)

        return ph_equipment_

    def create_ph_process_load(self, _ph_equipment):
        # type: (list[ph_equipment.PhEquipment]) -> list[Process]
        """Create the HB-Process-Load objects for the PhEquipment."""

        new_process_loads = []  # type: list[Process]
        for ph_equip in _ph_equipment:
            # -- Create the HB-Process-Load
            schd = self.schedules.get_schedule(ph_equip.__class__.__name__)
            watts = ph_equip.annual_avg_wattage(
                _schedule=schd,
                _num_occupants=self.num_occupants,
                _num_units=self.num_dwellings,
                _floor_area_ft2=self.total_floor_area_ft2,
                _num_bedrooms=self.num_bedrooms,
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

            # -- Add the PhEquipment to the new Process Load
            new_process.display_name = ph_equip.__class__.__name__
            hbph_prop = getattr(new_process.properties, "ph")  # type: ProcessPhProperties
            hbph_prop.ph_equipment = ph_equip
            new_process_loads.append(new_process)

        return new_process_loads

    def add_process_loads_to_rooms(self, _hb_rooms, _process_loads):
        # type: (list[Room], list[Process]) -> list[Room]
        """Add each of the Process Loads to each of the Rooms."""
        hb_rooms_ = []  # type: list[Room]
        for r in _hb_rooms:
            new_room = r.duplicate()  # type: Room
            hbe_prop = getattr(new_room.properties, "energy")  # type: RoomEnergyProperties
            for process_load in _process_loads:
                hbe_prop.add_process_load(process_load)
                print("Added Process Load: '{}' to '{}'".format(process_load.display_name, new_room.display_name))
            hb_rooms_.append(new_room)

        return hb_rooms_

    def run(self):
        # type: () -> list[Room] | None
        if not self.ready:
            return self.hb_rooms

        ph_equipment = self.gather_ph_equipment()
        new_process_loads = self.create_ph_process_load(ph_equipment)
        hb_rooms_ = self.add_process_loads_to_rooms(self.hb_rooms, new_process_loads)
        return hb_rooms_
