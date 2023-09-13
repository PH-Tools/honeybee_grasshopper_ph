# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Mech Supportive Devices"""

from copy import copy

try:
    from typing import List, Any
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.hvac.supportive_device import PhSupportiveDevice
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_AddMechSupportiveDevices(object):
    def __init__(self, _supportive_devices, _hb_rooms, *args, **kwargs):
        # type: (List[PhSupportiveDevice], List[room.Room], *Any, **Any) -> None
        self.supportive_devices = _supportive_devices
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> List[room.Room]

        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            # -- Build up a new HB-HVAC
            new_hvac = copy(hb_room.properties.energy.hvac.duplicate())  # type: ignore

            # ---------------------------------------------------------------------------
            # -- Supportive Devices
            for supportive_device in self.supportive_devices:
                new_hvac.properties.ph.supportive_devices.add(supportive_device)

            # -- Add the new room to the output
            new_room = hb_room.duplicate()
            new_room.properties.energy.hvac = new_hvac  # type: ignore
            hb_rooms_.append(new_room)

        return hb_rooms_
