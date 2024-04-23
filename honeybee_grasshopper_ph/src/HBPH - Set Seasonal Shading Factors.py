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
Set the seasonal shading factors for HB-Apertures. This is common when using PHPP
and bringing in shading factors from another source such as DesignPH. If using DesignPH, 
you can also use the "HBPH+ - Get Shading Factors from DesignPH" component to generate 
the list of shading factors from copy/pasted text.
-
EM February 15, 2024
    Args:
        _hb_apertures: (List[Aperture]) A List of the Honeybee Apertures to set
            the attribute values on.

        _winter_shading_factors: (List[float]) A list of numeric (0.0-1.0) shading
            factors for the HB-Apertures. These values should represent the 
            %-exposed (unshaded) for the season (winter/summer) as per the PHI/PHPP methods.
            ie: 0.0 = fully shaded, 1.0=fully exposed (unshaded)

        _summer_shading_factors: (List[float]) A list of numeric (0.0-1.0) shading
            factors for the HB-Apertures. These values should represent the 
            %-exposed (unshaded) for the season (winter/summer) as per the PHI/PHPP methods.
            ie: 0.0 = fully shaded, 1.0=fully exposed (unshaded)

    Returns:
        hb_apertures_: The Honeybee Apertures with their winter and summer 
            shading factor values set.
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
ghenv.Component.Name = "HBPH - Set Seasonal Shading Factors"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import win_set_seasonal_shading_factors as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetWindowSeasonalShadingFactors(
    IGH,
    _hb_apertures,
    _winter_shading_factors,
    _summer_shading_factors,
    )
hb_apertures_ = gh_compo_interface.run()