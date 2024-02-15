# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Visualize Window Frames."""

import math

try:
    from typing import Iterable, List, Tuple
except ImportError:
    pass

try:
    from itertools import izip  # type: ignore
except ImportError:
    izip = zip  # Python 3

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from Rhino.Geometry import (
        Brep,
        Interval,
        LineCurve,  # type: ignore
        Plane,
        Point3d,
        Vector3d,
    )
    from System import Object  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from ladybug_geometry.geometry3d import LineSegment3D
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_geometry:\n\t{}".format(e))

try:
    from ladybug_rhino.fromgeometry import (
        from_face3d,
        from_linesegment3d,
        from_plane,
        from_point3d,
    )
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee.aperture import Aperture
    from honeybee_energy.construction.window import WindowConstruction
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

from honeybee_energy_ph.construction.window import PhWindowFrame, PhWindowFrameElement
from honeybee_energy_ph.properties.construction.window import (
    WindowConstructionPhProperties,
)

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_VisualizeWindowFrameElements(object):
    def __init__(self, _IGH, _apertures):
        # type: (gh_io.IGH, List[Aperture]) -> None
        self.IGH = _IGH
        self.apertures = _apertures
        self.tolerance = _IGH.sc.doc.ModelAbsoluteTolerance

    def get_edge_midpoint(self, _edge):
        # type: (LineCurve) -> Point3d
        """Return the midpoint of a Rhino.Geometry.LineCurve."""
        new_domain = Interval(0, 1)
        _edge.Domain = new_domain
        return _edge.PointAt(0.5)

    def calc_edge_angle_about_origin(self, _edge, _center_pt, _pl, _tol=0.0001):
        # type: (LineCurve, Point3d, Plane, float) -> float
        """Return the angle of an edge's midpoint about the origin of its parent plane."""

        # -- Find the vector from the edge's midpoint to the center
        edge_midpoint = self.get_edge_midpoint(_edge)
        vec = edge_midpoint - _center_pt

        # -- Find the angle between the edge vector and the parent plane's local-Y axis
        angle = math.degrees(Vector3d.VectorAngle(_pl.YAxis, vec, _pl))
        angle = round(angle, 2)

        # -- Ensure no floating-point errors
        if abs(angle - 360.0) <= _tol:
            angle = 0.0

        return angle

    def sort_aperture_edges(self, _ap_edges, _ap_center_point, _ap_local_plane):
        # type: (List[LineCurve], Point3d, Plane) -> List[LineSegment3D]
        """Sort the edges of the aperture based on their angle about the aperture's center point.

        Note: the native Honeybee .get_left_right_edges methods don't seem to work properly?
        So using this 'calc_edge_angle_about_origin' custom implementation instead.
        """
        edges_sorted = sorted(
            _ap_edges,
            reverse=True,
            key=lambda e: self.calc_edge_angle_about_origin(
                e, _ap_center_point, _ap_local_plane
            ),
        )
        return edges_sorted

    def create_frame_surface(self, _ap_edges, _ap_frame_elements, ap_ctr_pt):
        # type: (Iterable[LineCurve], Iterable, Point3d) -> List[Brep]
        """Create the frame surfaces for the aperture."""
        frame_surfaces = []
        for edge, frame in izip(_ap_edges, _ap_frame_elements):
            crv_mid_pt = self.get_edge_midpoint(edge)
            extrusion_vector = self.IGH.ghc.Vector2Pt(crv_mid_pt, ap_ctr_pt, True).vector
            extrusion_vector = self.IGH.ghc.Amplitude(extrusion_vector, frame.width)
            ext = self.IGH.ghc.Extrude(base=edge, direction=extrusion_vector)
            frame_surfaces.append(ext)

        return frame_surfaces

    def create_glazing_surface(self, _frame_surfaces, _ap_srfc, _ap_ctr_pt):
        # type: (List[Brep], Brep, Point3d) -> Brep
        """Create the glazing surface for the aperture."""
        joined_frames = self.IGH.ghc.BrepJoin(_frame_surfaces).breps
        edges = self.IGH.ghc.DeconstructBrep(joined_frames).edges
        win_srfcs = self.IGH.ghc.SurfaceSplit(_ap_srfc, edges)

        # -- Figure out which of the split surfaces is the glazing surface
        # -- by choosing the surface with the closest point to the aperture's center point
        ct_pt_distances = []
        for test_srfc in win_srfcs:
            ct_pt_distances.append(
                self.IGH.ghc.SurfaceClosestPoint(_ap_ctr_pt, test_srfc).distance
            )
        glazing_srfc = win_srfcs[ct_pt_distances.index(min(ct_pt_distances))]

        return glazing_srfc

    def get_aperture_ph_frame_elements(self, _aperture):
        # type: (Aperture) -> Tuple[List[PhWindowFrameElement], List[str]]
        """Get the Passive House PhWindowFrameElements for of the aperture;s PH-Frame."""
        ap_const = _aperture.properties.energy.construction  # type: ignore
        ap_prop_ph = ap_const.properties.ph  # type: WindowConstructionPhProperties
        ap_ph_frame = ap_prop_ph.ph_frame

        if not ap_ph_frame:
            msg = "Error: The Aperture {} does not have a Passive House window frame?, skipping...".format(
                _aperture.display_name
            )
            self.IGH.warning(msg)
            return [], []

        el_names = [el.display_name for el in ap_ph_frame.elements]
        return ap_ph_frame.elements, el_names

    def get_aperture_geometry(self, _aperture):
        # type: (Aperture) -> tuple[Brep, Point3d, Plane, List[LineSegment3D]]
        """Get the geometric elements of the Honeybee-Aperture as Rhino Geometry."""
        ap_srfc = from_face3d(_aperture.geometry)
        ap_ctr_pt = self.IGH.ghc.Area(ap_srfc).centroid
        ap_local_plane = from_plane(_aperture.geometry.plane)
        ap_edges = [from_linesegment3d(s) for s in _aperture.geometry.boundary_segments]
        ap_edges_sorted = self.sort_aperture_edges(ap_edges, ap_ctr_pt, ap_local_plane)
        return ap_srfc, ap_ctr_pt, ap_local_plane, ap_edges_sorted

    def run(self):
        # type: () -> tuple[DataTree[Object], DataTree[Object], DataTree[str], DataTree[str], DataTree[str]]
        """Run the component."""
        frame_srfcs_ = DataTree[Object]()
        glazing_srfcs_ = DataTree[Object]()
        frame_element_type_names_ = DataTree[str]()
        edges_ = DataTree[LineCurve]()
        planes_ = DataTree[Plane]()

        for i, ap in enumerate(self.apertures):
            # -----------------------------------------------------------------------
            # -- Pull out all the relevant Aperture data that is needed throughout
            # -- Convert to from Ladubug to Rhino geometry for all the later operations.
            srfc, ctr_pt, local_plane, edges = self.get_aperture_geometry(ap)
            hbph_frame_elements, element_names = self.get_aperture_ph_frame_elements(ap)

            if not hbph_frame_elements:
                continue

            # -----------------------------------------------------------------------
            # -- Create all the Frame-Element Geometry
            frame_surfaces = self.create_frame_surface(edges, hbph_frame_elements, ctr_pt)
            frame_srfcs_.AddRange(frame_surfaces, GH_Path(i))

            # -----------------------------------------------------------------------
            # -- Create the Glazing Geometry
            glazing_srfc = self.create_glazing_surface(frame_surfaces, srfc, ctr_pt)
            glazing_srfcs_.Add(glazing_srfc, GH_Path(i))

            # -----------------------------------------------------------------------
            # -- Get the other bits for debugging
            frame_element_type_names_.AddRange(element_names, GH_Path(i))
            edges_.AddRange(edges, GH_Path(i))
            planes_.Add(local_plane, GH_Path(i))

        return (
            frame_srfcs_,
            glazing_srfcs_,
            frame_element_type_names_,
            edges_,
            planes_,
        )
