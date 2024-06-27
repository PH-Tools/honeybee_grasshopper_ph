#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
# 
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
# 
# Copyright (c) 2024, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com> 
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
Use to build up a 'mixed' material layer. This is most commonly something like studs in an insulation layer.
The mixed layer is defined as a grid of 'cell's with each cell having a different material applied. Use the 
rows and columns inputs to define the cell organization. Note that the cells are built from the upper left to 
the lower right, so inputing '_column_widths' of [0.5, 1, 0.5] will yield a grid of three columns and one row:

...|.C0..|....C1....|.C2..|
R0 |.....|..........|.....|

-
EM April 5, 2024

    Args:
        _base_material: (EnergyMaterial) A material to use as the 'base' for the Layer. This material will
            be used for any row/column area where a specific material has not been set in the '_additional_materials'
            input list.

        _additional_materials: (List[EnergyMaterial]) A list of Honeybee-Energy Materials to use
            for the different areas of the divided layer. Be sure to use the 'HBPH - Set Mixed-Material Column/Row'
            on the EnergyMaterial FIRST in order to set the row/column location.

        _column_widths: A list of the widths of the columns. ie: for 3 columns, enter
            [0.5, 1.2, 0.5]. You may also enter valus with unit informtion, for instance ['7.25in', '1.5in', '7.25']
        
        _row_heights: (List[float]) A list of the heights of the rows. ie: for 3 rows, enter
            [0.5, 1.2, 0.5]. You may also enter valus with unit informtion, for instance ['1.5in', '94in', '1.5']
        
    Returns:
        preview_: A rhino-geometry preview of the grid generated for the Layer, for troubleshooting and validation.

        hb_material_: The new Honeybee-Energy material which can be used a part of any normal Honeybee-Energy Construction. 
            When exported to WUFI-Passive or PHPP, the mixed materials will be output as part of the assembly.
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
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Heterogeneous Material"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv)
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_energy_ph.properties.materials import opaque
    reload(opaque)
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import assmbly_create_heterogeneous_material as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateHeterogeneousMaterial(
    IGH, _base_material, _additional_materials, _column_widths, _row_heights)
hb_material_, preview_ = gh_compo_interface.run()