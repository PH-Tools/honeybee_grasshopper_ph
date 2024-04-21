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
Create new PH-HVAC Hot-Water 'Trunk' Piping Object.

A 'Trunk' pipe will have one or more 'Branch' pipes connected to it. Trunk pipes are 
addded directly to a PH-HVAC Hot Water System.
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 21, 2024

    Args:
        _dhw_branches: (List[PhPipeBranch]) A list of the 'Branch' pipes that should 
            be connected to this 'trunk' line.
            
        _multiplier: (List[int]) default=1. A list of multiplier values. In WUFI, this will set the 
            'Count Units or floors" attribute for the trunk. This is useful if you want to 
            model one floor's set of fixture/branches and then use the multiplier to 
            set the number of identical floors with the same fixtures.
            
        _display_name: (Optional[str]) An optional name for the trunk line.
        
        _demand_recirculation: (bool) Default=False. Mark true if this line includes
            demand-bassed recirculation of hot-water.
        
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

        _geometry: (List[Curve]): A list of curves representing the Hot-Water Trunk
            Piping elements. Note that one new trunk will be created from EACH curve input
            and EACH branch input will be added to EACH trunk line which may cause 
            double entry of the branches. If you are trying to build a single trunk with 
            multiple segments, joing the curves together into a single polyline, or organize
            the branch-piping into separate datatree-branches first.
            
    Returns:
        dhw_trunk_piping_: (List[PhPipeTrunk]) A list of the new HBPH Trunk Pipe
            objects created. These can be added to an HBPH-SHW System.
"""

import ghpythonlib.components as ghc
import Grasshopper as gh
import Rhino as rh
import rhinoscriptsyntax as rs
import scriptcontext as sc
from honeybee_ph_utils import preview

# -------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
from honeybee_ph_rhino import gh_compo_io, gh_io

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create SHW Pipe | Trunks"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io.shw import create_pipe_trunks as gh_compo_io

    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)

# -------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSHWTrunkPipes(
    IGH,
    _dhw_branches,
    _multiplier,
    _display_name,
    _demand_recirculation,
    _material,
    _diameter,
    _geometry,
)
dhw_trunk_piping_ = gh_compo_interface.run()

# -------------------------------------------------------------------------------
# -- Preview
for trunk in dhw_trunk_piping_:
    preview.object_preview(trunk)
