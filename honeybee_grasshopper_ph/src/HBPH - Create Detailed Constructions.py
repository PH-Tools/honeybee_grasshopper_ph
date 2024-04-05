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
Create new Honeybee-Energy Constructions based on a JSON file and a set of 
Honeybee-Energy Materials. Note that the input JSON describing the construction 
should be a normal HB JSON, except that this component also allows for an optional
"thickness" attribute which will set the thickness of each material layer as 
the new construction is built. For example - 

"W1 - Below Grade Conc. Wall": {
    "type": "OpaqueConstructionAbridged",
    "identifier": "W1 - Below Grade Conc. Wall",
    "materials": ["Concrete (Heavily Reinforced) [R-0.05/in]", "XPS [R-5.0/in]"],
    "thicknesses": ["8in", "6in"]
}

Will create a new construction and set the thicknesses of the layers as indicated (8in, then 6in).

-
EM April 1, 2023
    Args:
        _materials (List[EnergyMaterials]): A list of the Honeybee-Energy materials
            that you would like to use to create the Honeybee Constructions.
        
        _path: (str) The path (or paths) to the .JSON file which describes the 
            Honeybee-Constructions.
            
    Returns:
        constructions_: The new Honeybee-Energy Constructions, built from the
            Honeybee-Energy Materials input.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from honeybee_ph_rhino import gh_compo_io, gh_io

# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Detailed Constructions"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import assmbly_create_detailed_const as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateDetailedConstructions(
    IGH,
    _path,
    _materials,
    )
constructions_ = gh_compo_interface.run()