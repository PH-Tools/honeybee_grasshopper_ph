# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Cooling Params."""

from copy import copy

from GhPython import Component  # type: ignore
from Grasshopper.Kernel.Parameters import Hints  # type: ignore

# Note: Use copy so that specific equipments can overwrite base with their own hints


try:
    from typing import Any, Dict, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
    from honeybee_ph_rhino.gh_io import ComponentInput, input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_phhvac import heat_pumps
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_phhvac:\n\t{}".format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))


class InputTypeNotFoundError(Exception):
    def __init__(self, _in):
        self.msg = 'Error: cooling type ID: "{}" is not a valid equip type.'.format(_in)
        super(InputTypeNotFoundError, self).__init__(self.msg)


# -----------------------------------------------------------------------------
# Setup all the component input node groups

inputs_base = {
    1: ComponentInput(
        _name="display_name",
        _description="(str) Optional display name for the cooling system.",
        _type_hint=Component.NewStrHint(),
    ),
    2: ComponentInput(
        _name="percent_coverage",
        _description="(float) default=1.0 The fraction of total cooling supplied by this system (0-1)",
        _type_hint=Component.NewFloatHint(),
    ),
}

inputs_ventilation = copy(inputs_base)
inputs_ventilation.update(
    {
        3: ComponentInput(
            _name="annual_COP",
            _description="(float) The Annual COP (W/W) of the equipment.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/W",
        ),
        4: ComponentInput(
            _name="single_speed",
            _description="(bool) Cyclical operation works through an on/off regulation of the compressor. If this is set to False, then the assumption is that the unit has a VRF (variant refrigerant flow), which  works by modulating the efficiency of the compressor.",
            _type_hint=Hints.GH_BooleanHint_CS(),
        ),
        5: ComponentInput(
            _name="min_coil_temp",
            _description="(float) Deg. C - Default=10.0 Deg. C",
            _type_hint=Component.NewStrHint(),
            _target_unit="C",
        ),
        6: ComponentInput(
            _name="capacity",
            _description="(float) Maximum kW output.",
            _type_hint=Component.NewStrHint(),
            _target_unit="KW",
        ),
    }
)

inputs_recirculation = copy(inputs_base)
inputs_recirculation.update(
    {
        3: ComponentInput(
            _name="annual_COP",
            _description="(float) The Annual COP (W/W) of the equipment.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/W",
        ),
        4: ComponentInput(
            _name="single_speed",
            _description="(bool) Cyclical operation works through an on/off regulation of the compressor. If this is set to False, then the assumption is that the unit has a VRF (variant refrigerant flow), which  works by modulating the efficiency of the compressor.",
            _type_hint=Hints.GH_BooleanHint_CS(),
        ),
        5: ComponentInput(
            _name="min_coil_temp",
            _description="(float) Deg. C",
            _type_hint=Component.NewStrHint(),
            _target_unit="C",
        ),
        6: ComponentInput(
            _name="capacity",
            _description="(float) Maximum kW output.",
            _type_hint=Component.NewStrHint(),
            _target_unit="KW",
        ),
        7: ComponentInput(
            _name="flow_rate_m3_s",
            _description="(float) The maximum airflow rate in m3/s",
            _type_hint=Component.NewStrHint(),
            _target_unit="=M3/S",
        ),
        8: ComponentInput(
            _name="flow_rate_variable",
            _description="(bool) VAV system: The volume flow changes proportionally  to the cooling capacity, thereby reducing the  temperature remains constant (usually better dehumidification)",
            _type_hint=Hints.GH_BooleanHint_CS(),
        ),
    }
)

inputs_dehumidification = copy(inputs_base)
inputs_dehumidification.update(
    {
        3: ComponentInput(
            _name="annual_COP",
            _description="(float) The Annual COP (W/W) of the equipment.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/W",
        ),
        4: ComponentInput(
            _name="useful_heat_loss",
            _description="If this is set to True, then the waste heat from the dehumidification unit will be considered as an internal heat gain. On the contrary, dehumidification has no influence on the thermal balance.",
            _type_hint=Hints.GH_BooleanHint_CS(),
        ),
    }
)

