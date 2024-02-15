# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Vent. Schedule."""

try:
    from typing import Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.lib.scheduletypelimits import schedule_type_limit_by_identifier
    from honeybee_energy.schedule import ruleset as hbe_ruleset
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties import ruleset as hbph_ruleset
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreateVentSched(object):
    def __init__(
        self,
        _IGH,
        _name,
        _operating_days_per_week_,
        _operating_weeks_per_year_,
        _op_period_high,
        _op_period_standard,
        _op_period_basic,
        _op_period_minimum,
    ):
        # type: (gh_io.IGH, str, float, float, hbph_ruleset.DailyOperationPeriod, hbph_ruleset.DailyOperationPeriod, hbph_ruleset.DailyOperationPeriod, hbph_ruleset.DailyOperationPeriod) -> None
        self.IGH = _IGH
        self.name = _name
        self.operating_day_per_week = _operating_days_per_week_ or 7
        self.operating_weeks_per_year = _operating_weeks_per_year_ or 52
        self.op_period_high = _op_period_high
        self.op_period_standard = _op_period_standard
        self.op_period_basic = _op_period_basic
        self.op_period_minimum = _op_period_minimum

    def run(self):
        # type: () -> Optional[hbe_ruleset.ScheduleRuleset]
        ph_properties = hbph_ruleset.ScheduleRulesetPhProperties(_host=None)

        ph_properties.operating_days_wk = self.operating_day_per_week
        ph_properties.operating_weeks_year = self.operating_weeks_per_year

        if self.op_period_high:
            self.op_period_high.name = "high"
            ph_properties.daily_operating_periods.add_period_to_collection(
                self.op_period_high
            )

        if self.op_period_standard:
            self.op_period_standard.name = "standard"
            ph_properties.daily_operating_periods.add_period_to_collection(
                self.op_period_standard
            )

        if self.op_period_basic:
            self.op_period_basic.name = "basic"
            ph_properties.daily_operating_periods.add_period_to_collection(
                self.op_period_basic
            )

        if self.op_period_minimum:
            self.op_period_minimum.name = "low"
            ph_properties.daily_operating_periods.add_period_to_collection(
                self.op_period_minimum
            )

        # ---------------------------------------------------------------------
        # -- User Warnings
        msg = ph_properties.validate_operating_period_hours(24.0)
        if msg:
            self.IGH.warning(msg)

        # ---------------------------------------------------------------------
        # -- Create the HB-ScheduleRuleset's constant value based on the user-input
        hb_schedule_const_value = ph_properties.annual_average_operating_fraction

        # ---------------------------------------------------------------------
        # -- Create a new constant-value honeybee-energy-ScheduleRuleset object
        # -- Set the properties.ph with the user-determined values above.
        name = (
            clean_and_id_ep_string("ConstantSchedule")
            if self.name is None
            else clean_ep_string(self.name)
        )
        type_limit = schedule_type_limit_by_identifier("Fractional")
        ventilation_sch_ = hbe_ruleset.ScheduleRuleset.from_constant_value(
            name, hb_schedule_const_value, type_limit
        )
        ph_properties._host = ventilation_sch_._properties
        ventilation_sch_._properties._ph = ph_properties  # type: ignore

        return ventilation_sch_
