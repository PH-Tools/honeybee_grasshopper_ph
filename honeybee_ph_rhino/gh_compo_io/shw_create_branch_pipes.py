# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Create SHW Branch Pipes."""

try:
    from typing import Union, List
except ImportError:
    pass  # IronPython 2.7

from ladybug_rhino.togeometry import to_polyline3d
from ladybug_geometry.geometry3d.polyline import Polyline3D, LineSegment3D

from honeybee_energy_ph.hvac import hot_water
from honeybee_ph_rhino import gh_io
from honeybee_ph_rhino.gh_compo_io import ghio_validators
from honeybee_ph_utils import input_tools


class _BranchPipeBuilder(object):
    """Interface for collect and clean DHW Branch Piping user-inputs"""

    diameter = ghio_validators.UnitM("diameter", default=0.0127)
    display_name = ghio_validators.HBName(
        "display_name", default="_unnamed_branch_pipe_")

    def __init__(self, IGH, _geometry, _name, _diameter):
        # type: (gh_io.IGH, Union[Polyline3D, LineSegment3D], str, float) -> None
        self.IGH = IGH
        self.geometry = _geometry
        self.display_name = _name
        self.diameter = _diameter

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
                self._geometry = to_polyline3d(
                    self._convert_to_polyline(_input))
            except Exception as e:
                raise Exception(
                    "{}\nError: Geometry input {} cannot be converted to an LBT Polyline3D?".format(
                        e, _input)
                )

    def create_hbph_dhw_branch_pipe(self):
        # type: () -> hot_water.PhPipeElement
        hbph_obj = hot_water.PhPipeElement()
        hbph_obj.display_name = self.display_name

        try:
            # If its a Polyline3D
            segments = self.geometry.segments
        except AttributeError:
            # If its a single LineSegment3D
            segments = [self.geometry]

        for segment in segments:
            hbph_obj.add_segment(
                hot_water.PhPipeSegment(segment, self.diameter)
            )

        return hbph_obj

 
class GHCompo_CreateSHWBranchPipes(object):
    """Component Interface"""
    
    def __init__(self, _IGH, _geometry, _name, _diameter):
        self.IGH = _IGH
        self.geometry = _geometry
        self.name = _name
        self.diameter = _diameter

    def run(self):
        # type: () -> List[hot_water.PhPipeElement]
        dhw_branch_piping_ = []
        
        for i in range(len(self.geometry)):
            branch_pipe_builder = _BranchPipeBuilder(
                    self.IGH,
                    input_tools.clean_get(self.geometry, i),
                    input_tools.clean_get(self.name, i, "_unnamed_"),
                    input_tools.clean_get(self.diameter, i),
                )
            dhw_branch_piping_.append(branch_pipe_builder.create_hbph_dhw_branch_pipe())
        
        return dhw_branch_piping_