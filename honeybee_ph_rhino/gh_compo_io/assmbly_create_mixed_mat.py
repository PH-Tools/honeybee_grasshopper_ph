# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Mixed-Material Column/Row."""

# TODO: Deprecate this component

from functools import reduce

try:
    from typing import List, Optional, Tuple
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.material import opaque
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties.materials.opaque import EnergyMaterialPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


def _merge_material_attrs(_mat_a, _mat_b, attr_name):
    # type: (opaque.EnergyMaterial, opaque.EnergyMaterial, str) -> float
    """Helper func to perform a weighted-add between two EnergyMaterial's attribute values."""
    attr_a = getattr(_mat_a, attr_name)  # type: float
    mat_a_percent = _mat_a.properties.ph.percentage_of_assembly  # type: float
    attr_b = getattr(_mat_b, attr_name)  # type: float
    mat_b_percent = _mat_b.properties.ph.percentage_of_assembly  # type: float

    attr_a_weighted_value = attr_a * mat_a_percent
    attr_b_weighted_value = attr_b * mat_b_percent
    total_percentage = mat_a_percent + mat_b_percent

    return (attr_a_weighted_value + attr_b_weighted_value) / total_percentage


def merge_two_materials(_mat_a, _mat_b):
    # type: (opaque.EnergyMaterial, opaque.EnergyMaterial) -> opaque.EnergyMaterial
    """Return a new EnergyMaterial with attributes merged from two 'source' EnergyMaterials."""
    new_mat = opaque.EnergyMaterial(
        "{}+{}".format(_mat_a.display_name, _mat_b.display_name),
        _merge_material_attrs(_mat_a, _mat_b, "thickness"),
        _merge_material_attrs(_mat_a, _mat_b, "conductivity"),
        _merge_material_attrs(_mat_a, _mat_b, "density"),
        _merge_material_attrs(_mat_a, _mat_b, "specific_heat"),
        _mat_a.roughness,
        _merge_material_attrs(_mat_a, _mat_b, "thermal_absorptance"),
        _merge_material_attrs(_mat_a, _mat_b, "solar_absorptance"),
        _merge_material_attrs(_mat_a, _mat_b, "visible_absorptance"),
    )
    return new_mat


class GHCompo_CreateMixedHBMaterial(object):
    display_name = ghio_validators.HBName("display_name")

    def __init__(
        self,
        IGH,
        _name_,
        _section_1_material,
        _section_1_percentage,
        _section_2_material,
        _section_2_percentage,
        _section_3_material,
        _section_3_percentage,
    ):
        # type: (gh_io.IGH, Optional[str], Optional[opaque.EnergyMaterial], Optional[float], Optional[opaque.EnergyMaterial], Optional[float], Optional[opaque.EnergyMaterial], Optional[float] ) -> None
        self.IGH = IGH
        self.display_name = _name_ or clean_and_id_ep_string("OpaqueMaterialMixed")

        sec_1_perc, sec_2_perc, sec_3_perc = self.clean_percentages(
            self._clean_percentage_input(_section_1_percentage) or 1.0,
            self._clean_percentage_input(_section_2_percentage) or 0.0,
            self._clean_percentage_input(_section_3_percentage) or 0.0,
        )

        self.section_1_material = _section_1_material
        if self.section_1_material:
            self.section_1_material.properties.ph.percentage_of_assembly = sec_1_perc

        self.section_2_material = _section_2_material
        if self.section_2_material:
            self.section_2_material.properties.ph.percentage_of_assembly = sec_2_perc

        self.section_3_material = _section_3_material
        if self.section_3_material:
            self.section_3_material.properties.ph.percentage_of_assembly = sec_3_perc

        self.display_instructions()

    def display_instructions(self):
        """Provide user warning if no values supplied"""
        if not self.section_1_material:
            msg = "Input at least one material to proceed."
            self.IGH.warning(msg)

    def _clean_percentage_input(self, _input):
        # type (float) -> Optional[float]
        """Validate / Convert the percentage inputs."""
        if not _input:
            return None
        if _input > 1.00:
            return _input / 100

    @property
    def materials(self):
        # type: () -> List[opaque.EnergyMaterial]
        """Return a list of all the materials in order (1, 2, 3)."""
        all_materials = (
            self.section_1_material,
            self.section_2_material,
            self.section_3_material,
        )
        return [m for m in all_materials if m is not None]

    def clean_percentages(self, _sec_1_perc, _sec_2_perc, _sec_3_perc):
        # type: (float, float, float) -> Tuple[float, float, float]
        """Enforce a total material percentage of 100%"""
        sec_1_perc = 1.0 - _sec_2_perc - _sec_3_perc

        if sec_1_perc < 0.0:
            total_input_percentage = abs(1.0 - (_sec_1_perc + _sec_2_perc + _sec_3_perc))
            msg = "Error: The total material percentages = {:.2%}? Total should add up to 100.0% exactly?".format(
                total_input_percentage
            )
            self.IGH.error(msg)

        return sec_1_perc, _sec_2_perc, _sec_3_perc

    def check_conductivities(self, _limit=5.0):
        # type: (float) -> None
        """Ensure that all the materials input are relatively low-conductivity."""
        for material in self.materials:
            if material.conductivity > _limit:
                msg = (
                    "Error: High Conductivity found ({} W/mk) for material '{}'\n"
                    "This component is not designed for assemblies which have high "
                    "conductivity values and will not calculate the correct U-Factor. For "
                    "assemblies of this sort, you should use a 2-D heat flow simulation "
                    "or another other method to correctly calculate the U-Factor.".format(
                        material.conductivity,
                        material.display_name,
                    )
                )
                print(msg)
                self.IGH.error(msg)

    def run(self):
        # type: () -> Optional[opaque.EnergyMaterial]

        # ---------------------------------------------------------------------
        if not self.section_1_material:
            return

        # ---------------------------------------------------------------------
        # -- Clean up and verify the inputs
        self.check_conductivities()

        # ---------------------------------------------------------------------
        # -- Merge all the Materials together to create a new
        # -- equivalent-value single material
        merged_material = reduce(merge_two_materials, self.materials)

        # ---------------------------------------------------------------------
        # -- Create a new HB-Material with the equiv. U-Factor
        new_hb_mat = opaque.EnergyMaterial(
            self.display_name,
            merged_material.thickness,
            merged_material.conductivity,
            merged_material.density,
            merged_material.specific_heat,
            merged_material.roughness,
            merged_material.thermal_absorptance,
            merged_material.solar_absorptance,
            merged_material.visible_absorptance,
        )

        # ---------------------------------------------------------------------
        # -- Pack all the base materials onto the .properties.ph.base_materials so that they
        # -- can be pulled out again later on, if need be (ie: in PHPP).
        new_ph_prop = new_hb_mat.properties.ph  # type: EnergyMaterialPhProperties
        new_ph_prop.clear_base_materials()
        for material_section in self.materials:
            new_ph_prop.add_base_material(material_section)
        return new_hb_mat
