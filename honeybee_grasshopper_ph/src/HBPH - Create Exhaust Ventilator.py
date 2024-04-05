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
Create a new HBPH Exhaust Ventilator for use in WUFI-Passive models. This device 
can be added to one or more rooms using the "HBPH - Add Exhaust Ventilator" component 
in order to simulate the  effect of direct exhaust ventilation without heat-recovery. 
This is useful for devices such as direct-vent dryers, kitchen hoods or other elements.
-
EM January 3, 2023
    Args:
        _name: (str) Name for the new HBPH Exhaust Ventilator
        
        _type: (str) The type of device. Input either -
        - "1-Dryer"
        - "2-Kitchen Hood"
        - "3-User Defined"
               
        _flow_rate_m3s: (float) The total m3/s of airflow from the exhaust 
            ventilation device.
            
        _annual_runtime_minutes: (float) Optional. If device type is 'User Defined'
            input the annual runtime (minutes).
        
    Returns:
        exhaust_vent_device_: An HBPH Exhaust Ventilator object which can be 
            added to one or more honeybee-rooms.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh


try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_utils:\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))
    
    
# -------------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Exhaust Ventilator"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_energy_ph.hvac import ventilation
    reload(ventilation)
    reload(gh_compo_io)
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
    reload(ghio_validators)
    from honeybee_ph_rhino.gh_compo_io import mech_create_exhaust_vent as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateExhaustVent(
        IGH, _name, _type, _flow_rate_m3s, _annual_runtime_minutes)
exhaust_vent_device_ = gh_compo_interface.run()

# -------------------------------------------------------------------------------------
preview.object_preview(exhaust_vent_device_)