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
Add PH-Spaces to honeybee-Rooms. Spaces represent smaller units than HB-Rooms and 
can be made up of one or more individual volumes. This is useful if you are calculating 
interior net-floor-area or volume as in the Passive House models. Each Space will map to 
a single entry in the WUFI 'Ventilation Rooms' or a PHPP 'Additional Ventilation'.
-
EM November 1, 2023
    Args:
        _spaces: (list[Space]) A list of the new PH-Spaces to add to the Honeybee-Rooms.
        
        _offset_dist_: (float) Default=0.1 An optional value to offset the 'test points' being 
            used to determine the right honeybee-Room to host the space in. This value 
            will be used to move the test point 'up' (world Z) by some dimension before 
            testing if it is 'inside' the honeybee-Room. This is useful you drew your
            floor-segments directly 'on' the floor surface of the honeybee room as this 
            sometimes leads to errors when testing for 'inside'.
        
        inherit_room_names_ (bool): default=False. Set to true if you would like all of the 
            PH-Spaces 'in' a Honeybee Room to automatically inherit the display name of the 
            Honeybee Room. Note: this will override any user-defined Space names.
        
        _hb_rooms: (list[Room]) The list of honeybee-Rooms to add to the spaces to.
            
    Returns:
        check_pts_: A preview of the test points being used to evaluate the right
            honeybee-Room to use for the host of the space. Useful for debugging 
            if you run into hosting problems.
            
        hb_rooms_: The honeyee-Rooms with the PH Spaces added to them.
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
ghenv.Component.Name = "HBPH - Add Spaces"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.make_spaces import make_space
    reload(make_space)
    from honeybee_ph_rhino.gh_compo_io import space_add_spc as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_AddPHSpaces(
    IGH,
    _spaces,
    _offset_dist_,
    inherit_room_names_,
    _hb_rooms,
    )
hb_rooms_, check_pts_, open_rooms_ = gh_compo_interface.run()