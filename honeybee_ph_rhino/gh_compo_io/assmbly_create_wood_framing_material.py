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
    from honeybee_energy_ph.properties.materials.opaque import EnergyMaterialPhProperties
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

        mat_.properties.ph.ph_color = PhColor.from_argb(255, 255, 128, 0)
        return mat_

    def _convert(self, value, to_unit="M"):
        # type: (Union[float, int, str], str) -> float
        return convert(*parse_input(value), _target_unit=to_unit) or 0.0

    def check_material_conductivity(self, _material):
        # type: (opaque.EnergyMaterial) -> None
        if _material.conductivity > 10.0:
            msg = (
                "WARNING: Material '{}' has a very high conductivity value of {:.2f} W/m-K. "
                "Note that metal elements like steel studs and metal fasteners may NOT be "
                "used as part of heterogeneous assemblies (as per ISO 6946).".format(
                    _material.display_name, _material.conductivity
                )
            )
            print(msg)
            self.IGH.error(msg)

    def run(self):
        # type: () -> Tuple[Optional[opaque.EnergyMaterial], Optional[List[Brep]]]
        if self.insulation_material is None or self.wood_framing_material is None:
            return (None, None)

        # -- Check
        self.check_material_conductivity(self.wood_framing_material)
        self.check_material_conductivity(self.insulation_material)

        # -- Setup the Division Grid
        new_material_ = self.insulation_material.duplicate()
        ph_prop = new_material_.properties.ph  # type: EnergyMaterialPhProperties

        insulation_width = (self.wood_framing_member_oc_spacing - self.wood_framing_member_width) / 2
        ph_prop.divisions.set_column_widths(
            [
                insulation_width,
                self.wood_framing_member_width,
                insulation_width,
            ]
        )
        ph_prop.divisions.set_row_heights(
            [
                self.top_plate_width,
                self.element_total_length - self.top_plate_width - self.bottom_plate_width,
                self.bottom_plate_width,
            ]
        )

        # -- Set the Wood Framing Materials on the relevant cells
        for row_number in range(ph_prop.divisions.row_count):
            ph_prop.divisions.set_cell_material(1, row_number, self.wood_framing_material)

        if self.top_plate_width != 0:
            ph_prop.divisions.set_cell_material(0, 0, self.wood_framing_material)
            ph_prop.divisions.set_cell_material(2, 0, self.wood_framing_material)

        if self.bottom_plate_width != 0:
            ph_prop.divisions.set_cell_material(0, ph_prop.divisions.row_count - 1, self.wood_framing_material)
            ph_prop.divisions.set_cell_material(2, ph_prop.divisions.row_count - 1, self.wood_framing_material)

        # -- Generate the Preview
        preview_ = generate_preview(
            self.IGH,
            convert_list_of_values(ph_prop.divisions.column_widths, self.IGH.get_rhino_unit_system_name()),
            convert_list_of_values(ph_prop.divisions.row_heights, self.IGH.get_rhino_unit_system_name()),
        )

        return new_material_, preview_
