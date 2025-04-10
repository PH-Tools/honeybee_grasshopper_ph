#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
# 
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
# 
# Copyright (c) 2025, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com> 
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
This component will read and extract all of the 'NON-Residential' Electric-Equipment Loads from a set of Honeybee-Rooms
in order to calculate the Phius Multi-Family NON-Residential Loads for Lighting 
and MEL. The calculations here align with the 'Phius Multifamily Calculator v24.0.2 | 2024 11'
> https://www.phius.org/phius-multifamily-lighting-misc-load-calculator
-
The results of this component can be passed to the "HBPH - Set Phius Multi-Family Non-Residential Room Loads"
in order to create the actual Equipment objects and add them to the Honeybee-Rooms.
-
EM April 8, 2025
    Args:

        _hb_rooms: (list[Room]) The Honeybee-Rooms to get the Non-Residential data from.

    Returns:

        program_data_: The non-residential Programs found in the Model, in text
            which an be copy/pasted into the Phius Multifamily Calculator.

        room_data_: The non-residential data for each room in the model, in text
            which an be copy/pasted into the Phius Multifamily Calculator.

        totals_: The Non-Residentital total energy consumption values (for checking 
            againt the Phius Multifamily Calculator)

        total_mel_: (kWh/a) The total annual Misc Electrical (MEL) energy consumption of all the Non-Residential
            Honeybee-Rooms input. This can be used to create a new MEL Equipment object
            which will match the values calculated by the Phius Multifamily Calculator.

        total_lighting_: (kWh/a) The total annual Lighting energy consumption of all the Non-Residential
            Honeybee-Rooms input. This can be used to create a new Lighting Equipment object
            which will match the values calculated by the Phius Multifamily Calculator.

        hb_rooms_: (list[Room]) The input Honeybee Rooms. Note that no modificiations have been made to the
            rooms, and no equipment has been added. In order to add electric-equipment to the model, use the 
            typical "HBPH - Add Process Equipment" or the "HBPH - Set Phius Multi-Family Non-Residential Room Loads".
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

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
ghenv.Component.Name = "HBPH - Get Phius Multi-Family Non-Residential Room Loads"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.program import get_phius_mf_nonres_data as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_GetPhiusMFNonResidentialLoadData(
    IGH,
    _hb_rooms,
)

(
    program_data_,
    room_data_,
    totals_,
    total_mel_,
    total_lighting_,
    hb_non_residential_rooms_,
) = gh_compo_interface.run()