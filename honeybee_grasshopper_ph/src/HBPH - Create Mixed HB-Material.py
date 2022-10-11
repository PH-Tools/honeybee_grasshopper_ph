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
Create a new detailed "PH-Style" HB-Material layer made up of one or more materials. This is 
useful if you are trying to model things like wood studs in an insulation layer. This 
component will store the individual materials for later use in tools such as the PHPP, 
and will calculate and APPROXIMATE U-Factor for the heterogeneous layer for use in 
the Honeybe-Energy simulations. Note that this U-Factor is an approximation only.
-
Note: This calculator follows the 'Isothermal Plane' method outlined in ASHRAE HoF
chapter 25 / 27, and the ISO 6946. Note that this method is appropriate ONLY for 
materials with relatively low conductivity (insulation, wood, etc...) and materials 
such as steel (studs) or concrete cannot be accurately modeled using the calculator. 
For assemblies including steel studs or other high conductivity elements: follow the 
procedures in ASHRAE HoF Chapter 25 (Zone method), or use pre-calculated assembly U-Factors
from a source such as ASHRAE 90.1 - Appendix A. You can also calculate the effective
U-Factor of such assemblies using 2-D heat flow simulation tools such as THERM or Flixo.
-
EM October 6, 2022

    Args:
        __name_: (str)
        
        _section_1_material: (EnergyMaterial) An HB-Energy Opaque Material to use for the 
            first section.
            
        _section_1_percentage: (float) The percentage of the total assembly layer made up of 
            the section-1-material (when viewing the surface from the face). ie: If the 
            section material describes a 1.5" wood stud, spaced 16" on-center, then the material 
            represents 9.4% of the assembly (1.5"/16" = 0.094)
            - 
            NOTE- in general, leave this first percentage input BLANK unless you want to override
            for some reason. If this first input is blank, the tool will automatically calculate 
            the percentage based on the inputs from _section_2_percentage and _section_3_percentage -
            >> _section_1_percentage = 1.0 - _section_2_percentage - _section_3_percentage
            
        _section_2_material: (EnergyMaterial) An HB-Energy Opaque Material to use for the 
            first section.
            
        _section_2_percentage: (float) The percentage of the total assembly layer made up of 
            the section-2-material (when viewing the surface from the face). ie: If the 
            section material describes a 1.5" wood stud, spaced 16" on-center, then the material 
            represents 9.4% of the assembly (1.5"/16" = 0.094)     
        
        _section_3_material: (EnergyMaterial) An HB-Energy Opaque Material to use for the 
            first section.
            
        _section_3_percentage: (float) The percentage of the total assembly layer made up of 
            the section-3-material (when viewing the surface from the face). ie: If the 
            section material describes a 1.5" wood stud, spaced 16" on-center, then the material 
            represents 9.4% of the assembly (1.5"/16" = 0.094)     
            
    Returns:
        hb_material_: The new heterogeneous material which can be used as part of 
            a Honeybee-Energy Opaque Construction. 
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh


try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_utils:\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))

#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Mixed HB-Material"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv)
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_compo_io)
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import assmbly_create_mixed_mat as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateMixedHBMaterial(
        IGH, 
        _name_,
        _section_1_material,
        _section_1_percentage,
        _section_2_material,
        _section_2_percentage,
        _section_3_material,
        _section_3_percentage,
    )
hb_material_ = gh_compo_interface.run()