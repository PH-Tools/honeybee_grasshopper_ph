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
Set the PH-Style occupancy for the Honeybee-Rooms input.
-
Note that this componet will create a new, unique 'People' load for EACH HB-Room input, and will
set the values accordigly. On some larger projects with many rooms, creating these duplicate 'People' 
objects may not be ideal, and may lead to longer run-times. As an alternative, use the 'Set People 
PH Attributes' component to create a Honeybee-Energy Program, which can then be assigned to multiple rooms at once.
-
For Phius residential projects, a room's "_num_people" should be the rooms's "number-of-bedrooms" + 1
-
EM January 28, 2025
    Args:
        _num_bedrooms: (list[int]) A list of number of bedrooms for EACH Honeybee-Room input.
            This should ideally be the same length as the '_hb_rooms' input, and in the same 
            order. If only a single value is input, that value will get applied to all of the 
            Honeybee-Rooms input. Note that this value is the number of bedrooms PER-HB-ROOM, 
            not the total number of bedrooms in the entire model.
        
        _num_people: (List[float]) A list of the number of people for EACH Honeybee-Room input.
            This should ideally be the same length as the '_hb_rooms' input, and in the same 
            order. If only a single value is input, that value will get applied to all of the 
            Honeybee-Rooms input. Note that this value is the number of people PER-HB-ROOM, 
            not the total number of people in the entire model.      

        _set_res_schedule_: (bool) Default=True. Set the Room's Occupancy and Occupant-Activity schedule
            to the Passive-House deffaults? If set to 'False', the Room's existing schedule will be 
            maintained. If None, will re-set the schedule to match the PH res-typical schedule.
        
        _hb_rooms: (List[Room]) A list of Honeybee-Rooms to set the occupancy values on.
            
    Returns:
        hb_rooms_ (List[Room]) A list of the Honeybee Rooms with the ph-style occupancy set.
"""


import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh


try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))


#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Set Res Occupancy"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.program import set_res_occupancy as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetResOccupancy(
        IGH,
        _num_bedrooms,
        _num_people,
        _set_res_schedule_,
        _hb_rooms,
    )
hb_rooms_= gh_compo_interface.run()