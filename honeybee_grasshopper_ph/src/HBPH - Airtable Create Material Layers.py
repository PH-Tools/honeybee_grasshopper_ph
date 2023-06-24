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
Use ths componet when building HB-Materials from AirTable source data. Note that
the structure of the source Table is assumed to match the HBPH format and if your 
table includes data with different column names or data types you may get errors when using
this component. 
-
EM June 19, 2023
    Args:
        _material_records: (List[TableRecord]) A list of all the AirTable "TableRecord" line items. 
            Use the HBPH "HBPH - Airtable Download Table Data" component to download 
            this data from your "Material Data" table.
            
        _layer_records: (List[TableRecord]) A list of all the AirTable "TableRecord" line items
            representing the layers with a material and a thickness. Use the 
            HBPH "HBPH - Airtable Download Table Data" component to download 
            this data from your "Material Layers" table.
            
    Returns:
        
        ep_mat_layers_: (Collection) A HB/EP Material Collection of all the layers built
            from the AirTable data. Note that the AirTable Material-Layer id number is used
            as the key for the collection. Connect this output to the "HBPH - Airtable Create Constructions"
            component in order to build up the actual EP/HB Constructions.
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
ghenv.Component.Name = "HBPH - Airtable Create Material Layers"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import airtable_create_mat_layers as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_AirTableCreateMaterialLayers(
    IGH,
    _material_records,
    _layer_records,
    )
ep_mat_layers_ = gh_compo_interface.run()