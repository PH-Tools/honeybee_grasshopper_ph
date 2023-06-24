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
Use this component to build up EP/HB Constructions from AirTable data. Note that
the structure of the source Table is assumed to match the HBPH format and if your 
table includes data with different column names or data types you may get errors when using
this component. 
-
EM June 19, 2023
    Args:
        _ep_mat_layers: (Collection) The material-layer collection with all the available 
            EP/HB materials. Use the "HBPH - Airtable Create Material Layers" component 
            to create this collection from the AirTable data.
            
        _const_records: (List[TableRecord]) A list of all the AirTable "TableRecord" line items
            representing the construction assembly. Use the 
            HBPH "HBPH - Airtable Download Table Data" component to download 
            this data from your "Assemblies" table.
            
    Returns:
        
        ep_const_: (List) All of the EP/HB Constructions created from the AirTable data.
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
ghenv.Component.Name = "HBPH - Airtable Create Constructions"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import airtable_create_constructions as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_AirTableCreateConstructions(
    IGH,
    _ep_mat_layers,
    _const_records,
    )
ep_const_ = gh_compo_interface.run()