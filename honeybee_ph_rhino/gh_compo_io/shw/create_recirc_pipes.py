# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Create SHW Recirculation Pipes."""

try:
    from typing import Any, Dict, List, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from ladybug_geometry.geometry3d.polyline import LineSegment3D, Polyline3D
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_geometry:\n\t{}".format(e))

try:
    from ladybug_rhino.togeometry import to_polyline3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee_phhvac import hot_water_piping
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_utils.input_tools import clean_get
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class _RecircPipeBuilder(object):
    """Interface for collect and clean DHW Recirculation Piping user-inputs

    Note: Following the LBT convention, the line-geometry may be stored in any units (m, mm, inch, etc).
    All non-line-geometry data like thickness, conductivity, temp. etc. must always be in SI units.
    """

    display_name = ghio_validators.HBName("display_name", default="_unnamed_recirc_pipe_")
    diameter_mm = ghio_validators.UnitMM("diameter_mm", default="25.4 MM")
    insul_thickness_mm = ghio_validators.UnitMM("insul_thickness_mm", default="25.4 MM")
    insul_conductivity = ghio_validators.UnitW_MK("insul_conductivity", default=0.04)
    daily_period = ghio_validators.FloatMax24("daily_period", default=24)
    water_temp_c = ghio_validators.UnitDegreeC("water_temp_c", default="60.0 C")

    def __init__(
        self,
        IGH,
        _geometry,
        _name="_unnamed_",
        _diameter_mm="025.4 MM",
        _insul_thickness_mm="25.4 MM",
        _insul_conductivity="0.04 W/MK",
        _insul_reflective=True,
        _insul_quality=None,
        _daily_period=24.0,
        _water_temp_c="60.0 DEG-C",
    ):
        # type: (gh_io.IGH, Union[Polyline3D, LineSegment3D], str, str, str, str, bool, None, float, str) -> None
        self.IGH = IGH
        self.geometry = _geometry
        self.display_name = _name
        self.diameter_mm = _diameter_mm
        self.insul_thickness_mm = _insul_thickness_mm
        self.insul_conductivity = _insul_conductivity
        self.insul_reflective = _insul_reflective
        self.insul_quality = _insul_quality
        self.daily_period = _daily_period
        self.water_temp_c = _water_temp_c

    def _convert_to_polyline(self, _input):
        """Try to convert input geometry to a Rhino Polyline object."""
        cps = self.IGH.ghpythonlib_components.ControlPoints(_input).points
        return self.IGH.ghpythonlib_components.PolyLine(cps, False)

    @property
    def geometry(self):
        # type: () -> Union[Polyline3D, LineSegment3D]
        return self._geometry

    @geometry.setter
    def geometry(self, _input):
        # type: (Union[Polyline3D, LineSegment3D]) -> None
        try:
            self._geometry = to_polyline3d(_input)
        except:
            try:
                self._geometry = to_polyline3d(self._convert_to_polyline(_input))
            except Exception as e:
                raise Exception(
                    "{}\nError: Geometry input {} cannot be converted to an LBT Polyline3D?".format(e, _input)
                )

    def create_hbph_dhw_recirc_pipe(self):
        # type: () -> hot_water_piping.PhHvacPipeElement
        hbph_obj = hot_water_piping.PhHvacPipeElement()
        hbph_obj.display_name = self.display_name

        # If its a Polyline3D or LineSegment3D
        segments = getattr(self.geometry, "segments", [self.geometry])

        for segment in segments:
            hbph_obj.add_segment(
                hot_water_piping.PhHvacPipeSegment(
                    segment,
                    float(self.diameter_mm),
                    float(self.insul_thickness_mm),
                    float(self.insul_conductivity),
                    self.insul_reflective,
                    self.insul_quality,
                    self.daily_period,
                    float(self.water_temp_c),
                )
            )

        return hbph_obj


class GHCompo_CreateSHWRecircPipes(object):
    """Component Interface"""

    def __init__(
        self,
        _IGH,
        _geometry,
        _name,
        _diameter_mm,
        _insul_thickness_mm,
        _insul_conductivity,
        _insul_reflective,
        _insul_quality,
        _daily_period,
        _water_temp_c,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, List[Union[Polyline3D, LineSegment3D]], List[str], List[str], List[str], List[str], List[bool], List, List[float], List[str], *Any, **Any) -> None
        self.IGH = _IGH
        self.geometry = _geometry
        self.name = _name
        self.diameter_mm = _diameter_mm
        self.insul_thickness_mm = _insul_thickness_mm
        self.insul_conductivity = _insul_conductivity
        self.insul_reflective = _insul_reflective
        self.insul_quality = _insul_quality
        self.daily_period = _daily_period
        self.water_temp_c = _water_temp_c

    def collection_input_data(self):
        # type: () -> List[Dict[str, Any]]
        input_data = []
        for i in range(len(self.geometry)):
            input_data.append(
                {
                    "IGH": self.IGH,
                    "_geometry": clean_get(self.geometry, i),
                    "_name": clean_get(self.name, i, "_unnamed_"),
                    "_diameter_mm": clean_get(self.diameter_mm, i, "25.4 MM"),
                    "_insul_thickness_mm": clean_get(self.insul_thickness_mm, i, "25.4 MM"),
                    "_insul_conductivity": clean_get(self.insul_conductivity, i, "0.04 W/MK"),
                    "_insul_reflective": clean_get(self.insul_reflective, i, True),
                    "_insul_quality": clean_get(self.insul_quality, i, None),
                    "_daily_period": clean_get(self.daily_period, i, 24),
                    "_water_temp_c": clean_get(self.water_temp_c, i, "60.0 C"),
                }
            )
        return input_data

    def run(self):
        # type: () -> List[hot_water_piping.PhHvacPipeElement]
        dhw_recirc_piping_ = []
        for d in self.collection_input_data():
            recirc_pipe_builder = _RecircPipeBuilder(**d)
            dhw_recirc_piping_.append(recirc_pipe_builder.create_hbph_dhw_recirc_pipe())

        return dhw_recirc_piping_
