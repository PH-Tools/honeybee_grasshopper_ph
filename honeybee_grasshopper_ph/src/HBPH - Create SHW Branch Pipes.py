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
Create new HBPH DHW Branch Piping Object.
-
EM October 2, 2022

    Args:
        _geometry: (List[Curve]): A list of curves representing the SHW Branch
            Piping elements.
            
        _name: (List[str]) A name for the Pipe element (Optional)
            
        _diameter: (List[float]): Default=0.0127m (1/2") A list of diameters (m) of 
            each DHW Branch Piping element input. If the length of this list matches 
            the _geometry input list, the diameter values will be used in order. 
            Otherwise the first element in this list will be used as the 
            default diameter.
            
    Returns:
        dhw_branch_piping_: (List[PhPipeElement]) A list of the new HBPH Piping
            objects created. These can be added to HB Rooms using the 'Add PH DHW Piping'
            component.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from honeybee_ph_rhino import gh_compo_io, gh_io
from honeybee_ph_utils import preview

#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create SHW Branch Pipes"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSHWBranchPipes(
        IGH,
        _geometry,
        _name,
        _diameter,
    )
dhw_branch_piping_ = gh_compo_interface.run()
    
#-------------------------------------------------------------------------------
# -- Preview
for pipe in dhw_branch_piping_:
    preview.object_preview(pipe)
    
    