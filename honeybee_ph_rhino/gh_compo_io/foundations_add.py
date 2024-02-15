# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Foundations."""

try:
    from typing import List
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
    from honeybee_ph.foundations import PhFoundation
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))


class GHCompo_AddFoundations(object):
    def __init__(self, _IGH, _foundations, _hb_rooms):
        # type: (gh_io.IGH, List[PhFoundation], List[room.Room]) -> None
        self.IGH = _IGH
        self.foundations = _foundations
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> List[room.Room]
        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            new_hb_room = hb_room.duplicate()

            for ph_foundation in self.foundations:
                new_hb_room.properties.ph.add_foundation(ph_foundation)

            hb_rooms_.append(new_hb_room)

        return hb_rooms_
