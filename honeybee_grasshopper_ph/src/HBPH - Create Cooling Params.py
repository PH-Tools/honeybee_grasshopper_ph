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
Define cooling-parameters which are set on a heat-pump system. Connect the 'cooling_params_'
output of this component to one of the '_cooling_params_' inputs on a 'Create Space 
Conditioning System' component in order to set the cooling attributes of the heat pump.
-
EM November 1, 2023
    Args:
        _cooling_type: (int) Enter the type of cooling parameters to define. Input either - 
- "1-Ventilation Air"
- "2-Recirculating Air"
- "3-Dehumidification"
- "4-Radiant Panel"

    Returns:
        cooling_params_: The new HBPH-Cooling Params which can be set on a space-conditioning 
            heat-pump system.
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
    from honeybee_ph_rhino.gh_compo_io import mech_create_cooling_params
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))


# -------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Cooling Params"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import mech_create_cooling_params as gh_compo_io

    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)


# -------------------------------------------------------------------------------
# -- Setup the input nodes, get all the user input values
input_dict = mech_create_cooling_params.get_component_inputs(_cooling_type)
gh_io.setup_component_inputs(IGH, input_dict, _start_i=1)
input_values_dict = gh_io.get_component_input_values(ghenv)


# -------------------------------------------------------------------------------
# -- Build the new System
gh_compo_interface = gh_compo_io.GHCompo_CreateCoolingSystem(
    IGH,
    _cooling_type,
    input_values_dict,
)
cooling_params_ = gh_compo_interface.run()


# -------------------------------------------------------------------------------
# -- Preview
preview.object_preview(cooling_params_)
