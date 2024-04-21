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
Create a new PH-HVAC Ventilation System which can serve one or more HB-Rooms.
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 21, 2024
    Args:
        system_name_: (str) The name to give to the fresh-air ventilation system.
            
        system_type_: Choose either -
            1-Balanced PH ventilation with HR [Default]
            2-Extract air unit
            3-Only window ventilation
        
        vent_unit_: (Optional[]) The Venilator (ERV/HRV) to use to ventilate the
            honeybee-Rooms.
        
        duct_01_: The supply cold-air duct (from ventilator to the building-envelope)
        
        duct_02_: The exhaust cold-air duct (from ventilator to the building-envelope)
        
    Returns:
        vent_system_: The new PH-HVAC Ventilation System object.
"""

try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_utils:\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_compo_io
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))


# ---
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Ventilation System"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.hvac import create_vent_sys as gh_compo_io

    reload(gh_compo_io)

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateVentSystem(
    system_name_,
    system_type_,
    vent_unit_,
    duct_01_,
    duct_02_,
)
vent_system_ = gh_compo_interface.run()

# ------------------------------------------------------------------------------
preview.object_preview(vent_system_)
