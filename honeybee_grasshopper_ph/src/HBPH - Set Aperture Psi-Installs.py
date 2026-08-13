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
Assign per-edge Psi-Install 'Install Types' to Honeybee Apertures. The install condition
(mid-wall, buried jamb, party-wall, ...) is a property of WHERE a window sits, not of the
window construction - so this component sets aperture-instance data and NEVER duplicates
the window construction. An edge with no Install Type assigned inherits the psi-install
value from the construction's PH Frame Element (the type default).
-
EM August 12, 2026
    Args:

        _install_types: (DataTree) The Install Types to assign, in top / right / bottom / left
            order (up to 4 items per branch). Accepts 'PhApertureInstallType' objects from an
            'HBPH - Create Aperture Install Type' component, or bare numbers / unit-strings
            (ie: "0.04" or "0.021 BTU/HR-FT-F") which are wrapped in anonymous content-keyed
            Install Types. Supply a single item to apply it to all four edges. Assign a
            zero-value Install Type to an edge to model 'no install thermal bridge' (ie: at
            a party-wall or a buried jamb). Branches are matched to the '_hb_apertures'
            branches wherever possible.

        _hb_apertures: (DataTree[Aperture]) The Honeybee-Apertures to assign the per-edge
            Install Types to.

    Returns:

        hb_apertures_: The Honeybee-Apertures with the Install Types assigned.
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
    _install_types,
    _hb_apertures,
)

hb_apertures_ = gh_compo_interface.run()
