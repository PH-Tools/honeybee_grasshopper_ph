# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Phius Multi-Family Residential Room Loads."""

import os

try:
    from typing import Any
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
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.load import ph_equipment
    from honeybee_energy_ph.properties.load.process import ProcessPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_rhino.gh_compo_io.program._get_room_data import (
        get_num_bedrooms,
        get_num_dwellings,
        get_num_occupants,
        get_room_floor_area_ft2,
    )
    from honeybee_ph_rhino.gh_compo_io.program._schedules import SchedulesCollection
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


# -----------------------------------------------------------------------------


def build_mel(total_mel, number_of_rooms):
    # type: (float, int) -> ph_equipment.PhCustomAnnualMEL
    """Build the Phius-MF-MEL object."""

    mel_obj = ph_equipment.PhCustomAnnualMEL()
    mel_obj.display_name = "Phius-MF-MEL"
    mel_obj.energy_demand = total_mel / number_of_rooms
    mel_obj.comment = "MEL_Dwelling"
    mel_obj.quantity = 1
    return mel_obj


def build_lighting_int(total_lighting_int, number_of_rooms):
    # type: (float, int) -> ph_equipment.PhCustomAnnualLighting
    """Build the Phius-MF-Int-Lighting object."""

    lighting_obj = ph_equipment.PhCustomAnnualLighting()
    lighting_obj.display_name = "Phius-MF-Int-Lighting"
    lighting_obj.energy_demand = total_lighting_int / number_of_rooms
    lighting_obj.comment = "LIGHTS_Int_Dwelling"
    lighting_obj.quantity = 1
    return lighting_obj


def build_lighting_ext(total_lighting_ext, number_of_rooms):
    # type: (float, int) -> ph_equipment.PhCustomAnnualLighting
    """Build the Phius-MF-Ext-Lighting object."""

    lighting_obj = ph_equipment.PhCustomAnnualLighting()
    lighting_obj.display_name = "Phius-MF-Ext-Lighting"
    lighting_obj.energy_demand = total_lighting_ext / number_of_rooms
    lighting_obj.comment = "LIGHTS_Ext_Dwelling"
    lighting_obj.quantity = 1
    lighting_obj.in_conditioned_space = False
    return lighting_obj


def build_lighting_garage(total_lighting_garage, number_of_rooms):
    # type: (float, int) -> ph_equipment.PhCustomAnnualLighting
    """Build the Phius-MF-Garage-Lighting object."""

    lighting_obj = ph_equipment.PhCustomAnnualLighting()
    lighting_obj.display_name = "Phius-MF-Garage-Lighting"
    lighting_obj.energy_demand = total_lighting_garage / number_of_rooms
    lighting_obj.comment = "LIGHTS_Garage"
    lighting_obj.quantity = 1
    lighting_obj.in_conditioned_space = False
    return lighting_obj


# -----------------------------------------------------------------------------
# -- Component Interface


class GHCompo_SetPhiusMFResidentialRoomLoads(object):
    PHIUS_DEFAULTS = [
        ph_equipment.PhDishwasher.phius_default,
        ph_equipment.PhClothesWasher.phius_default,
        ph_equipment.PhClothesDryer.phius_default,
        ph_equipment.PhFridgeFreezer.phius_default,
        ph_equipment.PhCooktop.phius_default,
    ]

    def __init__(
        self,
        _IGH,
        _equipment,
        _total_mel,
        _total_lighting_int,
        _total_lighting_ext,
        _total_lighting_garage,
        _hb_rooms,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, list[ph_equipment.PhEquipment],float, float, float, float, list[Room], *Any, **Any) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms or []
        self.ph_equipment = _equipment or []
        self.total_mel = _total_mel or 0.0
        self.total_lighting_int = _total_lighting_int or 0.0
        self.total_lighting_ext = _total_lighting_ext or 0.0
        self.total_lighting_garage = _total_lighting_garage or 0.0

        self.total_num_hb_rooms = 0
        self.total_num_occupants = 0.0
        self.total_num_dwellings = 0
        self.total_num_bedrooms = 0
        self.total_floor_area_ft2 = 0.0
        self.schedules = SchedulesCollection(
            os.path.join(folders.python_package_path, "honeybee_ph_standards", "schedules")
        )

    @property
    def ready(self):
        # type: () -> bool
        if not self.hb_rooms:
            return False
        return True

    def collect_hb_room_props(self):
        # type: () -> None
        """Collect the room properties for the Phius-MF-PhEquipment."""

        self.total_num_hb_rooms = len(self.hb_rooms)
        self.total_num_occupants = sum(get_num_occupants(rm, self.IGH) for rm in self.hb_rooms)
        self.total_num_dwellings = get_num_dwellings(self.hb_rooms)
        self.total_num_bedrooms = sum(get_num_bedrooms(rm) for rm in self.hb_rooms)
        self.total_floor_area_ft2 = sum(get_room_floor_area_ft2(rm, self.IGH) for rm in self.hb_rooms)

    def create_ph_process_load(self, _ph_equipment):
        # type: (list[ph_equipment.PhEquipment]) -> list[Process]
        """Create the HB-Process-Load objects for the PhEquipment."""

        new_process_loads = []  # type: list[Process]
        for ph_equip in _ph_equipment:
            # -- Create the HB-Process-Load
            schd = self.schedules.get_schedule(ph_equip.__class__.__name__)
            watts = ph_equip.annual_avg_wattage(
                _schedule=schd,
                _num_occupants=self.total_num_occupants,
                _num_units=self.total_num_dwellings,
                _floor_area_ft2=self.total_floor_area_ft2,
                _num_bedrooms=self.total_num_bedrooms,
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
            hb_rooms_.append(new_room)

        return hb_rooms_

    def setup_ph_equipment(self):
        # type: () -> None
        """Setup the Phius-MF-PhEquipment for the room loads."""

        # -- Build default MF-PhEquipment if none provided
        if not self.ph_equipment:
            self.ph_equipment.append(ph_equipment.PhDishwasher.phius_default())
            self.ph_equipment.append(ph_equipment.PhClothesWasher.phius_default())
            self.ph_equipment.append(ph_equipment.PhClothesDryer.phius_default())
            self.ph_equipment.append(ph_equipment.PhFridgeFreezer.phius_default())
            self.ph_equipment.append(ph_equipment.PhCooktop.phius_default())

        # -- Build the Phius-MF-PhEquipment
        self.ph_equipment.append(build_mel(self.total_mel, self.total_num_hb_rooms))
        self.ph_equipment.append(build_lighting_int(self.total_lighting_int, self.total_num_hb_rooms))
        self.ph_equipment.append(build_lighting_ext(self.total_lighting_ext, self.total_num_hb_rooms))
        self.ph_equipment.append(build_lighting_garage(self.total_lighting_garage, self.total_num_hb_rooms))

    def run(self):
        # type: () -> list[Room]

        if not self.ready:
            return self.hb_rooms

        self.collect_hb_room_props()
        self.setup_ph_equipment()
        new_process_loads = self.create_ph_process_load(self.ph_equipment)
        hb_rooms_ = self.add_process_loads_to_rooms(self.hb_rooms, new_process_loads)

        return hb_rooms_
