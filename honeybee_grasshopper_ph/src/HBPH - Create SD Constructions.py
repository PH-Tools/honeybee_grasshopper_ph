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
Create new "SD-Level" Honeybee-Energy Constructions. This component takes a simple 
list of names and U-Values (W/m2-k) and builds up new Honeybee-Energy Mateials and Constructions
from them. This is useful during early stages of design when you might not know the
actual constructions or materials yet, but you would like to test various U-Values 
to guage the impact.
- -
This component will create new Constructions which have three layers:
1) A "Mass Layer" on the outside
2) A No-Mass layer in the middle
3) A "Mass Layer" on the inside
- -
This method uses the steps and attributes outlined in:
* https://www.youtube.com/watch?v=XSFHdPHJ7zA
* https://bigladdersoftware.com/epx/docs/8-7/engineering-reference/conduction-through-the-walls.html#conduction-transfer-function-ctf-calculations-special-case-r-value-only-layers
-
EM October 6, 2022

    Args:
        _const_names: (List[str]) A list of the Construction names to use.
        
        _u_values: (List[float]) A list of the Construction U-Values (W/m2-k) to use.
        
    Returns:
        hb_constructions_: (List[OpaqueConstruction]) A List of the new Honeybee-Energy
            Constructions created with the simplified whole-assembly U-Values.
"""

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))


#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create SD Constructions"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv)
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_compo_io)
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import assmbly_create_sd_const as gh_compo_io
    reload(gh_compo_io)

    
# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSDConstructions(
        _const_names,
        _u_values,
    )
hb_constructions_ = gh_compo_interface.run()