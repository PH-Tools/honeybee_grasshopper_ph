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
    from ladybug_geometry.geometry3d.polyline import LineSegment3D
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_geometry:\n\t{}".format(e))

try:
    from honeybee_phhvac import ducting
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_phhvac:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from ph_units.parser import parse_input
    from ph_units.converter import convert
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


class GHCompo_CreateVentDuct(object):
    """Component Interface"""

    display_name = ghio_validators.HBName("display_name")
    insul_conductivity = ghio_validators.UnitW_MK("insul_conductivity")

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
        # type: (gh_io.IGH, List[Union[LineCurve, NurbsCurve, PolylineCurve]], Optional[str], Optional[str], Optional[str], Optional[str], Optional[bool], Optional[str], Optional[str], Optional[str]) -> None
        self.IGH = _IGH
        self.geometry_segments = self._to_LbtLineSegments3D(_geometry)
        self.display_name = _display_name or "__unnamed_vent_duct__"
        self.duct_type = _duct_type
        self.insul_conductivity = _insul_conductivity or 0.04
        self.insul_reflective = _insul_reflective

        # -- These values will all be in the Rhino-Document's Unit-Type (MM, M, inch, etc.)
        self.insul_thickness = _insul_thickness or "25.4 MM"
        self.diameter = _diameter or "160 MM"
        self.height = _height
        self.width = _width

    def _convert_input_value_to_rhino_units(self, _value, _attr_name):
        # type: (Union[str, int, float], str) -> float
        rh_unit = self.IGH.get_rhino_unit_system_name()
        input_value, input_unit = parse_input(_value)
        input_unit = input_unit or rh_unit
        value_in_rh_units = convert(input_value, input_unit, _target_unit=rh_unit)
        if not value_in_rh_units:
            raise ValueError("Failed to convert {} input '{}' to to Rhino units.".format(_attr_name, _value))
        print("Converting: {}-{} > {}-{}".format(input_value, input_unit, value_in_rh_units, rh_unit))
        return float(value_in_rh_units)

    @property
    def insul_thickness(self):
        # type: () -> float
        """The insul_thickness of the duct in Rhino-Document units."""
        return self._insul_thickness

    @insul_thickness.setter
    def insul_thickness(self, _value):
        # type: (Union[int, float, str]) -> None
        self._insul_thickness = self._convert_input_value_to_rhino_units(_value, "insul_thickness")

    @property
    def diameter(self):
        # type: () -> float
        """The diameter of the duct in Rhino-Document units."""
        return self._diameter

    @diameter.setter
    def diameter(self, _value):
        # type: (Union[int, float, str]) -> None
        self._diameter = self._convert_input_value_to_rhino_units(_value, "diameter")

    @property
    def height(self):
        # type: () -> Optional[float]
        """The height of the duct in Rhino-Document units."""
        return self._height

    @height.setter
    def height(self, _value):
        # type: (Optional[Union[int, float, str]]) -> None
        if not _value:
            self._height = None
            return
        self._height = self._convert_input_value_to_rhino_units(_value, "height")

    @property
    def width(self):
        # type: () -> Optional[float]
        """The width of the duct in Rhino-Document units."""
        return self._width

    @width.setter
    def width(self, _value):
        # type: (Optional[Union[int, float, str]]) -> None
        if not _value:
            self._width = None
            return
        self._width = self._convert_input_value_to_rhino_units(_value, "width")

    @property
    def duct_type(self):
        # type: () -> int
        return self._duct_type

    @duct_type.setter
    def duct_type(self, _in):
        # type: (Optional[str]) -> None
        input_int = input_tools.input_to_int(_in)
        self._duct_type = input_int or 1

    @property
    def insul_reflective(self):
        # type: () -> bool
        return self._insul_reflective

    @insul_reflective.setter
    def insul_reflective(self, _in):
        # type: (Optional[bool]) -> None
        if _in is None:
            self._insul_reflective = True
        else:
            self._insul_reflective = _in

    def _to_LbtLineSegments3D(self, _input):
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
                # -- It is a PolylineCurve
                lbt_line_segments.extend(lbt_crv.segments)
            else:
                # -- It is a LineCurve
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
