# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Get Occupancy."""

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
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")

try:
    from ph_units.converter import convert
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))

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


def get_num_of_dwellings(_hb_rooms):
    # type: (list[Room]) -> int
    """Return the total number of dwellings in the list of HB-Rooms."""
    ph_dwelling_objs = {r.properties.energy.people.properties.ph.dwellings for r in _hb_rooms}  # type: ignore
    print("Found {} unique PH-Dwelling objects".format(len(ph_dwelling_objs)))
    return sum(d.num_dwellings for d in ph_dwelling_objs)


class GHCompo_GetResOccupancy(object):
    def __init__(self, _IGH, _hb_rooms):
        # type: (gh_io.IGH, list[Room]) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> tuple

        total_num_ppl = 0.0
        total_num_br = 0.0
        total_num_dwellings = get_num_of_dwellings(self.hb_rooms)
        for hb_room in self.hb_rooms:
            print("- " * 25)
            hbe_prop = getattr(hb_room.properties, "energy")  # type: RoomEnergyProperties
            if not hbe_prop.people:
                continue

            # -- Calculate the number of occupants
            hbph_ppl_prop = getattr(hbe_prop.people.properties, "ph")  # type: PeoplePhProperties
            area_m2 = get_area_value_in_unit(self.IGH, hb_room.floor_area, "M2")
            if hbph_ppl_prop.number_people:
                # -- Try and get the PH-Style info first
                peak_ppl_per_m2 = hbph_ppl_prop.number_people / area_m2
                avg_ppl = float(hbph_ppl_prop.number_people)
            else:
                # -- If No PH-Style data, try and use the HB-E info
                peak_ppl_per_m2 = hbe_prop.people.people_per_area
                avg_occ_rate = mean(hbe_prop.people.occupancy_schedule.values())  # type: ignore
                avg_ppl = peak_ppl_per_m2 * area_m2 * avg_occ_rate

            num_br = hbph_ppl_prop.number_bedrooms

            total_num_ppl += avg_ppl
            total_num_br += num_br

            # -- Preview
            print("{} | Floor Area={:.1f} m2".format(hb_room.display_name, area_m2))
            print("{} | People [Peak]={:.3f} ppl/m2".format(hb_room.display_name, peak_ppl_per_m2))
            print("{} | People [Avg.]={:.1f} ppl".format(hb_room.display_name, avg_ppl))
            print("{} | Number of Bedrooms={}".format(hb_room.display_name, num_br))

        return total_num_br, total_num_ppl, total_num_dwellings
