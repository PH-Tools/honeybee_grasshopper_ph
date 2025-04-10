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
Create new Electric-Equipment (Process) objects and add them to the Honeybee-Rooms for Phius Multifamily
projects. This component will automate the creation of Phius Multifamily Residential loads. Input 
the values from the "HBPH - Get Phius Multi-Family Residential Room Loads", or calculate the 
values yourself using the 'Phius Multifamily Calculator v24.0.2 | 2024 11'
> https://www.phius.org/phius-multifamily-lighting-misc-load-calculator
-
EM April 8, 2025
    Args:

        _equipment_: (list[PhEquipment]) Optional list of Ph-Equipment (Process) objects
            which will be included.

        _total_mel: (float) The total MEL (kWh/a) of the Honeybee-Rooms provided. This total MEL 
            will be evenly divided into the Honeybee-Rooms, then a new MEL (Process) load 
            created and addded to each Honeybee-Room.

        _total_lighting: (float) The total Lighting (kWh/a) of the Honeybee-Rooms provided. This total MEL 
            will be evenly divided into the Honeybee-Rooms, then a new Lighting (Process) load 
            created and addded to each Honeybee-Room.

        _hb_non_residential_rooms: (list[Room]) The Honeybee Non-Residential Rooms to add the new loads to.

    Returns:

        hb_non_residential_rooms_: The Honeybee-Rooms with the new Non-Residential electrical
            equipment added to the relevant rooms.        
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
ghenv.Component.Name = "HBPH - Set Phius Multi-Family Non-Residential Room Loads"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.program import set_phius_mf_nonres as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetPhiusMFNonResidentialRoomLoads(
    IGH,
    _equipment_,
    _total_mel,
    _total_lighting,
    _hb_non_residential_rooms,
)

hb_non_residential_rooms_ = gh_compo_interface.run()