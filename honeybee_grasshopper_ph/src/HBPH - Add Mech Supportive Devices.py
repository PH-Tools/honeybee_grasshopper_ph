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
Set the PH-HVAC mechanical Supportive Devices (fans, pumps, etc.) serving the HB-Rooms.
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 21, 2024
    Args:
        _supportive_devices: (list[PhSupportiveDevice]) One or more PH-HVAC Supportive 
            Devices (fans, pumps, etc.) which will serve the HB-Rooms
        
        _hb_rooms: (list[Room]) A list of the HB-Rooms to add the new 
            HBPH Supportive Devices to.
        
    Returns:
        hb_rooms_: The input hb-rooms with the new PH-HVAC Supportive Devices set.
"""

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Add Mech Supportive Devices"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.hvac import add_supportive_devices as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)


#-------------------------------------------------------------------------------
# -- Add the new HBPH Supportive Devices to the HB-Rooms
gh_compo_interface = gh_compo_io.GHCompo_AddMechSupportiveDevices(
        _supportive_devices,
        _hb_rooms,
    )
hb_rooms_ = gh_compo_interface.run()