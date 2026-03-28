# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Write METr JSON."""

import os

try:
    from typing import Any, Optional
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

try:
    from honeybee_ph_rhino.gh_compo_io.write_wufi_xml_settings import WufiWriteSettings
except ImportError as e:
    raise ImportError("\nFailed to import WufiWriteSettings:\n\t{}".format(e))


class GHCompo_WriteMetrJson(object):
    """GHCompo Interface: HBPH - Write METr JSON."""

    def __init__(self, _IGH, _filename, _save_folder, _hb_json_file, _settings, _write_json, *args, **kwargs):
        # type: (gh_io.IGH, str, str, str, Optional[WufiWriteSettings], bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.filename = _filename
        self.save_folder = _save_folder
        self.hb_json_file = _hb_json_file
        self.settings = _settings or WufiWriteSettings()
        self.write_json = _write_json

    def give_user_warnings(self, _stdout):
        # type: (str) -> None
        """Give user warnings if any."""
        for line in _stdout.split("\n"):
            if "WARNING" in line:
                self.IGH.warning(line)

    def give_user_errors(self, _stderr):
        # type: (str) -> None
        """Give user errors if any."""
        print("_stderr=", _stderr)
        for line in _stderr.split("\n"):
            if "ERROR" in line:
                self.IGH.error(line)

    def run(self):
        # type: () -> Optional[str]
        if self.write_json and self.hb_json_file and self.settings:
            print("Logging with log-level: {}".format(self.settings.generate_log_files))
            save_dir, save_filename, stdout, stderr = PHX.run.convert_hbjson_to_METR_JSON(
                self.hb_json_file,
                self.filename,
                self.save_folder,
                self.settings.group_components,
                self.settings.merge_faces,
                self.settings.merge_spaces_by_erv,
                self.settings.merge_exhaust_vent_devices,
                self.settings.generate_log_files,
            )
            self.give_user_warnings(stdout)
            self.give_user_errors(stderr)
            save_filename += ".json"
            json_file_ = os.path.join(save_dir, save_filename)
            return json_file_
        else:
            return None
