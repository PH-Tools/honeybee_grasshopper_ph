# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Spec. Heat Capacity."""

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
    from ph_gh_component_io.input_tools import input_to_int
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))

try:
    from honeybee_ph.properties.room import PhSpecificHeatCapacity, RoomPhProperties, get_ph_prop_from_room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_utils.enumerables import ValueNotAllowedError
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))


class GHCompo_SetRoomSpecHeatCaps(object):
    def __init__(self, _IGH, _spec_capacities, _hb_rooms):
        # type: (gh_io.IGH, list[str], list[room.Room]) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms
        self.spec_capacities = _spec_capacities

    def _get_user_input_for_idx(self, idx):
        # type: (int) -> str | int
        """Get user input for a given index, or return default ("1")."""
        try:
            input = self.spec_capacities[idx]
        except IndexError:
            print("Warning: no input provided for index {}. Using default value (1).".format(idx))
            input = "1"
        
        try:
            value = input_to_int(input) or "1"
            return value
        except ValueError as e:
            msg = "Error: the input for index {}: '{}' is not valid.\n{}".format(idx, input, e)
            raise Exception(msg)


    def get_spec_capacity_for_input_idx(self, idx):
        # type: (int) -> tuple[PhSpecificHeatCapacity, int | None]
        """Get the specific heat capacity type and value for a given input index."""
        spec_capacity_input = self._get_user_input_for_idx(idx)
        try:
            spec_capacity_type = PhSpecificHeatCapacity(spec_capacity_input)
            spec_capacity_value = None
            return spec_capacity_type, spec_capacity_value
        except ValueNotAllowedError:
            return PhSpecificHeatCapacity("6-USER_DEFINED"), int(spec_capacity_input)

    def run(self):
        # type: () -> list[room.Room]
        hb_rooms_ = [room.duplicate() for room in self.hb_rooms]  # type: list[room.Room]

        for i, room in enumerate(hb_rooms_):
            room_ph_props = get_ph_prop_from_room(room) # type: RoomPhProperties
            spec_capacity_type, spec_capacity_value = self.get_spec_capacity_for_input_idx(i)
            room_ph_props.specific_heat_capacity = spec_capacity_type
            room_ph_props.specific_heat_capacity_wh_m2k = spec_capacity_value

        return hb_rooms_
