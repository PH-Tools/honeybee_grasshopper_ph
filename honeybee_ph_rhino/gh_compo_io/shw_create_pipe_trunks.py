# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Create SHW Pipe | Trunks."""

try:
    from typing import Any, Collection, Dict, List, Union
except ImportError:
    pass  # IronPython 2.7

from honeybee_energy_ph.hvac import hot_water
from honeybee_ph_utils.input_tools import clean_get, input_to_int
from ladybug_geometry.geometry2d.pointvector import Point2D
from ladybug_geometry.geometry2d.polyline import Polyline2D
from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
from ladybug_geometry.geometry3d.polyline import LineSegment3D, Polyline3D
from ladybug_rhino.togeometry import to_polyline3d

from honeybee_ph_rhino import gh_io
from honeybee_ph_rhino.gh_compo_io import ghio_validators


class _TrunkPipeBuilder(object):
    """Interface for collect and clean DHW 'Trunk' Piping user-inputs"""

    display_name = ghio_validators.HBName("display_name", default="_unnamed_trunk_pipe_")
    pipe_diameter_m = ghio_validators.UnitM("pipe_diameter_m", default=0.0127)

    def __init__(
        self,
        IGH,
        dhw_branches,
        multiplier,
        display_name,
        demand_recirculation,
        pipe_material,
        pipe_diameter,
        geometry,
    ):
        # type: (gh_io.IGH, List, int, str, bool, int, int, Union[Polyline3D, LineSegment3D]) -> None
        self.IGH = IGH
        self.dhw_branches = dhw_branches
        self.multiplier = multiplier
        self.display_name = display_name
        self.demand_recirculation = demand_recirculation
        self.pipe_material = pipe_material
        self.pipe_diameter = pipe_diameter
        self.geometry = geometry

    def _convert_to_polyline(self, _input):
        # type: (Any) -> Polyline3D
        """Try to convert input geometry to a Rhino Polyline object."""
        cps = self.IGH.ghpythonlib_components.ControlPoints(_input).points
        return self.IGH.ghpythonlib_components.PolyLine(cps, False)

    @property
    def geometry(self):
        # type: () -> Union[Polyline3D, LineSegment3D]
        return self._geometry

    @geometry.setter
    def geometry(self, _input):
        """Set geometry input. Will convert input to LBT-Polyline3D."""
        try:
            # -- First, assume it is Rhino geometry and convert it to an LBT Polyline3D
            self._geometry = to_polyline3d(_input)
        except:
            try:
                # -- If that fails, try and convert it to a Rhino Polyline, then an LBT one
                self._geometry = to_polyline3d(self._convert_to_polyline(_input))
            except Exception as e:
                raise Exception(
                    "{}\nError: Geometry input {} cannot be converted to an LBT Polyline3D?".format(e, _input)
                )

    @property
    def geometry_segments(self):
        # type: () -> Collection[LineSegment3D]
        if isinstance(self.geometry, LineSegment3D):
            return [self.geometry]
        elif isinstance(self.geometry, Polyline3D):
            return self.geometry.segments
        else:
            raise ValueError("Geometry input '{}' is not a Polyline3D or LineSegment3D?".format(type(self.geometry)))

    def create_hbph_dhw_trunk_pipe(self):
        # type: () -> hot_water.PhPipeTrunk
        """Create a Honeybee 'PhPipeTrunk' object for a DHW Trunk Pipe."""

        # -- Build the new PH-Trunk
        hbph_obj = hot_water.PhPipeTrunk()
        hbph_obj.display_name = self.display_name
        hbph_obj.multiplier = self.multiplier

        for geom_segment in self.geometry_segments:
            hbph_obj.pipe_element.add_segment(
                hot_water.PhPipeSegment(
                    _geom=geom_segment,
                    _diameter=self.pipe_diameter,
                    _insul_thickness_m=0.0,
                    _insul_conductivity=0.04,
                    _insul_refl=False,
                    _insul_quality=None,
                    _daily_period=24,
                    _material=self.pipe_material,
                )
            )

        # -- Add the Branch piping
        for hbph_branch in self.dhw_branches:
            if hasattr(hbph_branch, "fixtures"):
                # -- Its a branch, so just add it to the trunk
                hbph_obj.add_branch(hbph_branch)
            else:
                hbph_fixture = hbph_branch
                if len(hbph_obj.branches) == 0:
                    # -- Create a new branch, and add the input as a fixture
                    new_branch = hot_water.PhPipeBranch()
                    new_branch.display_name = self.display_name
                    new_branch.add_fixture(hbph_fixture)
                    hbph_obj.add_branch(new_branch)
                else:
                    # -- Host the fixture on the existing branch
                    hbph_obj.branches[0].add_fixture(hbph_fixture)

        return hbph_obj


class GHCompo_CreateSHWTrunkPipes(object):
    """Component Interface"""

    def __init__(
        self,
        _IGH,
        _dhw_branches,
        _multipliers,
        _display_name,
        _demand_recirculation,
        _pipe_material,
        _pipe_diameter,
        _geometry,
    ):
        # type: (gh_io.IGH, List[hot_water.PhPipeElement], List[int], List[str], List[bool], List[str], List[str], List[Union[Polyline3D, LineSegment3D]]) -> None
        self.IGH = _IGH
        self.dhw_branches = _dhw_branches
        self.multipliers = _multipliers
        self.display_name = _display_name
        self.demand_recirculation = _demand_recirculation
        self.pipe_material = _pipe_material
        self.pipe_diameter = _pipe_diameter
        self.geometry = _geometry

    def collect_trunk_data(self):
        # type: () -> List[Dict[str, Any]]
        """Organize all the input data, fill in any missing bits using 'clean_get'."""
        trunk_data = []
        for i in range(len(self.geometry)):
            trunk_data.append(
                {
                    "IGH": self.IGH,
                    "dhw_branches": self.dhw_branches,
                    "multiplier": clean_get(self.multipliers, i, 1),
                    "display_name": clean_get(self.display_name, i, "_unnamed_trunk_"),
                    "demand_recirculation": clean_get(self.demand_recirculation, i, False),
                    "pipe_material": input_to_int(clean_get(self.pipe_material, i, "2")),
                    "pipe_diameter": input_to_int(clean_get(self.pipe_diameter, i, "2")),
                    "geometry": self.geometry[i],
                }
            )

        return trunk_data

    def run(self):
        # type: () -> List[hot_water.PhPipeElement]
        dhw_trunk_piping_ = []

        for trunk_data in self.collect_trunk_data():
            trunk_pipe_builder = _TrunkPipeBuilder(**trunk_data)
            dhw_trunk_piping_.append(trunk_pipe_builder.create_hbph_dhw_trunk_pipe())

        return dhw_trunk_piping_
