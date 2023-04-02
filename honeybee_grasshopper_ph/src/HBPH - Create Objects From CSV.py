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
Create a series of new objects based on an arbitrary CSV file input. Note that
the first row in the CSV should be the 'headers' which are used as the attribute
names for the object. Each row in the CSV will become a new object with the 
attribute values as defined in the file.
-
EM April 2, 2023
    Args:
        _path: (str) The path to the .CSV file to read.
        
        _object_name: (str) Optional name for the class of the new Objects.
        
        _datatypes: (List[str]) Optional list of datatypes to use to cast the 
            input data values. This list should follow the structure "header: type"
            for instance, inputing:
- - -
"Height: float"
"Width: float"
"ID: int"
- - - 
            will case the "Height" and "Width" attributes to float types, but will cast the 
            "ID" attribute as an int. 
        
    Returns:
        objects_: The list of new Objects created from the CSV file.
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
ghenv.Component.Name = "HBPH - Create Objects From CSV"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import util_create_objs_from_csv as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateObjectsFromCSV(
    IGH,
    _path,
    _object_name,
    _datatypes,
    )
objects_ = gh_compo_interface.run()