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
EM September 7, 2022
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

from honeybee_ph import site
from honeybee_ph_rhino.gh_compo_io import ghio_climate
from honeybee_ph_utils import preview

# -------------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - PH Location"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev='SEP_07_2022')

if DEV:
    reload(site)
    reload(ghio_climate)
    reload(preview)
    
# -------------------------------------------------------------------------------------
# -- Create the new Location Object
ILocation_ = ghio_climate.ILocation(
        _display_name,
        _latitude,
        _longitude,
        _site_elevation,
        _climate_zone,
        _hours_from_UTC,
    )

location_ = ILocation_.create_hbph_obj()

# -------------------------------------------------------------------------------------
preview.object_preview(location_)