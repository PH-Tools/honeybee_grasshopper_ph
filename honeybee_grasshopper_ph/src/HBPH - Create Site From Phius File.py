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
Create a new PH-Site object with all the relevant attributes and data based on
a Phius climate-data file (.TXT). For information on Phius climate data files and to 
download climate data, see:
https://www.phius.org/climate-data-sets
-
EM March 21, 2024
    Args:
        _source_file_path: (str) Input the full path to the Phius climate file you would 
            like to read in. Note: use only the 'TXT' files.
            
        _site_elevation: (float) The site's elevation (m). 
            If none provided, the station elevation will be used.
        
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

    Returns:
        site_: A new PHX-Site object with all the relevant Phius climate and location
            data for the site specified. This PHX-Site object can be added to a 
            "PHX-Building Segment."
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
ghenv.Component.Name = "HBPH - Create Site From Phius File"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import climate_site_from_phius_file as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSiteFromPhiusFile(
        IGH,
        _source_file_path,
        _site_elevation,
        _climate_zone
    )

site_ = gh_compo_interface.run()


# -------------------------------------------------------------------------------------
preview.object_preview(site_)