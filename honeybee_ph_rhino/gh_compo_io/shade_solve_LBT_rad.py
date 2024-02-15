# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Shading Factors - LBT Rad."""

import math

try:
    from itertools import izip as zip  # type: ignore
except:
    pass  # Python3

try:
    from typing import Any, Collection, List, Optional, Tuple
except ImportError:
    pass  # IronPython

try:
    from System import Object  # type: ignore
except ImportError as e:
    raise ImportError("\nFailed to import System:\n\t{}".format(e))

try:
    import Rhino.Geometry as rg  # type: ignore
except ImportError as e:
    raise ImportError("\nFailed to import Rhino.Geometry:\n\t{}".format(e))

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
except ImportError as e:
    raise ImportError("\nFailed to import Grasshopper:\n\t{}".format(e))

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ladybug.graphic import GraphicContainer
    from ladybug.viewsphere import view_sphere
except ImportError as e:
    raise ImportError("\nFailed to import ladybug:\n\t{}".format(e))

try:
    from ladybug_geometry.geometry3d import Mesh3D, Point3D
    from ladybug_rhino.fromgeometry import from_mesh3d, from_point3d, from_vector3d
    from ladybug_rhino.fromobjects import legend_objects
    from ladybug_rhino.grasshopper import de_objectify_output
    from ladybug_rhino.intersect import intersect_mesh_rays
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.togeometry import to_joined_gridded_mesh3d, to_mesh3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io.shade_create_bldg_shd import (
        create_inset_aperture_surface,
    )
    from honeybee_ph_rhino.gh_compo_io.shade_LBT_rad_settings import HBPH_LBTRadSettings
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

# Radiation and Shading Factor Calcs
# -----------------------------------------------------------------------------


def hbph_to_joined_gridded_mesh3d(
    geometry, grid_size, offset_distance=0, _mesh_params=None
):
    # type: (Any, float, float, Optional[rg.MeshingParameters]) -> Mesh3D
    """
    ------------------------------------------------------------------
    ADAPTED FROM LADYBUG ladybug_rhino.togeometry.to_joined_gridded_mesh3d()
    in order to allow for custom Mesh Param settings.
    ------------------------------------------------------------------

    Create a single gridded Ladybug Mesh3D from an array of Rhino geometry.

    Args:
        * breps: An array of Rhino Breps and/or Rhino meshes that will be converted
            into a single, joined gridded Ladybug Mesh3D.

        * grid_size: A number for the grid size dimension with which to make the mesh.

        * offset_distance: A number for the distance at which to offset the mesh from
            the underlying brep. The default is 0.
    """
    lb_meshes = []
    for geo in geometry:
        if isinstance(geo, rg.Brep):
            lb_meshes.append(
                hbph_to_gridded_mesh3d(geo, grid_size, offset_distance, _mesh_params)
            )
        else:  # assume that it's a Mesh
            lb_meshes.append(to_mesh3d(geo))
    if len(lb_meshes) == 1:
        return lb_meshes[0]
    else:
        return Mesh3D.join_meshes(lb_meshes)


def hbph_to_gridded_mesh3d(brep, grid_size, offset_distance=0, _mesh_params=None):
    # type: (Any, float, float, Optional[rg.MeshingParameters]) -> Mesh3D
    """
    ------------------------------------------------------------------
    ADAPTED FROM LADYBUG ladybug_rhino.togeometry.to_gridded_mesh3d()
    in order to allow for custom Mesh Param settings.
    ------------------------------------------------------------------

    Create a gridded Ladybug Mesh3D from a Rhino Brep.

    This is useful since Rhino's grid meshing is often more beautiful than what
    ladybug_geometry can produce. However, the ladybug_geometry Face3D.get_mesh_grid
    method provides a workable alternative to this if it is needed.

    Args:
        * brep: Any:
            A Rhino Brep that will be converted into a gridded Ladybug Mesh3D.
        * grid_size: float:
            A number for the grid size dimension with which to make the mesh.
        * offset_distance: float:
            A number for the distance at which to offset the mesh from
            the underlying brep. The default is 0.
        * _mesh_params: Optional[rg.MeshingParameters]
            Optional Rhino Meshing Parameters to use for the meshing.
    """
    # -------------------------------------------------------------------------
    # Mesh the brep using the supplied Params
    mesh_grids = rg.Mesh.CreateFromBrep(brep, _mesh_params)

    # -------------------------------------------------------------------------
    # Join the meshes into one
    if len(mesh_grids) == 1:  # only one mesh was generated
        mesh_grid = mesh_grids[0]
    else:  # join the meshes into one
        mesh_grid = rg.Mesh()
        for m_grid in mesh_grids:
            mesh_grid.Append(m_grid)

    # -------------------------------------------------------------------------
    # Offset the mesh, if necessary
    if offset_distance != 0:
        temp_mesh = rg.Mesh()
        mesh_grid.Normals.UnitizeNormals()
        for pt, vec in zip(mesh_grid.Vertices, mesh_grid.Normals):
            temp_mesh.Vertices.Add(pt + (rg.Vector3f.Multiply(vec, offset_distance)))
        for face in mesh_grid.Faces:
            temp_mesh.Faces.AddFace(face)
        mesh_grid = temp_mesh

    return to_mesh3d(mesh_grid)


