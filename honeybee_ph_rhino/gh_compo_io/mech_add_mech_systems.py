# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Mech Systems."""

from copy import copy

try:
    from typing import Any, List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
    from honeybee_energy_ph.properties.hvac.idealair import IdealAirSystemPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.hvac import heat_pumps, heating, ventilation
    from honeybee_energy_ph.hvac.supportive_device import PhSupportiveDevice
    from honeybee_energy_ph.properties.hvac.idealair import IdealAirSystemPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_AddMechSystems(object):
    def __init__(
        self,
        _vent_sys,
        _conditioning_systems,
        _supportive_devices=[],
        _hb_rooms=[],
        *args,
        **kwargs
    ):
        # type: (ventilation.PhVentilationSystem, List[heating.PhHeatingSystem], List[PhSupportiveDevice], List[room.Room],  *Any, **Any) -> None

        self.ventilation_system = _vent_sys
        self.conditioning_systems = _conditioning_systems
        self.supportive_devices = _supportive_devices
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> List[room.Room]

        hb_rooms_ = []
        for hb_room in self.hb_rooms:
            # -- Build up the new HB-HVAC
            new_hvac = copy(hb_room.properties.energy.hvac.duplicate())  # type: ignore

            # -- Aliases
            new_hvac_prop = new_hvac.properties  # type: IdealAirSystemPhProperties
            new_hvac_prop_ph = (
                new_hvac_prop.ph
            )  # type: IdealAirSystemPhProperties # type: ignore

            # ---------------------------------------------------------------------------
            # -- Fresh-Air Ventilation
            if self.ventilation_system:
                if not self.ventilation_system.ventilation_unit:
                    continue

                # -- Set the new h-hvac's values to match the PH-Ventilator Inputs, if any
                new_hvac_prop_ph.ventilation_system = self.ventilation_system
                new_hvac.sensible_heat_recovery = (
                    self.ventilation_system.ventilation_unit.sensible_heat_recovery
                )
                new_hvac.latent_heat_recovery = (
                    self.ventilation_system.ventilation_unit.latent_heat_recovery
                )
                new_hvac.demand_controlled_ventilation = True

            # ---------------------------------------------------------------------------
            # -- Space Heating / Cooling
            for ph_conditioning_system in self.conditioning_systems:
                if isinstance(ph_conditioning_system, heat_pumps.PhHeatPumpSystem):
                    new_hvac_prop_ph.heat_pump_systems.add(ph_conditioning_system)
                else:
                    new_hvac_prop_ph.heating_systems.add(ph_conditioning_system)

            # ---------------------------------------------------------------------------
            # -- Supportive Devices
            for supportive_device in self.supportive_devices:
                new_hvac_prop_ph.supportive_devices.add(supportive_device)

            new_room = hb_room.duplicate()
            new_room.properties.energy.hvac = new_hvac  # type: ignore
            hb_rooms_.append(new_room)

        return hb_rooms_
