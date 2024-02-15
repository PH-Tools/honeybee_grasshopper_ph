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
    from honeybee_energy_ph.properties.hvac.idealair import IdealAirSystemPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.hvac.renewable_devices import PhRenewableEnergyDevice
    from honeybee_energy_ph.properties.hvac.idealair import IdealAirSystemPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_AddRenewableEnergyDevices(object):
    def __init__(self, _IGH, _renewable_devices=[], _hb_rooms=[], *args, **kwargs):
        # type: (gh_io.IGH, List[PhRenewableEnergyDevice], List[room.Room], *Any, **Any) -> None
        self.IGH = _IGH
        self.renewable_devices = _renewable_devices
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> List[room.Room]

        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            new_hvac = copy(hb_room.properties.energy.hvac.duplicate())  # type: ignore
            new_room = hb_room.duplicate()
            new_hvac_prop_ph = new_hvac.properties.ph  # type: IdealAirSystemPhProperties
            for renewable_device in self.renewable_devices:
                new_hvac_prop_ph.renewable_devices.add(renewable_device)
                print(
                    "Adding renewable device '{}' to the room: '{}'".format(
                        renewable_device.display_name, new_room.display_name
                    )
                )

            new_room.properties.energy.hvac = new_hvac  # type: ignore
            hb_rooms_.append(new_room)

        return hb_rooms_
