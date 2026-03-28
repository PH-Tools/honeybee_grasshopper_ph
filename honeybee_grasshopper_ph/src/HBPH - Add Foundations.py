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
Add PH-Foundation objects to the Honeybee-Rooms. Note that 
PHPP only allows 3 different Foundation types per Building-Segment.
-
EM March 18, 2023
    Args:
        _ph_foundation: One or more PH-Foundation Objects that you would like 
            to add to each of the Honyebee-Rooms input.
               
        _hb_rooms: List[room.Room] One or more Honeybee-Rooms you would like to 
            add the new PH-Foundations to.
    
    Returns:
        hb_rooms_: The honeyee-Rooms with building-segment information added.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh


try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))
    
    
# -------------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Add Foundations"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import foundations_add as gh_compo_io
    reload(gh_compo_io)

# -------------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_AddFoundations(
        IGH,
        _ph_foundations,
        _hb_rooms,
)
hb_rooms_ = gh_compo_interface.run()