def create_shading_mesh(_bldg_shading_breps, _mesh_params):
    # type: (Collection[rg.Brep], rg.MeshingParameters) -> rg.Mesh
    """Return a single new Rhino.Geometry.Mesh built from all the input shading surface Breps."""

    shade_mesh = rg.Mesh()
    for brep in _bldg_shading_breps:
        new_mesh = rg.Mesh.CreateFromBrep(brep, _mesh_params)
        if new_mesh:
            shade_mesh.Append(new_mesh)
        else:
            surface_name = brep.GetUserStrings().Get("display_name")
            msg = (
                "Error: Something is wrong with surface: {}. \n"
                "Cannot create a mesh properly for some reason. \n"
                "Check that all your geometry is correct with no overlaps or voids \n"
                "and check that the Honeybee surfaces are all being created correctly? \n"
                "If that surface has windows hosted on it, be sure the windows are not \n"
                "overlapping and that they are being generated correctly?".format(
                    surface_name
                )
            )
            raise Exception(msg)

    return shade_mesh


def deconstruct_sky_matrix(_sky_mtx):
    # type: (Any) -> Tuple[List[rg.Vector3d], List[float]]
    """Copied from Ladybug 'IncidentRadiation' Component

    Arguments:
    ----------
        * _sky_mtx: A Ladybug Sky Matrix for the season

    Returns:
    --------
        * [Tuple]
            - [0] sky_vecs: (List[rg.Vector3d])
            - [1] total_sky_rad: (list[float])
    """

    mtx = de_objectify_output(_sky_mtx)
    total_sky_rad = [dir_rad + dif_rad for dir_rad, dif_rad in zip(mtx[1], mtx[2])]
    lb_vecs = (
        view_sphere.tregenza_dome_vectors
        if len(total_sky_rad) == 145
        else view_sphere.reinhart_dome_vectors
    )
    if mtx[0][0] != 0:  # there is a north input for sky; rotate vectors
        north_angle = math.radians(mtx[0][0])
        lb_vecs = [vec.rotate_xy(north_angle) for vec in lb_vecs]
    sky_vecs = [from_vector3d(vec) for vec in lb_vecs]

    return (sky_vecs, total_sky_rad)


def build_window_meshes(
    _window_surface, _grid_size, _shading_mesh_params, _window_mesh_params=None
):
    # type: (Any, float, rg.MeshingParameters, Optional[rg.MeshingParameters]) -> Tuple[List[Point3D], List[Normal], Mesh3D, Optional[Mesh3D], rg.Mesh]
    """Create the Ladybug Mesh3D grided mesh for the window being analyzed

    Arguments:
    ----------
        * _window_surface: (Brep) A single window Brep from the scene
        * _grid_size: (float)
        * _shading_mesh_params: (Rhino.Geometry.MeshingParameters)
        * _window_mesh_params: (Rhino.Geometry.MeshingParameters)

    Returns: (tuple)
        * points: (list: Ladybug Point3D) All the analysis points on the window
        * normals: (list: Ladybug Normal) All the normals for the analysis points
        * window_mesh: (ladybug_geometry.geometry3d.Mesh3D) The window
        * window_back_mesh: (Optional[ladybug_geometry.geometry3d.Mesh3D]) A copy of the window shifted 'back'
            just a little bit (0.1 units). Used when solving the 'unshaded' situation.
        * window_rh_mesh: (Rhino.Geometry.Mesh): The window as a Rhino-Mesh
    """

    # Create the gridded mesh for the window surface
    # ---------------------------------------------------------------------------
    offset_dist = 0.001
    if not _window_mesh_params:
        window_mesh = to_joined_gridded_mesh3d([_window_surface], _grid_size, offset_dist)  # type: ignore
        # -- If no custom params are supplied, use the standard Ladybug method
    else:
        # -- otherwise, use the custom settings provided by the user
        window_mesh = hbph_to_joined_gridded_mesh3d(
            [_window_surface], _grid_size, offset_dist, _window_mesh_params
        )

    if not window_mesh:
        raise Exception(
            "Failed to create a mesh for the window surface {}.".format(_window_surface)
        )
    window_rh_mesh = from_mesh3d(window_mesh)
    points = [from_point3d(pt) for pt in window_mesh.face_centroids]
    normals = [from_vector3d(vec) for vec in window_mesh.face_normals]

    # Create a 'back' for the window
    # ---------------------------------------------------------------------------
    # Mostly this is done so it can be passed to the ladybug_rhino.intersect.intersect_mesh_rays()
    # solver as a surface which is certain to *not* shade the window at all
    window_back_mesh = None
    for sr in _window_surface.Surfaces:
        window_normal = sr.NormalAt(0.5, 0.5)
        window_normal.Unitize()
        window_normal = window_normal * -1 * 0.1

        window_back = _window_surface.Duplicate()
        window_back.Translate(window_normal)
        window_back_mesh = rg.Mesh.CreateFromBrep(window_back, _shading_mesh_params)[0]

    return points, normals, window_mesh, window_back_mesh, window_rh_mesh


