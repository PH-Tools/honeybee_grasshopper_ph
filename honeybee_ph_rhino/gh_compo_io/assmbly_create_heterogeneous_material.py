# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Heterogeneous Material."""

try:
    from typing import Any, Optional, Sequence
except ImportError:
    pass  # IronPython 2.7

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
        self.column_widths = self.convert_column_widths()
        self.row_heights = self.convert_row_heights()
        return True

    def check_materials_for_user_data(self):
        """Check to make sure all the additional materials have user_data attributes."""
        for mat in self.additional_materials:
            if not hasattr(mat.properties, "ph"):
                raise ValueError("Error: Material '{}' does not have a PH properties?".format(mat.display_name))
            if not hasattr(mat.properties.ph, "user_data"): # type: ignore
                raise ValueError("Error: Material '{}' does not have user_data?".format(mat.display_name))

    def convert_column_widths(self):
        # type: () -> Sequence[float]
        """Convert the column-width inputs to meters."""
        column_widths_ = []
        for col_width in self.column_widths:
            input_val, input_unit = parse_input(col_width)
            converted_value = convert(input_val, input_unit or "M", "M")
            column_widths_.append(converted_value)
            print("Converting {}-{} to {:.3f}-M".format(input_val, input_unit or "M", converted_value))
        return column_widths_

    def convert_row_heights(self):
        # type: () -> Sequence[float]
        """Convert the row-height inputs to meters."""
        row_heights_ = []
        for row_height in self.row_heights:
            input_val, input_unit = parse_input(row_height)
            converted_value = convert(input_val, input_unit or "M", "M")
            row_heights_.append(converted_value)
            print("Converting {}-{} to {:.3f}-M".format(input_val, input_unit or "M", converted_value))
        return row_heights_

    def run(self):
        # type: () -> Optional[opaque.EnergyMaterial]
        if not self.ready() or not self.base_material:
            return self.base_material

        # -- Setup the Base Material Division Grid
        new_material_ = self.base_material.duplicate()
        ph_prop = new_material_.properties.ph  # type: EnergyMaterialPhProperties # type: ignore

        ph_prop.divisions.set_column_widths(self.column_widths)
        ph_prop.divisions.set_row_heights(self.row_heights)

        for material in self.additional_materials:
            col = material.properties.ph.user_data.get("column_position", 0) # type: ignore
            row = material.properties.ph.user_data.get("row_position", 0) # type: ignore
            print("Setting Material at: Column-{} | Row-{} to '{}'".format(col, row, material.display_name))
            try:
                ph_prop.divisions.set_cell_material(col, row, material)
            except CellPositionError as e:
                print("- " *25)
                print("WARNING: Check the '_column_widths' and '_row_heights' inputs.\n")
                raise e

        return new_material_
