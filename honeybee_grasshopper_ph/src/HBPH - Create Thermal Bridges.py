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
Create a new HBPH Thermal Bridge object which can be added to an HB Model. Note that
these thermal bridges will have no effect on the EnergyPlus/OpenStudio simualtion and 
will only be considered when the model is exported to the PHPP/WUFI-Passive.
-
EM October 1, 2022

    Args:
        _names: (List[str]) A list of the HBPH Thermal Bridge names.
            
        _psi_values: (List[float]) The Psi-Values (W/mk) values to use. If 
            None are provied, default=0.1 W/mk
            
        _fRsi_values: (List[float]) The temperature-factor (fRsi) values. If 
            None are provided, default=0.75
        
        _lengths: (List[float]) The lengths (m). If None are provided, 
            default=0.0 m
            
        _types: (List[str]): Input either -
        - "15-Ambient" (default)
        - "16-Perimeter"
        - "17-FS/BC"
            
        _quantities: (List[float]): The number of times the bridge element occurs.
            
    Returns:
        thermal_bridges_: (List[PhThermalBridge]) A list of the new HBPH
            thermal bridge objects. These can be added to a Honeybee room
            using the "HBPH - Add Thermal Bridges" component.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from honeybee_ph_rhino import gh_io, gh_compo_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))

try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_utils:\t{}'.format(e))
    
#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Thermal Bridges"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev='OCT_01_2022')
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import tb_create as gh_compo_io
    reload(gh_compo_io)
    reload(preview)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateTB(
        IGH,
        _geometry,
        _names, 
        _psi_values,
        _fRsi_values,
        _types,
        _quantities,
    )
thermal_bridges_ = gh_compo_interface.run()
    
#-------------------------------------------------------------------------------
# -- Preview
for tb in thermal_bridges_:
    preview.object_preview(tb)