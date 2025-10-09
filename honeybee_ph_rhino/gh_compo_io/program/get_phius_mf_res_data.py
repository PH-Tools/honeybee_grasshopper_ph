# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Get Phius Multi-Family Residential Room Load Data."""

from collections import defaultdict

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))


try:
    from honeybee_energy_ph.load import phius_mf
    from honeybee_energy_ph.properties.load.people import PeoplePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


# -----------------------------------------------------------------------------


def stories_error(_hb_rooms):
    # type (list[Room]) -> bool
    """Returns False if HBE-Stories are less than 2."""
    try:
        stories = {rm.story for rm in _hb_rooms}
        if len(stories) < 2:
            return True
        else:
            return False
    except AttributeError:
        return True


def spaces_error(_hb_rooms):
    # type: (list[Room]) -> Room | None
    """Returns any Honeybee Room which does not have PH-Spaces."""
    for rm in _hb_rooms:
        if len(rm.properties.ph.spaces) == 0:  # type: ignore
            return rm
    return None


def people_error(_hb_rooms):
    # type: (list[Room]) -> Room | None
    """Returns any room that does not have the 'People' HBE property applied."""
    for rm in _hb_rooms:
        if rm.properties.energy.people is None:  # type: ignore
            return rm
    return None


def check_res_room_inputs(_hb_rooms, _IGH):
    # type: (list[Room], gh_io.IGH) -> None
    """Validate the input Honeybee-Rooms."""
    if not _hb_rooms:
        msg = "Warning: No Residential HB-Rooms found?"
        print(msg)
        _IGH.warning(msg)

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


def room_is_dwelling(_hb_room):
    # type: (Room) -> bool
    """Return True if the Honeybee-Room is a 'dwelling' (residential)?"""
    hb_room_prop_e = getattr(_hb_room.properties, "energy")  # type: RoomEnergyProperties
    hb_room_prop_e_prop_ph = getattr(hb_room_prop_e.people.properties, "ph")  # type: PeoplePhProperties
    return hb_room_prop_e_prop_ph.is_residential


def sort_rooms_by_story(_hb_rooms):
    # type: (list[Room]) -> list[list[Room]]
    """Returns lists of the rooms, grouped by their Honeybee 'story'."""

    d = defaultdict(list)
    for rm in _hb_rooms:
        d[rm.story].append(rm)
    return [d[story_key] for story_key in sorted(d.keys())]


# -----------------------------------------------------------------------------


def create_phius_stories(_hb_rooms, _area_unit):
    # type: (list[Room], str) -> list[phius_mf.PhiusResidentialStory]
    """Create a list of PhiusResidentialStory objects from the HB-Rooms."""

    rooms_by_story = sort_rooms_by_story(_hb_rooms)
    phius_stories = [phius_mf.PhiusResidentialStory(room_list, _area_unit) for room_list in rooms_by_story]
    phius_stories = sorted(phius_stories, reverse=True)
    return phius_stories


def get_res_room_data_as_string(phius_stories):
    # type: (list[phius_mf.PhiusResidentialStory]) -> tuple[list[str], list[str]]
    """Return the Phius Story electrical energy, by level, formatted to match the Phius Multifamily Calc."""

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
        res_totals_,
    )


def get_total_energy_consumption(phius_stories):
    # type: (list[phius_mf.PhiusResidentialStory]) -> tuple[float, float, float, float]
    total_mel_ = 0
    total_lighting_int_ = 0
    total_lighting_ext_ = 0
    total_lighting_garage_ = 0

    for story in phius_stories:
        total_mel_ += story.mel
        total_lighting_int_ += story.lighting_int
        total_lighting_ext_ += story.lighting_ext
        total_lighting_garage_ += story.lighting_garage

    return (
        total_mel_,
        total_lighting_int_,
        total_lighting_ext_,
        total_lighting_garage_,
    )


# -----------------------------------------------------------------------------
# -- Component Interface


class GHCompo_GetPhiusMFResidentialLoadData(object):
    def __init__(self, _IGH, _hb_rooms, *args, **kwargs):
        # type: (gh_io.IGH, list[Room], *Any, **Any) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> tuple[list[str], list[str], float, float, float, float, list[Room]]
        if not self.hb_rooms:
            return [], [], 0, 0, 0, 0, []

        # ---------------------------------------------------------------------
        # -- Break out the Res, from the Non-Res. HB-Rooms
        hb_res_rooms_ = [rm for rm in self.hb_rooms if room_is_dwelling(rm)]

        # -- Check the inputs for errors, display warnings
        check_res_room_inputs(hb_res_rooms_, self.IGH)

        # ---------------------------------------------------------------------
        phius_stories = create_phius_stories(hb_res_rooms_, self.IGH.get_rhino_areas_unit_name())
        mf_calculator_check = get_res_room_data_as_string(phius_stories)
        total_energy_consumption = get_total_energy_consumption(phius_stories)

        return mf_calculator_check + total_energy_consumption + (hb_res_rooms_,)
