# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Heterogeneous Material."""

try:
    from typing import Any, Optional, Sequence, Tuple, List
except ImportError:
    pass  # IronPython 2.7

try:
    from Rhino.Geometry import Brep # type: ignore
except ImportError as e:
    raise ImportError("\nFailed to import Rhino:\n\t{}".format(e))

try:
    from honeybee_energy.material import opaque
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties.materials.opaque import EnergyMaterialPhProperties, CellPositionError
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


def generate_preview(_IGH, _column_widths, _row_heights):
    # type: (gh_io.IGH, Sequence[float], Sequence[float]) -> List[Brep]
    """Generate a Rhino geometry preview of the grid material"""
    print("- " * 25)
    print("Generating Preview of the Heterogeneous Material Cells...")

    total_width = sum(_column_widths)
    total_height = sum(_row_heights)

    # -- Create the Vertical Edges
    left_edge = _IGH.ghc.LineSDL( _IGH.ghc.ConstructPoint(0,0,0), _IGH.ghc.UnitY(1), total_height)
    vertical_edges = [left_edge]
    vertical_move_dist = 0.0
    for width in _column_widths:
        vertical_move_dist += width
        vertical_edges.append(_IGH.ghc.Move(left_edge, _IGH.ghc.UnitX(vertical_move_dist)).geometry)

    # --- Crete the Horizontal Edges
    bottom_edge = _IGH.ghc.LineSDL(_IGH.ghc.ConstructPoint(0,0,0), _IGH.ghc.UnitX(1), total_width)

    horizontal_edges = [bottom_edge]
    horizontal_move_dist = 0.0
    for height in _row_heights[::-1]: # Reverse since we're now building 'up', not 'down'
        horizontal_move_dist += height
        horizontal_edges.append(_IGH.ghc.Move(bottom_edge, _IGH.ghc.UnitY(horizontal_move_dist)).geometry)

    # --- Create the Cell Surface Breps
    boundary = _IGH.ghc.BoundarySurfaces(
        _IGH.ghc.Rectangle2Pt(
            plane=_IGH.ghc.ConstructPlane(
                _IGH.ghc.ConstructPoint(0,0,0),
                _IGH.ghc.UnitX(1),
                _IGH.ghc.UnitY(1),
            ),
            point_a=_IGH.ghc.ConstructPoint(0,0,0),
            point_b=_IGH.ghc.ConstructPoint(total_width,total_height,0),
            radius=0,
        ).rectangle
    )

    surfaces = _IGH.ghc.SurfaceSplit(boundary, vertical_edges + horizontal_edges)

    return surfaces


