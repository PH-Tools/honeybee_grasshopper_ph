# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Functions to Add Spaces onto Honeybee Rooms."""

from collections import namedtuple

try:
    from typing import Dict, List, Tuple
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ladybug_rhino.fromgeometry import from_point3d
    from ladybug_rhino.togeometry import to_point3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from ladybug_geometry import geometry3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_geometry:\n\t{}".format(e))

try:
    from honeybee_ph import space
    from honeybee_ph.properties.room import RoomPhProperties
    from honeybee_ph.properties.space import SpacePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))


# SpaceData = namedtuple("SpaceData", ["space", "reference_points"])


class SpaceData(object):
    """Temporary data class for organizing the space data and test points"""

    def __init__(self, space, reference_points):
        # type: (space.Space, List[geometry3d.Point3D]) -> None
        self.space = space
        self.reference_points = reference_points


def offset_space_reference_points(IGH, _space, _dist=0.0):
    # type (gh_io.IGH, space.Space, float) -> space.Space
    """Move the Space's floor segments 'up' in the world-Z some distance. This is
        useful since if the reference point is directly 'on' the honeybee-Room's floor
        surface, sometimes it will not test as 'inside' correctly. Tolerance issue?

    Arguments:
    ----------
        * IGH (gh_io.IGH): The Grasshopper interface object.
        * _space (space.Space): A Space to operate on.
        * _dist (float): A distance to offset the reference point.

    Returns:
    --------
        * space.Space: A copy of the input Space with the floor-segment reference
            points modified.
    """
    # -------------------------------------------------------------------------
    if _dist == 0:
        return _space

    # -------------------------------------------------------------------------
    new_space = _space.duplicate()
    for volume in new_space.volumes:
        for seg in volume.floor._floor_segments:
            seg.reference_point = to_point3d(
                IGH.ghpythonlib_components.Move(
                    from_point3d(seg.reference_point),
                    IGH.ghpythonlib_components.UnitZ(_dist),
                ).geometry
            )
    return new_space


def set_absolute_ventilation(_hb_room, _new_room_airflow):
    # type: (room.Room, float) -> room.Room
    """Set the Absolute Ventilation on an HB-Room's .properties.energy

    Implemented to support HBE <1.5 and 1.6 where they corrected the type on the
    attribute name (added the missing 's' in 'absolute')

    Arguments:
    ----------
        * _hb_room (room.Room): The Room to set the
            .properties.energy.absolute_ventilation rate for.
        * _new_room_airflow (float): The new absolute ventilation flow-rate.

    Returns:
    --------
        * (room.Room): The HB-Room with the .properties.energy modified.
    """

    rm_prop_energy = (
        _hb_room.properties.energy
    )  # type: RoomEnergyProperties # type: ignore
    if hasattr(_hb_room, "abolute_ventilation"):
        rm_prop_energy.abolute_ventilation(_new_room_airflow)  # type: ignore
    else:
        rm_prop_energy.absolute_ventilation(_new_room_airflow)

    return _hb_room


def add_spaces_to_honeybee_rooms(_spaces, _hb_rooms, _inherit_names=False):
    # type: (List[space.Space], List[room.Room], bool) -> Tuple[List[room.Room], List[SpaceData], List[room.Room]]
    """Sorts a list of Spaces, checks which are 'in' which HB-Room, and adds the space to that room.

    Arguments:
    ----------
        * _spaces (list[space.Space]) A list of Spaces.
        * _hb_rooms (list[room.Room]): A list of Honeybee Rooms.
        * _inherit_names (bool) default=False. Set True to override all space names
            with the name of the parent Honeybee-Room.

    Returns:
    --------
        (list[room.Room]): A list of Honeybee rooms with Spaces added to them.
    """

    # -------------------------------------------------------------------------
    # -- Organize the spaces into a dict and pull out the reference points
    # -- This is done to avoid re-collecting the points at each is_point_inside
    # -- check and so that 'del' can be used to speed up the hosting checks.
    spaces_dict = {}  # type: Dict[int, SpaceData]
    for space in _spaces:
        spaces_dict[id(space)] = SpaceData(space, [pt for pt in space.reference_points])

    # -------------------------------------------------------------------------
    # -- Add the spaces to the host-rooms
    new_rooms = []
    open_rooms = []
    for hb_room in _hb_rooms:
        dup_room = hb_room.duplicate()  # type: room.Room # type: ignore

        # -- Check to ensure that the room is actually solid first
        if not dup_room.geometry.is_solid:
            print(
                "Error: Room {} not solid. Cannot host spaces.".format(
                    dup_room.display_name
                )
            )
            open_rooms.append(dup_room)
            continue

        # -- See if any of the Space Reference points are inside the Room Geometry
        for space_data_id, space_data in spaces_dict.items():
            for pt in space_data.reference_points:
                if not dup_room.geometry.is_point_inside(pt):
                    continue

                print(
                    "Hosting Space: {}  in HB-Room: {}".format(
                        space_data.space.name, dup_room.display_name
                    )
                )

                sp = space_data.space.duplicate()
                sp.host = dup_room

                # -- If 'inherit names', simplify the spaces so that
                # -- there is only a single space inside of the HB-Room
                # -- and it will inherit its name from the parent HB-Room.
                dup_rm_prop_ph = (
                    dup_room.properties.ph
                )  # type: RoomPhProperties # type: ignore
                if _inherit_names:
                    sp.name = dup_room.display_name
                    dup_rm_prop_ph.merge_new_space(sp)
                else:
                    dup_rm_prop_ph.add_new_space(sp)

                # -- Add in any detailed PH-Style vent flow rates if they exist
                sp_prop_ph = sp.properties.ph  # type: SpacePhProperties # type:ignore
                if sp_prop_ph.has_ventilation_flow_rates:
                    space_flow_rate = (
                        sp_prop_ph.honeybee_flow_rate
                    )  # type: float # type: ignore

                    dup_room_prop_energy = (
                        dup_room.properties.energy
                    )  # type: RoomEnergyProperties # type: ignore
                    existing_room_flow = float(
                        dup_room_prop_energy.ventilation.flow_per_zone
                    )
                    new_room_flow = space_flow_rate + existing_room_flow
                    dup_room = set_absolute_ventilation(dup_room, new_room_flow)

                # -- to speed up further checks
                del spaces_dict[space_data_id]
                break

        new_rooms.append(dup_room)

    # -- There should not be any spaces left in the dict if all were
    # -- hosted properly. Raise warning error if any are un-hosted?
    un_hosted_spaces = []
    if spaces_dict:
        for space in spaces_dict.values():
            un_hosted_spaces.append(space)

    return new_rooms, un_hosted_spaces, open_rooms
