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
Sort a set of Honeybee-Objects (Rooms, Apertures, etc..) by their Z-Height. A new output branch will
be created for each set of hb-objects at that level. Use the '_tolerance' input 
to adjust if the groupings are not correct at first.
-
EM May 13, 2023
    Args:
        _hb_objects: (List) A List of HB-Objects (Rooms, Apertures) to sort by their Z-Height
        
        _tolerance: (float) Default=0.001
        
        _groups_: (Optional[int]) If a target number of groups is provided, will attempt
            to split the objects into that many groups.
        
        _steps: (Optional[DataTree[Domain]): Enter the 'steps' as domains (ie: "0 To 3", etc..)
            and the component will attempt to sort to objects into the specified steps. This 
            is especially useful if attemptinto sort 2 sets of objects with different bounds (
            (for instance, sorting a group of HB Rooms and a group of HB Apertures into the same
            groups). The 'steps_' output from one component can be input into a second in order 
            ensure that the groups maintain the same 'splitting' levels.
        
    Returns:
        hb_apertures_: (DataTree[Aperture]) The HB-Apertures, sorted by height.
        
        steps_: (DataTre[Domain]): The 'steps' used to group the HB-Objects. This output 
            can be input into another 'HBPH - Sort HB Objects by Level' if you are trying 
            to filtter two sets of objects into similar groups.
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
ghenv.Component.Name = "HBPH - Sort HB Objects by Level"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import util_sort_hb_objects_by_level as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_SortHbObjectsByLevel(
    IGH,
    _hb_objects,
    _tolerance,
    _groups,
    _steps,
    )
hb_objects_, steps_ = gh_compo_interface.run()