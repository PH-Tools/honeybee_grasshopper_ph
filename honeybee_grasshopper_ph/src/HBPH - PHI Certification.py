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
Enter the relevant PHI PHPP configuration settings. Note that PHPP-9 and PHPP-10 
use different options, so enter the correct info for the version you will be 
writing your data to.
-
EM October 7, 2022
    Args:
        _phpp_version: Enter either "9" or "10" to configure the inputs for the
            PHPP version you will be writing to.
        
    Returns:
        phi_certification_: A new PHI Certifiction config object which can 
            be added to a "Building Segment" to control the PHPP settings.
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
ghenv.Component.Name = "HBPH - PHI Certification"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph import phi
    reload(phi)
    reload(gh_compo_io)
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import cert_PHI
    reload(cert_PHI)
    

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
# -- Setup the input nodes, get all the user input values
input_dict = gh_compo_io.cert_PHI.get_component_inputs(_phpp_version)
gh_io.setup_component_inputs(IGH, input_dict)
input_values_dict = gh_io.get_component_input_values(ghenv)

if DEV:
    from honeybee_ph_rhino.gh_compo_io import cert_PHI as gh_compo_io
    reload(gh_compo_io)


#-------------------------------------------------------------------------------
# -- Build the new PHI Settings object
gh_compo_interface = gh_compo_io.GHCompo_PhiCertification(
        IGH,
        _phpp_version,
        input_values_dict,
    )
phi_certification_ = gh_compo_interface.run()


# -------------------------------------------------------------------------------------
preview.object_preview(phi_certification_)