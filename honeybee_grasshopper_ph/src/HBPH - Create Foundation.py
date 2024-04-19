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
Create a new PH-Foundation object which can be added to one or more Honeybee-Rooms.
-
EM March 18, 2023
    Args:
        _type: (str) The Type of foundation. Input either-
"1-Heated Basement"
"2-Unheated Basement"
"3-Slab on Grade"
"4-Vented Crawlspace"
"5-None"
    
    Returns:
        ph_foundation: The new PH-Foundation object which can be added to one 
            or more Honeybee-Rooms using the "HBPH - Add Foundations" component.
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
    from honeybee_ph_rhino.gh_compo_io.foundations_create import get_component_inputs
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))


# -------------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Foundation"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph import foundations

    reload(foundations)
    from honeybee_ph_rhino.gh_compo_io import foundations_create as gh_compo_io

    reload(gh_compo_io)


# -------------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)


# -------------------------------------------------------------------------------
# -- Setup the input nodes, get all the user input values
input_dict = get_component_inputs(_type)
gh_io.setup_component_inputs(IGH, input_dict, _start_i=2)
input_values_dict = gh_io.get_component_input_values(ghenv)


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateFoundations(
    IGH,
    _type,
    input_values_dict,
)
ph_foundation_ = gh_compo_interface.run()


# -------------------------------------------------------------------------------------
preview.object_preview(ph_foundation_)
