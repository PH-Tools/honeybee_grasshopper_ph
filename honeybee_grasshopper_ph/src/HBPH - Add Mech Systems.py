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
Add HBPH mechanical ventilation, heating, and cooling systems to the HB-Rooms.
-
EM November 1, 2023
    Args:
        _ventilation_system: (PhVentilationSystem) Enter the type of heating system.
        
        _space_conditioning_systems: (List) A list of the HBPH 'Space Conditioning' 
            (Heating/Cooling) Systems to add to the HB-Rooms. Use the 'HBPH - Create
            Space Conditioning System' component in order to create heating and cooling equipment.
        
        _supportive_devices: (List) A list of any HBPH Supportive Devices (extra pumps, fans, etc)
            to add to the hb-rooms.
        
        _hb_rooms: (List[Room]) A list of the hb-rooms to add the mechanical systems to.
        
    Returns:
        hb_rooms_: A copy of the hb-rooms input, with the new HBPH Mechanical Systems added.
"""

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))


# -------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Add Mech Systems"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import mech_add_mech_systems as gh_compo_io

    reload(gh_compo_io)


# -------------------------------------------------------------------------------
# -- Add the new Systems to the HB-Rooms
gh_compo_interface = gh_compo_io.GHCompo_AddMechSystems(
    _ventilation_system,
    _space_conditioning_systems,
    _supportive_devices,
    _hb_rooms,
)
hb_rooms_ = gh_compo_interface.run()
