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
Set the geographic location data for the Passive House model. 
-
Note: If none is supplied, the default values for NYC, USA will be used.
-
Note: This component will -*-NOT-*- reset any of the Honeybee EnergyPlus climate values, 
and you will need to set those separately using a normal EPW file with hourly data for any
Honeybee-Energy / OpenStudio simulations.
-
EM March 21, 2024
    Args:
        _display_name: (str) The display-name for the Location (default="New York")

        _latitude: (deg) default = 40.6 (NYC)
        
        _longitude: (deg) default = -73.8 (NYC)
        
        _site_elevation: (m) default = None. If None, the weather-station elevation will be 
            used as the site-elevation.
            
        _climate_zone: (str) For WUFI-Passive. Input either
1-Not defined (default)
11-US 1
12-US 2
13-US 3
14-US 4
141-US 4C
15-US 5
16-US 6
17-US 7
18-US 8
        _hours_from_UTC: (hours) For WUFI-Passive.

    Returns:
        location_: A new HBPH Location object which can be passed to an "HBPH - PH Site"
            component.
"""

import ghpythonlib.components as ghc
import Grasshopper as gh
import Rhino as rh
import rhinoscriptsyntax as rs
import scriptcontext as sc

try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_utils:\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))

# -------------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - PH Location"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import climate_location as gh_compo_io

    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)


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
