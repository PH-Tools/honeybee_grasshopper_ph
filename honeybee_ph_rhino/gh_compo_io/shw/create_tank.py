# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Create SHW Tank."""

try:
    from honeybee_phhvac import hot_water_devices
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_phhvac:\n\t{}".format(e))


class GHCompo_CreateSHWTank(object):
    def __init__(
        self,
        _tank_type,
        _display_name_,
        _quantity,
        _for_solar,
        _heat_loss_rate,
        _volume,
        _standby_frac,
        _in_conditioned_space,
        _location_temp,
        _water_temp,
    ):
        self.tank_type = _tank_type
        self.display_name = _display_name_
        self.quantity = _quantity
        self.for_solar = _for_solar
        self.heat_loss_rate = _heat_loss_rate
        self.volume = _volume
        self.standby_frac = _standby_frac
        self.in_conditioned_space = _in_conditioned_space
        self.location_temp = _location_temp
        self.water_temp = _water_temp

    def run(self):
        # Create Storage Tank
        storage_tank = hot_water_devices.PhHvacHotWaterTank()

        storage_tank.tank_type = self.tank_type or storage_tank.tank_type
        storage_tank.display_name = self.display_name or storage_tank.display_name
        storage_tank.quantity = self.quantity or storage_tank.quantity

        if self.for_solar is not None:
            storage_tank.solar_connection = self.for_solar

        storage_tank.standby_losses = self.heat_loss_rate or storage_tank.standby_losses
        storage_tank.storage_capacity = self.volume or storage_tank.storage_capacity
        storage_tank.standby_fraction = self.standby_frac or storage_tank.standby_fraction

        if self.in_conditioned_space is not None:
            storage_tank.in_conditioned_space = self.in_conditioned_space

        storage_tank.room_temp = self.location_temp or 20
        storage_tank.water_temp = self.water_temp or 60

        return storage_tank
