# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Visualize Window Frames."""

import math

try:
    from typing import List, Iterable, Tuple
except ImportError:
    pass

try:
    from itertools import izip  # type: ignore
except ImportError:
    izip = zip  # Python 3

try:
    from System import Object  # type: ignore
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from Rhino.Geometry import Brep, Point3d  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from ladybug_geometry.geometry3d import LineSegment3D, Plane
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_geometry:\n\t{}".format(e))

try:
    from ladybug_rhino.fromgeometry import (
        from_face3d,
        from_linesegment3d,
        from_point3d,
        from_plane,
    )
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

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

    def calc_edge_angle_about_origin(self, _edge, _center_pt, _pl, _tol=0.0001):
        # type: (LineSegment3D, Point3d, Plane, float) -> float
        """Calculate the angle of an edge about the origin of its parent plane."""

        rh_edge = from_linesegment3d(_edge)
        edge_midpoint = self.IGH.ghc.CurveMiddle(rh_edge)
        v = self.IGH.ghc.Vector2Pt(_center_pt, edge_midpoint, False).vector
        (
            local_origin,
            local_x_axis,
            local_y_axis,
            local_z_axis,
        ) = self.IGH.ghc.DeconstructPlane(_pl)
        angle = math.degrees(self.IGH.ghc.Angle(local_y_axis, v, _pl).angle)
        angle = round(angle, 2)

        if abs(angle - 360.0) <= _tol:
            angle = 0.0

        return angle

    def get_ap_edges(self, _aperture):
        # type: (Aperture) -> List[LineSegment3D]
        """Sort the edges of the aperture based on their angle about the aperture's center point.

        Note: the native Honeybee .get_left_right_edges methods don't seem to work properly?
        So using this custom implementation instead.
        """
        aperture_face = from_face3d(_aperture.geometry)
        aperture_local_plane = from_plane(_aperture.geometry.plane)
        apeture_center_point = self.IGH.ghc.Area(aperture_face).centroid
        edges_sorted = sorted(
            _aperture.geometry.boundary_segments,
            reverse=True,
            key=lambda e: self.calc_edge_angle_about_origin(
                e, apeture_center_point, aperture_local_plane
            ),
        )

        return edges_sorted

    def create_frame_surface(self, _ap_edges, _ap_frame_elements, ap_ctr_pt):
        # type: (Iterable, Iterable, Point3d) -> List[Brep]
        """Create the frame surfaces for the aperture."""
        frame_surfaces = []
        for edge, frame in izip(_ap_edges, _ap_frame_elements):
            edge_rh = from_linesegment3d(edge)
            crv_mid_pt = from_point3d(edge.midpoint)
            extrusion_vector = self.IGH.ghc.Vector2Pt(crv_mid_pt, ap_ctr_pt, True).vector
            extrusion_vector = self.IGH.ghc.Amplitude(extrusion_vector, frame.width)
            ext = self.IGH.ghc.Extrude(base=edge_rh, direction=extrusion_vector)
            frame_surfaces.append(ext)

        return frame_surfaces

    def create_glazing_surface(self, _frame_surfaces, _ap_srfc, _ap_ctr_pt):
        # type: (List[Brep], Brep, Point3d) -> Brep
        """Create the glazing surface for the aperture."""
        joined_frames = self.IGH.ghc.BrepJoin(_frame_surfaces).breps
        edges = self.IGH.ghc.DeconstructBrep(joined_frames).edges
        win_srfcs = self.IGH.ghc.SurfaceSplit(_ap_srfc, edges)

        # -- Figure out which of the split surfaces is the glazing surface
        ct_pt_distances = []
        for test_srfc in win_srfcs:
            ct_pt_distances.append(
                self.IGH.ghc.SurfaceClosestPoint(_ap_ctr_pt, test_srfc).distance
            )
        glazing_srfc = win_srfcs[ct_pt_distances.index(min(ct_pt_distances))]

        return glazing_srfc

    def run(self):
        # type: () -> tuple[DataTree[Object], DataTree[Object], DataTree[str], DataTree[str], DataTree[str]]
        """Run the component."""
        frame_surfaces_ = DataTree[Object]()
        glazing_surfaces_ = DataTree[Object]()
        frame_element_type_names_ = DataTree[Object]()
        ap_edges_ = DataTree[Object]()
        ap_planes_ = DataTree[Object]()

        for i, ap in enumerate(self.apertures):
            # -----------------------------------------------------------------------
            # -- Pull out all the relevant Aperture data needed
            ap_srfc_rh = from_face3d(ap.geometry)
            ap_ctr_pt = self.IGH.ghc.Area(ap_srfc_rh).centroid
            ap_edges = self.get_ap_edges(ap)
            ap_const = ap.properties.energy.construction  # type: ignore
            ap_frame_elements = ap_const.properties.ph.ph_frame.elements

            # -----------------------------------------------------------------------
            # -- Frame Geometry
            frame_surfaces = self.create_frame_surface(
                ap_edges, ap_frame_elements, ap_ctr_pt
            )
            frame_surfaces_.AddRange(frame_surfaces, GH_Path(i))

            # -----------------------------------------------------------------------
            # -- Glazing Geometry
            glazing_surfaces_.Add(
                self.create_glazing_surface(frame_surfaces, ap_srfc_rh, ap_ctr_pt),
                GH_Path(i),
            )

            # -----------------------------------------------------------------------
            # -- Get the other bits for debugging
            frame_element_type_names_.AddRange(
                [el.display_name for el in ap_frame_elements],
                GH_Path(i),
            )
            ap_edges_.AddRange(
                [from_linesegment3d(_) for _ in self.get_ap_edges(ap)], GH_Path(i)
            )
            ap_planes_.Add(from_plane(ap.geometry.plane), GH_Path(i))

        return (
            frame_surfaces_,
            glazing_surfaces_,
            frame_element_type_names_,
            ap_edges_,
            ap_planes_,
        )
