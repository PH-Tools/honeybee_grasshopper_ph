# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Thermal Bridges to Rooms."""

try:
    from typing import List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph.properties.room import RoomPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction import thermal_bridge
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_AddTBs(object):
    def __init__(self, _hb_rooms, _thermal_bridges):
        # type: (List[room.Room], List[thermal_bridge.PhThermalBridge]) -> None
        self.hb_rooms = _hb_rooms
        self.thermal_bridges = _thermal_bridges

    def run(self):
        # type: () -> List[room.Room]
        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            new_room = hb_room.duplicate()

            # -- add the new TBs to the HB-Room Building Segment
            for tb in self.thermal_bridges:
                rm_prop_ph = getattr(new_room.properties, "ph")  # type: RoomPhProperties
                rm_prop_ph.ph_bldg_segment.thermal_bridges[str(tb.identifier)] = tb

            hb_rooms_.append(new_room)

        return hb_rooms_
