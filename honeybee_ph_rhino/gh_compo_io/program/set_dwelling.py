# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Dwelling."""

import os

try:
    from typing import Any
except ImportError as e:
    pass  # IronPython2.7

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from System import Object  # type: ignore
except ImportError as e:
    pass  # IronPython 2.7

try:
    from honeybee.config import folders
    from honeybee.room import Room
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.load.people import People
    from honeybee_energy.properties.room import RoomEnergyProperties
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties.load.people import PhDwellings
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties.load.people import PeoplePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_standards.schedules._load_schedules import load_schedules_from_json_file
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_standards:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


# -----------------------------------------------------------------------------
# -- Component Interface


def get_new_people(_hbe_people, _occ_schd, _act_schd):
    # type:  (People | None, ScheduleRuleset, ScheduleRuleset) -> People
    """Get a new HBE-People object."""
    if _hbe_people is None:
        return People(
            clean_and_id_ep_string("People"),
            0,
            _occ_schd,
            _act_schd,
        )
    else:
        return _hbe_people.duplicate()  # type: ignore


class GHCompo_SetDwelling(object):
    file_pth = os.path.join(
        folders.python_package_path, "honeybee_ph_standards", "schedules", "hbph_sfh_occupancy.json"
    )
    default_occ_schd = load_schedules_from_json_file(file_pth)["hbph_sfh_Occupant_Presence"]
    default_activity_schd = load_schedules_from_json_file(file_pth)["hbph_sfh_Occupant_Activity"]

    def __init__(self, _IGH, _num_dwellings, _hb_rooms, *args, **kwargs):
        # type: (gh_io.IGH, DataTree[int], DataTree[Room], *Any, **Any) -> None
        self.IGH = _IGH
        self.num_dwellings = _num_dwellings
        self.hb_rooms = _hb_rooms

    def get_num_dwellings(self, branch):
        # type: (int) -> int
        try:
            return self.num_dwellings.Branch(branch)[0]
        except Exception as e:
            return 1

    def run(self):
        # type: () -> DataTree[Room]
        hb_rooms_ = DataTree[Object]()
        for i, branch in enumerate(self.hb_rooms.Branches):

            # -- Create a new Dwelling Object to be applied to all the Rooms
            dwelling_name = clean_and_id_ep_string("HBPH_DWELLING")
            num_dwellings = self.get_num_dwellings(branch=i)
            ph_dwellings_obj = PhDwellings(_num_dwellings=num_dwellings)
            ph_dwellings_obj.identifier = dwelling_name

            # -- Set the Dwelling information on all the Rooms
            dup_rooms_ = []
            for hb_room in branch:
                print(
                    "Setting room: '{}' to residential: '{}' with {} dwelling unit(s)".format(
                        hb_room.display_name, dwelling_name, num_dwellings
                    )
                )
                dup_room = hb_room.duplicate()  # type: Room
                dup_room.zone = dwelling_name
                dup_room_prop_e = getattr(dup_room.properties, "energy")  # type: RoomEnergyProperties

                # -- Build the new People and add to the HB-Room
                # -- Note: be sure to duplicate the People before changing the dwelling.
                dup_ppl = get_new_people(dup_room_prop_e.people, self.default_occ_schd, self.default_activity_schd)
                ppl_prop_ph = getattr(dup_ppl.properties, "ph")  # type: PeoplePhProperties
                ppl_prop_ph.dwellings = ph_dwellings_obj
                dup_room_prop_e.people = dup_ppl

                dup_rooms_.append(dup_room)
            hb_rooms_.AddRange(dup_rooms_, GH_Path(i))
        return hb_rooms_
