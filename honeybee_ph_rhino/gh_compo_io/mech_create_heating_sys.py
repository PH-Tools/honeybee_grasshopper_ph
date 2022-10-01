# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Heating System."""

from copy import copy # Use copy so that specific equipments can overwrite base with their own hints

try:
    from typing import Optional, Dict, Any
except ImportError:
    pass # IronPython 2.7

from GhPython import Component # type: ignore

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_io import ComponentInput
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from honeybee_energy_ph.hvac import heating
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))


# -----------------------------------------------------------------------------
# Setup the component input node groups


inputs_base = {
    1: ComponentInput(_name='display_name',
                      _description='(str) Optional display name for the heating system.',
                      _type_hint=Component.NewStrHint()),
    2: ComponentInput(_name='percent_coverage',
                      _description='(float) default=1.0 The fraction of total heating supplied by this system (0-1)',
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
    3: ComponentInput(_name='annual_COP', _description='COP: watts-out/watts-in', _type_hint=Component.NewFloatHint()),
})

inputs_heat_pump_monthly = copy(inputs_base)
inputs_heat_pump_monthly.update({
    3: ComponentInput(_name='monthly_COPS', _description='(list[float]): A List of COP values.', _access=1, _type_hint=Component.NewFloatHint()),
    4: ComponentInput(_name='monthly_temps', _description='(list[float]): A List of temp [deg C] values.', _access=1, _type_hint=Component.NewFloatHint()),
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

def get_component_inputs(_heating_type):
    # type: (str) -> dict
    """Select the component input-node group based on the 'heating_type' specified"""

    if not _heating_type:
        return {}

    input_type_id = gh_io.input_to_int(_heating_type)
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


# -----------------------------------------------------------------------------
class GHCompo_CreateHeatingSystem(object):
    heating_classes = {
        1: heating.PhHeatingDirectElectric,
        2: heating.PhHeatingFossilBoiler,
        3: heating.PhHeatingWoodBoiler,
        4: heating.PhHeatingDistrict,
        5: heating.PhHeatingHeatPumpAnnual,
        6: heating.PhHeatingHeatPumpRatedMonthly,
        }

    valid_heating_types = [
        "1-direct_electric",
        "2-fossil_boiler",
        "3-wood_boiler",
        "4-district_heat",
        "5-heat_pump_annual",
        "6-heat_pump_monthly", 
    ]
    
    def __init__(self, _IGH, _system_type, _input_dict):
        # type: (gh_io.IGH, int, Dict[str, Any]) -> None
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
        # type: () -> Optional[heating.PhHeatingSystem]

        # -- Build the new PH equipment object
        if not self.system_type:
            msg = "Set the '_system_type' to configure the user-inputs."
            self.IGH.warning(msg)
            return None

        try:
            heating_class = self.heating_classes[self.system_type]
        except KeyError as e:
            raise Exception(
                "Error: Input Heating type: '{}' not supported by this GH-Component. Please only input: "\
                "{}".format(self.system_type, self.valid_heating_types)
            )

        heating_system_ = heating_class()
        for attr_name in dir(heating_system_):
            if attr_name.startswith('_'):
                continue

            input_val = self.input_dict.get(attr_name)
            if input_val:
                setattr(heating_system_, attr_name, input_val)