inputs_panel = copy(inputs_base)
inputs_panel.update(
    {
        3: ComponentInput(
            _name="annual_COP",
            _description="(float) The Annual COP (W/W) of the equipment.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/W",
        ),
    }
)


# -----------------------------------------------------------------------------
# -- Configure the Grasshopper Component with the right inputs nodes for the type

input_groups = {
    1: inputs_ventilation,
    2: inputs_recirculation,
    3: inputs_dehumidification,
    4: inputs_panel,
}


def get_component_inputs(_param_type):
    # type: (str) -> dict
    """Select the component input-node group based on the '_param_type' specified"""

    if not _param_type:
        return {}

    input_type_id = input_to_int(_param_type)
    if not input_type_id:
        raise InputTypeNotFoundError(input_type_id)

    try:
        return input_groups[input_type_id]
    except KeyError:
        raise InputTypeNotFoundError(input_type_id)


# -----------------------------------------------------------------------------
# -- Facades for Cooling-Param Constructors (So they can do input validation and unit conversion)
# -- DEV-NOTE: Do not use .get() during __init__ since the interface may pass a None value.
# -- Instead, use square brackets and the 'or' keyword to set a default value.


class FacadePhCoolingVentilation(object):
    display_name = ghio_validators.HBName("display_name", default="_unnamed_ventilation_cooling_")
    min_coil_temp = ghio_validators.UnitDegreeC("min_coil_temp", default=10)
    capacity = ghio_validators.UnitKW("capacity", default=10)

    def __init__(self, _IGH, _input_dict):
        # type: (gh_io.IGH, Dict) -> None
        self.IGH = _IGH
        self.display_name = _input_dict["display_name"]
        self.single_speed = _input_dict["single_speed"] or False
        self.min_coil_temp = _input_dict["min_coil_temp"]
        self.capacity = _input_dict["capacity"]
        self.annual_COP = _input_dict["annual_COP"] or 2.0

    def build(self):
        # type: () -> heat_pumps.PhHeatPumpCoolingParams_Ventilation
        obj = heat_pumps.PhHeatPumpCoolingParams_Ventilation()
        obj.used = True
        obj.display_name = self.display_name
        obj.single_speed = self.single_speed
        obj.min_coil_temp = self.min_coil_temp
        obj.capacity = self.capacity
        obj.annual_COP = self.annual_COP
        return obj


class FacadePhCoolingRecirculation(object):
    display_name = ghio_validators.HBName("display_name", default="_unnamed_recirculation_cooling_")
    min_coil_temp = ghio_validators.UnitDegreeC("min_coil_temp", default=10)
    flow_rate_m3_s = ghio_validators.UnitM3_S("flow_rate_m3_s", default=0.0278)
    capacity = ghio_validators.UnitKW("capacity", default=10)

    def __init__(self, _IGH, _input_dict):
        # type: (gh_io.IGH, Dict) -> None
        self.IGH = _IGH
        self.display_name = _input_dict["display_name"]
        self.single_speed = _input_dict["single_speed"] or False
        self.min_coil_temp = _input_dict["min_coil_temp"]
        self.flow_rate_m3_s = _input_dict["flow_rate_m3_s"]
        self.flow_rate_variable = _input_dict["flow_rate_variable"] or True
        self.capacity = _input_dict["capacity"]
        self.annual_COP = _input_dict["annual_COP"] or 2.0

        self.check_capacity()

    def check_capacity(self):
        # type: () -> None
        """Check if the capacity is below the WUFI limit of 200 kW (682 kBTU/HR).

        This is a bug in WUFI v3.3.x which requires that the user adds a second
        'fake' cooling system if the capacity is above 200 kW.
        """
        if self.capacity >= 200.0:
            msg = (
                "\nWARNING: The cooling capacity of the cooling system is above 200 KW (682 KBTUH). "
                "WUFI-Passive v3 has a bug which limits this size of any single cooling "
                "system to < 200 KW. As a result, in WUFI-Passive, the total cooling capacity "
                "of {} KW will be split across multiple systems. "
                "Please contact Phius for more information or questions on this issue.\n".format(self.capacity)
            )
            self.IGH.warning(msg)
            print(msg)

    def build(self):
        # type: () -> heat_pumps.PhHeatPumpCoolingParams_Recirculation
        obj = heat_pumps.PhHeatPumpCoolingParams_Recirculation()
        obj.used = True
        obj.display_name = self.display_name
        obj.single_speed = self.single_speed
        obj.min_coil_temp = self.min_coil_temp
        obj.flow_rate_m3_hr = self.flow_rate_m3_s * 60 * 60
        obj.flow_rate_variable = self.flow_rate_variable
        obj.capacity = self.capacity
        obj.annual_COP = self.annual_COP
        return obj


