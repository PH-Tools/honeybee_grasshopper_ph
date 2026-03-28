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
Convert an HBJSON file into a new METR-JSON file which can then be opened using
METR. This will read in the HBJSON, rebuild the HB-Model before converting the
Model into a METR-JSON file.
-
EM March 15, 2026
    Args:
        _filename: (str) The filename for the METR-JSON file.

        _save_folder: (str) The folder path to save the METR-JSON file to.

        _hb_json_file: (str) The path to the HBJSON file to convert into METR-JSON.

        _settings: The WUFI/METR Settings object. Connect the "HBPH - Write WUFI XML Settings"
            'settings_' output.

        _write_json: (bool) Set True to run.

    Returns:
        json_file_: The full path to the output METR-JSON file.
"""

import ghpythonlib.components as ghc
import Grasshopper as gh
import Rhino as rh
import rhinoscriptsyntax as rs
import scriptcontext as sc

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))


# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Write METR JSON"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev="260315")
if DEV:
    from PHX import run

    reload(run)
    from honeybee_ph_rhino.gh_compo_io import write_metr_json as gh_compo_io

    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)


# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_WriteMetrJson(
    IGH,
    _filename,
    _save_folder,
    _hb_json_file,
    _settings,
    _write_metr_json,
)
json_file_ = gh_compo_interface.run()
