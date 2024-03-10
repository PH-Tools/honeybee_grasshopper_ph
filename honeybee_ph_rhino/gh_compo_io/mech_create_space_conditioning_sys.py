# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Space Conditioning System."""

from copy import (
    copy,
)  # Use copy so that specific equipments can overwrite base with their own hints

try:
    from typing import Any, Dict, Iterable, List, Optional, Type, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from GhPython import Component  # type: ignore
except ImportError:
    pass  # Outside Grasshopper

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_io import ComponentInput
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_energy_ph.hvac import heat_pumps, heating
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from ph_units import converter, parser
except ImportError as e:
    raise ImportError("\nFailed to import ph-units:\n\t{}".format(e))


# -----------------------------------------------------------------------------
# Setup the component input node groups


inputs_base = {
    1: ComponentInput(
        _name="_display_name",
        _description="(str) Optional display name for the heating system.",
        _type_hint=Component.NewStrHint(),
    ),
    2: ComponentInput(
        _name="_percent_bldg_heating_covered",
        _description="(float) default=1.0 The fraction of the building's total heating covered by this system (0-1.0)",
        _type_hint=Component.NewFloatHint(),
    ),
    5: ComponentInput(
        _name="----------------------------",
        _description="",
        _type_hint=Component.NewFloatHint(),
    ),
}

inputs_direct_electric = copy(inputs_base)
inputs_direct_electric.update({})

inputs_fossil_boiler = copy(inputs_base)
inputs_fossil_boiler.update(
    {
        3: ComponentInput(
            _name="fuel", _description='Select Fuel type: "1-Natural-Gas" or "2-Oil"'
        ),
    }
)

inputs_wood_boiler = copy(inputs_base)
inputs_wood_boiler.update(
    {
        3: ComponentInput(
            _name="fuel", _description='Select Fuel type: "3-Logs" or "4-Pellets"'
        ),
    }
)

inputs_district_heat = copy(inputs_base)
inputs_district_heat.update(
    {
        3: ComponentInput(_name="energy_carrier", _description="Select Energy Carrier."),
    }
)

inputs_heat_pump_annual = copy(inputs_base)
inputs_heat_pump_annual.update(
    {
        3: ComponentInput(
            _name="annual_COP",
            _description="COP: watts-out/watts-in",
            _type_hint=Component.NewStrHint(),
        ),
        6: ComponentInput(_name="_percent_bldg_cooling_covered", _description=""),
        7: ComponentInput(_name="_cooling_params_ventilation_air", _description=""),
        8: ComponentInput(_name="_cooling_params_recirculation_air", _description=""),
        9: ComponentInput(_name="_cooling_params_dehumidification", _description=""),
        10: ComponentInput(_name="_cooling_params_chilled_panel", _description=""),
    }
)

inputs_heat_pump_monthly = copy(inputs_base)
inputs_heat_pump_monthly.update(
    {
        3: ComponentInput(
            _name="monthly_COPS",
            _description="(list[float]): A List of COP values.",
            _access=1,
            _type_hint=Component.NewStrHint(),
            _target_unit="W/W",
        ),
        4: ComponentInput(
            _name="monthly_temps",
            _description="(list[float]): A List of temp [deg C] values.",
            _access=1,
            _type_hint=Component.NewStrHint(),
            _target_unit="C",
        ),
        6: ComponentInput(_name="_percent_bldg_cooling_covered", _description=""),
        7: ComponentInput(_name="_cooling_params_ventilation_air", _description=""),
        8: ComponentInput(_name="_cooling_params_recirculation_air", _description=""),
        9: ComponentInput(_name="_cooling_params_dehumidification", _description=""),
        10: ComponentInput(_name="_cooling_params_chilled_panel", _description=""),
    }
)

# -----------------------------------------------------------------------------


input_groups = {
    1: inputs_direct_electric,
    2: inputs_fossil_boiler,
    3: inputs_wood_boiler,
    4: inputs_district_heat,
    5: inputs_heat_pump_annual,
    6: inputs_heat_pump_monthly,
}


# -----------------------------------------------------------------------------


def get_component_inputs(_system_type):
    # type: (str) -> dict
    """Select the component input-node group based on the 'heating_type' specified"""

    if not _system_type:
        return {}

    input_type_id = gh_io.input_to_int(_system_type)
    if not input_type_id:
        raise Exception(
            'Error: Heating type ID: "{}" is not a valid equip type.'.format(
                input_type_id
            )
        )

    try:
        return input_groups[input_type_id]
    except KeyError:
        raise Exception(
            'Error: Heating type ID: "{}" is not a valid equip type.'.format(
                input_type_id
            )
        )


def get_component_input_by_name(_input_group, _name):
    # type: (Dict[int, ComponentInput], str) -> Optional[ComponentInput]
    """Get the component input from the input group by name."""
    for k, v in _input_group.items():
        if v.name == _name:
            return v


