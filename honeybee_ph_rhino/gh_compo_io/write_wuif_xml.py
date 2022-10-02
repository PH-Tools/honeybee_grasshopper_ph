# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Write WUFI XML."""

import os

try:
    from typing import Optional
except ImportError:
    pass # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    import PHX.run # type: ignore
except ImportError as e:
    raise ImportError('\nFailed to import PHX:\n\t{}'.format(e))

class GHCompo_WriteWufiXml(object):

    def __init__(self, _IGH, _filename,_save_folder, _hb_json_file, _write_xml):
        # type: (gh_io.IGH, str, str, str, bool) -> None
        self.IGH = _IGH
        self.filename = _filename
        self.save_folder = _save_folder
        self.hb_json_file = _hb_json_file
        self.write_xml = _write_xml

    def run(self):
        # type: () -> Optional[str]
        if self.write_xml and self.hb_json_file:
            d, f = PHX.run.convert_hbjson_to_WUFI_XML(self.hb_json_file, self.filename, self.save_folder)
            xml_file_ = os.path.join(d, f)
            return xml_file_