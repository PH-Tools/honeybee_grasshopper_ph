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
EM April 22, 2024
    Args:
        certification_program_: Input either -
            "1-Default"
            "2-PHIUS 2015"
            "3-PHIUS 2018"
            "4-Italian"
            "5-PHIUS 2018 CORE"
            "6-PHIUS 2018 ZERO"
            "7-PHIUS 2021 CORE"
            "8-PHIUS 2021 ZERO"
        
        building_category_type_: Input either -
            "1-Residential building" (default)
            "2-Non-residential building"
        
        building_use_type_: Input either - 
            "1-Residential" (default)
            "4-Office/Administrative building"
            "5-School"
            "6-Other"
            "7-Undefined/unfinished"
        
        building_status_: Input either -
            "1-In planning" (default)
            "2-Under construction"
            "3-Completed"
        
        
        building_type_: Input either -
            "1-New construction" (default)
            "2-Retrofit"
            "3-Mixed - new construction/retrofit"
        
        
        _PHIUS_annual_heating_demand_kWh_m2:
        
        _PHIUS_annual_cooling_demand_kWh_m2:
        
        _PHIUS_peak_heating_load_W_m2:
        
        _PHIUS_peak_cooling_load_W_m2:
        
    Returns:
        certification_: A New Phius Certification Settings object which can be 
            added to the "Building Sectio"
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
ghenv.Component.Name = "HBPH - Phius Certification"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.cert import Phius as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_PhiusCertification(
        IGH,
        certification_program_,
        building_category_type_,
        building_use_type_,
        building_status_,
        building_type_,
        _PHIUS_annual_heating_demand_kWh_m2,
        _PHIUS_annual_cooling_demand_kWh_m2,
        _PHIUS_peak_heating_load_W_m2,
        _PHIUS_peak_cooling_load_W_m2,
        _icfa_override,
    )

phius_certification_ = gh_compo_interface.run()


# -------------------------------------------------------------------------------------
preview.object_preview(phius_certification_)