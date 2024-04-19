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
Set the column and row position for a material in a Mixed Material layer. Pass the output to a 
'HBPH - Create Heterogeneous Material' component in order to create mixed materials. Note that the 
columns and rows are specified from the upper-left to the lower-right, and both the row and column
counts start at '0', not '1'.
-
EM April 5, 2024

    Args:
        _column_position: (int) The column location. Note that columns start counting from '0', not '1'

        _row_position: (int) The row location. Note that columns start counting from '0', not '1'

        _hb_material: (EnergyMaterial) The Honeybee-Energy Material to use for the specified cell.
        
    Returns:
        hb_material_: The Honeybee-Energy Material with the column/row location specified.
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
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))

# -------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Set Mixed-Material Column and Row"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv)
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_energy_ph.properties.materials import opaque

    reload(opaque)
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import assmbly_set_material_column_and_row as gh_compo_io

    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)


# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetMaterialColumnAndRow(IGH, _column_position, _row_position, _hb_material)
hb_material_ = gh_compo_interface.run()
