# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set PH-Style Occupancy."""

try:
    from typing import List
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
except ImportError:
    pass  # Outside GH

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
    from honeybee_energy_ph.properties.load.people import PeoplePhProperties, PhDwellings
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


class GHCompo_SetResOccupancy(object):
    def __init__(self, _IGH, _num_bedrooms, _num_dwellings, _num_people, _hb_rooms):
        # type: (gh_io.IGH, DataTree[List[int]], DataTree[List[int]], DataTree[List[float]], DataTree[List[room.Room]]) -> None
        self.IGH = _IGH
        self._number_bedrooms = _num_bedrooms
        self._number_dwellings = _num_dwellings
        self._number_people = _num_people
        self.hb_rooms = _hb_rooms

    def input_has_branches(self, _input_tree):
        # type: (DataTree) -> bool
        return _input_tree.BranchCount > 0

    @property
    def any_input(self):
        # type: () -> bool
        """Return True if *any* input DataTrees are provided"""
        return any(
            (
                self.input_has_branches(self._number_bedrooms),
                self.input_has_branches(self._number_dwellings),
                self.input_has_branches(self._number_people),
            )
        )

    @property
    def all_inputs(self):
        # type: () -> bool
        """Return True if *all* input DataTrees are provided"""

        return all(
            (
                self.input_has_branches(self._number_bedrooms),
                self.input_has_branches(self._number_dwellings),
                self.input_has_branches(self._number_people),
            )
        )

    def get_number_bedrooms(self, _branch_number, _list_index):
        # type: (int, int) -> int
        """Figure out the right user-input Num. of Bedrooms to assign to the Room."""
        try:
            branch = self._number_bedrooms.Branch(_branch_number)  # type: List[int]
        except:
            msg = "Error: '_num_bedrooms' has no Branch number {}".format(_branch_number)
            raise Exception(msg)

        try:
            # -- Set the num. bedrooms according to the user input:
            return branch[_list_index]
        except ValueError as e:
            msg = "Error: No Num. of Bedrooms provided for " "Branch num. {}, item num. {}".format(
                _branch_number, _list_index
            )
            raise ValueError(msg)

    def get_number_people(self, _branch_number, _list_index):
        # type: (int, int) -> int
        """Figure out the right user-input Num. of People to assign to the Room."""
        try:
            branch = self._number_people.Branch(_branch_number)  # type: List[int]
        except:
            msg = "Error: '_number_people' has no Branch number {}".format(_branch_number)
            raise Exception(msg)

        try:
            # -- Set the num. dwellings according to the user input:
            return branch[_list_index]
        except ValueError as e:
            msg = "Error: No Num. of People provided for " "Branch num. {}, item num. {}".format(
                _branch_number, _list_index
            )
            raise ValueError(msg)

    def get_number_dwellings(self, _branch_num, _room_number):
        # type: (int, int) -> int
        """Return the user-input number of dwellings for each HB-Room."""
        try:
            num_dwellings = self._number_dwellings.Branch(_branch_num)[_room_number]
            hb_room = self.hb_rooms.Branch(_branch_num)[_room_number]
            self.IGH.remark("Setting HB-Room: '{}' num_dwellings to {}".format(hb_room.display_name, num_dwellings))
            return num_dwellings
        except Exception as e:
            msg = (
                "Error: Ensure that the data provided to '_num_dwellings' matches "
                "the shape of '_hb_rooms'. They should have the same number of "
                "DataTree Branches, and the same number of items on each branch."
            )
            raise Exception(msg)

    def duplicate_people(self, _hb_room):
        # type: (room.Room) -> people.People
        """If the room does not already have a 'people' object, give warning."""
        new_room_prop_e = _hb_room.properties.energy  # type: RoomEnergyProperties # type: ignore
        if not new_room_prop_e.people:
            msg = (
                "Error: The Honeybee-Room '{}' does not have an HB-Energy 'People' load. "
                "Please apply a 'People' load to the room before proceeding.".format(_hb_room.display_name)
            )
            raise Exception(msg)

        new_people = new_room_prop_e.people.duplicate()  # type: people.People # type: ignore
        return new_people

    def branch_is_single_family(self, _branch_num):
        # type: (int) -> bool
        """Return True if the user has set only a '1' as the branch input for _num_dwellings."""
        if len(self._number_dwellings.Branch(_branch_num)) != 1:
            return False
        if self._number_dwellings.Branch(_branch_num)[0] != 1:
            return False
        return True

    def check_has_hb_people(self, _hb_room):
        # type: (room.Room) -> bool
        if not _hb_room.properties.energy.people:  # type: ignore
            raise Exception("Error: room {} is missing an HB-Energy 'People' load?".format(_hb_room.display_name))
        else:
            return True

    @property
    def branch_lengths_match(self):
        # type: () -> bool
        hb_rm_branch_len = self.hb_rooms.BranchCount
        br_branch_len = self._number_bedrooms.BranchCount
        dw_branch_len = self._number_dwellings.BranchCount
        ppl_branch_len = self._number_people.BranchCount

        if not hb_rm_branch_len == br_branch_len == dw_branch_len == ppl_branch_len:
            msg = (
                "Error: The input data BranchCounts do not match. You entered "
                "{} Honeybee Rooms Branches, {} 'Num-Bedroom' Branches, {} 'Num-Dwelling' "
                "Branches, and {} 'Num-People' Branches? Please enure all input DataTrees "
                "are the same shape and length.".format(hb_rm_branch_len, br_branch_len, dw_branch_len, ppl_branch_len)
            )
            print(msg)
            self.IGH.warning(msg)
            return False
        return True

    def branch_input_lengths_match(self, _branch_num):
        # type: (int) -> bool
        hb_rm_lst_len = len(self.hb_rooms.Branch(_branch_num))
        br_list_len = len(self._number_bedrooms.Branch(_branch_num))
        ppl_list_len = len(self._number_people.Branch(_branch_num))
        dwellings_list_len = len(self._number_people.Branch(_branch_num))

        if not hb_rm_lst_len == br_list_len == ppl_list_len == dwellings_list_len:
            msg = (
                "Please make sure all the input values match. On Branch number {} you input "
                "{} Honeybee-Rooms, but then input {} 'Num-Bedroom' values, {} 'Num-People' values, "
                "and {} 'Num-Dwellings' values? Please ensure that all input values are the same length.".format(
                    _branch_num,
                    hb_rm_lst_len,
                    br_list_len,
                    ppl_list_len,
                    dwellings_list_len,
                )
            )
            print(msg)
            self.IGH.warning(msg)
            return False
        return True

    def create_rooms_with_ph_occupancies(self):
        # type: () -> DataTree[List[room.Room]]
        hb_rooms_ = DataTree[room.Room]()

        for i, branch in enumerate(self.hb_rooms.Branches):
            if not self.branch_input_lengths_match(i):
                continue

            ph_single_fam_dwelling_ob = PhDwellings(_num_dwellings=1)

            for k, hb_room in enumerate(branch):
                self.check_has_hb_people(hb_room)
                dup_hb_room = hb_room.duplicate()  # type: room.Room
                room_floor_area_m2 = convert(hb_room.floor_area, self.IGH.get_rhino_areas_unit_name(), "M2") or 0.0
                if not room_floor_area_m2:
                    self.IGH.warning("Error: Room: '{}' has no floor surfaces?".format(hb_room.display_name))

                # -- Determine the PhDwellings object to use
                if self.branch_is_single_family(i):
                    # -- If it is single-family branch, apply the same branch-level PhDwellings
                    # -- to *all* the rooms in the branch.
                    _rm_lst = list(self.hb_rooms.Branch(i))
                    self.IGH.remark("Creating a Single-Dwelling from rooms: '{}'".format(_rm_lst))
                    ph_dwelling_obj = ph_single_fam_dwelling_ob
                else:
                    # -- If it is *not* a single family branch, build a new a PhDwellings object
                    # -- for each room, and set the value according to the user-input.
                    ph_dwelling_obj = PhDwellings(_num_dwellings=self.get_number_dwellings(i, k))

                # -- Duplicate the Room's HB-People and assign the Occupancy Attributes
                dup_rm_prop_e = dup_hb_room.properties.energy  # type: RoomEnergyProperties # type: ignore
                dup_people = dup_rm_prop_e.people.duplicate()  # type: people.People # type: ignore

                dup_people_prop_ph = dup_people.properties.ph  # type: PeoplePhProperties # type: ignore
                dup_people_prop_ph.number_bedrooms = self.get_number_bedrooms(i, k)
                dup_people_prop_ph.number_people = self.get_number_people(i, k)
                _ppl_per_m2 = dup_people_prop_ph.number_people / room_floor_area_m2
                dup_people_prop_ph.dwellings = ph_dwelling_obj
                dup_people.people_per_area = _ppl_per_m2

                # -- Assign the new HB-People back to the HB-Room
                dup_rm_prop_e.people = dup_people
                hb_rooms_.Add(dup_hb_room, GH_Path(i))

        return hb_rooms_

    @property
    def all_required_inputs(self):
        # type: () -> bool
        """Return False if any of the required inputs are missing."""
        if not self.any_input:
            return False
        elif self.any_input and not self.all_inputs:
            msg = "Please provide the number of bedrooms, people and dwelling units for the Honeybee Rooms."
            self.IGH.warning(msg)
            return False
        else:
            return True

    def run(self):
        # type: () -> DataTree[List[room.Room]]
        if not self.all_required_inputs:
            return self.hb_rooms

        if not self.branch_lengths_match:
            return self.hb_rooms

        return self.create_rooms_with_ph_occupancies()
