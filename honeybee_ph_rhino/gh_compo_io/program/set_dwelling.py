# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Dwelling."""

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from System import Object  # type: ignore
except ImportError as e:
    pass  # IronPython 2.7

try:
    from honeybee.room import Room
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

# -----------------------------------------------------------------------------
# -- Component Interface


class GHCompo_SetDwelling(object):

    def __init__(self, _IGH, _hb_rooms):
        # type: (gh_io.IGH, DataTree[Room]) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> DataTree[Room]
        hb_rooms_ = DataTree[Object]()
        for i, branch in enumerate(self.hb_rooms.Branches):
            temp_ = []
            dwelling_name = clean_and_id_ep_string("HBPH_DWELLING")
            for hb_room in branch:
                new_room = hb_room.duplicate()
                new_room.zone = dwelling_name
                temp_.append(new_room)
            hb_rooms_.AddRange(temp_, GH_Path(i))
        return hb_rooms_
