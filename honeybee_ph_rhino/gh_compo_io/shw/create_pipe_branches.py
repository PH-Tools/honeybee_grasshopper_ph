# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Create SHW Pipe | Branches."""

try:
    from typing import Any, Collection, Dict, List, Union
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
    from honeybee_ph_utils.input_tools import clean_get, input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class _BranchPipeBuilder(object):
    """Interface for collect and clean DHW 'Branch' Piping user-inputs"""

    display_name = ghio_validators.HBName("display_name", default="_unnamed_branch_pipe_")

    def __init__(
        self,
        IGH,
        dhw_fixtures,
        display_name,
        pipe_material,
        pipe_diameter,
        geometry,
    ):
        # type: (gh_io.IGH, List, str, int, int, Union[Polyline3D, LineSegment3D]) -> None
        self.IGH = IGH
        self.dhw_fixtures = dhw_fixtures
        self.display_name = display_name
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
            self._geometry = to_polyline3d(_input)
        except:
            try:
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

    def create_hbph_dhw_branch_pipe(self):
        # type: () -> hot_water_piping.PhHvacPipeBranch
        """Create a Honeybee 'PhPipeBranch' object for a DHW Branch Pipe."""

        # -- Build the new PH-Branch
        hbph_obj = hot_water_piping.PhHvacPipeBranch()
        hbph_obj.display_name = self.display_name

        for segment in self.geometry_segments:
            hbph_obj.pipe_element.add_segment(
                hot_water_piping.PhHvacPipeSegment(
                    _geom=segment,
                    _diameter=self.pipe_diameter,
                    _insul_thickness=0.0,
                    _insul_conductivity=0.04,
                    _insul_refl=False,
                    _insul_quality=None,
                    _daily_period=24,
                    _material=self.pipe_material,
                )
            )

        # -- Add the Fixture piping
        for hbph_fixture in self.dhw_fixtures:
            hbph_obj.add_fixture(hbph_fixture)

        return hbph_obj


class GHCompo_CreateSHWBranchPipes(object):
    """Component Interface"""

    def __init__(
        self,
        _IGH,
        _dhw_fixtures,
        _display_name,
        _pipe_material,
        _pipe_diameter,
        _geometry,
    ):
        # type: (gh_io.IGH, List[hot_water_piping.PhHvacPipeElement], List[str],  List[str], List[str], List[Union[Polyline3D, LineSegment3D]]) -> None
        self.IGH = _IGH
        self.dhw_fixtures = _dhw_fixtures
        self.display_name = _display_name
        self.pipe_material = _pipe_material
        self.pipe_diameter = _pipe_diameter
        self.geometry = _geometry

    def collect_branch_data(self):
        # type: () -> List[Dict]
        """Organize all the input data, fill in any missing bits using 'clean_get'."""
        branch_data = []
        for i in range(len(self.geometry)):
            branch_data.append(
                {
                    "IGH": self.IGH,
                    "dhw_fixtures": self.dhw_fixtures,
                    "display_name": clean_get(self.display_name, i, "_unnamed_Branch_"),
                    "pipe_material": input_to_int(clean_get(self.pipe_material, i, "2")),
                    "pipe_diameter": input_to_int(clean_get(self.pipe_diameter, i, "2")),
                    "geometry": self.geometry[i],
                }
            )

        return branch_data

    def run(self):
        # type: () -> List[hot_water_piping.PhHvacPipeElement]
        dhw_branch_piping_ = []

        for branch_data in self.collect_branch_data():
            branch_pipe_builder = _BranchPipeBuilder(**branch_data)
            dhw_branch_piping_.append(branch_pipe_builder.create_hbph_dhw_branch_pipe())

        return dhw_branch_piping_
