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
a Phius climate-data file. For information on Phius climate data files and to 
download cliamte data, see:
https://www.phius.org/climate-data-sets
-
EM October 18, 2022
    Args:
        _source_file_path: Input the full path to the Phius climate file you would 
            like to read in. Note: use only the 'TXT' files.
        
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
    raise ImportError('Failed to import honeybee_ph_utils:\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))


#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH -  Create Site From Phius File"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_compo_io)
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import climate_site_from_phius_file as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSiteFromPhiusFile(
        IGH,
        _source_file_path
    )

site_ = gh_compo_interface.run()


# -------------------------------------------------------------------------------------
preview.object_preview(site_)