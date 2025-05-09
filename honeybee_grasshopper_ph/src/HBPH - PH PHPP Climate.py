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
Set the PHPP Climate Data set to use from the PHPP pre-loaded libraries. This component 
will only affect the PHPP, not WUFI-Passive.
-
Note: be sure that the inputs match the text in the  PHPP library exactly. The easiest 
way to do that is to just open the PHPP, find the dataset you would like to use, and 
copy/past the text into a GH Panel.
-
EM October 2, 2022
    Args:
        _country_code: (str) default = "US-United States of America" Optional country-code
            that matches the PHPP datasets. Note: be sure that the input matches the text in the 
            PHPP library exactly. The easiest way to do that is to just open the PHPP, find the 
            dataset you would like to use, and copy/past the text into a GH Panel.
        
        _region_code: (str) default = "New York" Optional region/state-code
            that matches the PHPP datasets. Note: be sure that the input matches the text in the 
            PHPP library exactly. The easiest way to do that is to just open the PHPP, find the 
            dataset you would like to use, and copy/past the text into a GH Panel.
        
        _dataset_name: (str) default = "US0055b-New York" Optional metro / dataset -code
            that matches the PHPP datasets. Note: be sure that the input matches the text in the 
            PHPP library exactly. The easiest way to do that is to just open the PHPP, find the 
            dataset you would like to use, and copy/past the text into a GH Panel.

    Returns:
        phpp_climate_: A new HBPH PHPP Code object that can passed along to an "HBPH - Site" component.
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

# -------------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - PH PHPP Climate"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )
    
    
# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_PHPPCodes(
                IGH,
                _country_code,
                _region_code,
                _dataset_name,
            )

phpp_climate_ = gh_compo_interface.run()

# -------------------------------------------------------------------------------------
preview.object_preview(phpp_climate_)