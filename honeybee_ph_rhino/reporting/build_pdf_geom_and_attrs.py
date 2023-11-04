# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Create PDF-Ready Geometry and Attribute Objects."""

try:
    from typing import Tuple, List, Any, Iterable
except ImportError:
    pass  # Python 2.7

try:
    from System import Object # type: ignore
    from System.Drawing import Color # type: ignore
except ImportError:
    pass  # Outside .NET

try:
    from Grasshopper import DataTree # type: ignore
except ImportError:
    pass # Outside Rhino

try:
    from Rhino.DocObjects import ObjectAttributes # type: ignore
    from Rhino.Geometry import Brep, BrepFace, Curve, Mesh, Polyline, Line, LineCurve # type: ignore
    Edge = (Curve, Polyline, Line, LineCurve)
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


from honeybee_ph_utils.input_tools import clean_get

class GHCompo_CreatePDFGeometryAndAttributes(object):
    """Create Rhino Object Attributes."""

    surface_color_default = Color.FromArgb(255, 255, 255) # type: ignore
    line_color_default = Color.FromArgb(0, 0, 0) # type: ignore
    lineweight_default = 0.25

    def __init__(self, _IGH, geometry, surface_color, line_color, lineweight, *args, **kwargs):
        # type: (gh_io.IGH, DataTree[Brep | Curve], List[Color], List[Color], List[float], Any, Any) -> None
        self.IGH = _IGH
        self.geometry = geometry
        self.surface_color = surface_color
        self.line_color = line_color
        self.lineweight = lineweight

    def get_brep_faces(self, _rh_brep):
        # type: (Brep) -> List[Brep]
        """Return a list of Brep-Surfaces from a Brep.
        
        Do not call 'DeconstructBrep' directly as sometimes it returns a list, sometimes not.
        """

        faces_ = self.IGH.ghpythonlib_components.DeconstructBrep(_rh_brep).faces
        if not isinstance(faces_, list):
            return [faces_]
        else:
            return faces_

    def get_mesh_from_brep(self, _rh_brep_face, _color):
        # type: (BrepFace, Color) -> Mesh
        """Return a Mesh of a BrepFace."""

        return self.IGH.ghpythonlib_components.MeshColours(_rh_brep_face, _color)

    def get_edges_from_brep(self, _rh_brep_face):
        # type: (BrepFace) -> List[Curve]
        """Return a Curve of the edges of a BrepFace."""

        all_edges = self.IGH.ghpythonlib_components.DeconstructBrep(_rh_brep_face).edges
        joined_edges = self.IGH.ghpythonlib_components.JoinCurves(all_edges, True)
        
        if not isinstance(joined_edges, list):
            return [joined_edges]
        else:
            return joined_edges

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
        
        return new_attr_obj

    def get_surface_geometry(self, _geometry):
        # type: (Iterable) -> List[Brep]
        """Return a list of Rhino Breps from a list of Rhino Geometry."""
        
        geom_ = []
        if not isinstance(_geometry, list):
            _geometry = [_geometry]

        for geom_item in _geometry:
            if isinstance(geom_item, Brep):
                for brep_face in self.get_brep_faces(_geometry):
                    geom_.append(brep_face)
        return geom_

    def get_edge_geometry(self, _geometry):
        # type: (Iterable) -> List
        """Return a list of Rhino Curves from a list of Rhino Geometry.
        
        If the input is a Brep, will extract the Edge curves.
        """

        geom_ = []
        if not isinstance(_geometry, list):
            _geometry = [_geometry]
                   
        for geom_item in _geometry:
            if isinstance(geom_item, Brep):
                for brep_face in self.get_brep_faces(_geometry):
                    for edge in self.get_edges_from_brep(brep_face):
                        geom_.append(edge)
            elif isinstance(geom_item, Edge):
                geom_.append(geom_item)
        return geom_

    def run(self):
        # type: () -> Tuple[DataTree, DataTree[ObjectAttributes]]
        """Return a new Rhino.DocObjects.ObjectAttributes object with specified settings."""
        geom_ = self.IGH.Grasshopper.DataTree[Object]()
        geom_attributes_ = self.IGH.Grasshopper.DataTree[Object]()

        for j, branch in enumerate(self.geometry.Branches):

            pdf_geom, pdf_geom_attributes = [], []

            # -- Create the colored Mesh and outline curves, along with their attributes
            for i, geometry in enumerate(branch):
                surface_color = clean_get(self.surface_color, i, self.surface_color_default)
                line_color = clean_get(self.line_color, i) or self.line_color_default
                lineweight = clean_get(self.lineweight, i) or self.lineweight_default
                
                for surface in self.get_surface_geometry(geometry):
                    pdf_geom.append(self.get_mesh_from_brep(surface, surface_color))
                    pdf_geom_attributes.append(self.create_rh_attr_object(surface_color, lineweight))

                for edge in self.get_edge_geometry(geometry):
                    pdf_geom.append(edge)
                    pdf_geom_attributes.append(self.create_rh_attr_object(line_color, lineweight))
            
            # -- Package up for outut
            geom_.AddRange(pdf_geom, self.IGH.GH_Path(j))
            geom_attributes_.AddRange(pdf_geom_attributes, self.IGH.GH_Path(j))

        return geom_, geom_attributes_