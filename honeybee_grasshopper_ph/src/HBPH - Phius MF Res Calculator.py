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
Calculate the Phius Multifamily Elec. Equipment Residential values (MEL and Lighting). The results of this 
component should match the Phius Multifamily Calculator.
Note also that for this to work properly, each dwelling unit (apt) should be its own Honeybee-Room.
-
The resulting elec_equipment_ objects can be added to the Honeybee-Rooms by using a "Add PH Equipment"
component and passing them to the 'equipment_' inputs. Note that this component will only calcuate the values
in the Phius Multifamily Workbook. These include MEL, Interior-Lighting, Exterior-Lighting, and Garage-Lighting.
This does NOT include the other residential appliances (fridge, cooking, etc..). Be sure to add those 
to the Residential Honeybee-Rooms in addition to the elec_equipment_ created by this component.
-
EM January 22, 2025

    Args:
        int_light_HE_frac_: (float) default=1.0 | The % (0-1.0) of interior lighting
            that is 'high efficiency'
            
        ext_light_HE_frac_: (float) default=1.0 default=1.0 | The % (0-1.0) of exterior
            lighting that is 'high efficiency'
        
        garage_light_HE_frac_: (float) default=1.0 | The % (0-1.0) of garage lighting
            that is 'high efficiency'
        
        include_garage_: (bool) Default=False. Set to True to include the standard Phius
            garage lighting.
        
        include_elevator_: (bool) Default=False. Set to True to include the standard Phius Elevator
            which is based on the number of stories. (<=6-stories Hyrdaulic, <=20-stories Geared Traction, 21+stories Gearless Traction)
-
The calculator will follow the protocol outlined in the Phius Multi-Family Calculator to estimate
elevator energy usage based on the total height of the building (num stories) and the total 
number of dwelling units. For more information, see:
https://www.energystar.gov/sites/default/files/asset/document/ENERGY_STAR_MFNC_Simulation_Guidelines_AppG2016_Version_1_Rev01.pdf

   
        _hb_rooms: (list[room.Room]): A list of the Honeybee Rooms to calculate the Phius Multifamily 
            Elec. Equipment for. 
            
    Returns:
        res_data_by_story_: (For Error-Checking) This is the input data for the residential stories. This 
            data can be copy/pasted into the Phius MF Claculator "Dwelling Units" B5 for vertification.
        
        res_totals_: (For Error-Checking) This is the computed residential story energy consumption. This
            data should match the values computed in the Phius MF Calculator "Dwelling Units" Columns J:N
            
        non_res_program_data_: (For Error-Checking) This is the input data for the non-residential programs
            found on the Honeybee-Rooms. This can be copy/pasted into the Phius MF Calculator worksheet 
            "Common Areas" "Default Space Types" section for verification.
        
        non_res_room_data_: (For Error-Checking) This is the input data for the non-residential spaces found
            in the Honeybee-Rooms. This can be copy/pasted intpo the Phius MF Calculator worksheet "Common Areas"
            "Rooms Table" section for verification.
        
        non_res_totals_: (For Error-Checking) This is the computed non-residential room energy consumption. This
            data should match the values computed in the Phius MF Calculator worksheet "Common Areas" columns H:M
            
        elec_equipment_: The PH-Electric Equipment objects for the MEL, Interior-Lighting, Exterior-Lighting 
            and Garage-Lighting. This equipment can be added to the Honeybee-Rooms by using an 'Add PH Equipment'
            component and passing these objects into the 'equipment_' input node.
            
        hb_res_rooms_: The residential HB-Rooms.
        
        hb_nonres_rooms_: The non-residential HB-Rooms.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))

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
ghenv.Component.Name = "HBPH - Phius MF Res Calculator"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_energy_ph.load import ph_equipment
    reload(ph_equipment)
    reload(gh_compo_io)
    reload(gh_io)
    from honeybee_energy_ph.load import phius_mf
    reload(phius_mf)
    from honeybee_ph_rhino.gh_compo_io.program._deprecated_ import phius_MF_calc as gh_compo_io
    reload(gh_compo_io)


# -------------------z-----------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CalcPhiusMFLoads(
        IGH,
        int_light_HE_frac_,
        ext_light_HE_frac_,
        garage_light_HE_frac_,
        include_elevator_,
        _hb_rooms,
        include_garage_,
    )

(
    res_data_by_story_, res_totals_, non_res_program_data_, non_res_room_data_,
    non_res_totals_, elec_equipment_, hb_res_rooms_, hb_nonres_rooms_ 
) = gh_compo_interface.run()