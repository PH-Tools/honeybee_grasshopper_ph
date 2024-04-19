# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Create Ventilation Duct"""

try:
    from typing import List, Optional, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from Rhino.Geometry import LineCurve, NurbsCurve, PolylineCurve  # type: ignore
except ImportError as e:
    raise ImportError("\nFailed to import Rhino:\n\t{}".format(e))

try:
    from ladybug_rhino.togeometry import to_polyline3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from ladybug_geometry.geometry3d.pointvector import Point3D
    from ladybug_geometry.geometry3d.polyline import LineSegment3D, Polyline3D
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_geometry:\n\t{}".format(e))

try:
    from honeybee_energy_ph.hvac import ducting
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))


class GHCompo_CreateVentDuct(object):
    """Component Interface"""

    display_name = ghio_validators.HBName("display_name")
    insul_thickness = ghio_validators.UnitMM("insul_thickness")
    insul_conductivity = ghio_validators.UnitW_MK("insul_conductivity")
    diameter = ghio_validators.UnitMM("diameter")
    height = ghio_validators.UnitMM("height")
    width = ghio_validators.UnitMM("width")

    def __init__(
        self,
        _IGH,
        _geometry,
        _display_name,
        _duct_type,
        _insul_thickness,
        _insul_conductivity,
        _insul_reflective,
        _diameter,
        _height,
        _width,
    ):
        # type: (gh_io.IGH, List[Union[LineCurve, NurbsCurve, PolylineCurve]], str, int, float, float, bool, float, Optional[float], Optional[float]) -> None
        self.IGH = _IGH
        self.geometry_segments = self.to_LbtLineSegments3D(_geometry)
        self.display_name = _display_name or "__unnamed_vent_duct__"
        self.duct_type = _duct_type
        self.insul_thickness = _insul_thickness or 25.4
        self.insul_conductivity = _insul_conductivity or 0.04
        self.diameter = _diameter or 160
        self.height = _height
        self.width = _width

        if _insul_reflective is None:
            self.insul_reflective = True
        else:
            self.insul_reflective = _insul_reflective

    @property
    def duct_type(self):
        # type: () -> int
        return self._duct_type

    @duct_type.setter
    def duct_type(self, _in):
        input_int = input_tools.input_to_int(_in)
        self._duct_type = input_int or 1

    def to_LbtLineSegments3D(self, _input):
        # type: (List[Union[LineCurve, NurbsCurve, PolylineCurve]]) -> List[LineSegment3D]
        """Convert Rhino geometry Inputs to Ladybug LineSegment3D."""
        lbt_line_segments = []  # type: List[LineSegment3D]

        if not _input:
            return lbt_line_segments

        if not isinstance(_input, list):
            _input = [_input]

        for rh_crv in [self._clean_rh_curves(rh_crv) for rh_crv in _input]:
            lbt_crv = to_polyline3d(rh_crv)

            if hasattr(lbt_crv, "segments"):
                # -- It is a Polyline3D
                lbt_line_segments.extend(lbt_crv.segments)
            else:
                # -- It is a LineSegment3D
                lbt_line_segments.append(lbt_crv)

        return lbt_line_segments

    def _clean_rh_curves(self, _input):
        # type: (Union[LineCurve, NurbsCurve, PolylineCurve]) -> Union[LineCurve, PolylineCurve]
        """Try to convert input Rhino geometry to a Rhino Polyline object."""
        try:
            cps = self.IGH.ghpythonlib_components.ControlPoints(_input).points
        except:
            raise Exception("Error: Geometry input '{}' cannot be converted to a Rhino PolylineCurve.".format(_input))
        return self.IGH.ghpythonlib_components.PolyLine(cps, False)

    @property
    def _default_geometry(self):
        # type: () -> LineSegment3D
        """Return a default geometry for the component (A line 1 unit long)."""
        pt1 = Point3D(0, 0, 0)
        pt2 = Point3D(1, 0, 0)
        return LineSegment3D.from_end_points(pt1, pt2)

    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        return len(self.geometry_segments) > 0

    def run(self):
        # type: () -> Optional[ducting.PhDuctElement]
        if not self.ready():
            return None

        hbph_obj = ducting.PhDuctElement()
        hbph_obj.display_name = self.display_name
        hbph_obj.duct_type = self.duct_type

        for segment in self.geometry_segments:
            hbph_obj.add_segment(
                ducting.PhDuctSegment(
                    segment,
                    self.insul_thickness,
                    self.insul_conductivity,
                    self.insul_reflective,
                    self.diameter,
                    self.height,
                    self.width,
                )
            )

        return hbph_obj
