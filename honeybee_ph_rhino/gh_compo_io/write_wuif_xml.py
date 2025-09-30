# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Write WUFI XML."""

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


class GHCompo_WriteWufiXml(object):
    """GHCompo Interface: HBPH - Write WUFI XML."""

    def __init__(self, _IGH, _filename, _save_folder, _hb_json_file, _settings, _write_xml, *args, **kwargs):
        # type: (gh_io.IGH, str, str, str, Optional[WufiWriteSettings], bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.filename = _filename
        self.save_folder = _save_folder
        self.hb_json_file = _hb_json_file
        self.settings = _settings or WufiWriteSettings()
        self.write_xml = _write_xml

    def give_user_warnings(self, _stdout):
        # type: (str) -> None
        """Give user warnings if any."""

        for line in _stdout.split("\n"):
            if "WARNING:" in line:
                self.IGH.warning(line)

    def run(self):
        # type: () -> Optional[str]
        if self.write_xml and self.hb_json_file and self.settings:
            print("Logging with log-level: {}".format(self.settings.generate_log_files))
            save_dir, save_filename, stdout, stderr = PHX.run.convert_hbjson_to_WUFI_XML(
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
            save_filename += ".xml"
            xml_file_ = os.path.join(save_dir, save_filename)
            return xml_file_
        else:
            return None