class GHCompo_CreateHeterogeneousMaterial(object):
    def __init__(self, IGH, _base_material, _additional_materials, _column_widths, _row_heights):
        # type: (gh_io.IGH, Optional[opaque.EnergyMaterial], Sequence[opaque.EnergyMaterial], Sequence[float], Sequence[float]) -> None
        self.IGH = IGH
        self.base_material = _base_material
        self.additional_materials = _additional_materials
        self.column_widths = _column_widths
        self.row_heights = _row_heights

    def ready(self):
        # type: () -> bool
        """Check if all the inputs are ready, perform some cleanup on the inputs."""
        
        if not self.base_material:
            return False
        
        if not self.additional_materials:
            return False

        if not self.column_widths and not self.row_heights:
            return False

        if (not self.column_widths) and self.row_heights:
            self.column_widths = [1.0]
        
        if (not self.row_heights) and self.column_widths:
            self.row_heights = [1.0]
        
        self.check_materials_for_user_data()
        self.column_widths = self.convert_column_widths(self.column_widths, "M")
        self.row_heights = self.convert_row_heights(self.row_heights, "M")
        return True

    def check_materials_for_user_data(self):
        # type: () -> None
        """Check to make sure all the additional materials have user_data attributes."""
        for mat in self.additional_materials:
            if not hasattr(mat.properties, "ph"):
                raise ValueError("Error: Material '{}' does not have a PH properties?".format(mat.display_name))
            if not hasattr(mat.properties.ph, "user_data"): # type: ignore
                raise ValueError("Error: Material '{}' does not have user_data?".format(mat.display_name))

    def convert_column_widths(self, _column_widths, _unit="M"):
        # type: (Sequence[str | float], str) -> List[float]
        """Convert the column-width inputs to meters."""
        column_widths_ = []
        for col_width in _column_widths:
            input_val, input_unit = parse_input(col_width)
            converted_value = convert(input_val, input_unit or "M", _unit)
            column_widths_.append(converted_value)
            print("Converting {}-{} to {:.3f}-{}".format(input_val, input_unit or "M", converted_value, _unit))
        return column_widths_

    def convert_row_heights(self, _row_heights, _unit="M"):
        # type: (Sequence[str | float], str) -> List[float]
        """Convert the row-height inputs to meters."""
        row_heights_ = []
        for row_height in _row_heights:
            input_val, input_unit = parse_input(row_height)
            converted_value = convert(input_val, input_unit or "M", _unit)
            row_heights_.append(converted_value)
            print("Converting {}-{} to {:.3f}-{}".format(input_val, input_unit or "M", converted_value, _unit))
        return row_heights_

    def check_material_thicknesses(self, material, _tol=0.001):
        # type: (opaque.EnergyMaterial, float) -> None
        """Check the thickness of the material and the division grid."""
        base_thickness = material.thickness
        for addnl_material in self.additional_materials:
            if abs(addnl_material.thickness - base_thickness) > _tol:
                msg = "WARNING: Material '{}' has a different thickness from the base material '{}'. "\
                    "The base-material thickness of {:.2f} will be used when creating the heterogeneous-material.".format(
                        material.display_name, addnl_material.display_name, material.thickness)
                print(msg)
                self.IGH.warning(msg)
                break

    def check_material_conductivities(self, material):
        # type: (opaque.EnergyMaterial) -> None
        for addnl_mat in self.additional_materials:
            if addnl_mat.conductivity > 10.0:
                msg = "WARNING: Material '{}' has a very high conductivity value of {:.2f} W/m-K. "\
                    "Note that metal elements like steel studs and metal fasteners may NOT be "\
                    "used as part of heterogeneous assemblies (as per ISO 6946).".format(
                        addnl_mat.display_name, addnl_mat.conductivity)
                print(msg)
                self.IGH.error(msg)
                break

    def run(self):
        # type: () -> Tuple[Optional[opaque.EnergyMaterial], Optional[Any]]
        if not self.ready() or not self.base_material:
            return (self.base_material, None)

        # -- Setup the Base Material Division Grid
        new_material_ = self.base_material.duplicate()
        ph_prop = new_material_.properties.ph  # type: EnergyMaterialPhProperties # type: ignore

        ph_prop.divisions.set_column_widths(self.column_widths)
        ph_prop.divisions.set_row_heights(self.row_heights)

        for material in self.additional_materials:
            col = material.properties.ph.user_data.get("column_position", 0) # type: ignore
            row = material.properties.ph.user_data.get("row_position", 0) # type: ignore
            print("Setting Material at: Column-{} | Row-{} to '{}' [id={}]".format(col, row, material.display_name, id(material)))
            try:
                ph_prop.divisions.set_cell_material(col, row, material)
            except CellPositionError as e:
                print("- " *25)
                print("WARNING: Check the '_column_widths' and '_row_heights' inputs.\n")
                raise e

        self.check_material_thicknesses(new_material_)
        self.check_material_conductivities(new_material_)

        preview_ = generate_preview(
            self.IGH,
            self.convert_column_widths(self.column_widths, self.IGH.get_rhino_unit_system_name()),
            self.convert_row_heights(self.row_heights, self.IGH.get_rhino_unit_system_name())
        )

        return new_material_, preview_
