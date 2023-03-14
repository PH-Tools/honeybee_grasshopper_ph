# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Ventilation System."""

try:
    from typing import Any, Optional
except ImportError:
    pass #IronPython 2.7

try:
    from honeybee_energy_ph.hvac import ventilation, ducting
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))


class GHCompo_CreateVentSystem(object):
    display_name = ghio_validators.HBName("display_name")

    def __init__(self, _display_name, _sys_type, _vent_unit, _duct_01, _duct_02):
        # type: (str, int, ventilation.Ventilator, Optional[ducting.PhDuctElement], Optional[ducting.PhDuctElement]) -> None
        self.display_name = _display_name or "__unnamed_ventilator__"
        self.system_type = _sys_type
        self.vent_unit = _vent_unit
        self.duct_01 = _duct_01
        self.duct_02 = _duct_02

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

        if self.duct_01:
            vent_system_.duct_01 = self.duct_01

        if self.duct_02:
            vent_system_.duct_02 = self.duct_02

        return vent_system_