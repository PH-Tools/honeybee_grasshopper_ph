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
Collects and organizes data for a PH-HVAC Ventilator Unit (HRV/ERV). Used as part of a 
PH-HVAC Ventilation System.
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 23, 2024
    Args:
        display_name_: (Optional[float]) The name of the Ventilator (ERV/HRV) Unit.
        
        sensible_hr_: (Optional[float]) Input the Ventialtion Unit's Heat Recovery %. Default is 75% 
        
        latent_hr_: (Optional[float]) Input the Ventialtion Unit's Moisture Recovery %. Default is 0% (HRV)
        
        elec_efficiency_: (Optional[float]) Input the Electrical Efficiency of the Ventialtion 
            Unit (W/m3h). Default is 0.55 W/m3h
        
        frost_protection: (bool): Unit requires frost-protection? Default=True. 
        
        frost_temp_: (Optional[float]) Min Temp [C] for frost protection to kick in. [deg.  C]. Default is -5 C
        
        inside_: (bool) Unt is installed inside the conditioned space? Default=True
    
    Returns:
        unit_: A Ventilator object for the Ventilation System. Connect to the 
            'ventUnit_' input on the 'Create Vent System' to build a PH-Style Ventilation System.
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
ghenv.Component.Name = "HBPH - Ventilator"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io.hvac import create_ventilator as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreatePhVentilator(
        IGH,
        display_name_,
        sensible_hr_,
        latent_hr_,
        elec_efficiency_,
        frost_protection_,
        frost_temp_,
        inside_,
    )
unit_ = gh_compo_interface.run()

# ------------------------------------------------------------------------------
preview.object_preview(unit_)