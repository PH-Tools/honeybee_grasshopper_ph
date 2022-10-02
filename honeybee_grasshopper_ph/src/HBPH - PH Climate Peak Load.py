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

Input for PH-Style 'Peak-Load' case. For PH Certification, two peak-load cases are evaluated for 
heating, and 2 for cooling. These cases represent daily average values and take into account both 
air-temp as well as solar radiation. This data will be used to configure the 'Climate' inputs in 
the Passive House models. Information on climate data can be found at:
-
    - PHI: https://passipedia.org/planning/climate_data_tool
    - PHIUS: https://www.phius.org/climate-data
-
Note also that this component will *NOT* reset any of the Honeybee EnergyPlus climate, and you will need to set
that separately using a normal EPW file with hourly data.
-
EM October 2, 2022
    Args:
        _display_name: (str) Optional display-name
        
        _temp: (float) An air-temp value (deg-C) value for the peak-load case. If 
            none is input, values will be set to 0.
            
        _rad_north: (float) A NORTH Radiation value (kWh/m2) value for the peak-load case. If 
            none is input, values will be set to 0.     
        
        _rad_east: (float) An EAST Radiation value (kWh/m2) value for the peak-load case. If 
            none is input, values will be set to 0.     
        
        _rad_south: (float) A SOUTH Radiation value (kWh/m2) value for the peak-load case. If 
            none is input, values will be set to 0.     
        
        _rad_west: (float) A WEST Radiation value (kWh/m2) value for the peak-load case. If 
            none is input, values will be set to 0.     
        
        _rad_global: (float) A GLOBAL Radiation value (kWh/m2) value for the peak-load case. If 
            none is input, values will be set to 0.     
                     
        _dewpoint_temp_: (float) A dewpoint temperature value (deg-C) value for the peak-load case. If 
            none is input, values will be set to None.  
        
        _ground_temp_: (float) A ground temperature value (deg-C) value for the peak-load case. If 
            none is input, values will be set to None.    
            
        _sky_temp_: (float) A sky temperature value (deg-C) value for the peak-load case. If 
            none is input, values will be set to None.    
                   
    Returns:
        peak_load_: A new HBPH Peak-Load object which can be passed to an "HBPH - PH Climate Data"
            component.
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

# -------------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - PH Climate Peak Load"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev='OCT_02_2022')
if DEV:
    reload(gh_compo_io)
    reload(gh_io)
    

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreatePeakLoad(
        IGH,
        _display_name,
        _temp,
        _rad_north,
        _rad_east,
        _rad_south,
        _rad_west,
        _rad_global,
        _dewpoint_temp_,
        _ground_temp_,
        _sky_temp_,
    )

peak_load_ = gh_compo_interface.run()

# -------------------------------------------------------------------------------------
preview.object_preview(peak_load_)