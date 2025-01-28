# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set PH-Style Occupancy."""

from collections import defaultdict
from contextlib import contextmanager
from statistics import mean
import os

try:
    from typing import Generator
except ImportError:
    pass  # IronPython 2.7

try:
    from itertools import izip  # type: ignore
except ImportError:
    izip = zip  # Python 3

try:
    from honeybee.config import folders
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.load.people import People
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties.load.people import PeoplePhProperties
    from honeybee_ph_standards.schedules._load_schedules import load_schedules_from_json_file
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


@contextmanager
def unlocked(_hbe_people):
    # type: (People) -> Generator[People, None, None]
    """Unlock the HB-Energy 'People' load."""
    _hbe_people.unlock()  # type: ignore
    yield _hbe_people
    _hbe_people.lock()  # type: ignore


def _get_avg_occ_rate(_hb_room):
    # type: (Room) -> float
    """Get the HBE-People Occupancy-Schedule average annual value."""
    hbe_prop = getattr(_hb_room.properties, "energy")  # type: RoomEnergyProperties
    return mean(hbe_prop.people.occupancy_schedule.values())  # type: ignore


def _group_rooms_by_dwellings(_hb_rooms):
    # type: (list[Room]) -> list[list[Room]]
    """Group the HB-Rooms by their 'dwelling'."""
    room_groups = defaultdict(list)
    for hb_room in _hb_rooms:
        rm_prop_e = getattr(hb_room.properties, "energy")  # type: RoomEnergyProperties
        ppl_prop_ph = getattr(rm_prop_e.people.properties, "ph") # type: PeoplePhProperties
        room_groups[ppl_prop_ph.dwellings.identifier].append(hb_room)

    return [v for v in room_groups.values()]


def _get_room_floor_area_m2(_hb_room, _IGH):
    # type: (Room, gh_io.IGH) -> float
    room_floor_area_m2 = convert(_hb_room.floor_area, _IGH.get_rhino_areas_unit_name(), "M2") or 0.0
    if not room_floor_area_m2:
        _IGH.warning("Error: Room: '{}' has no floor surfaces?".format(_hb_room.display_name))
    return room_floor_area_m2


def set_number_of_bedrooms(_hb_rooms, _num_bedrooms):
    # type: (list[Room], list[int]) -> None
    """Set the number of bedrooms on each HB-Room."""
    for hb_room, n_br in izip(_hb_rooms, _num_bedrooms):
        hbe_prop = getattr(hb_room.properties, "energy")  # type: RoomEnergyProperties
        people_prop_ph = getattr(hbe_prop.people.properties, "ph")  # type: PeoplePhProperties
        people_prop_ph.number_bedrooms = n_br
        print("[{}] Setting Number of Bedrooms: {}".format(hb_room.display_name, n_br))
    return None


def set_number_of_people(_hb_rooms, _num_people):
    # type: (list[Room], list[float]) -> None
    """Set the number of people on each HB-Room."""
    for hb_room, n_ppl in izip(_hb_rooms, _num_people):
        hbe_prop = getattr(hb_room.properties, "energy")  # type: RoomEnergyProperties
        people_prop_ph = getattr(hbe_prop.people.properties, "ph")  # type: PeoplePhProperties
        people_prop_ph.number_people = n_ppl
        print("[{}] Setting Number of People: {}".format(hb_room.display_name, n_ppl))
    return None


def set_people_per_m2(_hb_rooms, _IGH):
    # type: (list[Room], gh_io.IGH) -> None
    """Set the HB-Energy 'People' load on each HB-Room.

    The HBE Occupancy level will be set for the entire 'dwelling'.
    """

    def _get_num_ppl(_hb_room):
        # type: (Room) -> float
        """Get the PH-Properties AVERAGE number of people in the room."""
        hb_ppl = getattr(_hb_room.properties, "energy")  # type: RoomEnergyProperties
        ppl_prop_ph = getattr(hb_ppl.people.properties, "ph")  # type: PeoplePhProperties
        return ppl_prop_ph.number_people

    for room_group in _group_rooms_by_dwellings(_hb_rooms):
        # -- Get 'Group' level total values
        total_average_ph_ppl = sum(_get_num_ppl(rm) for rm in room_group)
        total_floor_area_m2 = sum(_get_room_floor_area_m2(rm, _IGH) for rm in room_group)

        # -- Set the 'People' load for each room in the 'Group'
        for hb_room in room_group:
            total_peak_ppl = total_average_ph_ppl / _get_avg_occ_rate(hb_room)
            people_per_area = total_peak_ppl / total_floor_area_m2
            room_e_prop = getattr(hb_room.properties, "energy")  # type: RoomEnergyProperties

            # Note: we made sure to duplicate the room and the People before
            # so we can safely unlock the People load here.
            with unlocked(room_e_prop.people) as ppl:
                ppl.people_per_area = people_per_area
                print("[{}] Setting People/Area: {:.3f} ppl/m2".format(hb_room.display_name, people_per_area))
    return


