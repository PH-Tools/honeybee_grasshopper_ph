#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
#
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
#
# Copyright (c) 2026, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com>
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
Set the Psi-Install values of Honeybee-Energy Window-Constructons. These values represent
the additional heat-loss where the aperture conncects to the host surface.
-
EM March 13, 2026
    Args:

        _psi_install_values_w_mk: (DataTree[float]) The Psi-Install values to apply to the
            Honeybee-Energy Window Constructons. If only a single value is supplied, it will be
            applied to eeach of the Constructions. If a DataTree of values is applied, this
            component will try and match up the values with the items in the `_hb_apertures`
            input wherever possible.

        _hb_win_constructions: (DataTree[Apertures]) The Honeybee-Apertures to set the Psi-Install
            values of.

    Returns:

        hb_win_constructions_: The Honeybee-Energy Window-Constructions with the new
            Psi-Install values applied.
"""

import ghpythonlib.components as ghc
import Grasshopper as gh
import Rhino as rh
import rhinoscriptsyntax as rs
import scriptcontext as sc

try:
    from honeybee_ph_rhino import gh_compo_io
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("Failed to import ph_gh_component_io:\t{}".format(e))


# -------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Set HB-Construction Psi-Installs"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.apertures import win_set_hb_const_psi_install_values as gh_compo_io

    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)

# -------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SetWindowConstructionPsiInstallValues(
    IGH,
    _psi_install_values_w_mk,
    _hb_win_constructions,
)

hb_win_constructions_ = gh_compo_interface.run()
