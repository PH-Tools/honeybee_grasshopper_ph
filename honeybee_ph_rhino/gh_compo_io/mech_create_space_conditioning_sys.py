# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Space Conditioning System."""

from copy import copy # Use copy so that specific equipments can overwrite base with their own hints

try:
    from typing import Optional, Dict, Any, Type, Union
except ImportError:
    pass # IronPython 2.7

try:
    from GhPython import Component # type: ignore
except ImportError:
    pass # Outside Grasshopper

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_io import ComponentInput
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from honeybee_energy_ph.hvac import heating
    from honeybee_energy_ph.hvac import heat_pumps
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))


# -----------------------------------------------------------------------------
# Setup the component input node groups


inputs_base = {
    1: ComponentInput(_name='_display_name',
                      _description='(str) Optional display name for the heating system.',
                      _type_hint=Component.NewStrHint()),
    2: ComponentInput(_name='_percent_bldg_heating_covered',
                      _description="(float) default=1.0 The fraction of the building's total heating covered by this system (0-1.0)",
                      _type_hint=Component.NewFloatHint()),
    5: ComponentInput(_name="----------------------------",
                      _description="",
                      _type_hint=Component.NewFloatHint()),
}

inputs_direct_electric = copy(inputs_base)
inputs_direct_electric.update({})

inputs_fossil_boiler = copy(inputs_base)
inputs_fossil_boiler.update({
    3: ComponentInput(_name='fuel', _description='Select Fuel type: "1-Natural-Gas" or "2-Oil"'),
})

inputs_wood_boiler = copy(inputs_base)
inputs_wood_boiler.update({
    3: ComponentInput(_name='fuel', _description='Select Fuel type: "3-Logs" or "4-Pellets"'),
})

inputs_district_heat = copy(inputs_base)
inputs_district_heat.update({
    3: ComponentInput(_name='energy_carrier', _description='Select Energy Carrier.'),
})

inputs_heat_pump_annual = copy(inputs_base)
inputs_heat_pump_annual.update({
    3: ComponentInput(_name='annual_COP', _description='COP: watts-out/watts-in', 
                      _type_hint=Component.NewStrHint()),
    6: ComponentInput(_name="_percent_bldg_cooling_covered",
                      _description=""),
    7: ComponentInput(_name="_cooling_params_ventilation_air",
                      _description=""),
    8: ComponentInput(_name="_cooling_params_recirculation_air",
                      _description=""),
    9: ComponentInput(_name="_cooling_params_dehumidification",
                      _description=""),
    10: ComponentInput(_name="_cooling_params_chilled_panel",
                      _description=""),
})

inputs_heat_pump_monthly = copy(inputs_base)
inputs_heat_pump_monthly.update({
    3: ComponentInput(_name='monthly_COPS', _description='(list[float]): A List of COP values.', _access=1, _type_hint=Component.NewStrHint()),
    4: ComponentInput(_name='monthly_temps', _description='(list[float]): A List of temp [deg C] values.', _access=1, _type_hint=Component.NewStrHint()),
    6: ComponentInput(_name="_percent_bldg_cooling_covered",
                      _description=""),
    7: ComponentInput(_name="_cooling_params_ventilation_air",
                      _description=""),
    8: ComponentInput(_name="_cooling_params_recirculation_air",
                      _description=""),
    9: ComponentInput(_name="_cooling_params_dehumidification",
                      _description=""),
    10: ComponentInput(_name="_cooling_params_chilled_panel",
                      _description=""),
})

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
            'Error: Heating type ID: "{}" is not a valid equip type.'.format(input_type_id)
        )

    try:
        return input_groups[input_type_id]
    except KeyError:
        raise Exception(
            'Error: Heating type ID: "{}" is not a valid equip type.'.format(input_type_id)
        )

class GHCompo_CreateSpaceConditioningSystem(object):
    
    system_classes = { 
        1: heating.PhHeatingDirectElectric,
        2: heating.PhHeatingFossilBoiler,
        3: heating.PhHeatingWoodBoiler,
        4: heating.PhHeatingDistrict,
        5: heat_pumps.PhHeatPumpAnnual,
        6: heat_pumps.PhHeatPumpRatedMonthly,
        } # type: Dict[int, Type[Union[heating.PhHeatingSystem, heat_pumps.PhHeatPumpSystem]]]

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

    def run(self):
        # type: () -> Optional[Union[heating.PhHeatingSystem, heat_pumps.PhHeatPumpSystem]]
        """Build the new PH Heating/Cooling System object."""
        
        if not self.system_type:
            msg = "Set the '_system_type' to configure the user-inputs."
            self.IGH.warning(msg)
            return None
        
        # --- Figure out which type of system should be built
        try:
            system_class = self.system_classes[self.system_type]
        except KeyError as e:
            raise Exception(
                "Error: Input Heating type: '{}' not supported by this GH-Component. Please only input: "\
                "{}".format(self.system_type, self.valid_system_types)
            )
        
        # --- Build the system
        new_system = system_class()
        for attr_name in dir(new_system):
            if attr_name.startswith('_'):
                continue

            input_val = self.input_dict.get(attr_name)
            if input_val:
                setattr(new_system, attr_name, input_val)
        
        # -- If its not a heat-pump with cooling, just return it
        if isinstance(new_system, heating.PhHeatingSystem):
            return new_system

        # -- Set any cooling params if its a heat-pump
        self.set_cooling_params(
            self.input_dict.get("_cooling_params_ventilation_air", None),
            new_system.cooling_params.ventilation
        )
        self.set_cooling_params(
            self.input_dict.get("_cooling_params_recirculation_air", None),
            new_system.cooling_params.recirculation
        )
        self.set_cooling_params(
            self.input_dict.get("_cooling_params_dehumidification", None),
            new_system.cooling_params.dehumidification
        )
        self.set_cooling_params(
            self.input_dict.get("_cooling_params_chilled_panel", None),
            new_system.cooling_params.panel
        )

        return new_system
    
    def set_cooling_params(self, _user_input_clg_params, _system_clg_params):
        # type: (str, heat_pumps.PhHeatPumpCoolingParams_Base) -> None
        """Set all the System's Cooling parameters to match the user-inputs"""
        print(_user_input_clg_params)
        if not _user_input_clg_params or _user_input_clg_params == "None":
            return
        
        for k, v in vars(_user_input_clg_params).items():
            setattr(_system_clg_params, k, v)