def set_ph_res_occ_schedule(_hb_rooms):
    # type: (list[Room]) -> None
    """Set the PH-Style Occupancy Schedule on each HB-Room."""
    file_pth = os.path.join(
        folders.python_package_path, "honeybee_ph_standards", "schedules", "hbph_sfh_occupancy.json"
    )
    occ_schd = load_schedules_from_json_file(file_pth)["hbph_sfh_Occupant_Presence"]
    activity_schd = load_schedules_from_json_file(file_pth)["hbph_sfh_Occupant_Activity"]

    for hb_room in _hb_rooms:
        room_e_prop = getattr(hb_room.properties, "energy")  # type: RoomEnergyProperties
        if not room_e_prop.people:
            continue

        # Note: we made sure to duplicate the room and the People before
        # so we can safely unlock the People load here.
        with unlocked(room_e_prop.people) as ppl:
            print("[{}] Setting PH-Style Occupancy Schedules".format(hb_room.display_name))
            ppl.occupancy_schedule = occ_schd
            ppl.activity_schedule = activity_schd


class GHCompo_SetResOccupancy(object):
    def __init__(self, _IGH, _num_bedrooms, _num_people, _set_ph_res_schedule, _hb_rooms):
        # type: (gh_io.IGH, list[int], list[float], bool | None, list[Room]) -> None
        self.IGH = _IGH
        self._number_bedrooms = _num_bedrooms
        self._number_people = _num_people
        self.set_ph_res_schedule = False if _set_ph_res_schedule == False else True
        self.hb_rooms = _hb_rooms

    @property
    def max_input_length(self):
        # type: () -> int
        """Return the maximum length of the inputs."""
        return max([len(self._number_bedrooms), len(self._number_people), len(self.hb_rooms)])

    @property
    def any_input(self):
        # type: () -> bool
        """Return True if *any* inputs are provided"""
        return any(
            (
                len(self._number_bedrooms) > 0,
                len(self._number_people) > 0,
            )
        )

    @property
    def all_inputs(self):
        # type: () -> bool
        """Return True if *all* inputs are provided"""
        return all(
            (
                len(self._number_bedrooms) > 0,
                len(self._number_people) > 0,
            )
        )

    @property
    def all_required_inputs(self):
        # type: () -> bool
        """Return False if any of the required inputs are missing."""
        if not self.any_input:
            return False
        elif self.any_input and not self.all_inputs:
            msg = "Please provide the '_num_bedrooms' and '_num_people' for the Honeybee Rooms."
            self.IGH.warning(msg)
            return False
        else:
            return True

    @property
    def all_rooms_have_HBE_People(self):
        # type: () -> bool
        """Return True if all rooms have an HB-Energy 'People' load."""
        for hb_room in self.hb_rooms:
            hbe_prop = getattr(hb_room.properties, "energy")  # type: RoomEnergyProperties
            if not hbe_prop.people:
                raise Exception("Error: room {} is missing an HB-Energy 'People' load?".format(hb_room.display_name))
        return True

    @property
    def number_bedrooms(self):
        # type: () -> list[int]
        """Return the number of bedrooms for each room."""
        if len(self._number_bedrooms) != self.max_input_length:
            self._number_bedrooms += [self._number_bedrooms[-1]] * (self.max_input_length - 1)
        return self._number_bedrooms

    @property
    def number_people(self):
        # type: () -> list[float]
        """Return the number of people for each room."""
        if len(self._number_people) != self.max_input_length:
            self._number_people += [self._number_people[-1]] * (self.max_input_length - 1)
        return self._number_people

    def duplicate_rooms(self, _hb_rooms):
        # type: (list[Room]) -> list[Room]
        """Duplicate the HB-Rooms AND the HBE-People Load."""
        dup_rooms_ = []  # type: list[Room]
        for r in _hb_rooms:
            dup_room = r.duplicate()
            room_e_prop = getattr(dup_room.properties, "energy")  # type: RoomEnergyProperties
            room_e_prop.people = room_e_prop.people.duplicate()
            dup_rooms_.append(dup_room)
        return dup_rooms_

    def run(self):
        # type: () -> list[Room]
        if not self.all_required_inputs:
            return self.hb_rooms

        if not self.all_rooms_have_HBE_People:
            return self.hb_rooms

        hb_rooms_ = self.duplicate_rooms(self.hb_rooms)
        if self.set_ph_res_schedule:
            set_ph_res_occ_schedule(hb_rooms_)
        set_number_of_bedrooms(hb_rooms_, self.number_bedrooms)
        set_number_of_people(hb_rooms_, self.number_people)
        set_people_per_m2(hb_rooms_, self.IGH)
        return hb_rooms_
