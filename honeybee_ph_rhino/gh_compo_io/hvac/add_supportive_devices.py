# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Mech Supportive Devices"""

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
    from honeybee_phhvac.properties.room import RoomPhHvacProperties
    from honeybee_phhvac.supportive_device import PhSupportiveDevice
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_AddMechSupportiveDevices(object):
    def __init__(self, _supportive_devices, _hb_rooms, *args, **kwargs):
        # type: (List[PhSupportiveDevice], List[room.Room], *Any, **Any) -> None
        self.supportive_devices = [d for d in _supportive_devices if d]
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> List[room.Room]

        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            new_room = hb_room.duplicate()
            ph_hvac = getattr(hb_room.properties, "ph_hvac")  # type: RoomPhHvacProperties
            new_hvac = copy(ph_hvac.duplicate())

            # -- Supportive Devices
            for supportive_device in self.supportive_devices:
                new_hvac.supportive_devices.add(supportive_device)
                print(
                    "Adding Supportive-Device '{}' to HB-Room: '{}'".format(
                        supportive_device.display_name, new_room.display_name
                    )
                )

            # -- Output
            setattr(new_room.properties, "ph_hvac", new_hvac)
            hb_rooms_.append(new_room)

        return hb_rooms_
