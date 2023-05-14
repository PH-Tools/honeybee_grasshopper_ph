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
This component can be used to help visualize and diagnose problems when you get the 
dreaded "Input faces do not form a closed volume" error when you are trying to create 
Honeybee  Rooms out of a set of Honeybee Faces. Pass in the faces here and this 
component will try and visualize where the failures are occuring.
-
EM May 14, 2023
    Args:
        _faces: The Honeybee Faces for the room you are trying to create. If you
            would like to test several rooms at once, make sure each room's faces 
            are on a separate branch of the input DataTree.
        
        _radius: (Optional[float]) default=1. When any error geometry is found, this 
            component will 'pipe' it in order to help make it visibe in the Rhino scene. 
            Use the _radius value to adjust the size of the Pipe object created.
    
    Returns:

        error_rooms_: If any erroring rooms are found.
        
        error_rooms_non_manifold_edges_: If any erroring non-manifold edges are found.
        
        error_rooms_naked_edges_: If any naked-edges are found.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from honeybee_ph_rhino import gh_compo_io, gh_io

# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Diagnose HB Rooms"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import util_diagnose_hb_rooms as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_DiagnoseBadHBRoomGeometry(
    IGH,
    _faces, 
    _radius,
    )
error_rooms_, error_rooms_non_manifold_edges_, error_rooms_naked_edges_ = gh_compo_interface.run()