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
Create a new PH-HVAC Ventilation Duct which can be added to a PH-HVAC Ventilation System.
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 21, 2024

    Args:
        _geometry: (List[Polyline Curves]) The Rhino Curves that describe the duct path.
            
        _display_name: (str) An optional name for the duct.
        
        _duct_type: Input either - 
"-Supply / outdoor air duct"
"2-Extract / Exhaust air duct"

        _insul_thickness: (float) Default=25.4 mm [1-inch] | The thickness (mm) of the duct insulation. 
        
        _insul_conductivity: (float) Default=0.04 W/mk | The conductivity (W/mk) of the duct insulation. 
        
        _insul_reflective: (bool) Default=True | If the insualtion has a reflective coating. 
        
        _diameter: (float) Default=160mm [6.2-inches] | The round-duct diameter (mm)
        
        _height: (Optional[float]) Default=None
        
        _width: (Optional[float]) Default=None
        
    Returns:
        
        vent_duct_: The new PH Ventilation Duct which can be added to a PH Ventilation System object.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from honeybee_ph_rhino import gh_compo_io, gh_io
from honeybee_ph_utils import preview

#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Ventilation Duct"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev="240419")
if DEV:
    reload(gh_io)
    from honeybee_energy_ph.hvac import ducting
    reload(ducting)
    from honeybee_ph_rhino.gh_compo_io.hvac import create_vent_duct as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateVentDuct(
        IGH,
        _geometry,
        _display_name,
        _duct_type,
        _insul_thickness,
        _insul_conductivity,
        _insul_reflective,
        _diameter,
        _height,
        _width,
    )
vent_duct_ = gh_compo_interface.run()
    
#-------------------------------------------------------------------------------
# -- Preview
preview.object_preview(vent_duct_)
