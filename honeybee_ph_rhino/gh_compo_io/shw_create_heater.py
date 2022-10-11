# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create SHW Heater."""

try:
    from typing import Dict, Optional, Type
except ImportError:
    pass # IronPython 2.7

try:
    from GhPython import Component # type: ignore
    from Grasshopper.Kernel.Parameters import Hints # type: ignore
except:
    pass # outside Grasshopper

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_io import ComponentInput
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from honeybee_energy_ph.hvac import hot_water
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy_ph:\n\t{}'.format(e))


# -----------------------------------------------------------------------------
# -- Functions for configuring the GH Component input nodes.

inputs_electric = {
    1: ComponentInput(_name='display_name',
                      _description=r'(str) An optional name for the HW-Heater.',
                      _type_hint=Component.NewStrHint()),
    2: ComponentInput(_name='percent_coverage',
                      _description=r'(float) The % of total HW energy covered by this device.',
                      _type_hint=Component.NewFloatHint()),
    3: ComponentInput(_name='in_conditioned_space',
                      _description=r'(bool) Is the boiler installed inside the conditioned space? default=True.',
                      _type_hint=Hints.GH_BooleanHint_CS()),
}

inputs_boiler_oil_gas = {
    1: ComponentInput(_name='display_name',
                      _description=r'(str) An optional name for the HW-Heater.',
                      _type_hint=Component.NewStrHint()),
    2: ComponentInput(_name='percent_coverage',
                      _description=r'(float) The % of total HW energy covered by this device.',
                      _type_hint=Component.NewFloatHint()),
    3: ComponentInput(_name='in_conditioned_space',
                      _description=r'(bool) Is the boiler installed inside the conditioned space? default=True.',
                      _type_hint=Hints.GH_BooleanHint_CS()),
    4: ComponentInput(_name='fuel',
                      _description=r'Input: "1-Gas" or "2-Oil"'),
    5: ComponentInput(_name='condensing',
                      _description='(bool) Is the boiler a more-efficient "condensing" boiler? default=True.',
                      _type_hint=Hints.GH_BooleanHint_CS()),
    6: ComponentInput(_name='effic_at_30_perc_load',
                      _description=r'(float) Boiler efficiency (%) at 30% of peak-load.',
                      _type_hint=Component.NewFloatHint()),
    7: ComponentInput(_name='effic_at_nominal_load',
                      _description=r'(float) Boiler efficiency (%) at nominal output.',
                      _type_hint=Component.NewFloatHint()),
    8: ComponentInput(_name='avg_return_temp_at_30_perc_load',
                      _description=r'(float) Boiler efficiency (%) at nominal output.',
                      _type_hint=Component.NewFloatHint()),
    9: ComponentInput(_name='avg_boiler_temp_at_70_55',
                      _description=r'(float) Average boiler temp. at 77C / 55C.',
                      _type_hint=Component.NewFloatHint()),
    10: ComponentInput(_name='avg_boiler_temp_at_55_45',
                       _description=r'(float) Average boiler temp. at 55C / 45C.',
                       _type_hint=Component.NewFloatHint()),
    11: ComponentInput(_name='avg_boiler_temp_at_35_28',
                       _description=r'(float) Average boiler temp. at 35C / 28C.',
                       _type_hint=Component.NewFloatHint()),
}

