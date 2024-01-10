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
    from PHX import run
except ImportError as e:
    raise ImportError('\nFailed to import PHX:\n\t{}'.format(e))


class GHCompo_WriteToPHPP(object):
              
    def __init__(self, _IGH, _hb_json_file, _activate_variants, _write):
        # type: (gh_io.IGH, str, str, bool) -> None
        self.IGH = _IGH
        self.hb_json_file = _hb_json_file
        self.activate_variants = _activate_variants or "False"
        self.write = _write or False

    def os_name(self, _os_name):
        # type: (str) -> str
        """Return the OS name as a nice string."""
        if _os_name == "nt":
            return "Windows"
        elif _os_name == "posix":
            return "Mac/Linux"
        else:
            return _os_name

    def run(self):
        # type: () -> None
        if self.write and self.hb_json_file:
            hb_python_site_packages = honeybee.config.folders.python_package_path
            stdout, stderr = run.write_hbjson_to_phpp(self.hb_json_file, hb_python_site_packages, self.activate_variants)
            self.check_for_verification_version_warning(stdout)
        else:
            msg = "Please open a valid PHPP file in Excel, and set '_write' to True."
            self.IGH.warning(msg)

    def check_for_verification_version_warning(self, _stdout):
        # type: (str) -> None
        for line in _stdout.split("\n"):
            if "PHPPVersionWarning:" in line:
                msg = (
                    "Warning: It appears that the PHPP Version and the PHI "
                    "Certification Version do not match? If you are writing to a "
                    "PHPP v10, be sure to add a 'HBPH PHI-Certification' component to the "
                    "'Building Segment', and set the '_phpp_version' to '10'."
                    )
                self.IGH.warning(msg)
                return None