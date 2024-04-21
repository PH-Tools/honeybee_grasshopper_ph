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
Create new PH-HVAC Hot Water Recirculation-Piping.
-
NOTE: Using the component will add ONLY the Passive House devices and will **NOT** add 
any components to the HB-Energy model. If you need to model mechancial equipment for an EnergyPlus
/ OpenStudio simulation then you must also use the Honeybee-Energy / IronBug components to setup
those devices separate from the inputs defined on the component here.
-
EM April 21, 2024

    Args:
        _geometry: (List[Curve]) A list of curves representing the SHW Recirculation
            Piping elements.
        
        _name: (List[str]) A list of names (Optional).
            
        _diameter: (List[float]) Default=0.0254m (1") A list of diameters (m) of 
            each DHW Recirculation Piping element input. If the length of this list matches 
            the _geometry input list, the diameter values will be used in order. 
            Otherwise the first element in this list will be used as the 
            default diameter for all pipe elements created.
            
        _insul_thickness: (List[float]) Default=0.0254m (1"). A list of thickness values
            for the pipe insulation. If the length of this list matches 
            the _geometry input list, the thickness values will be used in order. 
            Otherwise the first element in this list will be used as the 
            default thickness for all pipe elements created.
        
        _insul_conductivity: (List[float]) Default=0.04 W/mk (~R4/in). A list of conductivity values
            for the pipe insulation. If the length of this list matches 
            the _geometry input list, the conductivity values will be used in order. 
            Otherwise the first element in this list will be used as the 
            default conductivity for all pipe elements created.
            
        _insul_reflective: (List[bool]) Default=True. A list of boolean values
            for the pipe insulation. If the length of this list matches 
            the _geometry input list, the values will be used in order. 
            Otherwise the first element in this list will be used as the 
            default value for all pipe elements created.
        
        _insul_quality: (List[str]) The quality of the insulation installed at the 
            mountings, suspension elements, and other thermal-bridges.
            input either -
            - "0-None"
            - "1-Moderate"
            - "2-Good"
        
        _daily_period: (List[float]) The daily operating period in hours.
        
        _water_temp: (List[float]) The temp [C] of the water in the recirculation piping.
        
    Returns:
        dhw_recirc_piping_: (List[PhPipeElement]) A list of the new HBPH Piping
            objects created. These can be added to HB Rooms using the 'Add PH DHW Piping'
            component.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from honeybee_ph_rhino import gh_compo_io, gh_io
from honeybee_ph_utils import preview



#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create SHW Recirculation Pipes"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io.shw import create_recirc_pipes as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSHWRecircPipes(
    IGH,
    _geometry,
    _name,
    _diameter,
    _insul_thickness,
    _insul_conductivity,
    _insul_reflective,
    _insul_quality,
    _daily_period,
    _water_temp,
)
dhw_recirc_piping_ = gh_compo_interface.run()

#-------------------------------------------------------------------------------
# -- Preview
for pipe in dhw_recirc_piping_:
    preview.object_preview(pipe)