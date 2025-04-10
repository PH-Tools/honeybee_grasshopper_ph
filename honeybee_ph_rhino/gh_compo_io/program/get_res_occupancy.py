# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Get Occupancy."""

try:
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")

try:
    from honeybee_ph_rhino.gh_compo_io.program._get_room_data import get_num_dwellings, get_num_occupants, get_num_bedrooms
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

class GHCompo_GetResOccupancy(object):
    def __init__(self, _IGH, _hb_rooms):
        # type: (gh_io.IGH, list[Room]) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> tuple
        if not self.hb_rooms:
            return 0, 0, 0

        total_num_ppl = sum(get_num_occupants(rm, self.IGH) for rm in self.hb_rooms)
        total_num_br = sum(get_num_bedrooms(rm) for rm in self.hb_rooms)
        total_num_dwellings = get_num_dwellings(self.hb_rooms)
        
        return total_num_br, total_num_ppl, total_num_dwellings
