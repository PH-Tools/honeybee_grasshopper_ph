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
Create a new honeybee boundary-condition object which can be applied to one or more surfaces in a model.
For EnergyPlus/OpenStudio simulations, this component will apply a Honeybee-Energy 'Other Side Temp' 
boundary-condition, and for PH models this component will apply an 'Additional Zone' boundary-condition.
When this BC is applied, a new 'Attached Zone' will automatically be addded to the WUFI-Passive model.
-
This component follows the protocol as implementing in the Phius 'TRF' Calculator. For details, see:
https://www.phius.org/phius-temperature-reduction-factor-auxiliary-space-heating-estimator
-
EM January 7, 2026
    Args:

        _attached_zone_name: (str) A name for the Attached Zone.

        _attached_zone_temp_C: (float) Default=4.4°C (40°F) The drybulb-air-temp for the 
            attached zone. 

        _monthly_outdoor_air_drybulb_temps_C: (list[float]) A list of 12 outdoor drybulb air temperatures.
            
    Returns:
        bc_: (PhAdditionalZone) A new Boundary-Condition object which can be applied to one or 
            more surfaces using the standard Honeybee components such as 'HB Properties by Guide Surface'.
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
ghenv.Component.Name = "HBPH - PH Additional Zone"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_energy_ph import boundarycondition
    reload(boundarycondition)
    from honeybee_ph_rhino.gh_compo_io import addnl_zone as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_AdditionalZone(
        IGH,
        _attached_zone_name,
        _attached_zone_temp_C,
        _monthly_outdoor_air_drybulb_temps_C,
    )
bc_ = gh_compo_interface.run()