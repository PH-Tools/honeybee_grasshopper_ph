# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Create Ventilation Duct"""

try:
    from typing import Union, Optional, List
except ImportError:
    pass  # IronPython 2.7

try:
    from ladybug_rhino.togeometry import to_polyline3d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:
    from ladybug_geometry.geometry3d.polyline import Polyline3D, LineSegment3D
    from ladybug_geometry.geometry3d.pointvector import Point3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from honeybee_energy_ph.hvac import ducting
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))


class GHCompo_CreateVentDuct(object):
    """Component Interface"""
    
    display_name = ghio_validators.HBName("display_name")
    insul_thickness = ghio_validators.UnitMM("insul_thickness")
    insul_conductivity = ghio_validators.UnitW_MK("insul_conductivity")
    diameter = ghio_validators.UnitMM("diameter")
    height = ghio_validators.UnitMM("height")
    width = ghio_validators.UnitMM("width")

    def __init__(self,
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
        # type: (gh_io.IGH, Union[Polyline3D, LineSegment3D], str, int, float, float, bool, float, Optional[float], Optional[float]) -> None
        self.IGH = _IGH
        self.geometry = _geometry
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

    @property
    def geometry(self):
        # type: () -> Union[Polyline3D, LineSegment3D]
        return self._geometry

    @property
    def _default_geometry(self):
        # type: () -> LineSegment3D
        pt1 = Point3D(0,0,0)
        pt2 = Point3D(1,0,0)
        return LineSegment3D.from_end_points(pt1, pt2)

    @property
    def geometry_segments(self):
        # type: () -> List[LineSegment3D]
        if hasattr(self.geometry, "segments"):
            # If its a Polyline3D
            return self.geometry.segments
        else:
            # If its a single LineSegment3D
            return [self.geometry]

    @geometry.setter
    def geometry(self, _input):
        # type: (Union[Polyline3D, LineSegment3D]) -> None
        if not _input:
            self._geometry = self._default_geometry
            return None
        
        try:
            self._geometry = to_polyline3d(_input)
        except:
            try:
                self._geometry = to_polyline3d(self._convert_to_polyline(_input))
            except Exception as e:
                raise Exception(
                    "{}\nError: Geometry input {} cannot be converted " \
                        "to an LBT Polyline3D?".format(e, _input)
                )
    
    def _convert_to_polyline(self, _input):
        # type: (Union[Polyline3D, LineSegment3D]) -> Polyline3D
        """Try to convert input geometry to a Rhino Polyline object."""
        cps = self.IGH.ghpythonlib_components.ControlPoints(_input).points
        return self.IGH.ghpythonlib_components.PolyLine(cps, False)

    def run(self):
        # type: () -> Optional[ducting.PhDuctElement]
        if not self.geometry:
            return None

        hbph_obj = ducting.PhDuctElement()
        hbph_obj.display_name = self.display_name
        hbph_obj.duct_type = self.duct_type

        for geometry in self.geometry_segments:
            hbph_obj.add_segment(
                ducting.PhDuctSegment(geometry,
                                      self.insul_thickness,
                                      self.insul_conductivity,
                                      self.insul_reflective,
                                      self.diameter,
                                      self.height,
                                      self.width,
                                      )
            )

        return hbph_obj
        