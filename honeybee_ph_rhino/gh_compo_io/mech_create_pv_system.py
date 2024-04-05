# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create PV System."""

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_energy_ph.hvac.renewable_devices import PhPhotovoltaicDevice
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_CreatePVDevice(object):
    annual_yield = ghio_validators.UnitKWH("annual_yield", default=0.0)
    utilization_factor = ghio_validators.FloatPercentage("utilization_factor", default=1.0)
    array_size = ghio_validators.UnitM2("array_size", default=0.0)

    def __init__(self, _IGH, _display_name, _annual_yield, _array_size, _utilization_factor, *args, **kwargs):
        # type: (gh_io.IGH, str, float, float, float, *Any, **Any) -> None
        self.IGH = _IGH
        self.display_name = _display_name or "__unnamed_pv_system__"
        self.annual_yield = _annual_yield
        self.array_size = _array_size
        self.utilization_factor = _utilization_factor

    def run(self):
        # type: () -> PhPhotovoltaicDevice
        pv_sys = PhPhotovoltaicDevice()
        pv_sys.display_name = self.display_name
        pv_sys.photovoltaic_renewable_energy = self.annual_yield
        pv_sys.array_size = self.array_size
        pv_sys.utilization_factor = self.utilization_factor
        return pv_sys
