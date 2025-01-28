# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Program: Single Family Home."""

from collections import defaultdict
import os
from statistics import mean
from functools import partial

try:
    from System import Object  # type: ignore
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.room import Room
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
    from honeybee_energy.load.process import Process
    from honeybee_energy.programtype import ProgramType
    from honeybee_energy.schedule.ruleset import ScheduleRuleset
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_ph.properties.room import RoomPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_standards.schedules._load_schedules import load_schedules_from_json_file
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_standards:\n\t{}".format(e))

try:
    from honeybee_energy_ph.load import ph_equipment
    from honeybee_energy_ph.properties.load.process import ProcessPhProperties
    from honeybee_energy_ph.properties.load.lighting import LightingPhProperties
    from honeybee_energy_ph.properties.load.people import PeoplePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))

try:
    from honeybee_ph_rhino.gh_compo_io.program._schedules import SchedulesCollection
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


def get_total_spaces_area_rh_doc_units(_hb_rooms):
    # type: (list[Room]) -> float
    """Get the total area of all the spaces in the HB-Rooms."""
    return sum(
        space.weighted_net_floor_area 
        for room in _hb_rooms 
        for space in room.properties.ph.spaces # type: ignore
    ) or sum(r.floor_area for r in _hb_rooms)  


def _group_rooms_by_dwellings(_hb_rooms):
    # type: (list[Room]) -> list[list[Room]]
    """Group the HB-Rooms by their 'dwelling'."""
    room_groups = defaultdict(list)
    for hb_room in _hb_rooms:
        room_groups[hb_room.zone].append(hb_room)

    return [v for v in room_groups.values()]


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
        return new_value


def get_occupancy_values(_IGH, room_group):
    # type: (gh_io.IGH, list[Room]) -> tuple[float, float]
    num_bedrooms_ = 0
    num_people_ = 0

    # -- Try and get the PH-Style Occupancy, if it is set
    for room in room_group:
        prop_e = getattr(room.properties, "energy")  # type: RoomEnergyProperties
        if not prop_e.people:
            continue
        pp_prop_ph = getattr(prop_e.people.properties, "ph")  # type: PeoplePhProperties
        num_bedrooms_ += pp_prop_ph.number_bedrooms
        num_people_ += pp_prop_ph.number_people

    # -- If no PH-Style info, try and use the HBE-Style Occupancy information to determine the right values
    if not num_people_:
        msg = "No PH-Style Occupancy information found. Using HB-Energy-Occupancy information instead."
        _IGH.warning(msg)
        for room in room_group:
            prop_e = getattr(room.properties, "energy")  # type: RoomEnergyProperties
            if not prop_e.people:
                continue
            peak_ppl = prop_e.people.people_per_area * get_area_value_in_unit(_IGH, room.floor_area, "M2")
            num_people_ += peak_ppl * mean(prop_e.people.occupancy_schedule.values())  # type: ignore

        num_bedrooms_ = abs(num_people_ - 1) or 1

    return num_bedrooms_, num_people_


def set_people(_people, gross_floor_area_m2, num_people, _presence_schedule, _activity_schedule):
    # type: (People, float, float, ScheduleRuleset, ScheduleRuleset) -> People
    """Reset the HBE-People Load Attributes."""
    #
    # Note: For PH-Style residential occupancy, I think we should use the PH 'occupancy' as the 'peak' value,
    # even though it is really the 'average' value? If you have 2 BR, and an occupancy of '3',
    # then I think that should be the 'peak' for E+, even though it is the 'average' for PHPP/WUFI?
    #
    # If we wanted to determine a 'peak' value instead, we could use the occupancy schedule like this:
    # peak_ppl = num_people * mean(_presence_schedule.values()
    #
    peak_ppl = num_people
    people_per_m2 = peak_ppl / gross_floor_area_m2

    new_ppl = _people.duplicate() # type: People #type: ignore
    new_ppl.identifier=clean_and_id_ep_string("HBPH_SFH_People")
    new_ppl.people_per_area = people_per_m2
    new_ppl.occupancy_schedule = _presence_schedule
    new_ppl.activity_schedule = _activity_schedule
    return new_ppl


