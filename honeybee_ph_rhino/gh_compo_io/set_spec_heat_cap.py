# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Spec. Heat Capacity."""

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
    from honeybee_ph.properties.room import PhSpecificHeatCapacity
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))


class GHCompo_SetRoomSpecHeatCaps(object):
    
    def __init__(self, _IGH, _spec_capacities, _hb_rooms):
        # type: (gh_io.IGH, List[str], List[room.Room]) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms
        self.spec_capacities = _spec_capacities

    def _get_user_input_spec_heat(self, i):
        # type: (int) -> str
        """Return a Specific Heat Cap. Type number. If non input, return the default (1)."""
        try:
            return str(self.spec_capacities[i]).strip().upper()
        except:
            try:
                return str(self.spec_capacities[0]).strip().upper()
            except:
                return "1"

    def spec_capacity(self, i):
        """Return Specific Heat Capacity enum."""
        return PhSpecificHeatCapacity(self._get_user_input_spec_heat(i))

    def run(self):
        # type: () -> List[room.Room]
        hb_rooms_ = [room.duplicate() for room in self.hb_rooms] # type: List[room.Room]

        for i, room in enumerate(hb_rooms_):
            room.properties.ph.specific_heat_capacity = self.spec_capacity(i)

        return hb_rooms_

