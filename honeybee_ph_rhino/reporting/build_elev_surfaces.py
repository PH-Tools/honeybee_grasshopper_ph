# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Create the 'Elevation' Geometry for Export to PDF. """

import math
from collections import defaultdict

try:
    from typing import Tuple, List, Any, Dict, Iterable, Set
except ImportError:
    pass  # IronPython 2.7

try:
    from itertools import izip # type: ignore
except ImportError:
    import zip as izip  # type: ignore // Python 3

try:
    from System import Object # type: ignore
    from System.Drawing import Color # type: ignore
except ImportError:
    pass  # Outside .NET

try:
    from Grasshopper import DataTree # type: ignore
    from Grasshopper.Kernel.Data import GH_Path # type: ignore
except ImportError:
    pass  # Outside Grasshopper

try:
    from Rhino.Geometry import TextJustification, Brep, Mesh, Curve, Plane # type: ignore
    from Rhino.DocObjects import ObjectAttributes # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from ladybug_geometry.geometry3d import plane
    from ladybug_rhino.fromgeometry import from_face3d, from_plane, from_point3d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:
    from honeybee import boundarycondition, model, face
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


class GHCompo_CreateElevationPDFGeometry(object):

    def __init__(self, _IGH, hb_model, surface_color, line_color, lineweight, branch_count, *args, **kwargs):
        # type: (gh_io.IGH, model.Model, Color, Color, float, int, Any, Any) -> None
        self.IGH = _IGH
        self.hb_model = hb_model
        self.surface_color = surface_color or Color.FromArgb(255, 255, 255) # type: ignore
        self.line_color = line_color or Color.FromArgb(0, 0, 0) # type: ignore
        self.lineweight = lineweight or 0.25
        self.branch_count = branch_count or 1
        self.error = []

    def find_all_room_ids(self):
        # type: () -> Set[str]
        """Return a set of all the Room identifiers in the model."""
        return {room.identifier for room in self.hb_model.rooms}

    def get_exterior_hb_faces_by_const_type(self):
        # type: () -> Dict[str, List[face.Face]]
        """Return a Dict of all the 'Exterior' Honeybee Faces, keyed by construction-type and surface normal direction."""
        
        def _clean_val(val, tolerance=0000.1):
            # type: (float, float) -> float
            """Handle rounding the the -0 problem."""
            val = round(val, 4)
            if val - 0.0 < tolerance:
                return 0.0
            else:
                return val
        
        def _interior_surface(hb_face):
            # type: (face.Face) -> bool
            """Return True if the face is an 'Interior' Surface exposure."""
            if isinstance(hb_face.boundary_condition, boundarycondition.Surface):
                adjacent_room_name = hb_face.boundary_condition.boundary_condition_objects[-1]
                if adjacent_room_name in all_room_ids:
                    return True
            return False

        all_room_ids = self.find_all_room_ids()
        hb_faces_by_const_type = defaultdict(list)
        
        for room in self.hb_model.rooms:
            for hb_face in room.faces:
                # -- Filter out any 'Interior' Surface exposure faces.
                # -- If the face is a 'Surface' exposure, BUT the other side is NOT in the model, keep the face. 
                if _interior_surface(hb_face):
                    continue
                
                key = "{}-{:.4f}-{:.4f}-{:.4f}".format(
                    hb_face.properties.energy.construction.display_name,
                    _clean_val(hb_face.geometry.normal.x),
                    _clean_val(hb_face.geometry.normal.y),
                    _clean_val(hb_face.geometry.normal.z),
                    )
                hb_faces_by_const_type[key].append(hb_face)
        
        return hb_faces_by_const_type
    
    def get_punched_breps(self, _hb_face):
        # type: (List[face.Face]) -> List[Brep]
        """Return a list of the 'Punched' Breps for a group of HB-Faces."""
        breps_ = []
        for hb_face in _hb_face:
            if not hb_face.apertures:
                breps_.append(from_face3d(hb_face.geometry))
            else:
                breps_.append(from_face3d(hb_face.punched_geometry))
        return breps_

    def get_centered_aperture_plane(self, _aperture):
        # type (aperture.Aperture) -> plane.Plane
        """Return the 'Aperture' Plane centered on the Aperture's center point."""
        ap_cp = from_point3d(_aperture.geometry.center)
        ap_plane = from_plane(_aperture.geometry.plane)
        move_vec = self.IGH.ghpythonlib_components.Vector2Pt(ap_plane.Origin, ap_cp, False).vector
        centered_plane = self.IGH.ghpythonlib_components.Move(ap_plane, move_vec).geometry

        # -- Ensure that the plane's Y-Axis is always pointing up.
        if centered_plane.YAxis.Z < 0:
            centered_plane.Rotate(math.pi, centered_plane.Normal)

        return centered_plane

    def get_aperture_breps(self, _hb_faces):
        # type: (Iterable[face.Face]) -> Tuple[List[Brep], List[str], List[plane.Plane]]
        """Return a list of all the 'Aperture' Breps (and names / planes) for a group of HB-Faces."""
        return (
            [from_face3d(ap.geometry) for hb_face in _hb_faces for ap in hb_face.apertures ],
            [ap.display_name for hb_face in _hb_faces for ap in hb_face.apertures],
            [self.get_centered_aperture_plane(ap) for hb_face in _hb_faces for ap in hb_face.apertures],
        )

    def breps_to_meshes(self, _breps):
        # type: (Iterable[Brep]) -> List[Mesh]
        """Convert a group of Brep-Surface into to list of Meshes."""
        meshes_ = []
        for brep in _breps:
            meshes_.append( self.IGH.ghpythonlib_components.MeshColours(
                brep,
                self.surface_color
            ))
        return meshes_

    def get_mesh_naked_edges(self, _mesh):
        # type: (Mesh) -> List[Curve]
        """Extract the naked edges of a Mesh and return them as Curves."""

        srfc_edgs = self.IGH.ghc.MeshEdges(_mesh).naked_edges
        srfc_edgs = self.IGH.ghc.JoinCurves(srfc_edgs, True)
        
        if not isinstance(srfc_edgs, list):
            srfc_edgs = [srfc_edgs]

        return srfc_edgs

    def merge_rh_breps(self, _rh_breps):
        # type: (Iterable[Brep]) -> List[Brep]
        """Try to join and merge a group of Rhino Breps together."""

        joined_breps = self.IGH.ghpythonlib_components.BrepJoin(_rh_breps).breps
        if not isinstance(joined_breps, list):
            joined_breps = [joined_breps]
        
        merged_breps = self.IGH.ghpythonlib_components.MergeFaces(joined_breps).breps
        if not isinstance(merged_breps, list):
            merged_breps = [merged_breps]

        for brep in merged_breps:
            brep.Edges.MergeAllEdges((math.pi)/2)

        return merged_breps
    
    def create_rh_attr_object(self, _color, _lineweight):
        # type: (Color, float) -> ObjectAttributes
        """Return a Rhino Object Attributes object."""
        
        new_attr_obj = self.IGH.Rhino.DocObjects.ObjectAttributes()

        new_attr_obj.ObjectColor = _color
        new_attr_obj.PlotColor = _color
        new_attr_obj.ColorSource = self.IGH.Rhino.DocObjects.ObjectColorSource.ColorFromObject
        new_attr_obj.PlotColorSource = self.IGH.Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
        new_attr_obj.PlotWeight = _lineweight
        new_attr_obj.PlotWeightSource = self.IGH.Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject
        new_attr_obj.DisplayOrder = 0
        
        return new_attr_obj

    def run(self):
        # type: () -> Tuple
        all_geom, all_geom_attributes, all_aperture_names, all_aperture_planes = [], [], [], []

        if not self.hb_model:
            return self.error, all_geom, all_geom_attributes, all_aperture_names, all_aperture_planes

        ext_hb_faces = self.get_exterior_hb_faces_by_const_type()
        
        # -- Get all the Surface and Aperture Meshes, Edges, and Rhino-Attributes
        for face_group in ext_hb_faces.values():
            srfc_punched_breps = self.merge_rh_breps(self.get_punched_breps(face_group))
            srfc_aperture_breps, srfc_aperture_names, srfc_aperture_planes  = self.get_aperture_breps(face_group)

            # -- Base surfaces (wall, floor, roof, etc.)
            for srfc_msh in self.breps_to_meshes(srfc_punched_breps):
                all_geom.append(srfc_msh)
                all_geom_attributes.append(self.create_rh_attr_object(self.surface_color, self.lineweight))

                for edge in self.get_mesh_naked_edges(srfc_msh):
                    all_geom.append(edge)
                    all_geom_attributes.append(self.create_rh_attr_object(self.line_color, self.lineweight))
            
            # -- Apertures (windows, doors, etc.)
            all_aperture_names.extend(srfc_aperture_names)
            all_aperture_planes.extend(srfc_aperture_planes)
            for ap_msh in self.breps_to_meshes(srfc_aperture_breps):
                all_geom.append(ap_msh)
                all_geom_attributes.append(self.create_rh_attr_object(self.surface_color, self.lineweight))
                
                for edge in self.get_mesh_naked_edges(ap_msh):
                    all_geom.append(edge)
                    all_geom_attributes.append(self.create_rh_attr_object(self.line_color, self.lineweight))

        # -- Package up the data into DataTrees for Export
        # -- This is required to ensure the geom branches match the layout-views being printed.
        geom_ = self.IGH.duplicate_data_to_branches(all_geom, self.branch_count)
        geom_attributes_ = self.IGH.duplicate_data_to_branches(all_geom_attributes, self.branch_count)
        aperture_names_ = self.IGH.duplicate_data_to_branches(all_aperture_names, self.branch_count)
        aperture_planes_ = self.IGH.duplicate_data_to_branches(all_aperture_planes, self.branch_count)
        
        return self.error, geom_, geom_attributes_, aperture_names_, aperture_planes_