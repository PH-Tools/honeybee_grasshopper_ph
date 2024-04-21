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
Create new PH-HVAC Hot-Water System. This system can serve one or more Honeybee Rooms 
using the 'Apply SHW System' component. 
-
NOTE: Each unique device in the system will only be added ONCE to the PHPP or 
WUFI-Passive model, regardless of how many rooms the System is applied to. If each room needs
to have its own equipment, build devices for each room separately.
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 21, 2024

    Args:
        
        _name_: [str] Text to set the name for the PhHotWaterSystem and to be
            incorporated into unique system identifier. If the name is not
            provided, a random name will be assigned.
        
        _tank_1_: [PhHvacHotWaterTank] A new Passive House hot-water storage tank to add to the System.
        
        _tank_2_: [PhHvacHotWaterTank] A new Passive House hot-water storage tank to add to the System.        
        
        _buffer_tank_: [PhHvacHotWaterTank] A new Passive House hot-water buffer tank to add to the System.
        
        _solar_tank_: [PhHvacHotWaterTank] A new Passive House Solar-thermal hot-water storage tank to add 
            to the System.
    
        _heaters: List[PhHvacHotWaterHeater] A list of any PH style HW-Heaters to add to the System.
    
        _distribution_piping: List[PhPipeTrunk] A list of PH-HVAC 'Trunk' pipes which are part of this
            system. These 'Trunks' should have branches and fixtures which will also become part 
            of this hot-water system. 
            -
            Note that you can also pass in 'Fixture' elements directly, and it 
            will automatically create a 0-length 'trunk' and 'branch' for each fixture.
        
        _num_tap_points_: (Optional[int]) Allows for manual setting of the number 
            of 'tap points' (faucets or sim.) in the system.
            
        _recirc_piping: List[PhPipeElement] A List of any Recirculation Piping elements to
            add to the System.
    
    Returns:
        hb_shw_: [PhHotWaterSystem] A new PH-HVAC Hot Water System object which can be applied 
            to one or more Honeybee Rooms using the 'Apply SHW System' component.
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


# -------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create SHW System"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io.shw import create_system as gh_compo_io

    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSHWSystem(
    IGH,
    _name_,
    _tank_1_,
    _tank_2_,
    _buffer_tank_,
    _solar_tank_,
    _heaters,
    _distribution_piping,
    _num_tap_points_,
    _recirc_piping,
)

hb_shw_ = gh_compo_interface.run()

# -------------------------------------------------------------------------------
if hb_shw_:
    preview.object_preview(hb_shw_)
