# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Program: Single Family Home."""

import os

try:
    from typing import Optional
except ImportError:
    pass  # IronPython 2.7


try:
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))


try:
    from honeybee.config import folders
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))


try:
    from honeybee_energy.lib.programtypes import building_program_type_by_identifier, program_type_by_identifier
    from honeybee_energy.lib.schedules import schedule_by_identifier
    from honeybee_energy.load.equipment import ElectricEquipment
    from honeybee_energy.load.hotwater import ServiceHotWater
    from honeybee_energy.load.infiltration import Infiltration
    from honeybee_energy.load.lighting import Lighting
    from honeybee_energy.load.people import People
    from honeybee_energy.load.setpoint import Setpoint
    from honeybee_energy.load.ventilation import Ventilation
    from honeybee_energy.programtype import ProgramType
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))


try:
    from honeybee_ph_standards.schedules._load_schedules import load_schedules_from_json_file
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_standards:\n\t{}".format(e))


try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


def get_program(_base_program):
    # type: (str | ProgramType | None) -> ProgramType
    if _base_program is None:
        return ProgramType(clean_and_id_ep_string("HBPH_SFH_Program"))

    if isinstance(_base_program, str):
        try:
            _base_program = building_program_type_by_identifier(_base_program)
        except ValueError:
            _base_program = program_type_by_identifier(_base_program)
    new_program = _base_program.duplicate()
    new_program.identifier = clean_and_id_ep_string("HBPH_SFH_Program")
    return new_program


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


def create_people(gross_floor_area_m2, num_bedrooms, _presence_schedule, _activity_schedule):
    # type: (float, float, ScheduleRuleset, ScheduleRuleset) -> People
    """Create a People object for a single-family home.

    As per:
    Phius 2024 Certification Guidebook v24.1.1
    Residential: number-of-people = number of bedrooms + 1
    """

    num_people = num_bedrooms + 1
    peak_ppl = (num_people * len(_presence_schedule.values())) / sum(_presence_schedule.values())
    people_per_m2 = peak_ppl / gross_floor_area_m2

    print("{} Bedroom(s) | People={:.1f}".format(num_bedrooms, num_people))
    print("{:.1f} People [Avg.]".format(num_people))
    print("{:.1f} People [Peak] | Peak-People-per-m2={:.4f}".format(peak_ppl, people_per_m2))

    return People(
        identifier=clean_and_id_ep_string("HBPH_SFH_People"),
        people_per_area=people_per_m2,
        occupancy_schedule=_presence_schedule,
        activity_schedule=_activity_schedule,
    )


def create_interior_lighting(_net_floor_area_m2, _gross_floor_area_m2, _schedule, q_ffil=1.0):
    # type: (float, float, ScheduleRuleset, float) -> Lighting
    """Create a Lighting object for a single-family home

    * q_ffil is the ratio of the qualifying interior light fixtures to
        all interior light fixtures in qualifying interior light fixture locations.

    As per:
    Phius 2024 Certification Guidebook v24.1.1 | Normative Appendix 'N'
    """

    annual_kWH = (0.2 + 0.8 * (4 - 3 * q_ffil) / 3.7) * (455 + 0.8 * _net_floor_area_m2) * 0.8
    annual_WH = annual_kWH * 1000
    wH_per_timestep = annual_WH / len(_schedule.values())
    peak_watts = wH_per_timestep / sum(_schedule.values())
    watts_per_m2 = peak_watts / _gross_floor_area_m2

    return Lighting(
        identifier=clean_and_id_ep_string("HBPH_SFH_Lighting"),
        watts_per_area=watts_per_m2,
        schedule=_schedule,
        return_air_fraction=0.0,
        radiant_fraction=0.32,
        visible_fraction=0.25,
    )


