#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
# 
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
# 
# Copyright (c) 2025, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com> 
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
Report out the occupancy related information for a set of Honenybee-Rooms.
-
EM January 26, 2025
    Args:

        _hb_rooms: (list[Room]) A list of HB-Rooms to get the data from. 
        
    Returns:
        total_num_bedrooms_: The total number of bedrooms found in the
            HB-Rooms input.

        total_num_people_: The total number of occupants found in the 
            HB-Rooms input.

        total_num_dwellings_: The total number of 'dwelling units' found in the 
            HB-Rooms input.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

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
ghenv.Component.Name = "HBPH - Get Occupancy"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.program import get_res_occupancy as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
# -- Create the new Single-Family Home Program from the Rooms
gh_compo_interface = gh_compo_io.GHCompo_GetResOccupancy(
    IGH,
    _hb_rooms,
)
total_num_bedrooms_, total_num_people_, total_num_dwellings_ = gh_compo_interface.run()