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
Set the WUFI Defaulty Monthly Shading Correction Factor. This is the value shown when 
you look at a specific Aperture component in WUFI, and look at the "Solar Protection"
tab, and then the "WUFI mean monthly shading factors". This value is used to set additional
shading correction factors beyond the normal physical shading elements which are already
calculated automatically by WUFI. Note that this component does not affect PHPP models at 
all and is only used for WUFI-Passive Models.
-
EM May 21, 2023
    Args:
        _apertures: (list[Aperture]) The list of HB-Apertures to set the 
            monthly shading correction factors on.
            
        _correction_factors: (List[float]]) The list of correction factors
            to apply to the Apertures. This list should ideally be in the same 
            order and the same length as the list of Apertures. If not, the first
            input value will be used for all the Apertures.
            
    Returns:
        hb_rooms_: The honeyee-Rooms with the PH Spaces added to them.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from honeybee_ph_rhino import gh_compo_io, gh_io

# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Set Monthly Shade Factor"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import win_set_monthly_shd_fac as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetWindowMonthlyShadeFactor(
    IGH,
    _apertures,
    _correction_factors,
    )
apertures_ = gh_compo_interface.run()