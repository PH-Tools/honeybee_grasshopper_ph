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
Add one or more detailed Passive House style electric-equipment objects to the 
honeybee Rooms.
-
EM January 22, 2025

    Args:
        phius_defaults_: (int) Optional. Input either:
        > "1" for Single Family Residential appliance set.
        > "2" for Multifamily Residential appliance set.
            Note - for Multifamily, be sure to add in the Int. / Ext. Lighting and MEL from
            the Phius MF Calculator using a 'Create PH Appliance' HBPH Component.
        > "3" for Multifamily NonResidential appliance set (none).
            Note - for Multifamily, be sure to add in the Int. / Ext. Lighting and MEL from
            the Phius MF Calculator using a 'Create PH Appliance' HBPH Component.
        
        phi_defaults_: (bool) default=False. Set True to add the default PHI equipment
            set to the model.
        
        equipment_: (List[PhEquipment]) A List of Passive-House style electric
            equipment to add onto the Honeybee-Room.
            
    Returns:
        hb_rooms_: (List[Room]) A list of the Honeybee Rooms with the new appliances
            added to them.
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
ghenv.Component.Name = "HBPH - Add PH Equipment"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.program import add_elec_equip as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)
    
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_AddElecEquip(
        IGH,
        phius_defaults_,
        phi_defaults_,
        equipment_,
        _hb_rooms,
    )
hb_rooms_, ph_equipment = gh_compo_interface.run()


#-------------------------------------------------------------------------------
# -- Preview
for device in ph_equipment:
    preview.object_preview(device)