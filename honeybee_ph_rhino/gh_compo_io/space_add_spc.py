# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Add Spaces."""

try:
    from typing import List, Optional, Tuple
except ImportError:
    pass  # IronPython 2.7

try:
    from Rhino.Geometry import Point3d  # type: ignore
except ImportError as e:
    raise ImportError("Failed to import Rhino.Geometry.\n{}".format(e))

try:
    from ladybug_rhino.fromgeometry import from_point3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph import space
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.make_spaces import make_space
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


class GHCompo_AddPHSpaces(object):
    def __init__(self, _IGH, _spaces, _offset_dist, _inh_rm_nms, _hb_rooms):
        # type: (gh_io.IGH, List[space.Space], Optional[float], bool, List[room.Room]) -> None

        self.IGH = _IGH
        self.spaces = _spaces
        self.offset_dist = _offset_dist or "0.1 M"
        self.inherit_room_names = _inh_rm_nms
        self.hb_rooms = _hb_rooms

    def ready(self):
        return all([len(self.spaces) != 0 and len(self.hb_rooms) != 0])

    def run(self):
        # type: () -> Tuple[List[room.Room], List[Point3D], List[room.Room]]
        if not self.ready():
            return self.hb_rooms, [], []

        # ---------------------------------------------------------------------
        # -- Get the offset distance in Rhino document units
        val, unit = parse_input(self.offset_dist)
        doc_unit_name = self.IGH.get_rhino_unit_system_name()
        offset_dist = convert(val, unit or doc_unit_name, doc_unit_name)

        # ---------------------------------------------------------------------
        # -- Clean up the input spaces, host in the HB-Rooms
        spaces = [make_space.offset_space_reference_points(self.IGH, sp, offset_dist) for sp in self.spaces]
        (
            hb_rooms_,
            un_hosted_spaces,
            open_rooms_,
        ) = make_space.add_spaces_to_honeybee_rooms(spaces, self.hb_rooms, self.inherit_room_names)

        # ---------------------------------------------------------------------
        # -- Warn if any open rooms
        if open_rooms_:
            msg = "Error: Honeybee-Room are not closed: {}".format(open_rooms_)
            self.IGH.error(msg)

        # ---------------------------------------------------------------------
        # -- If any un_hosted_spaces, pull out their center points for troubleshooting
        # -- and raise a user-warning
        check_pts_ = [from_point3d(lbt_pt) for space_data in un_hosted_spaces for lbt_pt in space_data.reference_points]
        if un_hosted_spaces:
            msg = "Error: No host Honeybee-Rooms were found for the Spaces: '{}'".format(
                "\n".join([spd.space.full_name for spd in un_hosted_spaces])
            )
            print(msg)
            self.IGH.error(msg)

        # ---------------------------------------------------------------------
        return hb_rooms_, check_pts_, open_rooms_
