# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Ventilation System."""

try:
    from typing import Union, Optional, List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_energy_ph.hvac import ventilation, ducting
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))


class GHCompo_CreateVentSystem(object):
    display_name = ghio_validators.HBName("display_name")

    def __init__(
        self, _display_name, _sys_type, _vent_unit, _supply_ducts, _exhaust_ducts
    ):
        # type: (str, int, ventilation.Ventilator, List[Optional[ducting.PhDuctElement]], List[Optional[ducting.PhDuctElement]]) -> None
        self.display_name = _display_name or "__unnamed_ventilator__"
        self.system_type = _sys_type
        self.vent_unit = _vent_unit
        self.supply_ducts = _supply_ducts
        self.exhaust_ducts = _exhaust_ducts

    @property
    def supply_ducts(self):
        # type: () -> List[ducting.PhDuctElement]
        return self._supply_ducts or [
            ducting.PhDuctElement.default_supply_duct(
                _display_name="{}_supply".format(self.display_name)
            )
        ]

    @supply_ducts.setter
    def supply_ducts(self, _input):
        # type: (List[Optional[ducting.PhDuctElement]]) -> None
        self._supply_ducts = [d for d in _input if d is not None]

    @property
    def exhaust_ducts(self):
        # type: () -> List[ducting.PhDuctElement]
        return self._exhaust_ducts or [
            ducting.PhDuctElement.default_exhaust_duct(
                _display_name="{}_exhaust".format(self.display_name)
            )
        ]

    @exhaust_ducts.setter
    def exhaust_ducts(self, _input):
        # type: (List[Optional[ducting.PhDuctElement]]) -> None
        self._exhaust_ducts = [d for d in _input if d is not None]

    @property
    def system_type(self):
        # type: () -> int
        return self._system_type

    @system_type.setter
    def system_type(self, _in):
        input_int = input_tools.input_to_int(_in)
        self._system_type = input_int or 1

    def run(self):
        # type: () -> ventilation.PhVentilationSystem
        vent_system_ = ventilation.PhVentilationSystem()

        vent_system_.display_name = self.display_name or vent_system_.display_name
        vent_system_.sys_type = self.system_type
        vent_system_.ventilation_unit = self.vent_unit or ventilation.Ventilator()
        vent_system_.supply_ducting = self.supply_ducts
        vent_system_.exhaust_ducting = self.exhaust_ducts

        return vent_system_
