# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH Site."""

try:
    from typing import Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph import site
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_Site(object):
    def __init__(self, _IGH, _display_name, _location, _climate_data, _phpp_library_codes):
        # type: (gh_io.IGH, Optional[str], Optional[site.Location], Optional[site.Climate], Optional[site.PHPPCodes]) -> None
        self.IGH = _IGH
        self.display_name = _display_name or "_unnamed_"
        self.location = _location or site.Location()
        self.climate_data = _climate_data or site.Climate()
        self.phpp_library_codes = _phpp_library_codes or site.PHPPCodes()

    def run(self):
        # type: () -> site.Site
        hbph_obj = site.Site(
            self.location,
            self.climate_data,
            self.phpp_library_codes,
        )
        hbph_obj.display_name = self.display_name

        return hbph_obj