def generate_intersection_data(
    _shade_mesh, _win_mesh_back, _points, _sky_vecs, _normals, _cpu_count
):
    """Creates all the Intersection Matrix data for both the Shaded and the UNShaded conditions

    Note that for the 'Unshaded' case you still have to pass the solver *something*, so
    the _win_mesh_back is used for this case. This surface should block out any radiation coming from
    'behind' and also not interfere with the front-side radiation calculation.

    Adapted from Ladybug 'IncidentRadiation' Component

    Arguments:
        _shade_mesh: (Mesh) The context shading joined mesh
        _win_mesh_back: (Mesh) The window surface pushed 'back' a little.
        _points: (_)
        _sky_vecs: (_)
        _normals: (list: Ladybug Normals)
        _parallel: (int | None)
    Returns: (tuple)
        int_matrix_init_shaded: Intersection Matrix for window WITH shading
        int_matrix_init_unshaded: Intersection Matrix for window WITHOUT shading
        angles_s: Shaded
        angles_u: UN-Shaded
    """

    # intersect the rays with the mesh
    # ---------------------------------------------------------------------------
    int_matrix_init_shaded, angles_s = intersect_mesh_rays(
        _shade_mesh, _points, _sky_vecs, _normals, _cpu_count
    )

    int_matrix_init_unshaded, angles_u = intersect_mesh_rays(
        _win_mesh_back, _points, _sky_vecs, _normals, _cpu_count
    )

    return int_matrix_init_shaded, int_matrix_init_unshaded, angles_s, angles_u


def calc_win_radiation(_int_matrix_init, _angles, _total_sky_rad, _window_mesh):
    """Computes total kWh per window based on the int_matrix and sky vec angles

    Arguments:
        _int_matrix_init: (_)
        _angles: (_)
        _total_sky_rad: (_)
        _window_mesh: (ladybug_geometry.geometry3d.Mesh3D)
    Returns: (tuple)
        average_window_kWh: (float) The area-weighted average total kWh radiation
        for the window over the analysis period specified.
    """

    results_kWh = []
    window_face_areas = []
    int_matrix = []

    count = (k for k in range(len(_angles) * 10))  # just a super large counter

    for c, int_vals, angs in zip(count, _int_matrix_init, _angles):
        pt_rel = (ival * math.cos(ang) for ival, ang in zip(int_vals, angs))
        rad_result = sum(r * w for r, w in zip(pt_rel, _total_sky_rad))

        int_matrix.append(pt_rel)
        results_kWh.append(rad_result * _window_mesh.face_areas[c])
        window_face_areas.append(_window_mesh.face_areas[c])

    return results_kWh, window_face_areas


# Legend and Graphics
# -----------------------------------------------------------------------------


def create_graphic_container(_season, _data, _study_mesh, _legend_par):
    """Creates the Ladybug 'Graphic' Object from the result data

    Copied from Ladybug 'IncidentRadiation' Component

    Arguments:
        _season: (str) 'Winter' or 'Summer'. Used in the title.
        _data: (list: float:) A list of the result data to use to color / style the output
        _study_mesh: (ladybug_geometry.geometry3d.Mesh3D) The joined Mesh used in the analysis
        _legend_par: Ladybug Legend Parameters
    Returns: (tuple)
        graphic: (ladybug.graphic.GraphicContainer) The Ladybug Graphic Object
        title: The text title
    """

    graphic = GraphicContainer(_data, _study_mesh.min, _study_mesh.max, _legend_par)
    graphic.legend_parameters.title = "kWh"

    title = text_objects(
        "{} Incident Radiation".format(_season),
        graphic.lower_title_location,
        graphic.legend_parameters.text_height * 1.5,
        graphic.legend_parameters.font,
    )

    return graphic, title


