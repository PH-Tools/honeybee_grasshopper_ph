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
Visualize HBPH 'Spaces' as Rhino Geometry. Use the "Get Spaces" 
component in order collect all the HBPH Spaces from Hooneybee-Rooms.
-
EM October 18, 2023

    Args:
        _spaces: (list[Space]) A list of the HBPH Spaces that you would like
            to visualize in the Rhino scene.
        
        _attribute_: The Floor-Segment attribute to visualize by. Input either -
"display_name"
"weighting_factor"
"weighted_floor_area"
"floor_area"
            
    Returns:
        space_floor_segments_: The space floor-segments as Rhino surfaces.
        
        space_volumes_: The space volumes as Rhino Breps.
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
ghenv.Component.Name = "HBPH - Visualize Spaces"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import visualize_spaces as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_VisualizeSpaces(
    IGH,
    _spaces,
    _attribute_,
    )
space_floor_segments_, space_volumes_, wireframe_, legend_, values_ = gh_compo_interface.run()