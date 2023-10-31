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
Create artbitrary PDF-Ready geometry and geometry-attributes from Rhino Geometry. 
The Mesh, Curve, and ObjectAttruibutes created can by this component can be passed 
into the HBPH 'Export PDFs' object for printing to PDF.
-
EM October 23, 2023
    Args:
        _geom: List[Brep] A list of Brep objects which will be printed to PDF.
            
        _surface_colors: (default=White) A list of colors to use when printing the surfaces to PDF.
            If only one color is supplied, it will be used for all the surfaces in the PDF.
            
        _line_colors (default=Black) A list of colors to use when printing the surface-edges to PDF.
            If only one color is supplied, it will be used for all the lines in the PDF.
            
        _lineweights: (default=Black) A list of lineweights to use when printing the surface-edges. If
            only one lineweight is supplied, it will be used for all the lines in the PDF.
        
    Returns:
        geom_: List[Mesh | Curve] A list of PDF-ready Geometry which can be passed
            to the '_geom' input of the 'Export PDFs' HBPH Component.
        
        geom_attributes_: List[Rhino.DocObjects.ObjectAttributes] A list of Rhino Object 
            Attributes (color, etc) which can be passed to the '_geom_attributes' input 
            of the 'Export PDFs' HBPH Component.
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
ghenv.Component.Name = "HBPH - Create PDF Geometry"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.reporting import build_pdf_geom_and_attrs as gh_compo_io
    reload(gh_compo_io)
    

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

    
#-------------------------------------------------------------------------------
# -- Create the new Rhino Geometry Attributes
gh_compo_interface = gh_compo_io.GHCompo_CreatePDFGeometryAndAttributes(
        IGH,
        _geom,
        _surface_colors,
        _line_colors,
        _lineweights,
    )
geom_, geom_attributes_ = gh_compo_interface.run()
