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
Apply a Honeybee SHW Mechanical System to a Honeybee Room or Rooms. Note that
this component will completely override any existing SHW System on the rooms input. If 
the room does not already have a Honeybee-Energy 'service_hot_water' load, one will 
be added with a nominal load of 0.001 L/hour.
-
EM September 30, 2022

    Args:
        _hb_shw: [SHWSystem] A Honeybee-Energy SHW Mechanical System Object 
            to assign to each of the input Honeybee Rooms.
        
        _hb_rooms: List[Room] A list of the Honeneybee Rooms to assign
            the SHW object to.
            
    Returns:
        hb_rooms_: (List[PhPipeElement]) The Honeybee Rooms with the new 
            SHW system applied.
"""

from honeybee_ph_rhino import gh_compo_io

#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Apply SHW System"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev='SEP_30_2022')
if DEV:
    reload(gh_compo_io)

#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_ApplySHWSys(
        _hb_shw,
        _hb_rooms,
    )

hb_rooms_ = gh_compo_interface.run()