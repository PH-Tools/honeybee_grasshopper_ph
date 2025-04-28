# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Utility functions for getting room data from the Honeybee-Rooms."""

from statistics import mean

try:
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties.load.people import PeoplePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


def get_area_value_in_unit(_IGH, _input, _target_unit):
    # type: (gh_io.IGH, str | float, str) -> int | float
    """Get an area value in either the specified unit-type, or the Rhino-doc unit-type."""

    # -- If the user supplied an input unit, just use that
    input_value, input_unit = parse_input(_input)

    # -- Otherwise use the Rhino document unit system as the input unit-type
    if not input_unit:
        input_unit = _IGH.get_rhino_areas_unit_name()

    # -- convert the input value to Meters, always
    new_value = convert(input_value, input_unit, _target_unit)

    if not new_value:
        raise ValueError("Failed to parse {}?".format(_input))
    else:
        print("Converting: {} {} -> {:.4f} {}".format(input_value, input_unit, new_value, _target_unit))
        return new_value


def get_num_dwellings(_hb_rooms):
    # type: (list[Room]) -> int
    """Return the total number of dwellings in the list of HB-Rooms."""
    ph_dwelling_objs = {r.properties.energy.people.properties.ph.dwellings for r in _hb_rooms}  # type: ignore
    return sum(d.num_dwellings for d in ph_dwelling_objs)


def get_room_floor_area_ft2(_hb_room, _IGH):
    # type: (Room, gh_io.IGH) -> float
    """Get the floor area of the room in ft2."""

    return convert(_hb_room.floor_area, _IGH.get_rhino_areas_unit_name(), "FT2") or 0.0


def get_num_occupants(hb_room, _IGH):
    # type: (Room, gh_io.IGH) -> float
    hbe_prop = getattr(hb_room.properties, "energy")  # type: RoomEnergyProperties
    if not hbe_prop.people:
        return 0

    # -- Calculate the number of occupants
    hbph_ppl_prop = getattr(hbe_prop.people.properties, "ph", None)  # type: PeoplePhProperties | None
    area_m2 = get_area_value_in_unit(_IGH, hb_room.floor_area, "M2")
    if not hbph_ppl_prop:
        # -- If No PH-Style data, use the HB-Energy Program's info
        peak_ppl_per_m2 = hbe_prop.people.people_per_area
        avg_occ_rate = mean(hbe_prop.people.occupancy_schedule.values())  # type: ignore
        avg_ppl = peak_ppl_per_m2 * area_m2 * avg_occ_rate
    else:
        # -- Get the PH-Style info 
        peak_ppl_per_m2 = hbph_ppl_prop.number_people / area_m2
        avg_ppl = float(hbph_ppl_prop.number_people)

    return avg_ppl


def get_num_bedrooms(hb_room):
    # type: (Room) -> int
    hbe_prop = getattr(hb_room.properties, "energy")  # type: RoomEnergyProperties
    if not hbe_prop.people:
        return 0

    hbph_ppl_prop = getattr(hbe_prop.people.properties, "ph")  # type: PeoplePhProperties
    return hbph_ppl_prop.number_bedrooms
