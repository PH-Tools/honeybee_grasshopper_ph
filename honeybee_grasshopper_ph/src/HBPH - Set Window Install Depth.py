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
Set the install depth of a Honeybee-Aperture. This attribute is passed on to the 
"HBPH - Create Building Shading" tool, and is output directly for WUFI-Passive. 
The input value describes the distance 'back' in the host surface (wall, roof, etc) 
where the aperture is installed. This is relevant in Passive House buildings due to 
the typically very thick assemblies and the shading this causes on the glazing.
-
EM March 8, 2023
    Args:
        _install_depth: (float) The distance 'back' from the wall outer surface 
            where the aperture is installed.
    
        _hb_apertures: (list[Aperture]) A List of the Honeybee Apertures to set
            the attribute values on.
            
    Returns:
        hb_apertures_: The Honeybee Apertures with their attribute values set.
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
ghenv.Component.Name = "HBPH - Set Window Install Depth"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import win_set_inst_depth as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetApertureInstallDepth(
    IGH,
    _hb_apertures,
    _install_depth,
    )
hb_apertures_ = gh_compo_interface.run()