def set_interior_lighting(_lighting, _net_floor_area_ft2, _gross_floor_area_m2, _schedule, q_ffil=1.0):
    # type: (Lighting, float, float, ScheduleRuleset, float) -> Lighting
    """Reset the HBE-Lighting Attributes.

    ### Resnet 2014
    - https://codes.iccsafe.org/content/RESNET3012014P1/4-home-energy-rating-calculation-procedures-
    - Section 4.2.2.5.2.2: Interior Lighting
    - kWh/yr = 0.8 * [(4 - 3 * q_FFIL) / 3.7] * (455 + 0.8 * CFA) + 0.2 * (455 + 0.8 * CFA)

    ### Phius Certification Guidebook v24.1.1 | Appendix N | N-7
    - https://www.phius.org/phius-certification-guidebook
    - "The basic protocol for lighting and miscellaneous electric loads is that they are calculated at
    80% of RESNET (2013) levels for the 'Rated Home'. ... The RESNET lighting formulas have been expressed more
    compactly here but are algebraically equivalent to the published versions."
    - kWh/yr = n_unit * (0.2 + 0.8 * (4 - 3 * q_FFIL) / 3.7) * (455 + 0.8 * iCFA) * 0.8
    """

    INT_LIGHTING_W_PER_DWELLING = 455
    INT_LIGHTING_W_FT2 = 0.8
    PHIUS_RESNET_FRACTION = 0.8

    a = 0.2 + 0.8 * (4 - 3 * q_ffil) / 3.7
    b = INT_LIGHTING_W_PER_DWELLING + (INT_LIGHTING_W_FT2 * _net_floor_area_ft2)
    annual_kWh = a * b * PHIUS_RESNET_FRACTION
    annual_Wh = annual_kWh * 1000
    peak_watts = annual_Wh * mean(_schedule.values())
    peak_watts_per_m2 = peak_watts / _gross_floor_area_m2

    # -- Build the normal HBE-Lighting object
    hbe_lighting = _lighting.duplicate()  # type: Lighting # type: ignore
    hbe_lighting.identifier = clean_and_id_ep_string("HBPH_SFH_Lighting")
    hbe_lighting.watts_per_area = peak_watts_per_m2
    hbe_lighting.schedule = _schedule
    hbe_lighting.return_air_fraction = 0.0
    hbe_lighting.radiant_fraction = 0.32
    hbe_lighting.visible_fraction = 0.25

    # -- Add the PHEquipment Lighting Object
    ph_equip = ph_equipment.PhPhiusLightingInterior.phius_default()
    prop_ph = getattr(hbe_lighting.properties, "ph")  # type: LightingPhProperties
    prop_ph.ph_equipment = ph_equip
    return hbe_lighting


def set_zero_MEL(_elec_equip):
    # type: (ElectricEquipment) -> ElectricEquipment
    """Reset the HBE-Electric-Equipment Attributes. All electric equipment should be set using Process-Load objects."""

    hbe_ee = _elec_equip.duplicate()  # type: ElectricEquipment # type: ignore
    hbe_ee.identifier = clean_and_id_ep_string("HBPH_SFH_Equipment")
    hbe_ee.watts_per_area = 0.0
    hbe_ee.schedule = schedule_by_identifier("Always On")
    return hbe_ee


def set_infiltration(_infiltration, flow_per_ext_m2=0.0003):
    # type: (Infiltration, float) -> Infiltration
    """Reset the HBE-Infiltration Attributes."""
    hbe_infiltration = _infiltration.duplicate() # type: Infiltration # type: ignore
    hbe_infiltration.identifier=clean_and_id_ep_string("HBPH_PH_Infiltration")
    hbe_infiltration.flow_per_exterior_area=flow_per_ext_m2
    hbe_infiltration.schedule=schedule_by_identifier("Always On")
    return hbe_infiltration


def set_ventilation(_ventilation):
    # type: (Ventilation) -> Ventilation
    """Reset the HBE-Ventilation Attributes."""
    hbe_ventilation = _ventilation.duplicate()  # type: Ventilation # type: ignore
    hbe_ventilation.identifier=clean_and_id_ep_string("HBPH_SFH_Ventilation")
    hbe_ventilation.flow_per_person=0
    hbe_ventilation.flow_per_area=0
    hbe_ventilation.flow_per_zone=0
    hbe_ventilation.air_changes_per_hour=0.4
    hbe_ventilation.schedule=None
    return hbe_ventilation


