# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Shading Factor Settings - LBT Rad."""

try:
    import Rhino.Geometry as rg  # type: ignore
except ImportError:
    pass  # Outside Grasshopper

try:
    from typing import Any, Optional
except ImportError:
    pass  # IronPython

try:
    from honeybee_ph_utils import sky_matrix
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


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
        _epw_file,
        _north,
        _winter_sky_matrix,
        _summer_sky_matrix,
        _mesh_params,
        _grid_size,
        _legend_par,
        _cpus,
        _window_mesh_params=None,
    ):
        # type: (gh_io.IGH, str, float, Any, Any, rg.MeshingParameters, float, Any, Optional[int], Optional[rg.MeshingParameters]) -> None
        self.IGH = _IGH
        self.epw_file = _epw_file
        self.north = _north
        self.winter_sky_matrix = _winter_sky_matrix
        self.summer_sky_matrix = _summer_sky_matrix
        self.mesh_params = _mesh_params or rg.MeshingParameters.Default
        self.grid_size = _grid_size or 1.0
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
            self._winter_sky_matrix = sky_matrix.gen_matrix(
                self.epw_file, self.winter_period, self.north
            )
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
            self._summer_sky_matrix = sky_matrix.gen_matrix(
                self.epw_file, self.summer_period, self.north
            )
        else:
            self._summer_sky_matrix = None

    def run(self):
        # type: () -> Optional[HBPH_LBTRadSettings]
        if not self.winter_sky_matrix or not self.summer_sky_matrix:
            return None

        hbph_obj = HBPH_LBTRadSettings(
            self.winter_sky_matrix,
            self.summer_sky_matrix,
            self.mesh_params,
            self.grid_size,
            self.legend_par,
            self.cpus,
            self.window_mesh_params,
        )
        return hbph_obj
