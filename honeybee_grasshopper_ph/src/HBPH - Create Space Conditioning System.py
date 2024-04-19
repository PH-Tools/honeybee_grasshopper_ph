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
Create a new PH-Style Space Conditioning (Heating, Cooling) System which can be added to the HB-Rooms.
Connect the 'space_conditioning_system_' output to the '_space_conditioning_systems' input on a 
'HBPH - Add Mech Systems' component.
-
EM November 1, 2023
    Args:
        _system_type: (int) Enter the type of heating system.
        
    Returns:
        space_conditioning_system_: The new HBPH-Heating/Cooling System which can be 
            added to one or more HB-Rooms via the 'HBPH - Add Mech Systems' component.
"""

import ghpythonlib.components as ghc
import Grasshopper as gh
import Rhino as rh
import rhinoscriptsyntax as rs
import scriptcontext as sc

try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_utils:\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
    from honeybee_ph_rhino.gh_compo_io import mech_create_space_conditioning_sys
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))

# -------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Space Conditioning System"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import mech_create_space_conditioning_sys as gh_compo_io

    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)


# -------------------------------------------------------------------------------
# -- Setup the input nodes, get all the user input values
input_dict = mech_create_space_conditioning_sys.get_component_inputs(_system_type)
gh_io.setup_component_inputs(IGH, input_dict, _start_i=1)
input_values_dict = gh_io.get_component_input_values(ghenv)


# -------------------------------------------------------------------------------
# -- Build the new System
gh_compo_interface = gh_compo_io.GHCompo_CreateSpaceConditioningSystem(
    IGH,
    _system_type,
    input_values_dict,
)
space_conditioning_system_ = gh_compo_interface.run()


# -------------------------------------------------------------------------------
# -- Preview
preview.object_preview(space_conditioning_system_)
