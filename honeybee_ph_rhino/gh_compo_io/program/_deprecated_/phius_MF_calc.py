# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Phius MF Res Calculator."""

# TODO: REMOVE THIS MODULE... now just 'get' the data...

from collections import defaultdict

try:
    from typing import Any, List, Optional, Tuple, Type, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph.properties.room import RoomPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.load import ph_equipment, phius_mf
    from honeybee_energy_ph.properties.load.people import PeoplePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_standards.programtypes.default_elec_equip import ph_default_equip
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_standards:\n\t{}".format(e))

try:
    from honeybee_ph_utils.input_tools import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils.:\n\t{}".format(e))


def stories_error(_hb_rooms):
    # type (list[room.Room]) -> bool
    """Returns False if HBE-Stories are less than 2."""
    try:
        stories = {rm.story for rm in _hb_rooms}
        if len(stories) < 2:
            return True
        else:
            return False
    except AttributeError as e:
        return True


def spaces_error(_hb_rooms):
    # type: (list[room.Room]) -> Optional[room.Room]
    """Returns any Honeybee Room which does not have PH-Spaces."""
    for rm in _hb_rooms:
        if len(rm.properties.ph.spaces) == 0:  # type: ignore
            return rm
    return None


def people_error(_hb_rooms):
    # type: (list[room.Room]) -> Optional[room.Room]
    """Returns any room that does not have the 'People' HBE property applied."""
    for rm in _hb_rooms:
        if rm.properties.energy.people is None:  # type: ignore
            return rm
    return None


def check_inputs(_hb_rooms, _IGH):
    # type: (list[room.Room], gh_io.IGH) -> None
    """Validate the input Honeybee-Rooms.

    Arguments:
    ----------
        * _hb_rooms (list[room.Room]): A list of the honeybee-rooms to use.
        * _ghenv (ghenv): The Grasshopper Component ghenv for displaying warnings.

    Returns:
    --------
        * None
    """

    # -- Check the HBE-Stories
    if stories_error(_hb_rooms):
        msg = (
            "Warning: It appears that there is only 1 Honeybee-Story assigned to the "
            "Honeybee-Rooms? If that is true, ignore this warning. Otherwise, check that you "
            "have used the Honeybee 'Set Story' component to properly assign story ID numbers "
            "to each of the rooms in the project. This calculator sorts the rooms by story, "
            "so it is important to set the story attribute before using this component."
        )
        print(msg)
        _IGH.warning(msg)
    else:
        print("{} Stories found".format(len({rm.story for rm in _hb_rooms})))

    # -- Check that al the rooms have "PH-Spaces"
    rm_with_error = spaces_error(_hb_rooms)
    if rm_with_error:
        msg = (
            "Error: There are no PH-Spaces assigned to room: '{}'. Please be sure to assign the "
            "PH-Spaces before using this component. Use the HB-PH 'Create Spaces' and 'Add Spaces' "
            "components in order to add Spaces to all the Honeybee-Rooms.".format(rm_with_error.display_name)
        )
        print(msg)
        _IGH.error(msg)

    # -- Check that all the rooms have a "People"
    rm = people_error(_hb_rooms)
    if rm_with_error:
        msg = (
            "Error: There is no 'People' property assigned to room: '{}'. Be sure to use "
            "the HB-PH 'Set Occupancy' component to assign the number of bedrooms per-HB-Room "
            "before using this calculator.".format(rm_with_error.display_name)
        )
        _IGH.error(msg)
        print(msg)


def sort_rooms_by_story(_hb_rooms):
    # type: (list[room.Room]) -> list[list[room.Room]]
    """Returns lists of the rooms, organized by their Honeybee 'story'.

    Arguments:
    ----------
        * _hb_rooms (list[room.Room]):

    Returns:
    --------
        * list[list[room.Room]]:
    """

    d = defaultdict(list)
    for rm in _hb_rooms:
        d[rm.story].append(rm)
    return [d[story_key] for story_key in sorted(d.keys())]