class FacadePhCoolingDehumidification(object):
    display_name = ghio_validators.HBName("display_name", default="_unnamed_dehumidification_cooling_")
    percent_coverage = ghio_validators.FloatPercentage("percent_coverage", default=1.0)

    def __init__(self, _IGH, _input_dict):
        # type: (gh_io.IGH, Dict) -> None
        self.IGH = _IGH
        self.display_name = _input_dict["display_name"]
        self.useful_heat_loss = _input_dict["useful_heat_loss"] or False
        self.annual_COP = _input_dict["annual_COP"] or 2.0

    def build(self):
        # type: () -> heat_pumps.PhHeatPumpCoolingParams_Dehumidification
        obj = heat_pumps.PhHeatPumpCoolingParams_Dehumidification()
        obj.used = True
        obj.display_name = self.display_name
        obj.useful_heat_loss = self.useful_heat_loss
        obj.annual_COP = self.annual_COP
        return obj


class FacadePhCoolingPanel(object):
    display_name = ghio_validators.HBName("display_name", default="_unnamed_panel_cooling_")
    percent_coverage = ghio_validators.FloatPercentage("percent_coverage", default=1.0)

    def __init__(self, _IGH, _input_dict):
        # type: (gh_io.IGH, Dict) -> None
        self.IGH = _IGH
        self.display_name = _input_dict["display_name"]
        self.annual_COP = _input_dict["annual_COP"] or 2.0

    def build(self):
        # type: () -> heat_pumps.PhHeatPumpCoolingParams_Panel
        obj = heat_pumps.PhHeatPumpCoolingParams_Panel()
        obj.used = True
        obj.display_name = self.display_name
        obj.annual_COP = self.annual_COP
        return obj


# -----------------------------------------------------------------------------
# -- GH Component Interface


class GHCompo_CreateCoolingSystem(object):
    cooling_param_classes = {
        1: FacadePhCoolingVentilation,
        2: FacadePhCoolingRecirculation,
        3: FacadePhCoolingDehumidification,
        4: FacadePhCoolingPanel,
    }

    valid_cooling_param_types = [
        "1-Ventilation Air",
        "2-Recirculating Air",
        "3-Dehumidification",
        "4-Radiant Panel",
    ]

    def __init__(self, _IGH, _param_type, _input_dict, *args, **kwargs):
        # type: (gh_io.IGH, int, Dict[str, Any], *Any, **Any) -> None
        self.IGH = _IGH
        self.param_type = _param_type
        self.input_dict = _input_dict

    @property
    def param_type(self):
        # type: () -> Optional[int]
        return self._system_type

    @param_type.setter
    def param_type(self, _in):
        self._system_type = input_tools.input_to_int(_in)

    def run(self):
        # type: () -> Optional[heat_pumps.PhHeatPumpCoolingParams_Base]
        """Find the right System Builder and create the new System from the user inputs."""

        if not self.param_type:
            msg = "Set the '_cooling_type' to configure the input options."
            self.IGH.warning(msg)
            return None

        # -- Figure out which Cooling Param type is being built
        try:
            cooling_param_class = self.cooling_param_classes[self.param_type]
        except KeyError:
            raise Exception(
                "Error: Input '_cooling_type' value of: '{}' is not supported by this GH-Component. "
                "Please only input one of the types: {}".format(self.param_type, self.valid_cooling_param_types)
            )

        # --- Build the Cooling system from the user_inputs
        cooling_param_builder = cooling_param_class(self.IGH, self.input_dict)
        return cooling_param_builder.build()
