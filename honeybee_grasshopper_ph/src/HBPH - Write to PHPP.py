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
Convert an existing HBJSON file to a Passive House Exchange (PHX) model and write out 
the model data to a PHPP document. 
NOTE:
    - You must have a valid PHPP document to write to. The PHPP is *NOT* part of the 
    honeybee-ph plugin and must be purchased from PHI or your local reseller. For more 
    information, see: "https://passivehouse.com/04_phpp/04_phpp.htm"
    - The PHPP document you would like to write to should be open alongside Rhino, 
    and must be the the 'active' excel document. To ensure best results and least 
    likelihood of conflicts, it is recommended to close all other excel documents 
    on your system except the PHPP.
    - Once the PHPP file is open, set _write to True to run the writer. 
    - IMPORTANT: This component simply writes the data to the PHPP file. Once writen, 
    be sure to save your PHPP file with the new data to the appropriate location on 
    your computer.
-
EM October 2, 2022
    Args:
        _hbjson_file: (str) The full file path to the HBJSON you would like to write 
            out to PHPP.
        
        _activate_variants: (bool) Default="False", Set True if you would like to 
            connect all of the various PHPP inputs to the 'Variants' worksheet. This
            is used when testing various combinations of attributes during the 
            early design phase. Note that if activated, any inputs will get overwritten
            when the connection to the 'Variants' worksheet is made.
            Note: Args must be strings, not actual boolean True/False.
            
        _write: (bool) Set True to run the PHPP writer.
            
    Returns:
        hb_rooms_ (List[Room]) A list of the Honeybee Rooms with the ph-style occupancy set.
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


#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Write to PHPP"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_WriteToPHPP(
        IGH,
        _hbjson_file,
        _activate_variants,
        _write,
)
gh_compo_interface.run()