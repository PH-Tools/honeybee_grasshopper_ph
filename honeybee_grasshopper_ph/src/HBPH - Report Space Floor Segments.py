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
Generate PDF-Report geometry and notes for Floor-Plan views of either the 
TFA/iCFA or Fresh-air ventilation data. This component will read through the 
Honeybee-Model and pull out relevant data and prepare it for export using
the "HBPH - Export PDFs" component.
-
EM October 22, 2023
    Args:
        _hb_model: (honeybee.model.Model) The honeybee Model to use as the source.
        
        _type: (int) Input either -
            - 1 (TFA / iCFA) [default]
            - 2 (Ventilation)
        
        _units_: (str) Default=SI. Units type to output. Input either -
            - "SI" (default)
            - "IP"
            
        _flr_anno_txt_size: (float) Default=1.0 The size of the annotation text.

    Returns:
        floor_names_: A Tree of the floor/story-names found.
            
        clipping_plane_locations_: A Tree of the clipping plane locations.
            
        floor_geom_: A Tree of the geometry.
            
        floor_rh_attributes_: A Tree of the geometry ObjectAtrributes.
            
        floor_annotations_: A Tree of TextAnnotations.
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

# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Report Space Floor Segments"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.reporting import annotations
    reload(annotations)
    reload(gh_io)
    from honeybee_ph_rhino.reporting import build_floor_segments as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateFloorSegmentPDFGeometry(
        IGH,
        _hb_model,
        _type,
        _units_,
        _flr_anno_txt_size,
        )

(floor_names_, clipping_plane_locations_, floor_geom_,
        floor_rh_attributes_, floor_annotations_) = gh_compo_interface.run()