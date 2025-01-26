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
Add new PH Equipment (Appliances) to the HB-Rooms. 
-
Note that ALL of the equipment input will be added to ALL of the Honeybee-Rooms. 
This may not always be what you want, and so if you want to add equipment ONLY 
to certain rooms (ie: add a Cooktopto ONLY the Kitchen), then break up your 
Rooms accordingly and only pass in the relevant Honeybee-Room(s).
-
EM January 26, 2025
    Args:

        _equipment: (list[str | PHEquipment]) A List of new HBPH 'Equipment' to add 
            to the Honeybee Rooms. If a string is input (ie: "1-Dishwasher") a default
            ph-equipment of that type will be added. If you wish to input detailed
            equipment with specific values, use the "Create PH Equipment" component 
            to create that equipment and add it here.

        _num_bedrooms: (float) Enter the TOTAL number of bedrooms represented
            by the Honeybee-Rooms input. This is use to determine the total Phius
            appliance, lighting, and Misc. Electrical loads. 

        _num_occupants: (float) Enter the TOTAL number of occupants represented
            by the Honeybee-Rooms input. This is use to determine the total Phius
            appliance, lighting, and Misc. Electrical loads. 

        _num_dwellings: (float) default=1. Enter the TOTAL number of dwellings
            represented by the Honeybee-Rooms input. For single-family home and
            non-residential, enter '1' or leave empty. For Multi-Unit (apartment)
            buildings, enter the TOTAL number of dwellings. This values is used 
            to calculate Phius lighting and Misc. Electrical loads.

        _hb_rooms: (list[Room]) A list of HB-Rooms to add the PH-Equuipment to.
        
    Returns:
        hb_rooms_: The HB-Rooms with the .... added to them.
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
ghenv.Component.Name = "HBPH - Add Process Equipment"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.program import add_process_equip as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
# -- Create the new Single-Family Home Program from the Rooms
gh_compo_interface = gh_compo_io.GHCompo_AddProcessEquip(
    IGH,
    _equipment,
    _num_bedrooms,
    _num_occupants,
    _num_dwellings,
    _hb_rooms,
)
hb_rooms_ = gh_compo_interface.run()