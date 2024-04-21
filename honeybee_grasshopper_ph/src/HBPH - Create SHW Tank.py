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
Creates PH-HVAC Hot Water Tank which can be added to the a PH-HVAC Hot Water System.
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 21, 20224
    Args:
        _tank_type: ("0-No storage tank", "1-DHW and heating", "2-DHW only") The type of use for this tank.
        
        _name_: (str) The name / identifier for the hot water tank.
        
        quantity_: (int) Optional number of tanks. Default=1
        
        for_solar_: (bool) Is this tank hooked up to a Solar HW system?
        
        heat_loss_rate_: (W/k) Heat Loss rate from the tank. Default is 4.0 W/k
        
        volume_: (litres) Nominal tank volume. Default is 300 litres (80 gallons)
        
        standby_frac_: (%) The Standby Fraction. Default is 0.30 (30%)
        
        in_conditioned_space_: (bool) Default=True.
        
        location_temp_: (Deg C) The avg. air-temp of the tank location, if the tank is outside the building. 
        
        water_temp_: (Deg C) The avg. water temp in the tank. Default=60-C
    
    Returns:
        storage_tank_: A new HW Tank Object. You can add this tank to a Service Hot Water system.
"""

from honeybee_ph_utils import preview

# -------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
from honeybee_ph_rhino import gh_compo_io, gh_io

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create SHW Tank"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io.shw import create_tank as gh_compo_io

    reload(gh_compo_io)


# -------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSHWTank(
    _tank_type,
    _display_name_,
    quantity_,
    for_solar_,
    heat_loss_rate_,
    volume_,
    standby_frac_,
    in_conditioned_space_,
    location_temp_,
    water_temp_,
)
storage_tank_ = gh_compo_interface.run()


# ------------------------------------------------------------------------------
preview.object_preview(storage_tank_)
