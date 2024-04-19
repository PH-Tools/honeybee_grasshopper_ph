# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Supportive Device."""

try:
    from typing import Dict, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_phhvac import supportive_device
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_phhvac:\n\t{}".format(e))


class GHCompo_CreateSupportiveDevice(object):
    device_classes = {
        4: supportive_device.PhSupportiveDevice,
        6: supportive_device.PhSupportiveDevice,
        7: supportive_device.PhSupportiveDevice,
        10: supportive_device.PhSupportiveDevice,
    }  # type: (Dict[int, type[supportive_device.PhSupportiveDevice]])

    valid_device_types = [
        " 4-Heat Circulation Pump",
        "6-DHW Circulation Pump",
        "7-DHW Storage Pump",
        "10-Other / Custom ",
    ]

    norm_energy_demand_W = ghio_validators.UnitW("norm_energy_demand_W", default=0.0)
    annual_period_operation_khrs = ghio_validators.FloatPositiveValue("annual_period_operation_khrs", default=8.760)

    def __init__(
        self,
        _IGH,
        _display_name,
        _device_type,
        _quantity,
        _in_conditioned_space,
        _norm_energy_demand_W,
        _annual_period_operation_khrs,
    ):
        # type: (gh_io.IGH, str, int, int, bool, float, float) -> None
        self.IGH = _IGH
        self.display_name = _display_name
        self._device_type = input_tools.input_to_int(_device_type)
        self.quantity = _quantity or 1
        self.in_conditioned_space = _in_conditioned_space
        self.norm_energy_demand_W = _norm_energy_demand_W
        self.annual_period_operation_khrs = _annual_period_operation_khrs

    @property
    def device_type(self):
        # type: () -> Optional[int]
        return self._device_type

    @device_type.setter
    def device_type(self, _in):
        self._device_type = input_tools.input_to_int(_in)

    def run(self):
        # type: () -> Optional[supportive_device.PhSupportiveDevice]

        if not self.device_type:
            msg = "Set the '_device_type' to continue"
            self.IGH.warning(msg)
            return None

        # -- Figure out which Device type is being built
        try:
            print(type(self.device_type), self.device_type)
            device_class = self.device_classes[self.device_type]
        except KeyError as e:
            raise Exception(
                "Error: Input Device type: '{}' not supported by this GH-Component. "
                "Please only input:{}".format(self.device_type, self.valid_device_types)
            )

        # --- Build the new device
        supportive_device = device_class()
        supportive_device.display_name = self.display_name
        supportive_device.device_type = self.device_type
        supportive_device.quantity = self.quantity
        supportive_device.in_conditioned_space = self.in_conditioned_space
        supportive_device.norm_energy_demand_W = self.norm_energy_demand_W
        supportive_device.annual_period_operation_khrs = self.annual_period_operation_khrs

        return supportive_device