def create_window_mesh(_lb_meshes):
    return Mesh3D.join_meshes(_lb_meshes)


def create_rhino_mesh(_graphic, _lb_mesh):
    """Copied from Ladybug 'IncidentRadiation' Component

    Arguments:
        _graphic: (ladybug.graphic.GraphicContainer) The Ladybug Graphic object
        _lb_mesh: (Ladybug Mesh) A single joined mesh of the entire scene
    Returns: (tuple)
        mesh: (_)
        legend: (_)
    """

    # Create all of the visual outputs

    _lb_mesh.colors = _graphic.value_colors
    mesh = from_mesh3d(_lb_mesh)
    legend = legend_objects(_graphic.legend)

    return mesh, legend


# Component Interface
# -----------------------------------------------------------------------------


class GHCompo_SolveLBTRad(object):
    def __init__(
        self,
        _IGH,
        _settings,
        _shading_surfaces_winter,
        _shading_surfaces_summer,
        _hb_rooms,
        _run,
    ):
        # type: (gh_io.IGH, HBPH_LBTRadSettings, List, List, List[room.Room], bool) -> None
        self.IGH = _IGH
        self.settings = _settings
        self.shading_surfaces_winter = _shading_surfaces_winter
        self.shading_surfaces_summer = _shading_surfaces_summer
        self.hb_rooms = _hb_rooms
        self.run_solver = _run

        # ---------------------------------------------------------------------
        if not self.settings:
            msg = "Please input _settings to calculate Radiation results."
            self.IGH.warning(msg)

        if not self.hb_rooms:
            msg = "Please input Honeybee Rooms to calculate Radiation results."
            self.IGH.warning(msg)

        if not self.run_solver:
            msg = "Please set _run to True in order to calculate Radiation results."
            self.IGH.warning(msg)

    def run(self):
        # type: () -> Tuple[Any, Any, List[float], Any, List[float],  List[room.Room], List[str]]

        if not self.run_solver or not self.settings or not self.hb_rooms:
            return (None, None, [], None, [], self.hb_rooms, [])

        # -- Get the current Rhino doc's unit system
        rh_units_name = self.IGH.get_rhino_unit_system_name()

        # -- Create context Shade meshes
        # ---------------------------------------------------------------------
        shade_mesh_winter = create_shading_mesh(
            self.shading_surfaces_winter, self.settings.mesh_params
        )
        shade_mesh_summer = create_shading_mesh(
            self.shading_surfaces_summer, self.settings.mesh_params
        )

        # Deconstruct the sky-matrix and get the sky dome vectors. Winter (w) and Summer (s)
        # ---------------------------------------------------------------------
        w_sky_vecs, w_total_sky_rad = deconstruct_sky_matrix(
            self.settings.winter_sky_matrix
        )
        s_sky_vecs, s_total_sky_rad = deconstruct_sky_matrix(
            self.settings.summer_sky_matrix
        )

        # Calc window surface shaded and unshaded radiation
        # ---------------------------------------------------------------------
        lb_window_meshes = []
        winter_radiation_shaded_ = DataTree[Object]()
        winter_radiation_shaded_detailed_ = DataTree[Object]()
        winter_radiation_unshaded_ = DataTree[Object]()
        summer_radiation_shaded_ = DataTree[Object]()
        summer_radiation_shaded_detailed_ = DataTree[Object]()
        summer_radiation_unshaded_ = DataTree[Object]()
        mesh_by_window = DataTree[Object]()

        win_count = 0
        hb_rooms_ = []
        for room in self.hb_rooms:
            new_room = room.duplicate()  # type: room.Room # type: ignore

            for face in new_room.faces:
                for aperture in face.apertures:
                    window_surface = create_inset_aperture_surface(
                        aperture, rh_units_name
                    )

                    # Build the meshes
                    # ----------------------------------------------------------------------
                    pts, nrmls, win_msh, win_msh_bck, rh_msh = build_window_meshes(
                        window_surface,
                        self.settings.grid_size,
                        self.settings.mesh_params,
                        self.settings.window_mesh_params,
                    )
                    lb_window_meshes.append(win_msh)

                    # Solve Winter
                    # ----------------------------------------------------------------------
                    args_winter = (
                        shade_mesh_winter,
                        win_msh_bck,
                        pts,
                        w_sky_vecs,
                        nrmls,
                        self.settings.cpus,
                    )

                    (
                        int_matrix_s,
                        int_matrix_u,
                        angles_s,
                        angles_u,
                    ) = generate_intersection_data(*args_winter)
                    w_rads_shaded, face_areas = calc_win_radiation(
                        int_matrix_s, angles_s, w_total_sky_rad, win_msh
                    )
                    w_rads_unshaded, face_areas = calc_win_radiation(
                        int_matrix_u, angles_u, w_total_sky_rad, win_msh
                    )

                    winter_rad_shaded = sum(w_rads_shaded) / sum(face_areas)
                    winter_rad_unshaded = sum(w_rads_unshaded) / sum(face_areas)

                    winter_radiation_shaded_detailed_.AddRange(
                        w_rads_shaded, GH_Path(win_count)
                    )
                    winter_radiation_shaded_.Add(winter_rad_shaded, GH_Path(win_count))
                    winter_radiation_unshaded_.Add(
                        winter_rad_unshaded, GH_Path(win_count)
                    )

                    # Solve Summer
                    # ----------------------------------------------------------------------
                    args_summer = (
                        shade_mesh_summer,
                        win_msh_bck,
                        pts,
                        s_sky_vecs,
                        nrmls,
                        self.settings.cpus,
                    )

                    (
                        int_matrix_s,
                        int_matrix_u,
                        angles_s,
                        angles_u,
                    ) = generate_intersection_data(*args_summer)
                    s_rads_shaded, face_areas = calc_win_radiation(
                        int_matrix_s, angles_s, s_total_sky_rad, win_msh
                    )
                    s_rads_unshaded, face_areas = calc_win_radiation(
                        int_matrix_u, angles_u, s_total_sky_rad, win_msh
                    )

                    summer_rad_shaded = sum(s_rads_shaded) / sum(face_areas)
                    summer_rad_unshaded = sum(s_rads_unshaded) / sum(face_areas)

                    summer_radiation_shaded_detailed_.AddRange(
                        s_rads_shaded, GH_Path(win_count)
                    )
                    summer_radiation_shaded_.Add(summer_rad_shaded, GH_Path(win_count))
                    summer_radiation_unshaded_.Add(
                        summer_rad_unshaded, GH_Path(win_count)
                    )

                    mesh_by_window.Add(rh_msh, GH_Path(win_count))

                    # Set the aperture shading factors
                    # ----------------------------------------------------------------------
                    aperture.properties.ph.winter_shading_factor = (
                        winter_rad_shaded / winter_rad_unshaded
                    )
                    aperture.properties.ph.summer_shading_factor = (
                        summer_rad_shaded / summer_rad_unshaded
                    )

                    win_count += 1

            # -- Add the new room to the output set
            # ----------------------------------------------------------------------
            hb_rooms_.append(new_room)

        # Create the mesh and legend outputs
        # --------------------------------------------------------------------------
        # Flatten the radiation data trees
        winter_rad_vals = [
            item
            for branch in winter_radiation_shaded_detailed_.Branches
            for item in branch
        ]
        summer_rad_vals = [
            item
            for branch in summer_radiation_shaded_detailed_.Branches
            for item in branch
        ]

        # Create the single window Mesh
        joined_window_mesh = create_window_mesh(lb_window_meshes)

        winter_graphic, title = create_graphic_container(
            "Winter", winter_rad_vals, joined_window_mesh, self.settings.legend_par
        )
        winter_radiation_shaded_mesh_, legend_ = create_rhino_mesh(
            winter_graphic, joined_window_mesh
        )

        summer_graphic, title = create_graphic_container(
            "Summer", summer_rad_vals, joined_window_mesh, self.settings.legend_par
        )
        summer_radiation_shaded_mesh_, legend_ = create_rhino_mesh(
            summer_graphic, joined_window_mesh
        )

        # -- Pull out the shading factors
        winter_shading_factors_, summer_shading_factors_, aperture_names_ = [], [], []
        for room in hb_rooms_:
            for face in room.faces:
                for aperture in face.apertures:
                    aperture_names_.append(aperture.display_name)
                    winter_shading_factors_.append(
                        aperture.properties.ph.winter_shading_factor
                    )
                    summer_shading_factors_.append(
                        aperture.properties.ph.summer_shading_factor
                    )

        return (
            legend_,
            winter_radiation_shaded_mesh_,
            winter_shading_factors_,
            summer_radiation_shaded_mesh_,
            summer_shading_factors_,
            hb_rooms_,
            aperture_names_,
        )
