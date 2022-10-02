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
Set the geographic location data for the Passive House model. Note: if none is supplied, the default
values for NYC, USA will be used.
-
Note also that this component will *NOT* reset any of the Honeybee EnergyPlus climate, and you will need to set
that separately using a normal EPW file with hourly data.
-
EM October 2, 2022
    Args:
        _latitude: (deg) default = 40.6 (NYC)
        
        _longitude: (deg) default = -73.8 (NYC)
        
        _site_elevation: (m) default = None. If None, the weather-station elevation will be 
            used as the site-elevation.
            
        _climate_zone: (int) For WUFI-Passive.
        
        _hours_from_UTC: (hours) For WUFI-Passive.

    Returns:
        location_: A new HBPH Location object which can be passed to an "HBPH - PH Site"
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
ghenv.Component.Name = "HBPH - PH Location"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_compo_io)
    reload(gh_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

    
# -------------------------------------------------------------------------------------
# -- Create the new Location Object
gh_compo_interface = gh_compo_io.GHCompo_Location(
        IGH,
        _display_name,
        _latitude,
        _longitude,
        _site_elevation,
        _climate_zone,
        _hours_from_UTC,
    )

location_ = gh_compo_interface.run()

# -------------------------------------------------------------------------------------
preview.object_preview(location_)