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
Generate window Rhino surfaces based on a 'type', and a baseline curve to use as the starting
point. Use the "HBPH - Create Window Types" component to create these types from input data.
This geometry can be used to create HBPH Apertures which can be added to the HB Model.
-
EM May 12, 2023
    Args:
        _win_baselines: (List[LineCurve]) A list of 'baseline' curves to build the windows from.
            
        _win_names: (List[str]) A list of the window unit-type names corresponding to 
            the baseline curves input above.
            
        _win_collection: (Dict[str, WindowUnitType]) The collection of WindowUnitType objects
            to get the size information from. Use the "HBPH - Create Window Types" component 
            to create these types from input data.
    
    Returns:
        window_surfaces_ (List[Rhino.Geometry.Brep]): A list of the created
            window surface geometry. 
        
        srfc_names_ (List[str]): A list of the created window surface names.
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
ghenv.Component.Name = "HBPH - Create Window Geometry"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import win_create_geom as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateWindowRhinoGeometry(
    IGH,
    _win_baselines,
    _win_names, 
    _win_collection,
    )
win_surfaces_, srfc_names_ = gh_compo_interface.run()