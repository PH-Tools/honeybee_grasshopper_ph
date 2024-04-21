# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Create SHW System."""

try:
    from typing import List, Optional, Union
except ImportError:
    pass  # IronPython 2.7

try:  # import the honeybee extension
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:  # import the honeybee-energy extension
    from honeybee_energy import shw
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_phhvac import hot_water_system, hot_water_devices, hot_water_piping
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreateSHWSystem(object):
    """Interface for collect and clean SHW System user-inputs."""

    display_name = ghio_validators.HBName("display_name", default="SHW System")
    efficiency = ghio_validators.FloatPercentage("efficiency")
    loss_coeff = ghio_validators.UnitW_K("loss_coeff")

    def __init__(
        self,
        _IGH,
        display_name,
        tank_1,
        tank_2,
        buffer_tank,
        solar_tank,
        heaters,
        distribution_piping,
        _num_tap_points,
        recirc_piping,
    ):
        # type: (gh_io.IGH, str, Optional[hot_water_devices.PhHvacHotWaterTank], Optional[hot_water_devices.PhHvacHotWaterTank], Optional[hot_water_devices.PhHvacHotWaterTank], Optional[hot_water_devices.PhHvacHotWaterTank], List, List, Optional[int], List) -> None
        self.IGH = _IGH
        self.display_name = display_name
        self.tank_1 = tank_1
        self.tank_2 = tank_2
        self.buffer_tank = buffer_tank
        self.solar_tank = solar_tank
        self.heaters = heaters
        self.distribution_piping = distribution_piping
        self.number_tap_points = _num_tap_points
        self.recirc_piping = recirc_piping

    def run(self):
        # type: () -> hot_water_system.PhHotWaterSystem
        """Create a new PH-HVAC Hot Water System object."""
        ph_hvac_hw_sys = hot_water_system.PhHotWaterSystem()

        # -- Basic Attributes
        ph_hvac_hw_sys.display_name = self.display_name
        ph_hvac_hw_sys.number_tap_points = self.number_tap_points

        # -- Add any Tanks
        if self.tank_1:
            ph_hvac_hw_sys.tank_1 = self.tank_1
        if self.tank_2:
            ph_hvac_hw_sys.tank_2 = self.tank_2
        if self.buffer_tank:
            ph_hvac_hw_sys.tank_buffer = self.buffer_tank
        if self.solar_tank:
            ph_hvac_hw_sys.tank_solar = self.solar_tank

        # -- Add any Heaters
        for heater in self.heaters:
            ph_hvac_hw_sys.add_heater(heater)

        # -- Add any Piping
        for distribution_piping in self.distribution_piping:
            ph_hvac_hw_sys.add_distribution_piping(distribution_piping)
        for recirc_piping in self.recirc_piping:
            ph_hvac_hw_sys.add_recirc_piping(recirc_piping)

        return ph_hvac_hw_sys
