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
Input PH-Style monthly average temperature values for the air, dewpoint, sky and ground. This data 
will be used to configure the 'Climate' inputs in the Passive House models. Note that this data should
represent monthly average values. Information on climate data can be found at:
-
    - PHI: https://passipedia.org/planning/climate_data_tool
    - PHIUS: https://www.phius.org/climate-data
-
Note also that this component will *NOT* reset any of the Honeybee EnergyPlus climate, and you will need to set
that separately using a normal EPW file with hourly data.
-
EM October 2, 2022
    Args:
        _air_temps_: (List[float]) A list of 12 monthly air temperature values (deg. C). If none are 
            input, all values will be set to 0
        
        _dewpoints_: (List[float]) A list of 12 monthly dewpoint temperature values (deg. C). If none are 
            input, all values will be set to 0
            
        _sky_temps_: (List[float]) A list of 12 monthly sky temperature values (deg. C). If none are 
            input, all values will be set to 0
        
        _ground_temps_: (List[float]) A list of 12 monthly ground temperature values (deg. C). If none are 
            input, all values will be set to 0

    Returns:
        monthly_temps_: A new HBPH Monthly-Temps object which can be passed to an "HBPH - PH Climate Data"
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
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - PH Climate Monthly Temps"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_compo_io)
    reload(gh_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_MonthlyTemps(
        IGH,
        _air_temps_,
        _dewpoints_,
        _sky_temps_,
        _ground_temps_,
    )

monthly_temps_ = gh_compo_interface.run()


# -------------------------------------------------------------------------------------
preview.object_preview(monthly_temps_)