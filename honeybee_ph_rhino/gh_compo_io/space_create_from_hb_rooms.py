# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Spaces from HB-Rooms"""

try:
    from typing import List, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ladybug_rhino.config import units_abbreviation
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee_ph import space
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units import converter
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


class GHCompo_CreatePHSpacesFromHBRooms(object):
    DEFAULT_SPACE_HEIGHT = 2.5  # m

    def __init__(self, _IGH, _hb_rooms):
        # type: (gh_io.IGH, List[room.Room]) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms

    @property
    def rh_doc_unit_type_abbreviation(self):
        # type: () -> str
        """Return the Rhino file's unit-type as a string abbreviation. ie: "Meter" -> "M", etc.."""

        return units_abbreviation().upper()

    def _default_height_in_local_units(self):
        # type: () -> Union[float, int]
        """Return the default SpaceVolume height in the Rhino document unit-type."""

        default_height_value = self.DEFAULT_SPACE_HEIGHT
        default_height_unit = "M"
        local_unit = self.rh_doc_unit_type_abbreviation
        value = converter.convert(default_height_value, default_height_unit, local_unit)
        if not value:
            msg = "Error: Failed to convert:" "'{}{}' to local unit-type: '{}'".format(
                default_height_value,
                default_height_unit,
                local_unit,
            )
            raise Exception(msg)
        return value

    def add_default_space(self, _hb_room, _default_height):
        # type: (room.Room, Union[float, int]) -> room.Room
        """Create and then add a new Default Space to a Honeybee-Room based on the room's floor."""
        try:
            new_space = space.Space.from_room(_hb_room, _default_height)
        except (TypeError, ValueError) as e:
            self.IGH.error(str(e))
            raise
        _hb_room.properties.ph.add_new_space(new_space)

        return _hb_room

    def run(self):
        # type: () -> List[room.Room]
        try:
            default_height = self._default_height_in_local_units()
        except Exception as e:
            self.IGH.error(str(e))
            raise
        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            new_room = hb_room.duplicate()  # type: room.Room # type: ignore
            new_room = self.add_default_space(new_room, default_height)
            hb_rooms_.append(new_room)
        return hb_rooms_
