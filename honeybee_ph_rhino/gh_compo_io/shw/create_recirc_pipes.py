# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Create SHW Recirculation Pipes."""

try:
    from typing import Any, List, Union
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
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class _RecircPipeBuilder(object):
    """Interface for collect and clean DHW Recirculation Piping user-inputs"""

    diameter_m = ghio_validators.UnitM("diameter_m", default=0.0254)
    display_name = ghio_validators.HBName("display_name", default="_unnamed_recirc_pipe_")
    insul_thickness_m = ghio_validators.UnitM("insul_thickness_m", default=0.0254)
    insul_conductivity = ghio_validators.UnitW_MK("insul_conductivity", default=0.04)
    daily_period = ghio_validators.FloatMax24("daily_period", default=24)
    water_temp = ghio_validators.UnitDegreeC("water_temp", default=60)

    def __init__(
        self,
        IGH,
        _geometry,
        _name="_unnamed_",
        _diameter_m=0.0254,
        _insul_thickness_m=0.0254,
        _insul_conductivity=0.04,
        _insul_reflective=True,
        _insul_quality=None,
        _daily_period=24.0,
        _water_temp=60.0,
    ):
        # type: (gh_io.IGH, Union[Polyline3D, LineSegment3D], str, float, float, float, bool, None, float, float) -> None
        self.IGH = IGH
        self.geometry = _geometry
        self.display_name = _name
        self.diameter_m = _diameter_m
        self.insul_thickness_m = _insul_thickness_m
        self.insul_conductivity = _insul_conductivity
        self.insul_reflective = _insul_reflective
        self.insul_quality = _insul_quality
        self.daily_period = _daily_period
        self.water_temp = _water_temp

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

        try:
            # If its a Polyline3D
            segments = self.geometry.segments
        except AttributeError:
            # If its a single LineSegment3D
            segments = [self.geometry]

        for segment in segments:
            hbph_obj.add_segment(
                hot_water_piping.PhHvacPipeSegment(
                    segment,
                    self.diameter_m,
                    self.insul_thickness_m,
                    self.insul_conductivity,
                    self.insul_reflective,
                    self.insul_quality,
                    self.daily_period,
                    self.water_temp,
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
        _diameter_m,
        _insul_thickness_m,
        _insul_conductivity,
        _insul_reflective,
        _insul_quality,
        _daily_period,
        _water_temp,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, List[Union[Polyline3D, LineSegment3D]], List[str], List[float], List[float], List[float], List[bool], List[None], List[float], List[float], *Any, **Any) -> None
        self.IGH = _IGH
        self.geometry = _geometry
        self.name = _name
        self.diameter_m = _diameter_m
        self.insul_thickness_m = _insul_thickness_m
        self.insul_conductivity = _insul_conductivity
        self.insul_reflective = _insul_reflective
        self.insul_quality = _insul_quality
        self.daily_period = _daily_period
        self.water_temp = _water_temp

    def run(self):
        # type: () -> List[hot_water_piping.PhHvacPipeElement]
        dhw_recirc_piping_ = []
        for i in range(len(self.geometry)):
            recirc_pipe_builder = _RecircPipeBuilder(
                self.IGH,
                input_tools.clean_get(self.geometry, i),
                input_tools.clean_get(self.name, i, "_unnamed_"),
                input_tools.clean_get(self.diameter_m, i, 0.0254),
                input_tools.clean_get(self.insul_thickness_m, i, 0.0254),
                input_tools.clean_get(self.insul_conductivity, i, 0.04),
                input_tools.clean_get(self.insul_reflective, i, True),
                input_tools.clean_get(self.insul_quality, i, None),
                input_tools.clean_get(self.daily_period, i, 24),
                input_tools.clean_get(self.water_temp, i, 60.0),
            )

            dhw_recirc_piping_.append(recirc_pipe_builder.create_hbph_dhw_recirc_pipe())

        return dhw_recirc_piping_