def create_MEL(_net_floor_area_m2, _gross_floor_area_m2, _num_bedrooms, _schedule):
    # type: (float, float, float, ScheduleRuleset) -> ElectricEquipment
    """Create a Misc. Elec. (MEL) object for a single-family home.

    As per:
    2014 Building America House Simulation Protocols
    E. Wilson, C. Engebrecht Metzger, S. Horowitz, and R. Hendron
    National Renewable Energy Laboratory
    Section 2.1.8 Appliances and MEL | Table 25
    Miscellaneous electric loads (kWh/yr) = = 1185.4 + 180.2 x Nbr + 0.3188 x FFA
    """
    kWh_year = 1185.4 + 180.2 * _num_bedrooms + 0.3188 * _net_floor_area_m2
    Wh_year = kWh_year * 1000
    watts = Wh_year / 8760
    watts_per_m2 = watts / _gross_floor_area_m2
    return ElectricEquipment(
        identifier=clean_and_id_ep_string("HBPH_SFH_Equipment"),
        watts_per_area=watts_per_m2,
        schedule=_schedule,
    )


def create_infiltration(flow_per_ext_m2=0.0003):
    # type: (float) -> Infiltration
    """Create an Infiltration object for a single-family home."""
    return Infiltration(
        identifier=clean_and_id_ep_string("HBPH_PH_Infiltration"),
        flow_per_exterior_area=flow_per_ext_m2,
        schedule=schedule_by_identifier("Always On"),
    )


def create_ventilation():
    # type: () -> Ventilation
    """Create a Ventilation object for a single-family home."""
    return Ventilation(
        identifier=clean_and_id_ep_string("HBPH_SFH_Ventilation"),
        flow_per_person=0,
        flow_per_area=0,
        flow_per_zone=0,
        air_changes_per_hour=0.4,  # type: ignore
        schedule=None,
    )


def create_setpoint(_heating_schedule, _cooling_schedule, _dehumidifying_setpoint=60):
    # type: (ScheduleRuleset, ScheduleRuleset, float) -> Setpoint
    """Create a Setpoint object for a single-family home."""
    new_setpoint = Setpoint(
        identifier=clean_and_id_ep_string("HBPH_SFH_Setpoint"),
        heating_schedule=_heating_schedule,
        cooling_schedule=_cooling_schedule,
    )
    new_setpoint.dehumidifying_setpoint = _dehumidifying_setpoint
    return new_setpoint


def create_shw(_num_bedrooms, _gross_floor_area_m2, _schedule):
    # type: (float, float, ScheduleRuleset) -> ServiceHotWater
    """Create a Service Hot Water object for a single-family home.

    As per:
    2014 Building America House Simulation Protocols
    E. Wilson, C. Engebrecht Metzger, S. Horowitz, and R. Hendron
    National Renewable Energy Laboratory
    Section 2.1.4 Domestic Hot Water | Table 11
    Clothes washer = 2.35 + 0.78 x Nbr
    Dishwasher = 2.26 + 0.75 x Nbr
    Shower = 14.0 + 4.67 x Nbr
    Bath = 3.5 + 1.17 * Nbr
    Sinks = 12.5 + 4.16 x Nbr
    """

    gallons_per_day_clothes_washer = 2.35 + 0.78 * _num_bedrooms
    gallons_per_day_dishwasher = 2.26 + 0.75 * _num_bedrooms
    gallons_per_day_shower = 14 + 1.17 * _num_bedrooms
    gallons_per_day_bath = 3.5 + 1.17 * _num_bedrooms
    gallons_per_day_sinks = 12.5 + 4.16 * _num_bedrooms
    gallons_per_day_combined = (
        gallons_per_day_clothes_washer
        + gallons_per_day_dishwasher
        + gallons_per_day_shower
        + gallons_per_day_bath
        + gallons_per_day_sinks
    )
    gallons_per_hour_combined = gallons_per_day_combined / 24

    return ServiceHotWater(
        identifier=clean_and_id_ep_string("HBPH_PH_ServiceHotWater"),
        flow_per_area=convert(gallons_per_hour_combined, "GA", "L") / _gross_floor_area_m2,  # type: ignore
        schedule=_schedule,
        target_temperature=43.3,  # type: ignore
    )


