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
Set the PH-HVAC Renewable Energy Systems (PV, etc..) serving one or more Honeybee Rooms.
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 21, 2024
    Args:
        _renewable_systems: (PhRenewableEnergySystem) The renewable energy systems to add.
    
        _hb_rooms: (list[Room]) A list of the hb-rooms to add the renewable energy systems to.
        
    Returns:
        hb_rooms_: The input hb-rooms served by new PH-HVAC Renewable Systems added.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh


try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))


#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Add Renewable Energy Devices"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.hvac import add_renewable_system as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)
    

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
# -- Add the new Systems to the HB-Rooms
gh_compo_interface = gh_compo_io.GHCompo_AddRenewableEnergyDevices(
        IGH,
        _renewable_systems,
        _hb_rooms,
    )
hb_rooms_ = gh_compo_interface.run()
