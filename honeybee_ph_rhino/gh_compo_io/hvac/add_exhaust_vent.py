# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Exhaust Ventilators."""

from copy import copy

try:
    from typing import List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_energy_ph.hvac import ventilation
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_AddExhaustVent(object):
    def __init__(self, IGH, _exhaust_vent_devices, _hb_rooms):
        # type: (gh_io.IGH, List[ventilation._ExhaustVentilatorBase], List[room.Room]) -> None
        self.IGH = IGH
        self.exhaust_vent_devices = _exhaust_vent_devices
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> List[room.Room]
        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            # -- Build up the new HB-HVAC
            new_hvac = copy(hb_room.properties.energy.hvac.duplicate())  # type: ignore

            # -- Add the new Exhaust Devices to the room's vent system
            for exhaust_device in self.exhaust_vent_devices:
                new_hvac.properties.ph.exhaust_vent_devices.add(exhaust_device)

            # -- Output
            new_room = hb_room.duplicate()
            new_room.properties.energy.hvac = new_hvac  # type: ignore
            hb_rooms_.append(new_room)

        return hb_rooms_