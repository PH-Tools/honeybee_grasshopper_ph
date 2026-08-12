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
Create a new 'Install Type' - a named window-installation condition (mid-wall, buried jamb,
party-wall, ...) with its Psi-Install value. Assign Install Types to aperture edges using an
'HBPH - Set Aperture Psi-Installs' component. A Psi-Install of 0.0 is the 'no install
thermal bridge' state. Create each condition once and re-use it across the project - the
same named type on many windows keeps the model easy to QA and never duplicates any
window constructions.
-
EM August 12, 2026
    Args:

        _display_name: (str) The name for the Install Type (ie: "Phius Mid-Wall",
            "Buried Jamb", "Party Wall"). If none is supplied, a content-keyed name is
            generated from the value.

        _psi_install: (str) The Psi-Install value. Accepts a bare number (W/mK is assumed)
            or a value with a unit (ie: "0.021 BTU/HR-FT-F").

        _source: (str) Optional free-text provenance note (ie: "Phius 1.4.4.6",
            "Flixo calc 2026-08-01").

    Returns:

        install_type_: The new PhApertureInstallType. Connect to an
            'HBPH - Set Aperture Psi-Installs' component.
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
ghenv.Component.Name = "HBPH - Create Aperture Install Type"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import win_create_install_type as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateApertureInstallType(
    IGH,
    _display_name,
    _psi_install,
    _source,
)

install_type_ = gh_compo_interface.run()
