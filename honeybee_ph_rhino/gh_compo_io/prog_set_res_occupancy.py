# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Res Occupancy."""

try:
    from typing import List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
    from honeybee.properties import RoomProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.load import people
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties.load.people import PeoplePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_SetResOccupancy(object):
    def __init__(self, _IGH, _num_bedrooms, _num_dwellings, _num_people, _hb_rooms):
        # type: (gh_io.IGH, List[int], List[int], List[float], List[room.Room]) -> None
        self.IGH = _IGH
        self._number_bedrooms = _num_bedrooms
        self._number_dwellings = _num_dwellings
        self._number_people = _num_people
        self.hb_rooms = _hb_rooms

    @property
    def any_input(self):
        # type: () -> bool
        """Return True if any inputs are provided"""
        return any((self._number_bedrooms, self._number_dwellings, self._number_people))

    @property
    def all_inputs(self):
        # type: () -> bool
        """Return True if any inputs are provided"""
        return all((self._number_bedrooms, self._number_dwellings, self._number_people))

    def get_number_bedrooms(self, i):
        # type: (int) -> int
        """Figure out the right user-input Bedroom number to assign to the Room."""
        try:
            # -- Set the num. bedrooms according to the user input:
            return self._number_bedrooms[i]
        except IndexError:
            # -- Unless the user didn't provide the right number of input values
            # -- in which case: use the first provided value as the fallback.
            try:
                return self._number_bedrooms[0]
            except IndexError:
                msg = "Error: Please provided the num. of bedrooms in the HB-Room."
                raise Exception(msg)

    def get_number_dwellings(self, i):
        # type: (int) -> int
        """Figure out the right user-input Dwelling-Count to assign to the Room."""
        try:
            # -- Set the num. dwellings according to the user input:
            return self._number_dwellings[i]
        except IndexError:
            # -- Unless the user didn't provide the right number of input values
            # -- in which case: use the first provided value as the fallback.
            try:
                return self._number_dwellings[0]
            except IndexError:
                msg = "Error: Please provided the num. of dwellings units in the HB-Room."
                raise Exception(msg)

    def get_number_people(self, i):
        # type: (int) -> float
        """Figure out the right user-input Dwelling-Count to assign to the Room."""
        try:
            # -- Set the num. dwellings according to the user input:
            return self._number_people[i]
        except IndexError:
            # -- Unless the user didn't provide the right number of input values
            # -- in which case: use the first provided value as the fallback.
            try:
                return self._number_people[0]
            except IndexError:
                msg = "Error: Please provided the num. of people for the HB-Room."
                raise Exception(msg)

    def duplicate_people(self, _hb_room):
        # type: (room.Room) -> people.People
        """If the room does not already have a 'people' object, give warning."""
        new_room_prop_e = _hb_room.properties.energy # type: RoomEnergyProperties # type: ignore
        if not new_room_prop_e.people:
            msg = "Error: The Honeybee-Room '{}' does not have an HB-Energy 'People' load. "\
                "Please apply a 'People' load to the room before proceeding.".format(_hb_room.display_name)
            raise Exception(msg)
        
        new_people = new_room_prop_e.people.duplicate() # type: people.People # type: ignore
        return new_people

    def _new_room_with_properties_set(self, i, hb_room):
        # type: (int, room.Room) -> room.Room
        """Return a duplicate room with the new people attribute values set."""

        # -- Type Aliases
        new_room = hb_room.duplicate() # type: room.Room # type: ignore
        
        # -- Clean up the People (might be None)
        new_hb_ppl_obj = self.duplicate_people(new_room)
        new_hb_ppl_prop_ph = new_hb_ppl_obj.properties.ph  # type: PeoplePhProperties # type: ignore
        
        # -- Set the HB-people property attributes
        new_hb_ppl_prop_ph.is_dwelling_unit = True
        new_hb_ppl_prop_ph.number_dwelling_units = self.get_number_dwellings(i)
        new_hb_ppl_prop_ph.number_bedrooms = self.get_number_bedrooms(i)
        new_hb_ppl_prop_ph.number_people = self.get_number_people(i)
        _ppl_per_m2 = new_hb_ppl_prop_ph.number_people / hb_room.floor_area
        new_hb_ppl_obj.people_per_area = _ppl_per_m2

        # -- Set the new room's people with the new values
        new_room.properties.energy.people = new_hb_ppl_obj  # type: ignore

        return new_room

    def run(self):
        # type: () -> List[room.Room]

        # -- Check inputs
        if not self.any_input:
            return [rm for rm in self.hb_rooms]
        elif self.any_input and not self.all_inputs:
            msg = "Please provide the number of bedrooms, people and dwelling units for the Honeybee Rooms."
            self.IGH.warning(msg)
            return [rm for rm in self.hb_rooms]

        # -- Set the room bedroom count and figure out the number of people.
        return [
            self._new_room_with_properties_set(i, hb_room)
            for i, hb_room in enumerate(self.hb_rooms)
        ]
