#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
# 
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
# 
# Copyright (c) 2022, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com> 
# Honeybee-PH is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee-PH is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# For a copy of the GNU General Public License
# see <https://github.com/PH-Tools/honeybee_ph/blob/main/LICENSE>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
#
"""
Settings and congiguration options for the WUFI-Writer.
-
EM June 5, 2024
    Args:
        _group_components: (bool) Default=True. Set 'False' to keep each component
            (face) in the WUFI Model separate.
        
        _merge_faces: (bool | float [tolerance]) Default=False. Set 'True' to try and merge  
            together touching faces in order to simplify the model. This operation can 
            somethimes have unexpected results with some geometry, so only use 
            it if you really need to reduce the complexity of the WUFI model and 
            be sure to careufully check the resulting model faces for errors. If you
            have errors when merging, try passing in a different tolerance value here 
            (0.0001, 0.1, etc) and see if that helps.

        _merge_spaces_by_erv: (bool) Default=False. Set 'True' to have the WUFI-XML
            report out the spaces as 'merged' elements. In the WUFI "Rooms Ventilation"
            section there will be only a single 'room' entry for each ERV. This is 
            sometimes requested by Phiue when reviewing a project for Certification.
            Best practice is to leave it 'False' and to report out all the detailed
            rooms one at a time.

        _merge_exhaust_vent_devices: (bool) Default=False. Set 'True' to have the WUFI-XML
            report out the exhaust-ventilation (fans, kitchen hoods) 'merged' by type in order
            to simplify and shorten the WUFI-model. 

        _generate_log_files: (int) Default=0. Input a log-level here if 
            you would like PHX to generate log-files which record the operations 
            and progress of the HBJSON->XML process. Input either:

50 = CRITICAL
40 = ERROR
30 = WARNING
20 = INFO
10 = DEBUG
0 = NO LOGS (DEFAULT)
        
    Returns:
        settings_: The settings for the WUFI-Write operation.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Write WUFI XML Settings"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import write_wufi_xml_settings as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_WriteWufiXmlSettings(
    _IGH=IGH,
    _group_components=_group_components,
    _merge_faces=_merge_faces,
    _merge_spaces_by_erv=_merge_spaces_by_erv,
    _merge_exhaust_vent_devices=_merge_exhaust_vent_devices,
    _generate_log_files=_generate_log_files,
)
settings_ = gh_compo_interface.run()


# ------------------------------------------------------------------------------
preview.object_preview(settings_)