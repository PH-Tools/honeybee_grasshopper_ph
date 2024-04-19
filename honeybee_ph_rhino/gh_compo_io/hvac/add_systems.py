# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Mech Systems."""

from copy import copy

try:
    from typing import Any, List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_phhvac import heat_pumps, heating, ventilation
    from honeybee_phhvac.properties.room import RoomPhHvacEquipmentProperties
    from honeybee_phhvac.supportive_device import PhSupportiveDevice
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_phhvac:\n\t{}".format(e))


class GHCompo_AddMechSystems(object):
    def __init__(self, _vent_sys, _conditioning_systems, _supportive_devices=[], _hb_rooms=[], *args, **kwargs):
        # type: (ventilation.PhVentilationSystem, List[heating.PhHeatingSystem], List[PhSupportiveDevice], List[room.Room],  *Any, **Any) -> None

        self.ventilation_system = _vent_sys
        self.conditioning_systems = _conditioning_systems
        self.supportive_devices = _supportive_devices
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> List[room.Room]

        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            # -- Build up the new HB-HVAC
            ph_hvac = getattr(hb_room.properties, "ph_hvac")  # type: RoomPhHvacEquipmentProperties
            new_hvac = copy(ph_hvac.duplicate())

            # ---------------------------------------------------------------------------
            # -- Fresh-Air Ventilation
            if self.ventilation_system:
                if not self.ventilation_system.ventilation_unit:
                    continue

                # -- Set the new h-hvac's values to match the PH-Ventilator Inputs, if any
                new_hvac.ventilation_system = self.ventilation_system

            # ---------------------------------------------------------------------------
            # -- Space Heating / Cooling
            for ph_conditioning_system in self.conditioning_systems:
                if isinstance(ph_conditioning_system, heat_pumps.PhHeatPumpSystem):
                    new_hvac.heat_pump_systems.add(ph_conditioning_system)
                else:
                    new_hvac.heating_systems.add(ph_conditioning_system)

            # ---------------------------------------------------------------------------
            # -- Supportive Devices
            for supportive_device in self.supportive_devices:
                new_hvac.supportive_devices.add(supportive_device)

            new_room = hb_room.duplicate()
            setattr(new_room.properties, "ph_hvac", new_hvac)
            hb_rooms_.append(new_room)

        return hb_rooms_
