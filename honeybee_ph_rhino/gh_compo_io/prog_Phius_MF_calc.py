# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Phius MF Res Calculator."""


from collections import defaultdict

try:
    from typing import List, Optional
except ImportError:
    pass # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy_ph.load import phius_mf
    from honeybee_energy_ph.load import ph_equipment
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from honeybee_ph_standards.programtypes.default_elec_equip import ph_default_equip
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_standards:\n\t{}'.format(e))


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
        if len(rm.properties.ph.spaces) == 0:
            return rm
    return None


def people_error(_hb_rooms):
    # type: (list[room.Room]) -> Optional[room.Room]
    """Returns any room that does not have the 'People' HBE property applied."""
    for rm in _hb_rooms:
        if rm.properties.energy.people is None:
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
        msg = "Warning: It appears that there is only 1 Honeybee-Story assigned to the "\
            "Honeybee-Rooms? If that is true, ignore this warning. Otherwise, check that you "\
            "have used the Honeybee 'Set Story' component to properly assign story ID numbers "\
            "to each of the rooms in the project. This calculator sorts the rooms by story, "\
            "so it is important to set the story attribute before using this component."
        _IGH.warning(msg)
        print(msg)

    # -- Check that al the rooms have "PH-Spaces"
    rm_with_error = spaces_error(_hb_rooms)
    if rm_with_error:
        msg = "Error: There are no PH-Spaces assigned to room: '{}'. Please be sure to assign the "\
            "PH-Spaces before using this component. Use the HB-PH 'Create Spaces' and 'Add Spaces' "\
            "components in order to add Spaces to all the Honeybee-Rooms.".format(
                rm_with_error.display_name)
        _IGH.error(msg)

    # -- Check that all the rooms have a "People"
    rm = people_error(_hb_rooms)
    if rm_with_error:
        msg = "Error: There is no 'People' property assigned to room: '{}'. Be sure to use "\
            "the HB-PH 'Set Occupancy' component to assign the number of bedrooms per-HB-Room "\
            "before using this calculator.".format(rm_with_error.display_name)
        _IGH.error(msg)
        print(msg)


def sort_rooms_by_story(_hb_rooms):
    # type (list[room.Room]) -> list[list[room.Room]]
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


# -----------------------------------------------------------------------------
# -- Component Interface