inputs_boiler_wood = {
    1: ComponentInput(_name='display_name',
                      _description=r'(str) An optional name for the HW-Heater.',
                      _type_hint=Component.NewStrHint()),
    2: ComponentInput(_name='percent_coverage',
                      _description=r'(float) The % of total HW energy covered by this device.',
                      _type_hint=Component.NewFloatHint()),
    3: ComponentInput(_name='in_conditioned_space',
                      _description=r'(bool) Is the boiler installed inside the conditioned space? default=True.',
                      _type_hint=Hints.GH_BooleanHint_CS()),
    4: ComponentInput(_name='fuel',
                      _description=r'Input: "1-Pellets" or "2-Logs"'),
    5: ComponentInput(_name='effic_in_basic_cycle',
                      _description=r'(float) The efficiency of the heat generator in basic cycle. Standard Pellet=0.72, Standard Log=0.60',
                      _type_hint=Component.NewFloatHint()),
    6: ComponentInput(_name='effic_in_const_operation',
                      _description=r'(float) The efficiency of the heat generator in constant operation. Standard Pellet=0.80, Standard Log=0.70',
                      _type_hint=Component.NewFloatHint()),
    7: ComponentInput(_name='avg_frac_heat_released',
                      _description=r'(float) The average fraction of heat output released to heating circuit. Standard Pellet=0.50, Standard Log=0.40',
                      _type_hint=Component.NewFloatHint()),
    8: ComponentInput(_name='on_off_temp_diff',
                      _description=r'(float) The temperature difference (deg K) between power-on and power-off. Standard Pellet=10K, Standard Log=30K',
                      _type_hint=Component.NewFloatHint()),
}

inputs_district = {
    1: ComponentInput(_name='display_name',
                      _description=r'(str) An optional name for the HW-Heater.',
                      _type_hint=Component.NewStrHint()),
    2: ComponentInput(_name='percent_coverage',
                      _description=r'(float) The % of total HW energy covered by this device.',
                      _type_hint=Component.NewFloatHint()),
    3: ComponentInput(_name='in_conditioned_space',
                      _description=r'(bool) Is the boiler installed inside the conditioned space? default=True.'),
    4: ComponentInput(_name='energy_carrier',
                      _description=r'Energy Carrier for the district heat.'),
    5: ComponentInput(_name='solar_fraction',
                      _description=r'(float) The solar fraction for the space heating.',
                      _type_hint=Component.NewFloatHint()),
    6: ComponentInput(_name='util_fact_heat_transfer',
                      _description=r'(float) Utilization Factor of heat-transfer station.',
                      _type_hint=Component.NewFloatHint()),
}

inputs_heat_pump_annual = {
    1: ComponentInput(_name='display_name',
                      _description=r'(str) An optional name for the HW-Heater.',
                      _type_hint=Component.NewStrHint()),
    2: ComponentInput(_name='percent_coverage',
                      _description=r'(float) The % of total HW energy covered by this device.',
                      _type_hint=Component.NewFloatHint()),
    3: ComponentInput(_name='in_conditioned_space',
                      _description=r'(bool) Is the boiler installed inside the conditioned space? default=True.',
                      _type_hint=Hints.GH_BooleanHint_CS()),
    4: ComponentInput(_name='annual_COP',
                      _description=r'(float) Annual Coefficient of Performance (COP).',
                      _type_hint=Component.NewFloatHint()),
    5: ComponentInput(_name='annual_system_perf_ratio',
                      _description=r'(float) Annual system performance ratio of heat generator.',
                      _type_hint=Component.NewFloatHint()),
    6: ComponentInput(_name='annual_energy_factor',
                      _description=r'(float) OPTIONAL - Annual energy-factor (EF) of the heat pump.',
                      _type_hint=Component.NewFloatHint()),
}

inputs_heat_pump_monthly = {
    1: ComponentInput(_name='display_name',
                      _description=r'(str) An optional name for the HW-Heater.',
                      _type_hint=Component.NewStrHint()),
    2: ComponentInput(_name='percent_coverage',
                      _description=r'(float) The % of total HW energy covered by this device.',
                      _type_hint=Component.NewFloatHint()),
    3: ComponentInput(_name='in_conditioned_space',
                      _description=r'(bool) Is the boiler installed inside the conditioned space? default=True.',
                      _type_hint=Hints.GH_BooleanHint_CS()),
    4: ComponentInput(_name='rated_COP_at_T1',
                      _description=r'(float) The rated Coefficient of Performance (COP) at temperature T1',
                      _type_hint=Component.NewFloatHint()),
    5: ComponentInput(_name='rated_COP_at_T2',
                      _description=r'(float) The rated Coefficient of Performance (COP) at temperature T2',
                      _type_hint=Component.NewFloatHint()),
    6: ComponentInput(_name='temp_T1',
                      _description=r'(float) Temperature T1 (deg C)',
                      _type_hint=Component.NewFloatHint()),
    7: ComponentInput(_name='temp_T2',
                      _description=r'(float) Temperature T2 (deg C)',
                      _type_hint=Component.NewFloatHint()),
}


