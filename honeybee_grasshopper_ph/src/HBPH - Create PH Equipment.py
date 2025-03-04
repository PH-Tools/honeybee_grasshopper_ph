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
Create a new detailed Passive House style equipment which can be added to the 
honeybee Rooms.
-
EM March 4, 2025
    Args:
        _type: (str) Input either -
1-dishwasher,
2-clothes_washer,
3-clothes_dryer,
4-fridge,
5-freezer,
6-fridge_freezer,
7-cooking,
13-PHIUS_MEL,
14-PHIUS_Lighting_Int,
15-PHIUS_Lighting_Ext,
16-PHIUS_Lighting_Garage,
11-Custom_Electric_per_Year,
17-Custom_Electric_Lighting_per_Year,
18-Custom_Electric_MEL_per_Use,
100-PhiUS_Defaults,
200-Phi_Defaults,

        _display_name: (str) Optional display name
    
    Returns:
        equipment_: (list[PhEquipment]) New HBPH Electric Equipment which can be added to one 
            or more Honeybee-Rooms using the "HBPH - Add Process Equipment" component.
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
    from honeybee_ph_rhino.gh_compo_io.program import create_elec_equip
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))



#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create PH Equipment"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv)
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.program import create_elec_equip as gh_compo_io
    reload(gh_compo_io)
    reload(create_elec_equip)
    reload(gh_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
# -- Setup the input nodes, get all the user input values
input_dict = create_elec_equip.get_component_inputs(_type)
gh_io.setup_component_inputs(IGH, input_dict, _start_i=2)
input_values_dict = gh_io.get_component_input_values(ghenv)


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateElecEquip(
        IGH,
        _type,
        input_values_dict
    )
equipment_ = gh_compo_interface.run()


#-------------------------------------------------------------------------------
# -- Preview
for e in equipment_:
    preview.object_preview(e)