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
Create a new Honeybee Energy Program for a Single-Family-Home. 
-
Lighting, MEL, Hot-Water, and Occupancy:
    2014 Building America House Simulation Protocols
    E. Wilson, C. Engebrecht Metzger, S. Horowitz, and R. Hendron
    National Renewable Energy Laboratory
    https://www.nrel.gov/docs/fy14osti/60988.pdf
-
Infiltration: HB-Standard 'Average' 0.0003 m3/s-m2
- 
Ventilation: PH-Standard 0.4ACH
-
Setpoints: PH Standard- Heating=20C, Cooling=25C, Dehumid=60%RH
-
NOTE: This Program incluces ONLY Misc Electrical Loads. In order to add specific
Appliance loads (Refrigerator, Cooktop, etc.) either create and add the loads using 
a Honeybee 'Process Load' or use the 'HBPH - Create Residential Appliance' component.
-
EM January 22, 2025
    Args:

        _hb_rooms: (list[Room]) A list of the HB-Rooms to add the new 
            HBPH Supportive Devices to.

        _base_program: An optional ProgramType object that will be used as the
            starting point for the new ProgramType output from this component.
            This can also be text for the name of a ProgramType within the library
            such as that output from the "HB Search Program Types" component.

        _floor_area: (float): The reference floor area to use when determining the 
            load values to apply. In most cases this should the 'FFA' (finished floor area) /, 
            iCFA / TFA value representing the net-interior-floor-area.

        _num_bedrooms: (float) The total number of bedrooms for the group of HB Rooms input.
        
    Returns:
        program_: The new Honeybee-Energy Progam which can be applied to the Rooms.
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
ghenv.Component.Name = "HBPH - Create Program - Single Family Home"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.program import create_single_family as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
# -- Create the new Single-Family Home Program from the Rooms
gh_compo_interface = gh_compo_io.GHCompo_CreatePHProgramSingleFamilyHome(
    IGH,
    _base_program,
    _floor_area,
    _num_bedrooms,
    _hb_rooms,
)
program_ = gh_compo_interface.run()