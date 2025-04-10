# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Wood Framing Material."""

try:
    from typing import Any, List, Optional, Sequence, Tuple, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from Rhino.Geometry import Brep  # type: ignore
except ImportError as e:
    raise ImportError("\nFailed to import Rhino:\n\t{}".format(e))

try:
    from honeybee_energy.material import opaque
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_ph_utils.color import PhColor
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties.materials.opaque import EnergyMaterialPhProperties, PhDivisionGrid
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))

try:
    from honeybee_ph_rhino.gh_compo_io.assmbly_create_heterogeneous_material import generate_preview
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


def convert_list_of_values(_values, _unit="M"):
    # type: (Sequence[str | float], str) -> List[float]
    """Convert the Sequence of values to the specified unit."""
    values_ = []
    for col_width in _values:
        input_val, input_unit = parse_input(col_width)
        converted_value = convert(input_val, input_unit or "M", _unit)
        values_.append(converted_value)
        print("Converting {}-{} to {:.3f}-{}".format(input_val, input_unit or "M", converted_value, _unit))
    return values_


class GHCompo_CreateWoodFramingMaterial(object):
    """GHCompo Interface: HBPH - Create Wood Framing Material."""

    def __init__(
        self,
        IGH,
        _insulation_material,
        _wood_framing_material,
        _wood_framing_member_width,
        _wood_framing_member_oc_spacing,
        _top_plate_width,
        _bottom_plate_width,
        _element_total_length,
    ):
        # type: (gh_io.IGH, Optional[opaque.EnergyMaterial], Optional[opaque.EnergyMaterial], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]) -> None
        self.IGH = IGH
        self.insulation_material = _insulation_material
        self.wood_framing_material = _wood_framing_material or self.default_wood_framing_material
        self.wood_framing_member_width = self._convert(_wood_framing_member_width or "1.5in")
        self.wood_framing_member_oc_spacing = self._convert(_wood_framing_member_oc_spacing or "16in")
        self.top_plate_width = self._convert(_top_plate_width or 0.0)
        self.bottom_plate_width = self._convert(_bottom_plate_width or 0.0)
        self.element_total_length = self._convert(_element_total_length or "8ft")

    @property
    def default_wood_framing_material(self):
        # type: () -> opaque.EnergyMaterial
        mat_ = opaque.EnergyMaterial(
            "Softwood Lumber",
            conductivity=0.14,
            specific_heat=1210,
            density=545,
            roughness="MediumRough",
            thickness=0.1,
        )
        hbph_props_ph = getattr(mat_.properties, "ph")  # type: EnergyMaterialPhProperties
        hbph_props_ph.ph_color = PhColor.from_argb(255, 255, 128, 0)
        return mat_

    def _convert(self, value, to_unit="M"):
        # type: (Union[float, int, str], str) -> float
        return convert(*parse_input(value), _target_unit=to_unit) or 0.0

    def check_material_type(self, _material):
        # type: (opaque.EnergyMaterial) -> opaque.EnergyMaterial | None
        if not isinstance(_material, opaque.EnergyMaterial):
            msg = "ERROR: Material '{}' of type '{}' is not allowed. Use only EnergyMaterial.".format(
                _material, type(_material)
            )
            print(msg)
            self.IGH.error(msg)
            return None
        else:
            return _material

    def check_material_conductivity(self, _material):
        # type: (opaque.EnergyMaterial) -> opaque.EnergyMaterial | None
        if _material.conductivity > 10.0:
            msg = (
                "ERROR: Material '{}' has a very high conductivity value of {:.2f} W/m-K. "
                "Note that metal elements like steel studs and metal fasteners may NOT be "
                "used as part of heterogeneous assemblies (as per ISO 6946).".format(
                    _material.display_name, _material.conductivity
                )
            )
            print(msg)
            self.IGH.error(msg)
            return None
        else:
            return _material

    def check_material(self, _material):
        # type: (opaque.EnergyMaterial | None) -> opaque.EnergyMaterial | None
        if _material is None:
            return None
        if not self.check_material_type(_material):
            return None
        if not self.check_material_conductivity(_material):
            return None
        return _material

    def run(self):
        # type: () -> Tuple[Optional[opaque.EnergyMaterial], Optional[List[Brep]]]
        insulation_material = self.check_material(self.insulation_material)
        if not insulation_material:
            return (None, None)

        wood_framing_material = self.check_material(self.wood_framing_material)
        if not wood_framing_material:
            return (None, None)

        # --------------------------------------------------------------------------------------------------------------
        # -- Setup the new Division Grid
        division_grid = PhDivisionGrid()
        insulation_width = (self.wood_framing_member_oc_spacing - self.wood_framing_member_width) / 2
        division_grid.set_column_widths(
            [
                insulation_width,
                self.wood_framing_member_width,
                insulation_width,
            ]
        )
        division_grid.set_row_heights(
            [
                self.top_plate_width,
                self.element_total_length - self.top_plate_width - self.bottom_plate_width,
                self.bottom_plate_width,
            ]
        )

        # --------------------------------------------------------------------------------------------------------------
        # -- Set the Materials on the cells

        # -- Set the 'stud' to the framing material (column-1)
        for row_number in range(division_grid.row_count):
            division_grid.set_cell_material(0, row_number, insulation_material)
            division_grid.set_cell_material(1, row_number, wood_framing_material)
            division_grid.set_cell_material(2, row_number, insulation_material)

        # -- Set the top-plate
        if self.top_plate_width != 0:
            division_grid.set_cell_material(0, 0, wood_framing_material)
            division_grid.set_cell_material(1, 0, wood_framing_material)
            division_grid.set_cell_material(2, 0, wood_framing_material)

        # -- Set the bottom-plate
        if self.bottom_plate_width != 0:
            division_grid.set_cell_material(0, division_grid.row_count - 1, wood_framing_material)
            division_grid.set_cell_material(1, division_grid.row_count - 1, wood_framing_material)
            division_grid.set_cell_material(2, division_grid.row_count - 1, wood_framing_material)

        # --------------------------------------------------------------------------------------------------------------
        # -- Create a new Hybrid Material
        base_material = division_grid.get_base_material()
        if not base_material:
            return (None, None)
        new_material_ = base_material.duplicate()
        nm = "{} + {}".format(insulation_material.display_name, wood_framing_material.display_name)
        new_material_.display_name = nm
        new_material_.identifier = nm
        new_material_.conductivity = division_grid.get_equivalent_conductivity()
        hbph_props = getattr(new_material_.properties, "ph")  # type: EnergyMaterialPhProperties
        hbph_props.divisions = division_grid

        # --------------------------------------------------------------------------------------------------------------
        # -- Generate the Preview
        preview_ = generate_preview(
            self.IGH,
            convert_list_of_values(division_grid.column_widths, self.IGH.get_rhino_unit_system_name()),
            convert_list_of_values(division_grid.row_heights, self.IGH.get_rhino_unit_system_name()),
        )

        return new_material_, preview_