class GHCompo_CreateSpaceConditioningSystem(object):
    system_classes = {
        1: heating.PhHeatingDirectElectric,
        2: heating.PhHeatingFossilBoiler,
        3: heating.PhHeatingWoodBoiler,
        4: heating.PhHeatingDistrict,
        5: heat_pumps.PhHeatPumpAnnual,
        6: heat_pumps.PhHeatPumpRatedMonthly,
    }  # type: Dict[int, Type[Union[heating.PhHeatingSystem, heat_pumps.PhHeatPumpSystem]]]

    valid_system_types = [
        "1-direct_electric",
        "2-fossil_boiler",
        "3-wood_boiler",
        "4-district_heat",
        "5-heat_pump_annual",
        "6-heat_pump_monthly",
    ]

    def __init__(self, _IGH, _system_type, _input_dict, *args, **kwargs):
        # type: (gh_io.IGH, int, Dict[str, Any], *Any, **Any) -> None
        self.IGH = _IGH
        self.system_type = _system_type
        self.input_dict = _input_dict

    @property
    def system_type(self):
        # type: () -> Optional[int]
        return self._system_type

    @system_type.setter
    def system_type(self, _in):
        self._system_type = input_tools.input_to_int(_in)

    @property
    def gh_component_input_group(self):
        # type: () -> Dict[int, ComponentInput]
        """Get the GH-Component input group dict for this system type."""
        if self.system_type:
            return get_component_inputs(str(self.system_type))
        else:
            return {}

    def convert_input(self, _input, _target_unit):
        # type: (str, str) -> Optional[Union[float, int]]
        """Convert a single input to the target unit."""
        user_input, input_unit = parser.parse_input(_input)
        user_input = converter.convert(user_input, input_unit, _target_unit)
        return user_input

    def convert_list_of_inputs(self, _input_list, _target_unit):
        # type: (Iterable[Any], str) -> List[Optional[Union[float, int]]]
        """Convert a list of inputs to the target unit."""
        user_input = []
        for val in _input_list:
            val, input_unit = parser.parse_input(val)
            val = converter.convert(val, input_unit, _target_unit)
            user_input.append(val)
        return user_input

    def run(self):
        # type: () -> Optional[Union[heating.PhHeatingSystem, heat_pumps.PhHeatPumpSystem]]
        """Build the new PH Heating/Cooling System object."""

        if not self.system_type:
            msg = "Set the '_system_type' to configure the user-inputs."
            self.IGH.warning(msg)
            return None

        # --- Figure out which type of system should be built
        try:
            heating_system_class = self.system_classes[self.system_type]
        except KeyError as e:
            raise Exception(
                "Error: Input Heating type: '{}' not supported by this GH-Component. Please only input: "
                "{}".format(self.system_type, self.valid_system_types)
            )

        # -- Build the new Heating system
        new_heating_system = heating_system_class()
        for attr_name in dir(new_heating_system):
            if attr_name.startswith("_"):
                continue

            # -- Pull out the user-input-value for this attribute
            user_input = self.input_dict.get(attr_name, None)

            # -- Find the GH-Component's Input Node for the attribute so we can check the unit-conversion (if any)
            gh_compo_input = get_component_input_by_name(
                self.gh_component_input_group, attr_name
            )
            if gh_compo_input:
                target_unit = gh_compo_input.target_unit
            else:
                target_unit = None

            # -- Convert the attribute's user-input-value, if necessary
            if user_input and target_unit:
                if isinstance(user_input, (list, tuple, set)):
                    user_input = self.convert_list_of_inputs(user_input, target_unit)
                else:
                    user_input = self.convert_input(user_input, target_unit)

            # -- Set the attribute value
            if user_input:
                setattr(new_heating_system, attr_name, user_input)
        
        # -- Set the heating percent covered
        new_heating_system.percent_coverage = self.input_dict.get("_percent_bldg_heating_covered", 1.0)

        # -- If its not a heat-pump with cooling, just return it.
        if isinstance(new_heating_system, heating.PhHeatingSystem):
            return new_heating_system

        # -- Set any cooling params if its a heat-pump
        self.set_cooling_params(
            self.input_dict.get("_cooling_params_ventilation_air", None),
            new_heating_system.cooling_params.ventilation,
        )
        self.set_cooling_params(
            self.input_dict.get("_cooling_params_recirculation_air", None),
            new_heating_system.cooling_params.recirculation,
        )
        self.set_cooling_params(
            self.input_dict.get("_cooling_params_dehumidification", None),
            new_heating_system.cooling_params.dehumidification,
        )
        self.set_cooling_params(
            self.input_dict.get("_cooling_params_chilled_panel", None),
            new_heating_system.cooling_params.panel,
        )

        self.warn_cooling_without_dehumidification(new_heating_system)

        return new_heating_system

    def warn_cooling_without_dehumidification(self, _system):
        # type: (heat_pumps.PhHeatPumpSystem) -> None
        if _system.cooling_params.recirculation.used:
            if not _system.cooling_params.dehumidification.used:
                msg = (
                    "WARNING: The cooling system has recirculation-air but no dehumidification?"
                    "For WUFI-Passive projects, you should add dehumidification parameters in "
                    "order for the simulation results to work correctly. If you do not add "
                    "dehumidification parameters, certain output reports such as Monthly-Site-Energy "
                    "will have errors and will not print correctly."
                )
                self.IGH.warning(msg)
                print(msg)

    def set_cooling_params(self, _user_input_clg_params, _system_clg_params):
        # type: (str, heat_pumps.PhHeatPumpCoolingParams_Base) -> None
        """Set all the System's Cooling parameters to match the user-inputs"""
        if not _user_input_clg_params or _user_input_clg_params == "None":
            return

        for k, v in vars(_user_input_clg_params).items():
            setattr(_system_clg_params, k, v)
