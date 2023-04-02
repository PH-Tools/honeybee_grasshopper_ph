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
Re-build rectangular surface geometry based on a series of input widths and heights. This 
is useful when you need to re-draw windows based on a detailed schedule, or other similar 
model-wide revisions to geometry. This component will center the new geometry in the same location
as the old geometry. Use Bake (or HumanUI Bake to get names and custom layers) to push this 
new geometry back to the Rhino scene.
-
EM April 2, 2023
    Args:
        _window_surfaces: (List[Guid]) A list of surface Guids to perform the transformation on.
        
        _widths: (List[float]) A list of the new widths.
        
        _heights: (List[float]) A list of the new heights.
       
    Returns:
        new_surfaces_: The new surfaces with the specified width and height values
        
        names_: A list of the names of the new surfaces.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_utils:\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))

# -------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Rebuild Window Surfaces"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev="23402")
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import win_rebuild_rh_geom as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_RebuildWindowSurfaces(
    IGH, _window_surfaces, _widths, _heights
)
new_surfaces_, names_ = gh_compo_interface.run()
