# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Write WUFI XML."""

import os

try:
    from typing import Optional, List, Dict, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    import PHX.run  # type: ignore
except ImportError as e:
    raise ImportError("\nFailed to import PHX:\n\t{}".format(e))


class GHCompo_WriteWufiXml(object):
    def __init__(
        self,
        _IGH,
        _filename,
        _save_folder,
        _hb_json_file,
        _write_xml,
        _group_components,
        _merge_faces,
        _generate_log_files,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, str, str, str, bool, bool, Union[bool, float], int, List, Dict) -> None
        self.IGH = _IGH
        self.filename = _filename
        self.save_folder = _save_folder
        self.hb_json_file = _hb_json_file
        self.write_xml = _write_xml
        self.generate_log_files = _generate_log_files or 0

        # -- Group the model components during export to XML?
        if _group_components is None or _group_components == True:
            self.group_components = True  # default == True
        else:
            self.group_components = False

        # -- Merge the model faces during export to XML?
        if _merge_faces is None or _merge_faces is False:
            self.merge_faces = False # Default = will not merge faces
        elif _merge_faces == True:
            self.merge_faces = True # Will use default model tolerance
        else:
            self.merge_faces = float(_merge_faces) # Tolerance


    def give_user_warnings(self, _stdout):
        # type: (str) -> None
        """Give user warnings if any."""
        
        for line in _stdout.split("\n"):
            if "WARNING:" in line:
                self.IGH.warning(line)

    def run(self):
        # type: () -> Optional[str]
        if self.write_xml and self.hb_json_file:
            print("Logging with log-level: {}".format(self.generate_log_files))
            save_dir, save_filename, stdout, stderr = PHX.run.convert_hbjson_to_WUFI_XML(
                self.hb_json_file,
                self.filename,
                self.save_folder,
                self.group_components,
                self.merge_faces,
                self.generate_log_files,
            )
            self.give_user_warnings(stdout)
            save_filename += ".xml"
            xml_file_ = os.path.join(save_dir, save_filename)
            return xml_file_
        else:
            return None
