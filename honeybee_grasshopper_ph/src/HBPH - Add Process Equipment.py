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
to certain rooms (ie: add a Cooktop to ONLY the Kitchen), then break up your
Rooms accordingly and only pass in the relevant Honeybee-Room(s).
-
WUFI-Passive, METr and PHPP read the equipment's own values (set them with the
"Create PH Equipment" component). The '_num_bedrooms', '_num_occupants' and
'_num_dwellings' inputs below only size the Honeybee / EnergyPlus process load.
-
EM October 24, 2026
    Args:
        _equipment: (list[str | PhEquipment]) The equipment to add to the Honeybee-Rooms.
            Input either PH-Equipment from the "Create PH Equipment" component, or a
            type string to add a default: "1-dishwasher", "2-clothes_washer", ...
            "100" adds the full Phius default set, "200" the full PHI default set.
            Note: a single type string always builds the Phius default for that
            type, even on a PHI project. Use "Create PH Equipment" for PHI values.

        _num_bedrooms: (float) The TOTAL number of bedrooms in the Honeybee-Rooms input.
            Used ONLY to size the Honeybee / EnergyPlus process load. WUFI-Passive and
            METr take the bedroom count from the rooms' PH occupancy data instead.

        _num_occupants: (float) The TOTAL number of occupants in the Honeybee-Rooms input.
            Used ONLY to size the Honeybee / EnergyPlus process load. WUFI-Passive and
            METr take the occupant count from the rooms' PH occupancy data instead.

        _num_dwellings: (float) default=1. The TOTAL number of dwelling units in the
            Honeybee-Rooms input ('1' for a single-family home or non-residential).
            Used ONLY to size the Honeybee / EnergyPlus process load. WUFI-Passive and
            METr take the dwelling-unit count from the rooms' PH occupancy data instead.

        _hb_rooms: (list[Room]) The Honeybee-Rooms to add the PH-Equipment to.

    Returns:
        hb_rooms_: The Honeybee-Rooms with the PH-Equipment added as Honeybee
            process loads.
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