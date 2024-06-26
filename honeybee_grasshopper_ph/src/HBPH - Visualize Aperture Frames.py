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
Pull out all the frame and glazing surfaces from a given list of HB-Apertures. This
will create Rhino geometry for each of the elements which can be visualized in the
scene and used to check the model construction.
- -
Note: The UV of your window surfaces is CRITICAL for this component to work properly. Your 
window's UV in Rhino MUST be the standard orientation with U (green)='up' and V (red)='to the right'
and the surface's normal pointing 'out' from the HB-Zone. Use the Rhino 'Show Object Direction' tool in 
the 'Surfaces' toolbar to view and modify your window-surfaces until they are all consistently oriented.
If you do not do this, the edges cannot be ordered properly and you will get unpredictable 
results from this component. 
-
EM May 24, 2024
    Args:
        _aperture: (List[Aperture]) The list of HB-Aperatures to get the frame and 
            glass geometry for.
            
    Returns:
        aperture_surfaces_: The aperture surface.

        frame_surfaces_: The aperture frame element surfaces.
            
        glazing_surfaces_: The aperture glazing surfaces.
        
        frame_typenames_: The display-name of each frame element. This 
            is mostly useful for debugging.
        
        aperture_edges_: A DataTree of the aperture edge geometry in 
            order (Top, Right, Bottom, Left). This is useful for debugging.
            
        aperture_planes_: A DataTree of the aperture surface planes. This 
            is mostly useful for debugging.
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
ghenv.Component.Name = "HBPH - Visualize Aperture Frames"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import visualize_win_frames as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_VisualizeWindowFrameElements(
    IGH,
    _apertures,
    )
    
(
    aperture_surfaces_,
    frame_surfaces_,
    glazing_surfaces_,
    frame_typenames_,
    aperture_edges_, 
    aperture_planes_,
) = gh_compo_interface.run()
