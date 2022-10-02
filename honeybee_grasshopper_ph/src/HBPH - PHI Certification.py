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
Enter the relevant Phius Certification threshold data for the building-segment.
-
EM October 2, 2022
    Args:
        _building_category_type: Input either -
            "1-Residential building" (default)
            "2-Non-residential building"
        
        _building_use_type: Input either - 
            "10-Dwelling" (default)
            "11-Nursing home / students"
            "12-Other"
            "20-Office / Admin. building"
            "21-School"
            "22-Other"
            
        _ihg_type: Input either-
            "2-Standard" (default),
            "3-PHPP calculation ('IHG' worksheet)",
            "4-PHPP calculation ('IHG non-res' worksheet)",
            
        _occupancy_type: Input either-
            "1-Standard (only for residential buildings)",
            "2-User determined",
        
        _certification_type: Input either -
            "1-Passive House" (default)
            "2-EnerPHit"
            "3-PHI Low Energy Building"
            "4-Other"

        _certification_class: Input either -
            "1-Classic" (default)
            "2-Plus"
            "3-Premium"

        _primary_energy_type: Input either -
            "1-PE (non-renewable)"
            "2-PER (renewable)" (default)

        _enerphit_type: Input either -
            "1-Component method"
            "2-Energy demand method" (default)

        _retrofit: Input either -
            "1-New building" (default)
            "2-Retrofit"
            "3-Step-by-step retrofit"

    Returns:
        phi_certification_: The PHI Certification Settings object to 
            assign to one or more Building Segments.
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
ghenv.Component.Name = "HBPH - PHI Certification"
DEV = True
honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev='OCT_02_2022')
if DEV:
    reload(gh_compo_io)
    reload(gh_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_PhiCertification(
        IGH,
        _building_category_type,
        _building_use_type,
        _ihg_type,
        _occupancy_type,
        _certification_type,
        _certification_class,
        _primary_energy_type,
        _enerphit_type,
        _retrofit,
    )

phi_certification_ = gh_compo_interface.run()


# -------------------------------------------------------------------------------------
preview.object_preview(phi_certification_)