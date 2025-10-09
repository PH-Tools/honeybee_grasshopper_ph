# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Exhaust Ventilator."""

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
    from honeybee_phhvac import ventilation
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_CreateExhaustVent(object):
    device_classes = {
        1: ventilation.ExhaustVentDryer,
        2: ventilation.ExhaustVentKitchenHood,
        3: ventilation.ExhaustVentUserDefined,
    }  # type: (Dict[int, type[ventilation._ExhaustVentilatorBase]])

    valid_device_types = [
        "1-Dryer",
        "2-Kitchen Hood",
        "3-User Defined",
    ]

    flow_rate_m3s = ghio_validators.UnitM3_S("flow_rate_m3s", default=0.0)

    def __init__(self, _IGH, _name, _type, _flow_rate_m3s, _annual_runtime_minutes):
        # type: (gh_io.IGH, str, str, str, float) -> None
        self.IGH = _IGH
        self.name = _name
        self.system_type = _type
        self.flow_rate_m3s = _flow_rate_m3s
        self.annual_runtime_minutes = _annual_runtime_minutes or 0.0

    @property
    def system_type(self):
        # type: () -> Optional[int]
        return self._system_type

    @system_type.setter
    def system_type(self, _in):
        self._system_type = input_tools.input_to_int(_in)

    def run(self):
        # type: () -> Optional[ventilation._ExhaustVentilatorBase]

        if not self.system_type:
            msg = "Set the '_system_type' to continue"
            self.IGH.warning(msg)
            return None

        # -- Figure out which Vent Device type is being built
        try:
            device_class = self.device_classes[self.system_type]
        except KeyError:
            raise Exception(
                "Error: Input Device type: '{}' not supported by this GH-Component. "
                "Please only input:{}".format(self.system_type, self.valid_device_types)
            )

        # --- Build the Vent. Device
        vent_device_ = device_class()
        vent_device_.display_name = self.name
        vent_device_.annual_runtime_minutes = self.annual_runtime_minutes
        try:
            vent_device_.exhaust_flow_rate_m3s = float(self.flow_rate_m3s)
        except Exception as e:
            raise e

        return vent_device_
