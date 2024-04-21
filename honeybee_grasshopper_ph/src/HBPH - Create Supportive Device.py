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
PH-HVAC Supportive devices such as pumps and fans add energy use (and internal heat
gains) to a hb-room. This component will create new devices which can then be 
added to the HBPH Mechanical System. These devices will be used to add to the 
WUFI-Passive "Supportive Device / Auixilliary Energy" section in Systems / Distribution.
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 21, 2024
    Args:
        _display_name: (str) Name for the new PH-HVAC Supportive Device created
        
        _device_type: (str) The type of device. Input either -
4-Heat Circulation Pump
6-DHW Circulation Pump
7-DHW Storage Pump
10-Other / Custom 
               
        _device_quantity: (int) The number of devices to include.
            
        _inside: (bool) True if the device is inside the conditioned space and 
            will affect the overall internal heat gain rate.
            
        _energy_demand_W: (float) The Wattage of the device
        
        _yearly_runtime_kHrs: (float) The total annual runtime of the devide 
            expressed in kilo-hours (ie: 8,760 hrs/year = 8.760 kHrs/year)
        
    Returns:
        supportive_device_: A PH-HVAC Supportive Device which can be added to a 
            mechanical system.
"""

import ghpythonlib.components as ghc
import Grasshopper as gh
import Rhino as rh
import rhinoscriptsyntax as rs
import scriptcontext as sc

try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_utils:\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))


# -------------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Supportive Device"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import ghio_validators

    reload(ghio_validators)
    from honeybee_energy_ph.hvac import supportive_device

    reload(supportive_device)
    from honeybee_ph_rhino.gh_compo_io.hvac import create_supportive_device as gh_compo_io

    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSupportiveDevice(
    IGH, _display_name, _device_type, _device_quantity, _inside, _energy_demand_W, _yearly_runtime_kHrs
)
supportive_device_ = gh_compo_interface.run()

# -------------------------------------------------------------------------------------
preview.object_preview(supportive_device_)