def room_is_dwelling(_hb_room):
    # type: (room.Room) -> bool
    """Return True if the Honeybee-Room is a 'dwelling' (residential)?"""
    hb_room_prop_e = getattr(_hb_room.properties, "energy")  # type: RoomEnergyProperties
    hb_room_prop_e_prop_ph = getattr(hb_room_prop_e.people.properties, "ph")  # type: PeoplePhProperties
    return hb_room_prop_e_prop_ph.is_residential


# -----------------------------------------------------------------------------
# -- Component Interface


class GHCompo_CalcPhiusMFLoads(object):
    def __init__(
        self,
        _IGH,
        _int_light_HE_frac_,
        _ext_light_HE_frac_,
        _garage_light_HE_frac_,
        _include_elevator,
        _hb_rooms,
        _include_garage=False,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, float, float, float, bool, List[room.Room], bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.int_light_HE_frac_ = _int_light_HE_frac_
        self.ext_light_HE_frac_ = _ext_light_HE_frac_
        self.garage_light_HE_frac_ = _garage_light_HE_frac_
        self.include_elevator = _include_elevator
        self.include_garage = bool(_include_garage)
        self.hb_rooms = _hb_rooms

        msg = (
            "Deprecation Warning: This component should not be used any longer. Please use the new"
            "'HBPH - Set Residential Program' component instead."
        )
        print(msg)
        self.IGH.error(msg)
        raise Exception(msg)

    @property
    def num_dwelling_units(self):
        # type: () -> int
        """Return the total number of dwellings in the list of HB-Rooms."""
        ph_dwelling_objs = {r.properties.energy.people.properties.ph.dwellings for r in self.hb_rooms}  # type: ignore
        print("Found {} unique PH-Dwelling objects".format(len(ph_dwelling_objs)))
        return sum(d.num_dwellings for d in ph_dwelling_objs)

    @property
    def num_of_stories(self):
        # type: () -> int
        return len({rm.story for rm in self.hb_rooms})

    def calc_res_electric_consumption(self, _hb_res_rooms):
        # type: (List[room.Room]) -> Tuple[List[str], float, float, float, float, List[str]]

        # -------------------------------------------------------------------------------
        # -- Determine the Input Res Honeybee Room attributes by story

        rooms_by_story = sort_rooms_by_story(_hb_res_rooms)
        phius_stories = [phius_mf.PhiusResidentialStory(room_list) for room_list in rooms_by_story]
        phius_stories = sorted(phius_stories, reverse=True)

        # -------------------------------------------------------------------------------
        # -- Calculate the total Res. Elec. Energy Consumption
        mel_by_story = [story.mel for story in phius_stories]
        lighting_int_by_story = [story.lighting_int for story in phius_stories]
        lighting_ext_by_story = [story.lighting_ext for story in phius_stories]
        lighting_garage_by_story = [story.lighting_garage for story in phius_stories]

        total_res_mel = sum(mel_by_story)
        total_res_int_lighting = sum(lighting_int_by_story)
        total_res_ext_lighting = sum(lighting_ext_by_story)
        total_res_garage_lighting = sum(lighting_garage_by_story)

        # -------------------------------------------------------------------------------
        # -- Collect for output preview
        res_data_by_story_ = [
            ",".join(
                [
                    str(story.story_number),
                    str(story.total_floor_area_ft2),
                    str(story.total_number_dwellings),
                    str(story.total_number_bedrooms),
                ]
            )
            for story in phius_stories
        ]
        res_totals_ = [
            ",".join(
                [
                    str(story.design_occupancy),
                    str(story.mel),
                    str(story.lighting_int),
                    str(story.lighting_ext),
                    str(story.lighting_garage),
                ]
            )
            for story in phius_stories
        ]
        res_totals_.insert(
            0,
            str(
                "FLOOR-Design Occupancy, FLOOR-Televisions + Mis. Elec. Loads (kWh/yr), FLOOR-Interior Lighting (kWh/yr), FLOOR-Exterior Lighting (kWh/yr), Garage Lighting (kWh/yr)"
            ),
        )

        return (
            res_data_by_story_,
            total_res_mel,
            total_res_int_lighting,
            total_res_ext_lighting,
            total_res_garage_lighting,
            res_totals_,
        )

    def calc_non_res_electric_consumption(self, _hb_nonres_rooms):
        # type: (List[room.Room]) -> Tuple[float, float, List[str], List[str], List[str]]

        prog_collection = phius_mf.PhiusNonResProgramCollection()

        # -- Build a new Phius Non-Res-Space for each PH-Space found
        non_res_spaces = []  # type: List[phius_mf.PhiusNonResRoom]
        for hb_room in _hb_nonres_rooms:
            room_prop_ph = getattr(hb_room.properties, "ph")  # type: RoomPhProperties
            for space in room_prop_ph.spaces:
                new_nonres_space = phius_mf.PhiusNonResRoom.from_ph_space(space)
                prog_collection.add_program(new_nonres_space.program_type)
                non_res_spaces.append(new_nonres_space)

        # -- Calc total MEL
        total_nonres_mel = sum(sp.total_mel_kWh for sp in non_res_spaces)

        # -- Calc total Lighting
        total_nonres_int_lighting = sum(sp.total_lighting_kWh for sp in non_res_spaces)

        # -- Collect the program data for preview / output
        non_res_program_data_ = prog_collection.to_phius_mf_workbook()

        non_res_room_data_ = [sp.to_phius_mf_workbook() for sp in sorted(non_res_spaces, key=lambda x: x.name)]
        non_res_totals_ = [sp.to_phius_mf_workbook_results() for sp in sorted(non_res_spaces, key=lambda x: x.name)]
        non_res_totals_.insert(
            0,
            str(
                "Lighting Power Density (W/sf), Usage (days/year), Daily Usage (hrs/day), MELCOMM (kWh/yr.sf), LIGHTCOMM (kWh/yr), MELCOMM (kWh/yr)"
            ),
        )

        return (
            total_nonres_mel,
            total_nonres_int_lighting,
            non_res_program_data_,
            non_res_room_data_,
            non_res_totals_,
        )

    def get_elevator_class(self):
        # type: () -> Type[Union[ph_equipment.PhElevatorHydraulic, ph_equipment.PhElevatorGearedTraction, ph_equipment.PhElevatorGearlessTraction]]
        """Return the Elevator class, based on the number of stories."""
        if self.num_of_stories <= 6:
            return ph_equipment.PhElevatorHydraulic
        elif self.num_of_stories <= 20:
            return ph_equipment.PhElevatorGearedTraction
        else:
            return ph_equipment.PhElevatorGearlessTraction

    def build_elevator(self):
        # type: () -> Optional[Union[ph_equipment.PhElevatorHydraulic, ph_equipment.PhElevatorGearedTraction, ph_equipment.PhElevatorGearlessTraction]]
        """Return a new Elevator object."""
        elevator_class = self.get_elevator_class()
        elevator = elevator_class(_num_dwellings=self.num_dwelling_units)

        # -- Split out the energy across all the rooms
        elevator.energy_demand = elevator.energy_demand / len(self.hb_rooms)
        return elevator

    def build_garage_lighting(self, _bldg_avg_lighting_garage):
        # type: (float) -> ph_equipment.PhCustomAnnualLighting
        """Return a new Garage Lighting object."""
        lighting_garage = ph_equipment.PhCustomAnnualLighting(
            _defaults=ph_default_equip["PhCustomAnnualLighting"]["PHIUS"]
        )
        lighting_garage.energy_demand = _bldg_avg_lighting_garage
        lighting_garage.comment = "Garage Lighting - Phius MF Calculator"
        lighting_garage.in_conditioned_space = False
        return lighting_garage

    def create_new_MF_elec_equip(
        self,
        _hb_res_rooms,
        _hb_nonres_rooms,
        _total_res_mel,
        _total_nonres_mel,
        _total_res_int_lighting,
        _total_nonres_int_lighting,
        _total_res_ext_lighting,
        _total_res_garage_lighting,
    ):
        # type: (List[room.Room], List[room.Room], float, float, float, float, float, float) -> List[ph_equipment.PhEquipment]

        elec_equipment_ = []
        # ---------------------------------------------------------------------------
        # -- Calculate the Elec. Energy average per Honeybee-Room
        total_hb_rooms = len(_hb_res_rooms) + len(_hb_nonres_rooms)
        bldg_avg_mel_dwellings = _total_res_mel / total_hb_rooms
        bldg_avg_mel_non_res = _total_nonres_mel / total_hb_rooms
        bldg_avg_lighting_int = (_total_res_int_lighting + _total_nonres_int_lighting) / total_hb_rooms
        bldg_avg_lighting_ext = _total_res_ext_lighting / total_hb_rooms
        bldg_avg_lighting_garage = _total_res_garage_lighting / total_hb_rooms

        # ---------------------------------------------------------------------------
        # -- Create the new Phius MF Elec Equip
        mel = ph_equipment.PhCustomAnnualMEL(_defaults=ph_default_equip["PhCustomAnnualMEL"]["PHIUS"])
        mel.energy_demand = bldg_avg_mel_dwellings
        mel.comment = "MEL_Dwell - Phius MF Calculator"
        elec_equipment_.append(mel)

        mel = ph_equipment.PhCustomAnnualMEL(_defaults=ph_default_equip["PhCustomAnnualMEL"]["PHIUS"])
        mel.energy_demand = bldg_avg_mel_non_res
        mel.comment = "MEL_Comm - Phius MF Calculator"
        elec_equipment_.append(mel)

        lighting_int = ph_equipment.PhCustomAnnualLighting(
            _defaults=ph_default_equip["PhCustomAnnualLighting"]["PHIUS"]
        )
        lighting_int.energy_demand = bldg_avg_lighting_int
        lighting_int.comment = "Interior Lighting - Phius MF Calculator"
        elec_equipment_.append(lighting_int)

        lighting_ext = ph_equipment.PhCustomAnnualLighting(
            _defaults=ph_default_equip["PhCustomAnnualLighting"]["PHIUS"]
        )
        lighting_ext.energy_demand = bldg_avg_lighting_ext
        lighting_ext.comment = "Exterior Lighting - Phius MF Calculator"
        elec_equipment_.append(lighting_ext)

        if self.include_garage:
            elec_equipment_.append(self.build_garage_lighting(bldg_avg_lighting_garage))

        if self.include_elevator:
            elec_equipment_.append(self.build_elevator())

        return elec_equipment_

    def run(self):
        # defaults
        res_data_by_story_ = []
        res_totals_ = []
        non_res_program_data_ = []
        non_res_room_data_ = []
        non_res_totals_ = []
        elec_equipment_ = []
        hb_res_rooms_ = []
        hb_nonres_rooms_ = []
        total_nonres_mel = 0.0
        total_nonres_int_lighting = 0.0

        if self.hb_rooms:
            # ---------------------------------------------------------------------------
            # -- Break out the Res from the non-Res HB-Rooms
            hb_res_rooms_ = [rm for rm in self.hb_rooms if room_is_dwelling(rm)]
            hb_nonres_rooms_ = [rm for rm in self.hb_rooms if not room_is_dwelling(rm)]

            if not hb_res_rooms_:
                msg = "Warning: No Residential HB-Rooms found?"
                self.IGH.warning(msg)

            # -- Check the inputs for errors, display warnings
            check_inputs(hb_res_rooms_, self.IGH)

            (
                res_data_by_story_,
                total_res_mel,
                total_res_int_lighting,
                total_res_ext_lighting,
                total_res_garage_lighting,
                res_totals_,
            ) = self.calc_res_electric_consumption(hb_res_rooms_)

            if hb_nonres_rooms_:
                (
                    total_nonres_mel,
                    total_nonres_int_lighting,
                    non_res_program_data_,
                    non_res_room_data_,
                    non_res_totals_,
                ) = self.calc_non_res_electric_consumption(hb_nonres_rooms_)

            elec_equipment_ = self.create_new_MF_elec_equip(
                hb_res_rooms_,
                hb_nonres_rooms_,
                total_res_mel,
                total_nonres_mel,
                total_res_int_lighting,
                total_nonres_int_lighting,
                total_res_ext_lighting,
                total_res_garage_lighting,
            )

        return (
            res_data_by_story_,
            res_totals_,
            non_res_program_data_,
            non_res_room_data_,
            non_res_totals_,
            elec_equipment_,
            hb_res_rooms_,
            hb_nonres_rooms_,
        )
