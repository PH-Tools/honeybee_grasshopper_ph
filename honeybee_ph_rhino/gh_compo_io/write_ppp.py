# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Write PPP File."""

import os

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    import PHX.run
except ImportError as e:
    raise ImportError("\nFailed to import PHX:\n\t{}".format(e))


class GHCompo_WritePPPFile(object):
    """GHCompo Interface: HBPH - Write PPP File."""

    def __init__(self, _IGH, _hb_json_file, _filename, _save_folder, _write, *args, **kwargs):
        # type: (gh_io.IGH, str, str, str, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.filename = _filename
        self.save_folder = _save_folder
        self.hb_json_file = _hb_json_file
        self.write = _write

    def give_user_warnings(self, _stdout):
        # type: (str) -> None
        """Give user warnings if any."""
        for line in _stdout.split("\n"):
            if "WARNING" in line:
                self.IGH.warning(line)

    def run(self):
        # type: () -> str | None
        if self.write and self.hb_json_file:
            save_dir, save_filename, stdout, stderr = PHX.run.write_hbjson_to_ppp(
                self.hb_json_file,
                self.filename,
                self.save_folder,
            )
            self.give_user_warnings(stdout)
            save_filename += ".ppp"
            ppp_file_ = os.path.join(save_dir, save_filename)
            return ppp_file_
        else:
            return None
