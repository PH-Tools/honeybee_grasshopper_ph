# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Write to PHPP."""

import os

try:
    from typing import Optional
except ImportError:
    pass # IronPython 2.7

try:
    import honeybee.config
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    import PHX.run
except ImportError as e:
    raise ImportError('\nFailed to import PHX:\n\t{}'.format(e))


class GHCompo_WriteToPHPP(object):

    def __init__(self, _IGH, _hb_json_file, _activate_variants, _write):
        # type: (gh_io.IGH, str, str, bool) -> None
        self.IGH = _IGH
        self.hb_json_file = _hb_json_file
        self.activate_variants = _activate_variants or "False"
        self.write = _write or False
        
        #-------------------------------------------------------------------------------
        if os.name != 'nt':
            msg = "Error: This PHPP writer is only supported on Windows OS. It looks like "\
                "you are running '{}'?".format(os.name)
            self.IGH.error(msg)

    def run(self):
        # type: () -> None
        if self.write and self.hb_json_file:
            hb_python_site_packages = honeybee.config.folders.python_package_path
            PHX.run.write_hbjson_to_phpp(self.hb_json_file, hb_python_site_packages, self.activate_variants)
        else:
            msg = "Please open a valid PHPP file in Excel, and set '_write' to True."
            self.IGH.warning(msg)