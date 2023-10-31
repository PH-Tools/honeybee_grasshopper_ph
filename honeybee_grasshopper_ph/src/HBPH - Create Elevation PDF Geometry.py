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
Generate PDF-Report geometry and notes for Elevation views. This component 
will read through the Honeybee-Model and pull out relevant data and prepare 
it for export using the "HBPH - Export PDFs" component. If you would like to 
print this geometry to multiple Layouts (multiple views, etc..) then use the 
'_branch_count' input to create multiple identical branches of the geometry 
which can then be passed to the 'Export PDF' component.
-
EM October 22, 2023
    Args:
        _hb_model: The Honeybee-Model object to build the PDF Geometry from.
            
        _surface_color: (default=White) A color to use when printing the surfaces to PDF.

        _line_color: (default=Black) A color to use when printing surface edges to PDF.
            
        _lineweight: (default=Black) A list of colors to use when printing the surface edges.

        _branch_count: (int) The number of geom branches to output. The component will copy the 
            same geometry objects to each branch. This is required since the 'Export PDFS' component
            will want the geometry organized into branches that match the layout pages being printed.
        
    Returns:
        geom_: (List[Mesh | Curve]) A list of PDF-ready Geometry which can be passed
            to the '_geom' input of the 'Export PDFs' HBPH Component.
        
        geom_attributes_: (List[Rhino.DocObjects.ObjectAttributes]) A list of Rhino Object 
            Attributes (color, etc) which can be passed to the '_geom_attributes' input 
            of the 'Export PDFs' HBPH Component.
            
        aperture_names_: (List[str]) All of the HB-Model aperture names. These are useful if
            you want to add TextAnnotations to the elevations views with the ap-names.
            
        aperture_planes_: (List[Plane]) All of the HB-Aperture Planes, which can be passed to 
            a TextAnnotation '_location' input in order to position the Text objects in the 3D Scene.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('Failed to import honeybee_ph_rhino:\t{}'.format(e))


#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Elevation PDF Geometry"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:    
    from honeybee_ph_rhino.reporting import annotations
    reload(annotations)
    reload(gh_io)
    from honeybee_ph_rhino.reporting import build_elev_surfaces as gh_compo_io
    reload(gh_compo_io)
    

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

    
#-------------------------------------------------------------------------------
# -- Create the new Rhino Geometry Attributes
gh_compo_interface = gh_compo_io.GHCompo_CreateElevationPDFGeometry(
        IGH,
        _hb_model,
        _surface_color,
        _line_color,
        _lineweight,
        _branch_count,
    )
error_, geom_, geom_attributes_, aperture_names_, aperture_planes_ = gh_compo_interface.run()
