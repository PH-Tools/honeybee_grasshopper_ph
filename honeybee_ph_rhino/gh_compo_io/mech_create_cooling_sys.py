# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Cooling System."""

from copy import copy
# Note: Use copy so that specific equipments can overwrite base with their own hints

from GhPython import Component # type: ignore
from Grasshopper.Kernel.Parameters import Hints # type: ignore

try:
    from typing import Optional, Dict, Any
except ImportError:
    pass # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_io import input_to_int, ComponentInput
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from honeybee_energy_ph.hvac import cooling
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))


class InputTypeNotFoundError(Exception):
    def __init__(self, _in):
        self.msg = 'Error: cooling type ID: "{}" is not a valid equip type.'.format(_in)
        super(InputTypeNotFoundError, self).__init__(self.msg)


# -----------------------------------------------------------------------------
# Setup the component input node groups
inputs_base = {
    1: ComponentInput(_name='display_name',
                      _description='(str) Optional display name for the cooling system.',
                      _type_hint=Component.NewStrHint()),
    2: ComponentInput(_name='percent_coverage',
                      _description='(float) default=1.0 The fraction of total cooling supplied by this system (0-1)',
                      _type_hint=Component.NewFloatHint()),
}

inputs_ventilation = copy(inputs_base)
inputs_ventilation.update({
    3: ComponentInput(_name='annual_COP',
                      _description='(float) The Annual COP (W/W) of the equipment.',
                      _type_hint=Component.NewFloatHint()),
    4: ComponentInput(_name='single_speed',
                      _description='(bool) Cyclical operation works through an on/off regulation of the compressor. If this is set to False, then the assumption is that the unit has a VRF (variant refrigerant flow), which  works by modulating the efficiency of the compressor.',
                      _type_hint=Hints.GH_BooleanHint_CS()),
    5: ComponentInput(_name='min_coil_temp',
                      _description='(float) Deg. C',
                      _type_hint=Component.NewFloatHint()),
    6: ComponentInput(_name='capacity',
                      _description='(float) Maximum kW output.',
                      _type_hint=Component.NewFloatHint()),
})


inputs_recirculation = copy(inputs_base)
inputs_recirculation.update({
    3: ComponentInput(_name='annual_COP',
                      _description='(float) The Annual COP (W/W) of the equipment.',
                      _type_hint=Component.NewFloatHint()),
    4: ComponentInput(_name='single_speed',
                      _description='(bool) Cyclical operation works through an on/off regulation of the compressor. If this is set to False, then the assumption is that the unit has a VRF (variant refrigerant flow), which  works by modulating the efficiency of the compressor.',
                      _type_hint=Hints.GH_BooleanHint_CS()),
    5: ComponentInput(_name='min_coil_temp',
                      _description='(float) Deg. C',
                      _type_hint=Component.NewFloatHint()),
    6: ComponentInput(_name='capacity',
                      _description='(float) Maximum kW output.',
                      _type_hint=Component.NewFloatHint()),
    7: ComponentInput(_name='flow_rate_m3_hr',
                      _description='(float) The maximum airflow rate in m3/hr',
                      _type_hint=Component.NewFloatHint()),
    8: ComponentInput(_name='flow_rate_variable',
                      _description='(bool) VAV system: The volume flow changes proportionally  to the cooling capacity, thereby reducing the  temperature remains constant (usually better dehumidification)',
                      _type_hint=Hints.GH_BooleanHint_CS()),
})

inputs_dehumidification = copy(inputs_base)
inputs_dehumidification.update({
    3: ComponentInput(_name='annual_COP',
                      _description='(float) The Annual COP (W/W) of the equipment.',
                      _type_hint=Component.NewFloatHint()),
    4: ComponentInput(_name='useful_heat_loss',
                      _description='If this is set to True, then the waste heat from the dehumidification unit will be considered as an internal heat gain. On the contrary, dehumidification has no influence on the thermal balance.',
                      _type_hint=Component.NewFloatHint()),
})

inputs_panel = copy(inputs_base)
inputs_panel.update({
    3: ComponentInput(_name='annual_COP',
                      _description='(float) The Annual COP (W/W) of the equipment.',
                      _type_hint=Component.NewFloatHint()),
})


# -----------------------------------------------------------------------------

input_groups = {
    1: inputs_ventilation,
    2: inputs_recirculation,
    3: inputs_dehumidification,
    4: inputs_panel,
}

# -----------------------------------------------------------------------------


def get_component_inputs(_cooling_type):
    # type: (str) -> dict
    """Select the component input-node group based on the 'cooling_type' specified"""

    if not _cooling_type:
        return {}

    input_type_id = input_to_int(_cooling_type)
    if not input_type_id:
        raise InputTypeNotFoundError(input_type_id)

    try:
        return input_groups[input_type_id]
    except KeyError:
        raise InputTypeNotFoundError(input_type_id)

# -----------------------------------------------------------------------------

class GHCompo_CreateCoolingSystem(object):
    cooling_classes = {
        1: cooling.PhCoolingVentilation,
        2: cooling.PhCoolingRecirculation,
        3: cooling.PhCoolingDehumidification,
        4: cooling.PhCoolingPanel,
    } # type: (Dict[int, type[cooling.PhCoolingSystem]])
    
    valid_cooling_types = [
        "1-ventilation",
        "2-recirculation",
        "3-dehumidification",
        "4-panel",
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
        # type: () -> Optional[cooling.PhCoolingSystem]

        if not self.system_type:
            msg = "Set the '_system_type' to configure the user-inputs."
            self.IGH.warning(msg)
            return None

        # -- Figure out which Cooling system type is being built
        try:
            cooling_class = self.cooling_classes[self.system_type]
        except KeyError as e:
            raise Exception(
                "Error: Input Cooling type: '{}' not supported by this GH-Component. Please only input: "\
                "{}".format(self.system_type, self.valid_cooling_types)
            )

        # --- Build the Cooling system
        cooling_system_ = cooling_class()
        for attr_name in dir(cooling_system_):
            if attr_name.startswith('_'):
                continue

            input_val = self.input_dict.get(attr_name)
            if input_val:
                setattr(cooling_system_, attr_name, input_val)
       
        return cooling_system_

