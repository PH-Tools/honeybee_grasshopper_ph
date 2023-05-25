# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Visualize Window Frames."""

try:
    from typing import List, Iterable
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
    from ladybug_geometry.geometry3d import LineSegment3D
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_geometry:\n\t{}".format(e))

try:
    from ladybug_rhino.fromgeometry import from_face3d, from_linesegment3d, from_point3d
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

    def get_ap_edges(self, ap):
        # type: (Aperture) -> tuple[LineSegment3D, LineSegment3D, LineSegment3D, LineSegment3D]
        lr_edges = ap.geometry.get_left_right_vertical_edges(self.tolerance)
        if not lr_edges:
            raise Exception("Failed to get left and right edges of the aperture.")
        ap_edge_l, ap_edge_r = lr_edges

        bt_edges = ap.geometry.get_top_bottom_horizontal_edges(self.tolerance)
        if not bt_edges:
            raise Exception("Failed to get bottom and top edges of the aperture.")
        ap_edge_b, ap_edge_t = bt_edges

        return (ap_edge_t, ap_edge_r, ap_edge_b, ap_edge_l)

    def create_frame_surface(self, _ap_edges, _ap_frame_elements, ap_ctr_pt):
        # type: (Iterable, Iterable, Point3d) -> List[Brep]
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
        # type: () -> tuple[DataTree[Object], DataTree[Object]]
        frame_surfaces_, glazing_surfaces_ = DataTree[Object](), DataTree[Object]()

        for i, ap in enumerate(self.apertures):
            # -- Pull out all the relevant Aperture data needed
            ap_srfc_rh = from_face3d(ap.geometry)
            ap_ctr_pt = self.IGH.ghc.Area(ap_srfc_rh).centroid
            ap_edges = self.get_ap_edges(ap)
            ap_const = ap.properties.energy.construction
            ap_frame_elements = ap_const.properties.ph.ph_frame.elements

            # --
            frame_surfaces = self.create_frame_surface(
                ap_edges, ap_frame_elements, ap_ctr_pt
            )
            frame_surfaces_.AddRange(frame_surfaces, GH_Path(i))

            # --
            glazing_surfaces_.Add(
                self.create_glazing_surface(frame_surfaces, ap_srfc_rh, ap_ctr_pt),
                GH_Path(i),
            )

        return frame_surfaces_, glazing_surfaces_
