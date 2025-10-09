# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Get Phius Multi-Family Non-Residential Room Load Data."""

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
    from honeybee_ph.properties.room import RoomPhProperties
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


def room_is_dwelling(_hb_room):
    # type: (Room) -> bool
    """Return True if the Honeybee-Room is a 'dwelling' (residential)?"""
    hb_room_prop_e = getattr(_hb_room.properties, "energy")  # type: RoomEnergyProperties
    hb_room_prop_e_prop_ph = getattr(hb_room_prop_e.people.properties, "ph")  # type: PeoplePhProperties
    return hb_room_prop_e_prop_ph.is_residential


# -----------------------------------------------------------------------------


def get_PhiusNonResRooms(_hb_rooms, _area_unit):
    # type: (list[Room], str) -> list[phius_mf.PhiusNonResRoom]
    """Returns a list of PhiusNonResRoom objects."""

    non_res_spaces = []
    for hb_room in _hb_rooms:
        room_prop_ph = getattr(hb_room.properties, "ph")  # type: RoomPhProperties
        for space in room_prop_ph.spaces:
            new_nonres_space = phius_mf.PhiusNonResRoom.from_ph_space(space, _area_unit)
            non_res_spaces.append(new_nonres_space)

    return non_res_spaces


def get_mf_calc_program_data(_phius_non_res_rooms):
    # type: (list[phius_mf.PhiusNonResRoom]) -> list[str]
    """Return the Phius Non-Res-Space program data, formatted to match the Phius Multifamily Calc."""

    prog_collection = phius_mf.PhiusNonResProgramCollection()
    for phius_non_res_room in _phius_non_res_rooms:
        prog_collection.add_program(phius_non_res_room.program_type)

    return prog_collection.to_phius_mf_workbook()


def get_mf_calc_room_data_as_string(non_res_spaces):
    # type: (list[phius_mf.PhiusNonResRoom]) -> tuple[list[str], list[str]]
    """Return the Phius Non-Res-Space electrical energy, by room, formatted to match the Phius Multifamily Calc."""

    non_res_room_data_ = [sp.to_phius_mf_workbook() for sp in sorted(non_res_spaces, key=lambda x: x.name)]
    non_res_totals_ = [sp.to_phius_mf_workbook_results() for sp in sorted(non_res_spaces, key=lambda x: x.name)]

    HEADER = "Lighting Power Density (W/sf), Usage (days/year), Daily Usage (hrs/day), MELCOMM (kWh/yr.sf), LIGHTCOMM (kWh/yr), MELCOMM (kWh/yr)"
    non_res_totals_.insert(0, HEADER)

    return non_res_room_data_, non_res_totals_


def get_total_energy_consumption(non_res_spaces):
    # type: (list[phius_mf.PhiusNonResRoom]) -> tuple[float, float]
    """Return the total annual energy consumption for the Non-Res. HB-Rooms."""

    total_mel_ = sum(sp.mel_kWh_yr for sp in non_res_spaces)
    total_lighting_ = sum(sp.total_lighting_kWh for sp in non_res_spaces)

    return total_mel_, total_lighting_


# -----------------------------------------------------------------------------
# -- Component Interface


class GHCompo_GetPhiusMFNonResidentialLoadData(object):
    def __init__(self, _IGH, _hb_rooms, *args, **kwargs):
        # type: (gh_io.IGH, list[Room], *Any, **Any) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> tuple[list[str], list[str], list[str], float, float, list[Room]]
        if not self.hb_rooms:
            return [], [], [], 0, 0, []

        # ---------------------------------------------------------------------
        # -- Break out the Non-Res. HB-Rooms, Create Non-Res. Spaces
        hb_nonres_rooms = [rm for rm in self.hb_rooms if not room_is_dwelling(rm)]
        phius_non_res_rooms = get_PhiusNonResRooms(hb_nonres_rooms, self.IGH.get_rhino_areas_unit_name())

        # ---------------------------------------------------------------------
        program_data = get_mf_calc_program_data(phius_non_res_rooms)
        room_data = get_mf_calc_room_data_as_string(phius_non_res_rooms)
        total_energy_consumption = get_total_energy_consumption(phius_non_res_rooms)

        return (program_data,) + room_data + total_energy_consumption + (hb_nonres_rooms,)
