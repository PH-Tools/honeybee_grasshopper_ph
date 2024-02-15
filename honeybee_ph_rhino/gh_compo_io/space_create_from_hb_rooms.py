# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Spaces from HB-Rooms"""

try:
    from typing import Any, List, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
    from honeybee.facetype import Floor
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ladybug_geometry.geometry3d import face
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_geometry:\n\t{}".format(e))

try:
    from ladybug_rhino.config import units_abbreviation
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee_ph import space
    from honeybee_ph.properties.room import RoomPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.make_spaces import make_volume
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
        value = converter.convert(
            default_height_value, default_height_unit, self.rh_doc_unit_type_abbreviation
        )
        if not value:
            msg = "Error: Failed to convert:" "'{}{}' to local unit-type: '{}'".format(
                default_height_value,
                default_height_unit,
                self.rh_doc_unit_type_abbreviation,
            )
            raise Exception(msg)
        return value

    def get_room_floor_surface(self, _hb_room):
        # type: (room.Room) -> List[face.Face3D]
        """Return a list of all the HB-Room's Floor surfaces as Face3Ds."""
        floor_faces_ = []
        for face in _hb_room.faces:
            if type(face.type) is Floor:
                floor_faces_.append(face.geometry)

        if not floor_faces_:
            msg = "Error: HB-Room '{}' has no floor surfaces?".format(
                _hb_room.display_name
            )
            raise Exception(msg)

        return floor_faces_

    def add_default_space(self, _hb_room):
        # type: (room.Room) -> room.Room
        """Create and then add a new Default Space to a Honeybee-Room based on the room's floor."""
        rm_ph_prop = _hb_room.properties.ph  # type: RoomPhProperties # type: ignore

        # -- Build new Floor Segment
        new_segments = []  # type: List[space.SpaceFloorSegment]
        for flr_srfc_geometry in self.get_room_floor_surface(_hb_room):
            new_segment = space.SpaceFloorSegment()
            new_segment.geometry = flr_srfc_geometry
            new_segment.reference_point = flr_srfc_geometry.center
            new_segments.append(new_segment)

        # -- Build new Floor
        new_floor = space.SpaceFloor()
        for new_segment in new_segments:
            new_floor.add_floor_segment(new_segment)
            new_floor.geometry = new_segment.geometry

        # -- Build new Volume
        new_volume = make_volume.volumes_from_floors(
            self.IGH, [new_floor], [self._default_height_in_local_units()]
        )

        # -- Build new Space
        new_space = space.Space(_host=rm_ph_prop)
        new_space.name = "{}_default_space".format(_hb_room.display_name)
        new_space.add_new_volumes(new_volume)

        # -- Add the space to the room
        rm_ph_prop.add_new_space(new_space)

        return _hb_room

    def run(self):
        # type: () -> List[room.Room]
        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            new_room = hb_room.duplicate()  # type: room.Room # type: ignore
            new_room = self.add_default_space(new_room)
            hb_rooms_.append(new_room)
        return hb_rooms_
