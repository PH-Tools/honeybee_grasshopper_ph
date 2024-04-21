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
Set the shading 'reveal' distance ('d_reveal') of a Honeybee-Aperture. This attribute is
output directly for WUFI-Passive models as: 
    "Component > Solar Protection > General > Distance from edge of glazing to reveal". 
- 
The input value describes the horizontal distance from the edge of the glazing to the 
shading element. 
-
If this value is not set, the face-width of the window frame will be used
as the default for all Apertures.
-
EM December 19, 2023
    Args:
        _reveal_distance: (float) The horizontal distance from the 
            glazing edge to the shading element.
    
        _hb_apertures: (list[Aperture]) A List of the Honeybee Apertures to set
            the attribute values on.
            
    Returns:
        hb_apertures_: The Honeybee Apertures with their attribute values set.
"""

import ghpythonlib.components as ghc
import Grasshopper as gh
import Rhino as rh
import rhinoscriptsyntax as rs
import scriptcontext as sc

# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
from honeybee_ph_rhino import gh_compo_io, gh_io

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Set Window Reveal Distance"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import win_set_reveal_distance as gh_compo_io

    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetApertureRevealDistance(
    IGH,
    _reveal_distance,
    _hb_apertures,
)
hb_apertures_ = gh_compo_interface.run()
