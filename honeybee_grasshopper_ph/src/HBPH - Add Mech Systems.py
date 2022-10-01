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
Add HBPH mechanical ventilation, heating, and cooling to HB-Rooms.
-
EM October 1, 2022
    Args:
        _vent_system: (PhVentilationSystem) Enter the type of heating system.
        
        _space_heating_systems: (list[PhHeatingSystem]) A list of the HBPH Heating Systems to add to the hb-rooms.
        
        _space_cooling_systems: (list[PhCoolingSystem]) A list of the HBPH Cooling Systems to add to the hb-rooms.
        
        _hb_rooms: (list[Room]) A list of the hb-rooms to add the mechanical systems to.
        
    Returns:
        hb_rooms_: The input hb-rooms with the new HBPH Mechanical Systems added.
"""

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))


#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Add Mech Systems"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev='OCT_01_2022')
if DEV:
    reload(gh_compo_io)
    reload(gh_io)


#-------------------------------------------------------------------------------
# -- Add the new Systems to the HB-Rooms
gh_compo_interface = gh_compo_io.GHCompo_AddMechSystems(
        _vent_system,
        _space_heating_systems,
        _space_cooling_systems,
        _hb_rooms,
    )
hb_rooms_ = gh_compo_interface.run()