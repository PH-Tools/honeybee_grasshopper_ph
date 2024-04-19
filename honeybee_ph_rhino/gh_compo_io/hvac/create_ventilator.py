# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Ventilator."""

try:
    from honeybee_phhvac import ventilation
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_phhvac:\n\t{}".format(e))

try:
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreatePhVentilator(object):
    display_name = ghio_validators.HBName("display_name")
    sensible_hr = ghio_validators.FloatPercentage("sensible_hr", default=0.75)
    latent_hr = ghio_validators.FloatPercentage("latent_hr", default=0.0)
    elec_efficiency = ghio_validators.UnitWH_M3("elec_efficiency", default=0.45)
    frost_temp = ghio_validators.UnitDegreeC("frost_temp", default=-5.0)

    def __init__(
        self,
        _display_name,
        _sens_hr,
        _lat_hr,
        _elec_eff,
        _frost_protect,
        _frost_temp,
        _inside,
    ):
        self.display_name = _display_name or "_unnamed_ventilator_"
        self.sensible_hr = _sens_hr
        self.latent_hr = _lat_hr
        self.elec_efficiency = _elec_eff
        self.frost_protection = _frost_protect
        self.frost_temp = _frost_temp
        self.inside = _inside

    def run(self):
        # type: () -> ventilation.Ventilator
        ventilator = ventilation.Ventilator()

        if self.display_name:
            ventilator.display_name = self.display_name
        if self.sensible_hr:
            ventilator.sensible_heat_recovery = self.sensible_hr
        if self.latent_hr:
            ventilator.latent_heat_recovery = self.latent_hr
        if self.elec_efficiency:
            ventilator.electric_efficiency = self.elec_efficiency
        if self.frost_protection is not None:
            ventilator.frost_protection_reqd = self.frost_protection
        if self.frost_temp:
            ventilator.temperature_below_defrost_used = self.frost_temp
        if self.inside is not None:
            ventilator.in_conditioned_space = self.inside

        return ventilator
