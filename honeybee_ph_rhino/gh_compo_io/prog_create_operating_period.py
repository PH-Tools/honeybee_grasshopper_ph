# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Operation Period."""

try:
    from honeybee_energy_ph.properties import ruleset
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreateOccPeriod(object):

    hours_per_day = ghio_validators.FloatMax24("hours_per_day")
    operating_fraction = ghio_validators.FloatPercentage("operating_fraction")

    def __init__(self, _IGH, _name, _hrs_per_day, _op_frac):
        # type: (gh_io.IGH, str, float, float) -> None
        self.IGH = _IGH
        self.name = _name or "_unnamed_op_period_"
        self.hours_per_day = _hrs_per_day
        self.operating_fraction = _op_frac

    def run(self):
        # type: () -> ruleset.DailyOperationPeriod
        return ruleset.DailyOperationPeriod.from_operating_hours(
            self.hours_per_day or 0.0, self.operating_fraction or 0.0, self.name
        )
