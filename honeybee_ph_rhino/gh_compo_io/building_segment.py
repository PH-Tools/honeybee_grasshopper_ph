# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Bldg Segment."""

try:
    from typing import Any, List, Tuple
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph import bldg_segment, phi, phius, site
    from honeybee_ph.bldg_segment import PhVentilationSummerBypassMode
    from honeybee_ph.properties.room import RoomPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_standards.sourcefactors import (
        factors,
        phius_CO2_factors,
        phius_source_energy_factors,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_standards:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_utils.input_tools import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))


class _SetPoints(object):
    """Temp holder to collect and clean SetPoint user-inputs"""

    winter = ghio_validators.UnitDegreeC("winter", default=20.0)
    summer = ghio_validators.UnitDegreeC("summer", default=25.0)

    def __init__(self, _winter, _summer):
        # type: (str, str) -> None
        self.winter = _winter
        self.summer = _summer

    def __str__(self):
        return "{}()".format(self.__class__.__name__)

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)


class GHCompo_BuildingSegment(object):
    _allowed_fuels = list(
        set(list(phius_source_energy_factors.factors_2021.keys()) + list(phius_CO2_factors.factors_2021.keys()))
    )
    _display_name = ghio_validators.HBName("display_name")
    num_floor_levels = ghio_validators.IntegerNonZero("num_floor_levels", default=1)
    num_dwelling_units = ghio_validators.IntegerNonZero("num_dwelling_units", default=1)
    site = ghio_validators.NotNone("site")
    phius_certification = ghio_validators.NotNone("phius_certification")
    phi_certification = ghio_validators.NotNone("phi_certification")
    mech_room_temp = ghio_validators.UnitDegreeC("mech_room_temp", default=20.0)

    def __init__(
        self,
        _IGH,
        _segment_name,
        _num_floor_levels,
        _num_dwelling_units,
        _site,
        _source_energy_factors,
        _co2_factors,
        _phius_certification,
        _phi_certification,
        _winter_set_temp,
        _summer_set_temp,
        _mech_room_temp,
        _hb_rooms,
        _non_combustible_materials=False,
        _hvr_summer_bypass_mode="4",
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, str, int, int, site.Site, List, List, phius.PhiusCertification, phi.PhiCertification, str, str, str, List[room.Room], bool, str, *Any, **Any) -> None
        self.IGH = _IGH
        self._display_name = _segment_name or "_unnamed_bldg_segment_"
        self.num_floor_levels = _num_floor_levels
        self.num_dwelling_units = _num_dwelling_units
        self.site = _site or site.Site()
        self.phius_certification = _phius_certification or phius.PhiusCertification()
        self.phi_certification = _phi_certification or phi.PhiCertification()
        self.hb_rooms = _hb_rooms
        self.set_points = _SetPoints(_winter_set_temp, _summer_set_temp)
        self.mech_room_temp = _mech_room_temp
        self.thermal_bridges = {}
        self.non_combustible_materials = _non_combustible_materials or False
        self._create_tb_dict()

        # -------------------------------------------------------------------------------------
        # -- Sort out the fuel factors and any inputs
        self._source_energy_factors = factors.FactorCollection(
            "Source_Energy", self._default_phius_source_energy_factors
        )
        self._co2e_factors = factors.FactorCollection("CO2", self._default_phius_CO2_factors)

        for factor in (
            factors.build_factors_from_library(phius_source_energy_factors.factors_2021) + _source_energy_factors
        ):
            self.source_energy_factors.add_factor(factor)
        for factor in factors.build_factors_from_library(phius_CO2_factors.factors_2021) + _co2_factors:
            self.co2e_factors.add_factor(factor)

        self.co2e_factors.validate_fuel_types(self._allowed_fuels)
        self.summer_hrv_bypass_mode = _hvr_summer_bypass_mode or "4"

    @property
    def source_energy_factors(self):
        return self._source_energy_factors

    @source_energy_factors.setter
    def source_energy_factors(self, _input_list):
        # type: (List[factors.Factor]) -> None
        for factor in _input_list:
            self._source_energy_factors.add_factor(factor)

    @property
    def co2e_factors(self):
        return self._co2e_factors

    @co2e_factors.setter
    def co2e_factors(self, _input_list):
        # type: (List[factors.Factor]) -> None
        for factor in _input_list:
            self._source_energy_factors.add_factor(factor)

    @property
    def _default_phius_source_energy_factors(self):
        # type: () -> List[factors.Factor]
        """Return a list of default source-energy factors."""
        return factors.build_factors_from_library(phius_source_energy_factors.factors_2021)

    @property
    def _default_phius_CO2_factors(self):
        # type: () -> List[factors.Factor]
        return factors.build_factors_from_library(phius_CO2_factors.factors_2021)

    @property
    def summer_hrv_bypass_mode(self):
        # type: () -> PhVentilationSummerBypassMode
        return self._summer_hrv_bypass_mode

    @summer_hrv_bypass_mode.setter
    def summer_hrv_bypass_mode(self, _input):
        # type: (str) -> None
        self._summer_hrv_bypass_mode = PhVentilationSummerBypassMode(input_to_int(_input) or 4)

    def _create_hbph_set_points(self):
        # type: () -> bldg_segment.SetPoints
        """Return a new HBPH SetPoints object with attributes from user input."""
        obj = bldg_segment.SetPoints()
        obj.winter = self.set_points.winter
        obj.summer = self.set_points.summer
        return obj

    def _create_tb_dict(self):
        # -- Collect all the Thermal Bridges from all the Rooms input
        # -- note that only one instance of each TB will be maintained on the
        # -- final Building Segment
        tb_dict = {}
        for room in self.hb_rooms:
            if not room:
                continue
            room_prop_ph = room.properties.ph  # type: RoomPhProperties
            tb_dict.update(room_prop_ph.ph_bldg_segment.thermal_bridges)
        self.thermal_bridges = tb_dict

    def _create_bldg_segment(self):
        # type: () -> bldg_segment.BldgSegment
        """Returns a new HBPH BldgSegment object with attribute value set."""

        obj = bldg_segment.BldgSegment()
        ignore = [
            "_identifier",
            "user_data",
        ]
        for attr_name in vars(obj).keys():
            if attr_name in ignore:
                continue
            setattr(obj, attr_name, getattr(self, attr_name))

        # override...
        obj.set_points = self._create_hbph_set_points()

        return obj

    def run(self):
        # type: () -> Tuple[List[room.Room], bldg_segment.BldgSegment]

        # -------------------------------------------------------------------------------------
        # -- Create the actual HBPH Building Segment Object
        hbph_segment = self._create_bldg_segment()

        # -------------------------------------------------------------------------------------
        # -- Set the new HBPH Building Segment on the HB rooms
        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            if not hb_room:
                continue

            new_room = hb_room.duplicate()
            new_room.properties.ph.ph_bldg_segment = hbph_segment  # type: ignore
            hb_rooms_.append(new_room)

        return hb_rooms_, hbph_segment

    def __str__(self):
        return "{}()".format(self.__class__.__name__)

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)
