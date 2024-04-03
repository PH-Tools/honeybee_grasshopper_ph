# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Spaces."""

try:
    from typing import Any, List, Optional, Tuple, TypeVar, Union, Optional

    T = TypeVar("T")
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper import DataTree  # type: ignore
except ImportError:
    pass  # outside Grasshopper

try:
    from System import Double, Object, String  # type: ignore
except:
    pass  # outside .NET

try:
    from ladybug_geometry.geometry3d import face
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_geometry:\n\t{}".format(e))

try:
    from ladybug_rhino.config import units_abbreviation
    from ladybug_rhino.fromgeometry import from_face3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee_ph import space
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.make_spaces import make_floor, make_volume
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units import converter, parser
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))

try:
    from honeybee_ph_rhino.gh_compo_io.space_create_vent_rates import SpacePhVentFlowRates
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreatePHSpaces(object):
    DEFAULT_SPACE_HEIGHT = 2.5  # m

    def __init__(
        self,
        _IGH,
        _flr_seg_geom,
        _weighting_factors,
        _volume_geometry,
        _volume_heights,
        _space_names,
        _space_numbers,
        _space_ph_vent_rates,
    ):
        # type: (gh_io.IGH, DataTree, DataTree, DataTree, DataTree, DataTree, DataTree, DataTree) -> None
        self.IGH = _IGH
        self.flr_geom = _flr_seg_geom
        self.weighting_factors = _weighting_factors
        self.vol_geom = _volume_geometry
        self.vol_heights = _volume_heights
        self.names = _space_names
        self.numbers = _space_numbers
        self.vent_rates = _space_ph_vent_rates

    @property
    def rh_doc_unit_type_abbreviation(self):
        # type: () -> str
        """Return the Rhino file's unit-type as a string abbreviation. ie: "Meter" -> "M", etc.."""

        return units_abbreviation().upper()

    def _default_height_in_local_units(self):
        # type: () -> Union[float, int]
        """Return the default SpaceVolume height in the Rhino document unit-type."""

        default_height_value = self.DEFAULT_SPACE_HEIGHT
        default_height_unit = "M"
        value = converter.convert(
            default_height_value, default_height_unit, self.rh_doc_unit_type_abbreviation
        )
        if not value:
            msg = "Error: Failed to convert:" "'{}{}' to local unit-type: '{}'".format(
                default_height_value,
                default_height_unit,
                self.rh_doc_unit_type_abbreviation,
            )
            raise Exception(msg)
        return value

    def _clean_input_tree(self, _input_tree, branch_count, default, _type):
        # type: (DataTree, int, Any, T) -> DataTree[T]
        """Align the input DataTrees so they are all the same length. Apply defaults.
        
        Arguments:
        ----------
            * _input_tree: The input DataTree to clean.
            * branch_count: The number of branches to align the input tree to.
            * default: The default value to apply to any missing or None items.
            * _type: The Type of the input tree Data items.

        Returns:
        --------
            DataTree[T]: A new DataTree with the same structure as the input tree, but with
                all branches the same length.
        """
        new_tree = self.IGH.Grasshopper.DataTree[_type]()  # type: DataTree[T]
        pth = self.IGH.Grasshopper.Kernel.Data.GH_Path
        for i in range(branch_count):
            try:
                new_tree.AddRange(_input_tree.Branch(i), pth(i))
            except ValueError:
                new_tree.Add(default, pth(i))
        return new_tree

    def _clean_volume_heights_tree(
        self, _input_tree, _branch_count, _default_height, _type
    ):
        # type: (DataTree, int, Any, T) -> DataTree[T]
        """Return a cleaned DataTree of the volume height inputs. Allows for conversion of user input.

        ie: if the user inputs "15 m" will convert to the Rhino document unit-type.
        """

        new_tree = self.IGH.Grasshopper.DataTree[_type]()  # type: DataTree[T]
        pth = self.IGH.Grasshopper.Kernel.Data.GH_Path

        for i in range(_branch_count):
            try:
                if not _input_tree.Branch(i):
                    new_tree.Add(_default_height, pth(i))

                for input_item in _input_tree.Branch(i):
                    val, unit = parser.parse_input(input_item)
                    converted_value = converter.convert(
                        val, unit, self.rh_doc_unit_type_abbreviation
                    )
                    new_tree.Add(converted_value, pth(i))
            except ValueError:
                new_tree.Add(_default_height, pth(i))
        return new_tree

    def _create_space_floors(self, _flr_srfc_list, _weighting_factor_branch):
        # type: (List, DataTree[Double]) -> Tuple[List[space.SpaceFloor], List[Optional[face.Face3D]]]
        """Return a list of space.SpaceFloor objects based on Rhino Geometry and TFA weighting factors."""

        space_floors, e = make_floor.space_floor_from_rh_geom(
            self.IGH, list(_flr_srfc_list), list(_weighting_factor_branch)
        )

        error_faces = [from_face3d(s) for s in e]  # type: List[Optional[face.Face3D]]
        if error_faces:
            msg = (
                "Error: There was a problem joining together one or more group of floor surfaces?\n"
                'Check the "error_" output for a preview of the surfaces causing the problem\n'
                "Check the names and numbers of the surfaces, and make sure they can be properly merged?"
            )
            self.IGH.error(msg)

        return space_floors, error_faces

    def _create_space_volumes(self, _space_floors, _vol_heights):
        # type: (List[space.SpaceFloor], List[float]) -> List[space.SpaceVolume]
        """Return a new space.SpaceVolume based on a floor and a height."""

        volumes = make_volume.volumes_from_floors(
            self.IGH, _space_floors, list(_vol_heights)
        )
        return volumes

    def _add_flow_rates_to_space(self, _vent_rates, _new_space):
        # type: (List[SpacePhVentFlowRates], space.Space) -> space.Space
        """Add any user-determined vent flow rates, if any."""

        try:
            flow_rate_obj = sum(_vent_rates)
            _new_space.properties.ph._v_sup = flow_rate_obj.v_sup  # type: ignore
            _new_space.properties.ph._v_eta = flow_rate_obj.v_eta  # type: ignore
            _new_space.properties.ph._v_tran = flow_rate_obj.v_tran  # type: ignore
        except TypeError:
            pass
        return _new_space

    def _space_volumes_as_rh_geom(self, _space_volumes):
        # type: (List[space.SpaceVolume]) -> List
        """Return a list of space.SpaceVolumes as Rhino Geometry (Brep)."""

        volume_rh_breps_ = []
        for vol in _space_volumes:
            volume_rh_breps_.append(
                self.IGH.ghpythonlib_components.BrepJoin(
                    self.IGH.convert_to_rhino_geom(vol.geometry)
                ).breps
            )
        return volume_rh_breps_

    def _create_ph_spaces(
        self,
        _space_names,
        _space_numbers,
        _weighting_factors,
        _volume_heights,
        _vent_rates,
    ):
        # type: (DataTree[str], DataTree[str], DataTree[Double], DataTree[Double], DataTree) -> Tuple[List[Optional[face.Face3D]], List, List, List[space.Space]]
        """Create all the PH space.Spaces based on the user input."""

        spaces_ = []
        errors_ = []
        floor_breps_ = DataTree[Object]()
        volume_breps_ = DataTree[Object]()

        # -- Build one Space for each branch on the _flr_seg_geom input tree
        for i, floor_surface_list in enumerate(self.flr_geom.Branches):
            new_space = space.Space()
            new_space.name = _space_names.Branch(i)[0]
            new_space.number = _space_numbers.Branch(i)[0]
            space_floors, errors_ = self._create_space_floors(
                floor_surface_list, _weighting_factors.Branch(i)
            )
            space_volumes = self._create_space_volumes(
                space_floors, _volume_heights.Branch(i)
            )
            new_space.add_new_volumes(space_volumes)
            new_space = self._add_flow_rates_to_space(_vent_rates.Branch(i), new_space)
            spaces_.append(new_space)

            # -- Output Preview: Floor Surfaces
            pth = self.IGH.Grasshopper.Kernel.Data.GH_Path
            flr_rh_geom = [from_face3d(flr.geometry) for flr in space_floors]
            floor_breps_.AddRange(flr_rh_geom, pth(i))

            # -- Output Preview: Volume Breps
            volume_breps_.AddRange(self._space_volumes_as_rh_geom(space_volumes), pth(i))

        spaces_ = sorted(spaces_, key=lambda sp: sp.full_name)

        return errors_, floor_breps_, volume_breps_, spaces_

    def run(self):
        # type: () -> Tuple[List[Optional[face.Face3D]], List, List, List[space.Space]]
        """Run the space maker."""

        # -------------------------------------------------------------------------------
        # -- Organize the input trees, lists, lengths, defaults
        default_height = self._default_height_in_local_units()
        input_len = len(self.flr_geom.Branches)

        space_names = self._clean_input_tree(self.names, input_len, "_Unnamed_", String)
        space_numbers = self._clean_input_tree(self.numbers, input_len, "000", String)
        weighting_factors = self._clean_input_tree(
            self.weighting_factors, input_len, 1.0, Object
        )
        volume_heights = self._clean_volume_heights_tree(
            self.vol_heights, input_len, default_height, Object
        )
        vent_rates = self._clean_input_tree(self.vent_rates, input_len, None, Object)

        return self._create_ph_spaces(
            space_names, space_numbers, weighting_factors, volume_heights, vent_rates
        )
