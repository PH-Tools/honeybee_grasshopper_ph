# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Shading Factor Settings - LBT Rad."""


try:
    from typing import Any, Optional
except ImportError:
    pass  # IronPython

try:
    import Rhino.Geometry as rg  # type: ignore
except ImportError:
    pass  # Outside Grasshopper

try:
    from honeybee_ph_utils import sky_matrix
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
    from ph_units.unit_type import Unit
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


class HBPH_LBTRadSettings:
    """LBT Radiation Solver Settings."""

    def __init__(self, _wsm, _ssm, _mshp, _gs, _lgp, _cpus, _win_mshp=None):
        # type: (Any, Any, rg.MeshingParameters, float, Any, Optional[int], Optional[rg.MeshingParameters]) -> None
        self.winter_sky_matrix = _wsm
        self.summer_sky_matrix = _ssm
        self.mesh_params = _mshp
        self.grid_size = _gs
        self.legend_par = _lgp
        self.cpus = _cpus
        self.window_mesh_params = _win_mshp

    def __str__(self):
        return "{}()".format(self.__class__.__name__)

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)


class GHCompo_CreateLBTRadSettings(object):
    """Interface for LBT Radiation Solver Settings."""

    # -- Defaults
    winter_period = (10, 3)  # October 1 to March 31
    summer_period = (6, 9)  # June 1 to September 30'

    def __init__(
        self,
        _IGH,
        _epw_file=None,
        _north=None,
        _winter_sky_matrix=None,
        _summer_sky_matrix=None,
        _mesh_params=None,
        _grid_size=None,
        _legend_par=None,
        _cpus=None,
        _window_mesh_params=None,
    ):
        # type: (gh_io.IGH, str | None, float | None, Any, Any, rg.MeshingParameters | None, str | None, Any, int | None, rg.MeshingParameters | None) -> None
        self.IGH = _IGH
        self.epw_file = _epw_file
        self.north = _north
        self.winter_sky_matrix = _winter_sky_matrix
        self.summer_sky_matrix = _summer_sky_matrix
        self.mesh_params = _mesh_params or rg.MeshingParameters.Default
        self.grid_size_in_rhino_doc_units = _grid_size
        self.legend_par = _legend_par or None
        self.cpus = _cpus or None
        self.window_mesh_params = _window_mesh_params

    @property
    def winter_sky_matrix(self):
        return self._winter_sky_matrix

    @winter_sky_matrix.setter
    def winter_sky_matrix(self, _in):
        if _in:
            self._winter_sky_matrix = _in
        elif self.epw_file:
            self._winter_sky_matrix = sky_matrix.gen_matrix(self.epw_file, self.winter_period, self.north)
        else:
            self._winter_sky_matrix = None

    @property
    def summer_sky_matrix(self):
        return self._summer_sky_matrix

    @summer_sky_matrix.setter
    def summer_sky_matrix(self, _in):
        if _in:
            self._summer_sky_matrix = _in
        elif self.epw_file:
            self._summer_sky_matrix = sky_matrix.gen_matrix(self.epw_file, self.summer_period, self.north)
        else:
            self._summer_sky_matrix = None

    @property
    def grid_size_in_rhino_doc_units(self):
        # type: () -> Unit
        return self._grid_size_in_rhino_doc_units

    @grid_size_in_rhino_doc_units.setter
    def grid_size_in_rhino_doc_units(self, _input):
        # type: (Optional[str]) -> None
        """Set the grid-size to use for the radiation analysis mesh, considering Rhino unit-types."""

        if _input is None:
            input_value, input_unit = "152.4", "MM"  # default = 6-INCH
        else:
            input_value, input_unit = parse_input(_input)

        # -- Be sure to convert the input to the active Rhino-doc's unit-type
        target_unit = self.IGH.get_rhino_unit_system_name()
        grid_size = convert(input_value, input_unit or target_unit, target_unit)

        if not grid_size:
            raise ValueError("Failed to understand the grid-size input of: '{}'?".format(_input))
        else:
            print("Converting: {} {} -> {:.4f} {}".format(input_value, input_unit, grid_size, target_unit))
            self._grid_size_in_rhino_doc_units = Unit(value=grid_size, unit=target_unit)

    def check_grid_size(self):
        # type: () -> None
        """Check the grid size and issue a warning if it seems too small (less than 4-inch)."""

        THRESHOLD_IN_INCHES = Unit("4", "INCH")
        THRESHOLD_IN_RH_DOC_UNITS = THRESHOLD_IN_INCHES.as_a(self.IGH.get_rhino_unit_system_name())

        if self._grid_size_in_rhino_doc_units < THRESHOLD_IN_RH_DOC_UNITS:
            msg = (
                "WARNING: The analysis grid size is set to {:.3f}-{} x {:.3f}-{}. "
                "This is very small and will likely result in long calculation times. "
                "Are you really sure you need an analysis grid with segments "
                "this small? If so, you can proceed, but expect slow execution.".format(
                    self._grid_size_in_rhino_doc_units.value,
                    self._grid_size_in_rhino_doc_units.unit,
                    self._grid_size_in_rhino_doc_units.value,
                    self._grid_size_in_rhino_doc_units.unit,
                )
            )
            print(msg)
            self.IGH.warning(msg)
        else:
            msg = "Analysis grid size is set to {:.3f}-{} x {:.3f}-{}. ".format(
                self._grid_size_in_rhino_doc_units.value,
                self._grid_size_in_rhino_doc_units.unit,
                self._grid_size_in_rhino_doc_units.value,
                self._grid_size_in_rhino_doc_units.unit,
            )
            print(msg)

    def run(self):
        # type: () -> Optional[HBPH_LBTRadSettings]
        if not self.winter_sky_matrix or not self.summer_sky_matrix:
            return None

        self.check_grid_size()

        hbph_obj = HBPH_LBTRadSettings(
            self.winter_sky_matrix,
            self.summer_sky_matrix,
            self.mesh_params,
            self.grid_size_in_rhino_doc_units.value,
            self.legend_par,
            self.cpus,
            self.window_mesh_params,
        )
        return hbph_obj