input_groups = {
    1: inputs_electric,
    2: inputs_boiler_oil_gas,
    3: inputs_boiler_wood,
    4: inputs_district,
    5: inputs_heat_pump_annual,
    6: inputs_heat_pump_monthly,
}

valid_heater_types = ["1-Electric", "2-Boiler (gas/oil)",
                      "3-Boiler (wood)", "4-District", "5-HeatPump", "6-HeatPump"]


def get_component_inputs(_heater_type):
    # type: (str) -> dict
    """Select the component input-node group based on the 'type' specified"""

    if '1' in str(_heater_type):
        return input_groups[1]
    elif '2' in str(_heater_type):
        return input_groups[2]
    elif '3' in str(_heater_type):
        return input_groups[3]
    elif '4' in str(_heater_type):
        return input_groups[4]
    elif '5' in str(_heater_type):
        return input_groups[5]
    elif '6' in str(_heater_type):
        return input_groups[6]
    else:
        return input_groups[1]


# -----------------------------------------------------------------------------
# -- Component Interface

class GHCompo_CreateSHWHeater(object):
    """Component Interface."""

    heater_classes = {
        1: {"cls": hot_water.PhSHWHeaterElectric, "name":"1-Electric"},
        2: {"cls": hot_water.PhSHWHeaterBoiler, "name":"2-Boiler (gas/oil)"},
        3: {"cls": hot_water.PhSHWHeaterBoilerWood, "name":"3-Boiler (wood)"},
        4: {"cls": hot_water.PhSHWHeaterDistrict, "name":"4-District"},
        5: {"cls": hot_water.PhSHWHeaterHeatPump, "name":"5-HeatPump (annual COP)"},
        6: {"cls": hot_water.PhSHWHeaterHeatPump, "name":"6-HeatPump (monthly COP)"},
    }

    valid_types = [heater_class["name"] for heater_class in heater_classes.values()]

    def __init__(self, _IGH, _heater_type, _input_dict):
        # type: (gh_io.IGH, int, Dict) -> None
        self.IGH = _IGH
        self.heater_type = _heater_type
        self.input_dict = _input_dict

    def _determine_heater_type_input(self):
        # type: () -> Optional[int]
        if not self.heater_type:
            msg = "Set the 'heater_type' to configure the user-inputs. Options include: {}".format(self.valid_types)
            self.IGH.warning(msg)
            return None

        return gh_io.input_to_int(self.heater_type)

    def _determine_heater_class(self, _type_number):
        # type: (int) -> Type[hot_water.PhHotWaterHeater]
        try:
            return self.heater_classes[_type_number]["cls"]
        except KeyError:
            msg = "Error: Input Heater Type: '{}' not supported. Please only input: '{}'".format(
                self.heater_type,
                self.valid_types)
            raise Exception(msg)

    def run(self):
        # type: () -> Optional[hot_water.PhHotWaterHeater]

        heater_type_number = self._determine_heater_type_input()
        if heater_type_number is None:
            return None

        heater_class = self._determine_heater_class(heater_type_number)
        heater_ = heater_class() # type: hot_water.PhHotWaterHeater

        # -- Set all the attributes.
        for attr_name in dir(heater_):
            input_val = self.input_dict.get(attr_name, None)
            if input_val:
                setattr(heater_, attr_name, input_val)

        return heater_