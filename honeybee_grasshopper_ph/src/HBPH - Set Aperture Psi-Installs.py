#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
# 
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
# 
# Copyright (c) 2025, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com> 
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
Set the Psi-Install values of a Honeybee Aperture or set of Apertures. These values represent
the additional heat-loss where the aperture conncects to the host surface. 
-
EM October 9, 2025
    Args:

        _psi_installs_w_mk: (DataTree[float]) The Psi-Install values to apply to the 
            Honeybee-Apertures. If only a single value is supplied, it will be applied to 
            each of the Aperture PH-Frame Elements. If a DataTree of values is applied, this
            component will try and match up the values with the items in the `_hb_apertures`
            input wherever possible.

        _hb_apertures: (DataTree[Apertures]) The Honeybee-Apertures to set the Psi-Install
            values of. 

    Returns:

        hb_apertures_: The Honeybee-Apertures with the new Psi-Install values applied.    
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from honeybee_ph_rhino import gh_compo_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))


#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Set Aperture Psi-Installs"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import win_set_psi_install_values as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetAperturePsiInstallValues(
    IGH,
    _psi_installs_w_mk,
    _hb_apertures,
)

hb_apertures_ = gh_compo_interface.run()