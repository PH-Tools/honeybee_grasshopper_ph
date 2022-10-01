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
Will calculate dimensions to shading-objects for each window in the project. These 
are written to the 'Shading' worksheet in the PHPP which will then calculate 
shading factors based on these dimensions. 
-
Reference: Shading factors will go from 0.0 (fully shaded) to 1.0 (fully unshaded) and are 
calculated using the simplified numerical method as implemented in the Passive 
House Planning Package and DesignPH 1.5 or earlier. 
-
Note that this method matches the 'old' style PHPP input (before DesignPH 2). It is 
a pretty fast way for the PHPP to calc. shading factors, but might be a bit less 
accurate than other methods for irregular situations (asymetric shading, irregular trees, etc).
It's useful if you want to match the exact procedure of an older style PHPP document.
-
For background and reference on the methodology used, see: "Solar Gains in a 
Passive House: A Monthly Approach to Calculating Global Irradiaton Entering a 
Shaded Window" By Andrew Peel, 2007.
-
EM October 1, 2022
    Args:
        _shading_surfaces: (List[Brep]) <Optional> Any shading geometry (walls, overhangs, side-reveals
            neighbors, trees, etc...) you'd like to take into account when generating 
            shading factors. Note that the more elements included, the slower this will run.
            You can use the "HBPH - Create Building Shading" component to easily generate the 
            building-surface and window reveal shading.
                
        _hb_rooms: (List[room.Room]) The Honeybee Rooms with apertures.
        
        _run: (Bool) Set True to run the shading-object finder.
    
    Returns:
        checklines_: (List[LineCurve]) Preview geometry showing the search lines used to find shading geometry.
            
        hb_rooms_: (List[room.Room]) The Honeybe Rooms with the shading-object dimensions added to all the apertures.
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

# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Add Shading Dims"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev='OCT_01_2022')
if DEV:
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SolveShadingDims(
        IGH,
        _shading_surfaces,
        _hb_rooms, 
        _run)
checklines_, hb_rooms_ = gh_compo_interface.run()