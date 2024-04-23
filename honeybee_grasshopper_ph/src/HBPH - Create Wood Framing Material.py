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
Create a simple heteregeneous Honeybee-Energy Material for a wood-stud + insulation material.
Note that ONLY wood studs/joists are supported - NOT steel studs. This component will create 
a mixed-material layer which will output detailed constructions for WUFI-Passive and PHPP.
If you need to create a material with more complex geometry, use the 
"HBPH - Create Heterogeneous Material" component. For all dimensions input, enter the values as if 
the material was being viewed from the inside or outside face, ie: in 'elevation' view.
-
EM April 5, 2024

    Args:
        _insulation_material: (EnergyMaterial) The base material to use for the cavities of the stud wall.

        _wood_framing_material: (EnergyMaterial) The wood-framing material to use for the studs/joists.

        _wood_framing_member_width: (float) Default=1.5in [0.038m] The thickness of the wood stud/joist, when
            viewed from the inside face (in 'elevation').

        _wood_framing_member_oc_spacing: (float) Default=16in [0.184m] The center-to-center spacing from one
            stud/joist element to the next.

        _top_plate_width: (float) Default=0.0 Optional face width (in 'elevation') of any top-plate elements
            that should be added to the material. In most cases, this would be either 1.5in (single plate) or 
            3.0in (double plate).

        _bottom_plate_width: (float) Default=0.0 Optional face width (in 'elevation') of any bottom-plate elements
            that should be added to the material. In most cases, this would be 1.5in (single plate).

        _element_total_length: (float) Default=96in [2.438m]. Optional 'length' of the material, when viewed
            in 'elevation'. For a wall, this is the distance from the top of the top-plate, to the bottom of the 
            bottom-plate. For a roof, this would be the distance from the Rim-Joist/edge to the ridge. Etc...
            This value only matters if you add top- and / or bottom-plate elements - otherwise it will have no 
            effect on the material's conductivity.

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
    raise ImportError('Failed to import honeybee_ph_utils:\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))

#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Wood Framing Material"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv)
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_energy_ph.properties.materials import opaque
    reload(opaque)
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import assmbly_create_wood_framing_material as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateWoodFramingMaterial(
    IGH,
    _insulation_material,
    _wood_framing_material,
    _wood_framing_member_width,
    _wood_framing_member_oc_spacing,
    _top_plate_width,
    _bottom_plate_width,
    _element_total_length,
)
hb_material_, preview_ = gh_compo_interface.run()