# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Visualize Window Frames."""

import math

try:
    from typing import Iterable, List, Sequence, Tuple
except ImportError:
    pass

try:
    from itertools import izip  # type: ignore
except ImportError:
    izip = zip  # Python 3

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from Rhino.Geometry import LineCurve  # type: ignore
    from Rhino.Geometry import Brep, Interval, Plane, Point3d, Vector3d  # type: ignore
    from System import Object  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from ladybug_rhino.fromgeometry import from_face3d, from_linesegment3d, from_plane
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.properties.aperture import ApertureEnergyProperties
    from honeybee_energy.properties.extension import WindowConstructionProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction.window import PhWindowFrameElement
    from honeybee_energy_ph.properties.construction.window import WindowConstructionPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.converter import convert
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


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
        vector_from_mid_to_center = Point3d.Subtract(edge_midpoint, _center_pt)

        # -- Find the angle between the edge vector and the parent plane's local-Y axis
        angle = math.degrees(Vector3d.VectorAngle(_pl.YAxis, vector_from_mid_to_center, _pl))
        angle = round(angle, 2)
        # -- Ensure no floating-point errors
        if abs(angle - 360.0) <= _tol:
            angle = 0.0

        return angle

    def sort_aperture_edges(self, _ap_edges, _ap_center_point, _ap_local_plane):
        # type: (Sequence[LineCurve], Point3d, Plane) -> List[LineCurve]
        """Sort the edges of the aperture based on their angle about the aperture's center point.

        Note: the native Honeybee .get_left_right_edges methods don't seem to work properly?
        See: https://discourse.ladybug.tools/t/trouble-getting-left-and-right-aperture-edges/
        So using this 'calc_edge_angle_about_origin' custom implementation instead.
        """
        edges_sorted = sorted(
            _ap_edges,
            reverse=True,
            key=lambda e: self.calc_edge_angle_about_origin(e, _ap_center_point, _ap_local_plane),
        )
        # This sorting yields the edges in an order like: [270, 180, 90, 0] (clockwise starting from the RIGHT edge)
        #
        #      0
        #      |
        #      |
        # 90-------270
        #      |
        #      |
        #     180
        #
        # We need to shift this so that the first edge is the top
        edges_sorted = edges_sorted[-1:] + edges_sorted[:-1]
        return edges_sorted

    def create_frame_surface(self, _ap_edges, _ap_frame_elements, ap_ctr_pt):
        # type: (Iterable[LineCurve], Iterable, Point3d) -> List[Brep]
        """Create the frame surfaces for the aperture."""
        frame_surfaces = []
        for edge, frame in izip(_ap_edges, _ap_frame_elements):

            # -- Get the width in the Rhino-document's units
            # -- From AirTable, and in Honeybee, width will ALWAYS be in meters.
            doc_unit_type = self.IGH.get_rhino_unit_system_name()
            width_in_doc_units = convert(frame.width, "M", doc_unit_type)

            crv_mid_pt = self.get_edge_midpoint(edge)
            extrusion_vector = self.IGH.ghc.Vector2Pt(crv_mid_pt, ap_ctr_pt, True).vector
            extrusion_vector = self.IGH.ghc.Amplitude(extrusion_vector, width_in_doc_units)
            ext = self.IGH.ghc.Extrude(base=edge, direction=extrusion_vector)
            frame_surfaces.append(ext)

        return frame_surfaces

    def create_glazing_surface(self, _frame_surfaces, _ap_surface, _ap_ctr_pt):
        # type: (List[Brep], Brep, Point3d) -> Brep
        """Create the glazing surface for the aperture."""
        joined_frames = self.IGH.ghc.BrepJoin(_frame_surfaces).breps
        edges = self.IGH.ghc.DeconstructBrep(joined_frames).edges
        win_surfaces = self.IGH.ghc.SurfaceSplit(_ap_surface, edges)

        # -- Figure out which of the split surfaces is the glazing surface
        # -- by choosing the surface with the closest point to the aperture's center point
        ct_pt_distances = []
        for test_surface in win_surfaces:
            ct_pt_distances.append(self.IGH.ghc.SurfaceClosestPoint(_ap_ctr_pt, test_surface).distance)
        glazing_surface = win_surfaces[ct_pt_distances.index(min(ct_pt_distances))]

        return glazing_surface

    def get_aperture_ph_frame_elements(self, _aperture):
        # type: (Aperture) -> Tuple[List[PhWindowFrameElement], List[str]]
        """Get the Passive House PhWindowFrameElements for of the aperture;s PH-Frame."""
        ap_prop_energy = getattr(_aperture.properties, "energy")  # type: ApertureEnergyProperties
        ap_const = ap_prop_energy.construction

        # -------------------------------------------------------------------------------
        # -- Find the actual Window Construction
        if hasattr(ap_const, "window_construction"):
            """
            If it's a Honeybee Energy WindowConstructionShade the actual HB-
            construction will be inside the 'window_construction' attribute
            """
            ap_const = getattr(ap_const, "window_construction")

        # -------------------------------------------------------------------------------
        # -- Find the PH-Properties for the Window Construction
        if not hasattr(ap_const, "properties"):
            msg = "Error: The Aperture {} does not have a Window Construction?, skipping...".format(
                _aperture.display_name
            )
            self.IGH.warning(msg)
            return [], []

        ap_const_prop = getattr(ap_const, "properties", None)  # type: WindowConstructionProperties | None
        ap_prop_ph = getattr(ap_const_prop, "ph", None)  # type: WindowConstructionPhProperties | None

        if not ap_prop_ph:
            msg = "Error: The Aperture '{}' does not have a Passive House window construction?, skipping...".format(
                _aperture.display_name
            )
            self.IGH.warning(msg)
            return [], []

        # -------------------------------------------------------------------------------
        # -- Try and get the PH-Frame from the Window Construction
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
        # type: (Aperture) -> tuple[Brep, Point3d, Plane, List[LineCurve]]
        """Get the geometric elements of the Honeybee-Aperture as Rhino Geometry."""
        ap_surface = from_face3d(_aperture.geometry)  # type: Brep # type: ignore
        ap_ctr_pt = self.IGH.ghc.Area(ap_surface).centroid
        ap_local_plane = from_plane(_aperture.geometry.plane)
        ap_edges = [from_linesegment3d(s) for s in _aperture.geometry.boundary_segments]
        ap_edges_sorted = self.sort_aperture_edges(ap_edges, ap_ctr_pt, ap_local_plane)
        return ap_surface, ap_ctr_pt, ap_local_plane, ap_edges_sorted

    def run(self):
        # type: () -> tuple[DataTree[Object], DataTree[Object], DataTree[Object], DataTree[str], DataTree[str], DataTree[str]]
        """Run the component."""
        aperture_surfaces_ = DataTree[Object]()
        frame_surfaces_ = DataTree[Object]()
        glazing_surfaces_ = DataTree[Object]()
        frame_element_type_names_ = DataTree[str]()
        edges_ = DataTree[LineCurve]()
        planes_ = DataTree[Plane]()

        for i, ap in enumerate(self.apertures):
            # -----------------------------------------------------------------------
            # -- Pull out all the relevant Aperture data that is needed throughout
            # -- Convert to from Ladybug to Rhino geometry for all the later operations.
            surface, ctr_pt, local_plane, edges = self.get_aperture_geometry(ap)
            hbph_frame_elements, element_names = self.get_aperture_ph_frame_elements(ap)

            if not hbph_frame_elements:
                continue

            # -----------------------------------------------------------------------
            # -- Collect the Aperture Geometry for Export
            aperture_surfaces_.Add(surface, GH_Path(i))

            # -----------------------------------------------------------------------
            # -- Create all the Frame-Element Geometry
            frame_surfaces = self.create_frame_surface(edges, hbph_frame_elements, ctr_pt)
            frame_surfaces_.AddRange(frame_surfaces, GH_Path(i))

            # -----------------------------------------------------------------------
            # -- Create the Glazing Geometry
            glazing_surface = self.create_glazing_surface(frame_surfaces, surface, ctr_pt)
            glazing_surfaces_.Add(glazing_surface, GH_Path(i))

            # -----------------------------------------------------------------------
            # -- Get the other bits for debugging
            frame_element_type_names_.AddRange(element_names, GH_Path(i))
            edges_.AddRange(edges, GH_Path(i))
            planes_.Add(local_plane, GH_Path(i))

        return (
            aperture_surfaces_,
            frame_surfaces_,
            glazing_surfaces_,
            frame_element_type_names_,
            edges_,
            planes_,
        )
