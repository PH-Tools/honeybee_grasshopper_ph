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
Set the residential PH-Style occupancy for the Honeybee-Rooms input. For Phius, the 
total occupancy with be the number-of-bedrooms + 1 for each dwelling unit.
-
EM October 22, 2022
    Args:
        _name_: (str) The name of the Phius program to search the dataset for.
        
        description_: (Optional[str]) Search within the 'description' field of the Phius
            program data set instead of the name.
        
        protocol_: (Optional[str]) A sub-category "Protocol" to filter the Phius programs by. For
            instance - "PHIUS_MultiFamily" or "PHIUS_NonRes", etc...
            
        base_program_: (Optional[honeybee_energy.programtype.ProgramType]) A base program 
            to use for the Phius Program, to fill in any missing info (hot-water, gas, etc..)
            
    Returns:
        programs_ (List[honeybee_energy.programtype.ProgramType]) A list of the Honeybee
            ProgramTypes found in the Phius dataset which match the search criteria.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh


try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Phius Program Finder"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_energy_ph.library import programtypes
    reload(programtypes)
    reload(gh_io)
    from honeybee_ph_standards.programtypes import PHIUS_programs
    reload(PHIUS_programs)
    from honeybee_ph_rhino.gh_compo_io import prog_find_Phius_program as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_FindPhiusProgram(
        IGH,
        _name_,
        description_,
        protocol_,
        base_program_,
    )
programs_ = gh_compo_interface.run()