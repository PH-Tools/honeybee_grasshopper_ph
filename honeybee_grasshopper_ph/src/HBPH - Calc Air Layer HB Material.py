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
Create a new Honeybee-Energy "Air-Layer" material. This calculator will 
determine an equivalent conductivity based on the parameters input. The 
procedue implemented here follows the PHPP v9/10 which closely matches the 
ISO-6946-2017, Appendix D method. This material can be used in Honeybee
Constructions to approiximate the insulating effect of closed air-layers 
such as service caviies. 
- 
Note: This "Air-Layer" is only suitable for CLOSED air layers which 
are have a length AND width at least 10x the thickness, and which have less
thank 5 deg-K temperature change accross the layer.
-
EM April 1, 2023
    Args:
        _heat_flow_direction: Input either -
"1-Upwards"
"2-Horizontal"
"3-Downwards"
        
        _thickness: (mm) The thickness of the Air Layer
        
        _srfc_1_emissivity: (%) Default=0.9
        
        _srfc_2_emissivity: (%) Default=0.9
            
    Returns:
        marterial_: The new Honeybee-Energy Material.
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
ghenv.Component.Name = "HBPH - Calc Air Layer HB Material"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import assmbly_create_air_layer_mat as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_AirLayerMaterial(
    IGH, 
    _display_name,
    _heat_flow_direction,
    _thickness, 
    _srfc_1_emissivity,
    _srfc_1_emissivity
    )
material_ = gh_compo_interface.run()