class SchedulesCollection(object):
    """Convenience class to hold all the schedules for a single-family home."""

    def __init__(self, root_directory):
        # type: (str) -> None
        self.all_occupancy = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_occupancy.json"))
        self.all_lighting = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_lighting.json"))
        self.all_mel = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_electric_equipment.json"))
        self.all_setpoint = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_setpoint.json"))
        self.all_hot_water = load_schedules_from_json_file(os.path.join(root_directory, "hbph_sfh_hot_water.json"))

    @property
    def occupancy_presence(self):
        # type: () -> ScheduleRuleset
        return self.all_occupancy["hbph_sfh_Occupant_Presence"]

    @property
    def occupancy_activity(self):
        # type: () -> ScheduleRuleset
        return self.all_occupancy["hbph_sfh_Occupant_Activity"]

    @property
    def lighting(self):
        # type: () -> ScheduleRuleset
        return self.all_lighting["hbph_sfh_Lighting"]

    @property
    def mel(self):
        # type: () -> ScheduleRuleset
        return self.all_mel["hbph_sfh_MEL"]

    @property
    def heating_setpoint(self):
        # type: () -> ScheduleRuleset
        return self.all_setpoint["hbph_sfh_Heating_Setpoint"]

    @property
    def cooling_setpoint(self):
        # type: () -> ScheduleRuleset
        return self.all_setpoint["hbph_sfh_Cooling_Setpoint"]

    @property
    def hot_water(self):
        # type: () -> ScheduleRuleset
        return self.all_hot_water["hbph_sfh_Combined_HotWater"]


class GHCompo_CreatePHProgramSingleFamilyHome(object):
    # Schedule Files

    def __init__(self, _IGH, _base_program, _net_floor_area, _num_bedrooms, _hb_rooms):
        # type: (gh_io.IGH, str | ProgramType | None, float, float, list[Room]) -> None
        self.schedules = SchedulesCollection(
            os.path.join(folders.python_package_path, "honeybee_ph_standards", "schedules")
        )
        self.IGH = _IGH
        self._base_program = _base_program
        self.net_floor_area = _net_floor_area
        self.num_bedrooms = _num_bedrooms
        self.hb_rooms = _hb_rooms

    @property
    def ready(self):
        # type: () -> bool
        if self.net_floor_area is None or self.num_bedrooms is None or not self.hb_rooms:
            return False
        else:
            return True

    def run(self):
        # type: () -> ProgramType | None
        if not self.ready:
            return None

        # -- Figure out the reference areas to use
        net_floor_area_m2 = get_area_value_in_unit(self.IGH, self.net_floor_area, "M2")
        gross_floor_area_in_rh_doc_units = sum(r.floor_area for r in self.hb_rooms)
        gross_floor_area_m2 = get_area_value_in_unit(self.IGH, gross_floor_area_in_rh_doc_units, "M2")
        if not gross_floor_area_m2:
            raise ValueError("Failed to get gross floor area of HB-Rooms?")

        # -- Create the new ProgramType object and set all the loads and schedules
        prog = get_program(self._base_program)
        prog.people = create_people(
            gross_floor_area_m2,
            self.num_bedrooms,
            self.schedules.occupancy_presence,
            self.schedules.occupancy_activity,
        )
        prog.lighting = create_interior_lighting(
            net_floor_area_m2,
            gross_floor_area_m2,
            self.schedules.lighting,
        )
        prog.electric_equipment = create_MEL(
            net_floor_area_m2,
            gross_floor_area_m2,
            self.num_bedrooms,
            self.schedules.mel,
        )
        prog.infiltration = create_infiltration()
        prog.ventilation = create_ventilation()
        prog.setpoint = create_setpoint(
            self.schedules.heating_setpoint,
            self.schedules.cooling_setpoint,
        )
        prog.service_hot_water = create_shw(
            self.num_bedrooms,
            gross_floor_area_m2,
            self.schedules.hot_water,
        )
        return prog
