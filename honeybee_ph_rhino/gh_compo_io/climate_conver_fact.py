# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Conversion Factor."""

try:
    from typing import Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_standards.sourcefactors import factors 
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_standards:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

class GHCompo_ConversionFactor(object):

    def __init__(self, _IGH, _fuel_name, _factor):
        # type: (gh_io.IGH, Optional[str], Optional[float]) -> None
        self.IGH = _IGH
        self.fuel_name = factors.clean_input(_fuel_name)
        self.factor = _factor

    def run(self):
        # type: () -> Optional[factors.Factor]
        if not self.fuel_name or not self.factor:
            return None

        factor_ = factors.Factor()
        factor_.fuel_name = self.fuel_name
        factor_.value = self.factor
        return factor_