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
Create new PH-HVAC Hot Water Branch Piping Object.

A Branch will have one or more 'Fixture' pipes connected to it. Branch pipes are 
then connected to a 'Trunk' pipe. 
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 21, 20234

    Args:
        _dhw_fixture_piping: (List[PhPipeElement]) A list of the 'Fixture' (twig) pipes that should 
            be connected to this 'branch' line.
            
        _display_name: (Optional[str]) An optional name for the trunk line.
        
        _material: (str) Input either -
1-COPPER_M
2-COPPER_L
3-COPPER_K
4-CPVC_CTS_SDR
5-CPVC_SCH_40
6-PEX
7-PE
8-PEX_CTS_SDR
 
        _diameter: (str) Input either - 
3/8"
1/2"
5/8"
3/4"
1"
1-1/4"
1-1/2
2"

        _geometry: (List[Curve]): A list of curves representing the Hot-Water Branch
            Piping elements. Note that one new branch will be created from EACH curve input
            and EACH fixture input will be added to EACH branch line which may cause 
            double entry of the fixtures. If you are trying to build a single branch with 
            multiple segments, joing the curves together into a single polyline, or organize
            the fixture-piping into separate datatree-branches first.
            
    Returns:
        dhw_branch_piping_: (List[PhPipeBranch]) A list of the new HBPH Piping
            objects created. These branches can be added to an HBPH "Trunk" pipe object.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from honeybee_ph_rhino import gh_compo_io, gh_io
from honeybee_ph_utils import preview

#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create SHW Pipe | Branches"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io.shw import create_pipe_branches as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSHWBranchPipes(
        IGH,
        _dhw_fixture_piping,
        _display_name,
        _material,
        _diameter,
        _geometry,
    )
dhw_branch_piping_ = gh_compo_interface.run()
    
#-------------------------------------------------------------------------------
# -- Preview
for pipe in dhw_branch_piping_:
    preview.object_preview(pipe)
    
    