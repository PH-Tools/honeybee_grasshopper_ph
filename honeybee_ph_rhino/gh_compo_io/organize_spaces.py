# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Organize Spaces."""

try:
    from typing import Any, List
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from System import Object  # type: ignore
except:
    pass  # Outside Rhino

try:
    from honeybee.room import Room
except:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph.space import Space
except:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_OrganizeSpaces(object):
    """Transform HBPH Spaces into Rhino geometry which can be visualized."""

    def __init__(self, _IGH, _hb_rooms, *args, **kwargs):
        # type: (gh_io.IGH, List[Room], Any, Any) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> DataTree[List[Space]]
        spaces_ = DataTree[Object]()

        if not self.hb_rooms:
            return spaces_

        for i, room in enumerate(self.hb_rooms):
            spaces_.AddRange([sp.duplicate() for sp in room.properties.ph.spaces], GH_Path(i))

        return spaces_
