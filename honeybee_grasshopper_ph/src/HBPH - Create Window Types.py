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
Create the Window Unit Type objects. Each window unit type can be made of one 
or more window 'Elements' (sashes) which are arranged in columns and rows to 
form gangs of windows in a grid. When supplying the '_pos_cols' and '_pos_rows'
be sure that the IDS can be sorted in order to get all the elements in the right
position. The column IDS should go from left to right, and the row IDs should go
from bottom to top. For instance
      c1   c2
    ----- -----
r2 |  x  |  x  |
   |-----|-----|
r1 |  x  |  x  |
    ----- -----

-
EM May 12, 2023
    Args:
        _type_names: (List[str]) A list of the type names to use.
        
        _ widths: (List[float) A list of the window widths to use.
        
        _heights: (List[float]) A list of the window heights to use.
        
        _pos_cols: (List[str]) A list of the window Column Position IDs to use.
        
        _pos_rows: (List[str]) A list of the window Row Position IDs to use.
    
    Returns:
        window_types_ (List[Rhino.Geometry.Brep]}:
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
ghenv.Component.Name = "HBPH - Create Window Types"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import win_create_types as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateWindowUnitTypes(
    IGH,
    _type_names,
    _widths,
    _heights,
    _pos_cols,
    _pos_rows,
    )
window_types_ = gh_compo_interface.run()