def set_setpoint(_setpoint, _heating_schedule, _cooling_schedule, _dehumidifying_setpoint=60):
    # type: (Setpoint, ScheduleRuleset, ScheduleRuleset, float) -> Setpoint
    """Reseet the HBE-Setpoint Attributes."""
    new_setpoint = _setpoint.duplicate()  # type: Setpoint # type: ignore
    new_setpoint.identifier=clean_and_id_ep_string("HBPH_SFH_Setpoint")
    new_setpoint.heating_schedule=_heating_schedule
    new_setpoint.cooling_schedule=_cooling_schedule
    new_setpoint.dehumidifying_setpoint = _dehumidifying_setpoint
    return new_setpoint


def set_shw(_shw, _num_bedrooms, _gross_floor_area_m2, _schedule):
    # type: (ServiceHotWater, float, float, ScheduleRuleset) -> ServiceHotWater
    """Reset the HBE-ServiceHotWater Attributes. If none exist, add a new one.

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
    
    if _shw:
        hbe_shw = _shw.duplicate()  # type: ServiceHotWater # type: ignore
    else: # -- Create a new ServiceHotWater object
        hbe_shw = ServiceHotWater(
            identifier=clean_and_id_ep_string("HBPH_SFH_ServiceHotWater"),
            flow_per_area=convert(gallons_per_hour_combined, "GA", "L") / _gross_floor_area_m2,  # type: ignore,
            schedule=_schedule,
            target_temperature= 43.3  # type: ignore
        )
    hbe_shw.identifier = clean_and_id_ep_string("HBPH_SFH_ServiceHotWater")
    hbe_shw.flow_per_area = convert(gallons_per_hour_combined, "GA", "L") / _gross_floor_area_m2  # type: ignore
    hbe_shw.schedule = _schedule
    hbe_shw.target_temperature = 43.3  # type: ignore
    return hbe_shw


def create_phius_default_equipment_set(_schedules, _num_occupants, _num_bedrooms, _total_floor_area_ft2):
    # type: (SchedulesCollection, float, float, float) -> list[Process]
    """Create the default Phius Process Loads Set for a single-family home."""
    default_ph_equipment = [
        ph_equipment.PhDishwasher.phius_default(),
        ph_equipment.PhClothesWasher.phius_default(),
        ph_equipment.PhClothesDryer.phius_default(),
        ph_equipment.PhCooktop.phius_default(),
        ph_equipment.PhPhiusLightingExterior.phius_default(),
        ph_equipment.PhPhiusLightingGarage.phius_default(),
        ph_equipment.PhPhiusMEL.phius_default(),
    ]

    new_process_loads = []  # type: list[Process]
    for ph_equip in default_ph_equipment:
        # -- Create the HB-Process-Load
        schd = _schedules[ph_equip.__class__.__name__]
        watts = ph_equip.annual_avg_wattage(
            _schedule=schd,
            _num_occupants=_num_occupants,
            _num_units=1,
            _floor_area_ft2=_total_floor_area_ft2,
            _num_bedrooms=_num_bedrooms,
        )

        new_process = Process(
            identifier=clean_and_id_ep_string("HBPH_Process"),
            watts=watts,
            schedule=schd,
            fuel_type="Electricity",
            end_use_category="HBPH_Process",
            radiant_fraction=0,
            latent_fraction=0,
            lost_fraction=0,
        )

        # -- Add the PhEquipment to the new Process Load
        new_process.display_name = ph_equip.__class__.__name__
        hbph_prop = getattr(new_process.properties, "ph")  # type: ProcessPhProperties
        hbph_prop.ph_equipment = ph_equip
        new_process_loads.append(new_process)

    return new_process_loads



class GHCompo_CreatePHProgramSingleFamilyHome(object):
    # Schedule Files

    def __init__(self, _IGH, _hb_rooms):
        # type: (gh_io.IGH, list[Room]) -> None
        self.schedules = SchedulesCollection(
            os.path.join(folders.python_package_path, "honeybee_ph_standards", "schedules")
        )
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms

    @property
    def ready(self):
        # type: () -> bool
        if not self.hb_rooms:
            return False
        return True
    
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
    
    def get_gross_floor_area(self, _hb_rooms):
        # type: (list[Room]) -> float
        """Get the Gross Floor Area [m2] of a set of HB-Rooms."""
        gross_floor_area_in_rh_doc_units = sum(r.floor_area for r in _hb_rooms)
        if not gross_floor_area_in_rh_doc_units:
            raise ValueError("Failed to get gross floor area of HB-Rooms?")
        gross_floor_area_m2 = get_area_value_in_unit(self.IGH, gross_floor_area_in_rh_doc_units, "M2")
        return gross_floor_area_m2

    def get_net_floor_area(self, _hb_rooms):
        # type: (list[Room]) -> float
        """Get the Net Interior Floor Area [ft2] of a set of HB-Rooms."""
        net_floor_area_in_rh_doc_units = get_total_spaces_area_rh_doc_units(_hb_rooms)
        if not net_floor_area_in_rh_doc_units:
            raise ValueError("Failed to get net floor area of HB-Rooms?")
        net_floor_area_m2 = get_area_value_in_unit(self.IGH, net_floor_area_in_rh_doc_units, "M2")
        net_floor_area_ft2 = get_area_value_in_unit(self.IGH, net_floor_area_in_rh_doc_units, "FT2")
        return net_floor_area_ft2

    def set_room_program(self, _hb_room, _gross_floor_area_m2, _net_floor_area_ft2, _num_occupants, _num_bedrooms):
        # type: (Room, float, float, float, float) -> None
        """Set the ProgramType values on a single HB-Room.
        
        Rather than create a new program, re-set the program values one at a time to ensure that we 
        preserve any extension attributes (ph, revive, etc.)
        """
        hb_prop_e = getattr(_hb_room.properties, "energy")  # type: RoomEnergyProperties
        hb_prop_e.people = set_people(
            hb_prop_e.people,
            _gross_floor_area_m2,
            _num_occupants,
            self.schedules.occupancy_presence,
            self.schedules.occupancy_activity,
        )
        hb_prop_e.lighting = set_interior_lighting(
            hb_prop_e.lighting,
            _net_floor_area_ft2,
            _gross_floor_area_m2,
            self.schedules.lighting,
        )
        hb_prop_e.electric_equipment = set_zero_MEL(hb_prop_e.electric_equipment)
        hb_prop_e.infiltration = set_infiltration(hb_prop_e.infiltration)
        hb_prop_e.ventilation = set_ventilation(hb_prop_e.ventilation)
        hb_prop_e.setpoint = set_setpoint(
            hb_prop_e.setpoint,
            self.schedules.heating_setpoint,
            self.schedules.cooling_setpoint,
        )
        hb_prop_e.service_hot_water = set_shw(
            hb_prop_e.service_hot_water,
            _num_bedrooms,
            _gross_floor_area_m2,
            self.schedules.hot_water,
        )
        return None

    def run(self):
        # type: () -> DataTree[Room]
        hb_rooms_ = DataTree[Object]()
        
        if not self.ready:
            return hb_rooms_

        room_groups = _group_rooms_by_dwellings(self.hb_rooms)
        for i, room_group in enumerate(room_groups):
            dup_rooms = self.duplicate_rooms(room_group)

            # -- Figure out the reference values to use for this whole Dwelling
            gross_floor_area_m2 = self.get_gross_floor_area(dup_rooms)
            net_floor_area_ft2 = self.get_net_floor_area(dup_rooms)
            num_bedrooms, num_occupants = get_occupancy_values(self.IGH, dup_rooms)
            
            # -- Create the Phius default Process Loads (Appliances)
            default_process_loads = create_phius_default_equipment_set(
                self.schedules,
                num_occupants,
                num_bedrooms,
                net_floor_area_ft2,
            )

            for rm in dup_rooms:
                # -- Set the Room's HBE-Program Attributes
                self.set_room_program(
                    rm,
                    gross_floor_area_m2,
                    net_floor_area_ft2,
                    num_occupants,
                    num_bedrooms,
                )

                # -- Add the default Process Loads to the HB-Rooms
                rm_prop_e = getattr(rm.properties, "energy")  # type: RoomEnergyProperties
                for equip in default_process_loads:
                    rm_prop_e.add_process_load(equip)

            # -- Add to the output DataTrees
            hb_rooms_.AddRange(dup_rooms, GH_Path(i))

        return hb_rooms_