class GHCompo_CalcPhiusMFLoads(object):
    
    def __init__(self, _IGH, _int_light_HE_frac_, _ext_light_HE_frac_, _garage_light_HE_frac_, _hb_rooms):
        # type: (gh_io.IGH, float, float, float, List[room.Room]) -> None
        self.IGH = _IGH
        self.int_light_HE_frac_ =_int_light_HE_frac_
        self.ext_light_HE_frac_ = _ext_light_HE_frac_
        self.garage_light_HE_frac_ = _garage_light_HE_frac_
        self.hb_rooms = _hb_rooms

    def _room_is_dwelling(self, _hb_room):
        # type: (room.Room) -> bool
        """Return True if the Honeybee-Room is a 'dwelling' (residential)?"""
        return _hb_room.properties.energy.people.properties.ph.is_dwelling_unit # type: ignore

    def run(self):
        res_data_by_story_ = []
        res_totals_ = []
        non_res_program_data_ = []
        non_res_room_data_ = []
        non_res_totals_ = []
        elec_equipment_ = []
        hb_res_rooms_ = []
        hb_nonres_rooms_ = []
        
        if self.hb_rooms:
            # ------------------------------------------------------------------------------
            # -- Break out the Res from the non-Res HB-Rooms
            hb_res_rooms_ = [rm for rm in self.hb_rooms if self._room_is_dwelling(rm)]
            hb_nonres_rooms_ = [rm for rm in self.hb_rooms if not self._room_is_dwelling(rm)] 
            
            if not hb_res_rooms_:
                msg = "Warning: No Residential HB-Rooms found?"
                self.IGH.warning(msg)

            # Calculate the Elec. Energy use for the residential HB-Rooms
            # ------------------------------------------------------------------------------
            # -- Check the inputs for errors, display warnings
            check_inputs(hb_res_rooms_, self.IGH.ghenv)

            # ------------------------------------------------------------------------------
            # -- Determine the Input Res Honeybee Room attributes by story

            rooms_by_story = sort_rooms_by_story( hb_res_rooms_ )
            phius_stories = [phius_mf.PhiusResidentialStory(room_list) for room_list in rooms_by_story]
            floor_area_by_story_m2_ = [story.total_floor_area_m2 for story in phius_stories]
            floor_area_by_story_ft2_ = [story.total_floor_area_ft2 for story in phius_stories]
            num_dwellings_by_story_ = [story.total_number_dwellings for story in phius_stories]
            num_bedrooms_by_story_ = [story.total_number_bedrooms for story in phius_stories]


            # ------------------------------------------------------------------------------
            # -- Calculate the total Res. Elec. Energy Consumption

            mel_by_story = [story.mel for story in phius_stories]
            lighting_int_by_story = [story.lighting_int for story in phius_stories]
            lighting_ext_by_story = [story.lighting_ext for story in phius_stories]
            lighting_garage_by_story = [story.lighting_garage for story in phius_stories]

            total_dwelling_units = sum(story.total_number_dwellings for story in phius_stories)
            total_res_mel = sum(mel_by_story)
            total_res_int_lighting = sum(lighting_int_by_story)
            total_res_ext_lighting = sum(lighting_ext_by_story)
            total_res_garage_lighting = sum(lighting_garage_by_story)
            
            # -- Collect for output preview
            res_data_by_story_ = [
                ",".join([
                    str(story.story_number),
                    str(story.total_floor_area_ft2),
                    str(story.total_number_dwellings),
                    str(story.total_number_bedrooms)
                ])
                for story in phius_stories]
                
            res_totals_ = [
                ",".join([
                    str(story.design_occupancy),
                    str(story.mel),
                    str(story.lighting_int),
                    str(story.lighting_ext),
                    str(story.lighting_garage),
                ])
                for story in phius_stories]
            res_totals_.insert(0, 
                    str("FLOOR-Design Occupancy, FLOOR-Televisions + Mis. Elec. Loads (kWh/yr), FLOOR-Interior Lighting (kWh/yr), FLOOR-Exterior Lighting (kWh/yr), Garage Lighting (kWh/yr)"))
            
            # ------------------------------------------------------------------------------
            # -- Calculate the Non-Res Elec. Energy Consumption
            total_nonres_mel = 0
            total_nonres_int_lighting = 0
            if hb_nonres_rooms_:
                prog_collection = phius_mf.PhiusNonResProgramCollection()

                # -- Build a new Phius Non-Res-Space for each PH-Space found
                non_res_spaces = []
                for hb_room in hb_nonres_rooms_:
                    for space in hb_room.properties.ph.spaces: # type: ignore
                        new_nonres_space = phius_mf.PhiusNonResRoom.from_ph_space(space)
                        
                        prog_collection.add_program(new_nonres_space.program_type)
                        
                        non_res_spaces.append(new_nonres_space)


                # -- Calc total MEL
                total_nonres_mel = sum( sp.total_mel_kWh for sp in non_res_spaces )
                
                # -- Calc total Lighting
                total_nonres_int_lighting = sum( sp.total_lighting_kWh for sp in non_res_spaces )
                
                # -- Collect the program data for preview / output
                non_res_program_data_ = prog_collection.to_phius_mf_workbook()
                
                non_res_room_data_ = [
                    sp.to_phius_mf_workbook() for sp in 
                    sorted(non_res_spaces, key=lambda x: x.name)
                    ]
                non_res_totals_ = [
                    sp.to_phius_mf_workbook_results() for sp in
                    sorted(non_res_spaces, key=lambda x: x.name)
                    ]
                non_res_totals_.insert(0, 
                    str("Lighting Power Density (W/sf), Usage (days/year), Daily Usage (hrs/day), MELCOMM (kWh/yr.sf), LIGHTCOMM (kWh/yr), MELCOMM (kWh/yr)"))
                
            
            # ------------------------------------------------------------------------------
            # -- Calculate the Elec. Energy average per Honeybee-Room
            total_hb_rooms = len(hb_res_rooms_) + len(hb_nonres_rooms_)
            bldg_avg_mel = (total_res_mel + total_nonres_mel) / total_hb_rooms
            bldg_avg_lighting_int = (total_res_int_lighting + total_nonres_int_lighting) / total_hb_rooms
            bldg_avg_lighting_ext = total_res_ext_lighting / total_hb_rooms
            bldg_avg_lighting_garage = total_res_garage_lighting / total_hb_rooms


            # ------------------------------------------------------------------------------
            # -- Create the new Phius MF Elec Equip
            mel = ph_equipment.PhCustomAnnualMEL(_defaults=ph_default_equip['PhCustomAnnualMEL']['PHIUS'])
            mel.energy_demand = bldg_avg_mel
            mel.comment = "MEL - Phius MF Calculator"
            elec_equipment_.append(mel)

            lighting_int = ph_equipment.PhCustomAnnualLighting(_defaults=ph_default_equip['PhCustomAnnualLighting']['PHIUS'])
            lighting_int.energy_demand = bldg_avg_lighting_int
            lighting_int.comment = "Interior Lighting - Phius MF Calculator"
            elec_equipment_.append(lighting_int)

            lighting_ext = ph_equipment.PhCustomAnnualLighting(_defaults=ph_default_equip['PhCustomAnnualLighting']['PHIUS'])
            lighting_ext.energy_demand = bldg_avg_lighting_ext
            lighting_ext.comment = "Exterior Lighting - Phius MF Calculator"
            elec_equipment_.append(lighting_ext)

            lighting_garage = ph_equipment.PhCustomAnnualLighting(_defaults=ph_default_equip['PhCustomAnnualLighting']['PHIUS'])
            lighting_garage.energy_demand = bldg_avg_lighting_garage
            lighting_garage.comment = "Garage Lighting - Phius MF Calculator"
            lighting_garage.in_conditioned_space = False
            elec_equipment_.append(lighting_garage)
        
        return (
            res_data_by_story_, res_totals_, non_res_program_data_, non_res_room_data_, 
            non_res_totals_, elec_equipment_, hb_res_rooms_,hb_nonres_rooms_
            )