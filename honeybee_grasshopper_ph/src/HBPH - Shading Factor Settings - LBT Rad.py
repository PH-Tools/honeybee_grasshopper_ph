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
Settings and parameter values used when calculating the Window Shading Factors
using the Passive House LBT-Radiation solver.
-
EM October 2, 2022
    Args:
        _epw_file: The EPW file to use to generate the sky-matrix objects.
        
        north_: Optional North Vetor or angle.
        
        _winter_sky_matrix: Optional winter-period Ladybug Sky Matrix. Default
            if None is supplied is October 1 - March 31
            
        _summer_sky_matrix: Optional summer-period Ladybug Sky Matrix. Default
            if None is supplied is June 1 - September 30
            
        _window_mesh_settings_: Optional Rhino Mesh Settings for the window 
            surface geometry. Use this if you want to controlexactly how the 
            window surfaces are gridded for analysis. For instance, if you supply a 
            Grasshopper Mesh Settings Custom, and set the "Min" and "Max" to "16", 
            you will always get exactly 16 segments for your analysis, which can 
            then be used to match other tools like DesignPH.
            
        _shading_mesh_setings: Optional Rhino Mesh settings for the shading geometry. 
            default = Rhino.Geometry.MeshingParameters.Default
            
        _grid_size: default=1.0
            
        _legend_par_: Optional Ladybug legend parameter object to control the 
            output visualizations.
            
        _cpus_: (int) Optional. The number of computer CPUs to use to calculate the result.
    
    Returns:
        settings_: The new HBPH Settings which are used to configure the LBT-Radiation
            shading solver.
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
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Shading Factor Settings - LBT Rad"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import shade_LBT_rad_settings as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateLBTRadSettings(
        IGH,
        _epw_file,
        _north_,
        _winter_sky_matrix_,
        _summer_sky_matrix_,
        _shading_mesh_settings_,
        _grid_size_,
        _legend_par_,
        _cpus_,
        _window_mesh_settings_,
    )
settings_ = gh_compo_interface.run()


# ------------------------------------------------------------------------------  
preview.object_preview(settings_)