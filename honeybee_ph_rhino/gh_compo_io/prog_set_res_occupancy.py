# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Res Occupancy."""

try:
    from typing import List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.load import people
    from honeybee_energy.lib import schedules
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

    def dup_hb_people(self, hb_obj, object_name, object_class):
        # type: (room.Room, str, type[people.People]) -> people.People
        """Duplicate an HB-People Load."""
        # get the always on schedule
        always_on = schedules.schedule_by_identifier("Always On")

        # try to get the load object assigned to the Room or ProgramType
        try:  # assume it's a Room
            load_obj = hb_obj.properties
            for attribute in ("energy", object_name):
                load_obj = getattr(load_obj, attribute)
        except AttributeError:  # it's a ProgramType
            load_obj = getattr(hb_obj, object_name)

        load_id = "{}_{}".format(hb_obj.identifier, object_name)
        try:  # duplicate the load object
            dup_load = load_obj.duplicate()
            dup_load.identifier = load_id
            return dup_load
        except AttributeError:  # create a new object
            try:  # assume it's People, Lighting, Equipment or Infiltration
                return object_class(load_id, 0, always_on)
            except:  # it's a Ventilation object
                return object_class(load_id)

    def get_number_bedrooms(self, i):
        # type: (int) -> int
        """Figure out the right user-input Bedroom number to assign to the Room."""
        try:
            # -- Set the num. bedrooms according to the user input:
            return self._number_bedrooms[i]
        except IndexError:
            # -- Unless the user didn't provide the right number of input values
            # -- in which case: use the first provided value as the fallback.
            return self._number_bedrooms[0]

    def get_number_dwellings(self, i):
        # type: (int) -> int
        """Figure out the right user-input Dwelling-Count to assign to the Room."""
        try:
            # -- Set the num. dwellings according to the user input:
            return self._number_dwellings[i]
        except IndexError:
            # -- Unless the user didn't provide the right number of input values
            # -- in which case: use the first provided value as the fallback.
            return self._number_dwellings[0]

    def get_number_people(self, i):
        # type: (int) -> float
        """Figure out the right user-input Dwelling-Count to assign to the Room."""
        try:
            # -- Set the num. dwellings according to the user input:
            return self._number_people[i]
        except IndexError:
            # -- Unless the user didn't provide the right number of input values
            # -- in which case: use the first provided value as the fallback.
            return self._number_people[0]

    def _new_room_with_properties_set(self, i, hb_room):
        # type: (int, room.Room) -> room.Room
        """Return a duplicate room with the new people attribute values set."""

        # -- Type Aliases
        new_room = hb_room.duplicate()
        new_hb_ppl_obj = self.dup_hb_people(new_room, "people", people.People)
        new_hb_ppl_prop_ph = new_hb_ppl_obj.properties.ph  # type: PeoplePhProperties

        # -- Set the HB-people property attributes
        new_hb_ppl_prop_ph.is_dwelling_unit = True
        new_hb_ppl_prop_ph.number_dwelling_units = self.get_number_dwellings(i)
        new_hb_ppl_prop_ph.number_bedrooms = self.get_number_bedrooms(i)
        new_hb_ppl_prop_ph.number_people = self.get_number_people(i)
        ppl_per_m2 = new_hb_ppl_prop_ph.number_people / hb_room.floor_area
        new_hb_ppl_obj.people_per_area = ppl_per_m2

        # -- Set the new room's people
        new_room.properties.energy.people = new_hb_ppl_obj  # type: ignore

        return new_room

    def run(self):
        # type: () -> List[room.Room]

        # -- If no bedroom info provided, just pass along the same rooms input.
        if not self._number_bedrooms:
            return [rm for rm in self.hb_rooms]

        # -- Set the room bedroom count and figure out the number of people.
        hb_rooms_ = [
            self._new_room_with_properties_set(i, hb_room)
            for i, hb_room in enumerate(self.hb_rooms)
        ]

        return hb_rooms_
