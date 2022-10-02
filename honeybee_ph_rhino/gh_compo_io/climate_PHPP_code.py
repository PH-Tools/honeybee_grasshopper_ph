# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH PHPP Climate."""

try:
    from typing import List, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph import site
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


class GHCompo_PHPPCodes(object):

    def __init__(self, _IGH, _country_code, _region_code, _dataset_name):
        # type: (gh_io.IGH, str, str, str) -> None
        self.IGH = _IGH
        self.country_code = _country_code or "US-United States of America"
        self.region_code = _region_code or "New York"
        self.dataset_name = _dataset_name or "US0055b-New York"

    @property
    def dataset_name(self):
        # type: () -> str
        return self._dataset_name

    @dataset_name.setter
    def dataset_name(self, _in):
        if _in is None:
            self._dataset_name = ""

        vals = _in.split("-")
        if len(vals) != 2:
            raise Exception(
                "Error: input for '_dataset_name' format should be "
                "'xx01234-xxxx'. Got: '{}'?".format(_in)
            )
        self._dataset_name = _in
        self.display_name = vals[1]

    def run(self):
        # type: () -> site.PHPPCodes
        hbph_obj = site.PHPPCodes(
            self.country_code,
            self.region_code,
            self.dataset_name,
        )
        return hbph_obj
