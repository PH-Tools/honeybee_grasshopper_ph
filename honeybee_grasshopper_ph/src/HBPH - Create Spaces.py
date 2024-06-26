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
Create new PH-Spaces. 
-
Spaces represent smaller units than HB-Rooms and can be made up of one or more individual 
volumes. This is useful if you are calculating interior net-floor-area or volume 
as in the Passive House models. Each Space will map to a single entry in the WUFI 
'Ventilation Rooms' or a PHPP 'Additional Ventilation'.
-
A single Space is made of one or more 'Volumes'. ie: a bedroom might have a volume for 
the main space, and another volume for the closet which is separated by the thicknes of 
a wall. 
-
Each Volume is made of one or more floor-segments. Each floor-segment can have a
'weighting factor' applied for calculating the TFA/iCFA for Passive House certification.
-
EM June 25, 2024
    Args:
        _flr_seg_geom: (Tree[Geometry]) The Rhino geometry that you would like to use 
            to create the Floor-Segments of the various Spaces. Each branch should be a list 
            of Rhino geometry objects that will be used to create a single new Space.
        
        _weighting_factors: (Tree[float]) An optional input Tree of TFA/iCFA weighting
            factors to apply to the input floor-segment geometry.
        
        _volume_heights: (Tree[float]) Default=2.5m An optional input Tree of heights
            to use when building the volume geometry.
        
        _volume_geometry: (Tree[Geometry]) An optional input Tree of Rhino Geometry
            describing the space-shape of the individual volumes. 
        
        _space_names: (Tree[float]) Default="_Unnamed_" An optional input Tree of names
            to use when building the spaces
        
        _space_numbers: Default="000" An optional input Tree of space numbers
            to use when building the spaces

        _space_ph_vent_rates: (Tree[SpacePhVentFlowRates]) An optional tree of detailed
            PH-Style space-level fresh air ventilaton flow rate objets. These can be created
            using the "HBPH - Create Space PH Ventilation" component or gotten directly 
            from the Rhino scene using the "HBPH - Get FloorSegment Data" component.

        _flr_seg_net_area: (Tree[float]) Optional input for 'net' (interior) floor area
            for the floor-segments. This 'net' area is used for the Phius Multifamily calculator
            since they insist on using net-area instead for that calculator, but gross area
            for their iCFA, but only for the non-residential zones like hallways. The
            input data here (branches, items, ...) should ideally match the structure of the
            the '_flr_seg_geometry' input. In none is input, the area of the '_flr_seg_geometry'
            will be used for both the gross and net floor areas.
    
    Returns:
        floor_breps_: Preview of the Space Floor geometry created. Useful for debugging.
        
        volume_breps_: Preview of the Space Volume geometry created. Useful for debugging.
        
        spaces_: The new PH-Spaces created. These can be added to Honeybee-Rooms.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from honeybee_ph_rhino import gh_io, gh_compo_io

# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Spaces"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import space_create_spc as gh_compo_io
    from honeybee_ph_rhino.make_spaces import make_floor, make_floor_segment
    from honeybee_ph import space
    reload(space)
    reload(make_floor_segment)
    reload(make_floor)
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
if _volume_geometry.BranchCount != 0:
    msg = " Sorry - Detailed input using '_volume_geometry' is not "\
            "implemented just yet. Coming soon."
    raise NotImplementedError(msg)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreatePHSpaces(
    IGH,
    _flr_seg_geom,
    _weighting_factors,
    _volume_geometry,
    _volume_heights,
    _space_names,
    _space_numbers,
    _space_ph_vent_rates,
    _flr_seg_net_areas,
    )
error_, floor_breps_, volume_breps_, spaces_ = gh_compo_interface.run()
