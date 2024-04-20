# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Renewable Energy Systems."""

from copy import copy

try:
    from typing import Any, List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_phhvac.properties.room import RoomPhHvacProperties
    from honeybee_phhvac.renewable_devices import PhRenewableEnergyDevice
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_AddRenewableEnergyDevices(object):
    def __init__(self, _IGH, _renewable_devices=[], _hb_rooms=[], *args, **kwargs):
        # type: (gh_io.IGH, List[PhRenewableEnergyDevice], List[room.Room], *Any, **Any) -> None
        self.IGH = _IGH
        self.renewable_devices = [d for d in _renewable_devices if d]
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> List[room.Room]

        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            new_room = hb_room.duplicate()
            ph_hvac = getattr(hb_room.properties, "ph_hvac")  # type: RoomPhHvacProperties
            new_hvac = copy(ph_hvac.duplicate())

            # -- Add the new Renewable Devices to the room's hvac system
            for renewable_device in self.renewable_devices:
                new_hvac.add_renewable_device(renewable_device)
                print(
                    "Adding Renewable-Device '{}' to HB-Room: '{}'".format(
                        renewable_device.display_name, new_room.display_name
                    )
                )

            # -- Output
            setattr(new_room.properties, "ph_hvac", new_hvac)
            hb_rooms_.append(new_room)

        return hb_rooms_
