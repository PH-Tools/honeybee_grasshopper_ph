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
Convert an HBJSON file into a new WUFI-XML file which can then be opened using 
WUFI-Passive. This will read in the HBJSON, rebuild the HB-Model before converting the 
Model into a WUFI-Passive file.
-
EM June 5, 2024
    Args:
        _filename: (str) The filename for the WUFI XML file.
        
        _save_folder: (str) The folder path to save the WUFI XML file to.
        
        _hb_json_file: (str) The path to the HBJSON file to convert into WUFI XML.
        
        _settings: The WUFI Settings object. Connect the "HBPH - Write WUFI XML Settings"
            'settings_' output.

        _write_xml: (bool) Set True to run. 
            
    Returns:
        xml_file_: The full path to the output WUFI XML file.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh


try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))


# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Write WUFI XML"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from PHX import run
    reload(run)
    from honeybee_ph_rhino.gh_compo_io import write_wuif_xml as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)
    
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_WriteWufiXml(
        IGH,
        _filename,
        _save_folder,
        _hb_json_file,
        _settings,
        _write_xml,
)
xml_file_ = gh_compo_interface.run()