# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH Climate Monthly Radiation."""

try:
    from typing import Any, Dict, List, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from GhPython import Component  # type: ignore
    from Grasshopper.Kernel.Parameters import Hints  # type: ignore
except:
    pass  # outside Grasshopper

try:
    from honeybee_ph import phi
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_io import ComponentInput
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


# -----------------------------------------------------------------------------
# -- Functions for configuring the GH Component input nodes.


def _build_options_string(_input_options):
    # type: (List) -> str
    """Build the description string."""
    _ = ["(str) Input either - "]
    for input_option in _input_options:
        _.append("    " + str(input_option))
    return "\n".join(_)


inputs_phpp_9 = {
    1: ComponentInput(_name="- " * 20, _description="", _type_hint=Component.NewStrHint()),
    2: ComponentInput(
        _name="_building_category_type",
        _description=_build_options_string(["1-Residential building (default)", "2-Non-residential building"]),
        _type_hint=Component.NewStrHint(),
    ),
    3: ComponentInput(
        _name="_building_use_type",
        _description=_build_options_string(
            [
                "10-Dwelling (default)",
                "11-Nursing home / students",
                "12-Other",
                "20-Office / Admin. building",
                "21-School",
                "22-Other",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    4: ComponentInput(
        _name="_ihg_type",
        _description=_build_options_string(
            [
                "2-Standard (default)",
                "3-PHPP calculation ('IHG' worksheet)",
                "4-PHPP calculation ('IHG non-res' worksheet)",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    5: ComponentInput(
        _name="_occupancy_type",
        _description=_build_options_string(
            [
                "1-Standard (only for residential buildings)",
                "2-User determined",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    6: ComponentInput(_name="- " * 20, _description="", _type_hint=Component.NewStrHint()),
    7: ComponentInput(
        _name="_certification_type",
        _description=_build_options_string(
            [
                "1-Passive House (default)",
                "2-EnerPHit",
                "3-PHI Low Energy Building",
                "4-Other",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    8: ComponentInput(
        _name="_certification_class",
        _description=_build_options_string(
            [
                "1-Classic (default)",
                "2-Plus",
                "3-Premium",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    9: ComponentInput(
        _name="_primary_energy_type",
        _description=_build_options_string(
            [
                "1-PE (non-renewable)",
                "2-PER (renewable) (default)",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    10: ComponentInput(
        _name="_enerphit_type",
        _description=_build_options_string(
            [
                "1-Component method",
                "2-Energy demand method (default)",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    11: ComponentInput(
        _name="_retrofit",
        _description=_build_options_string(
            [
                "1-New building (default)",
                "2-Retrofit",
                "3-Step-by-step retrofit",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
}

inputs_phpp_10 = {
    1: ComponentInput(_name="- " * 20, _description="", _type_hint=Component.NewStrHint()),
    3: ComponentInput(
        _name="_building_use_type",
        _description=_build_options_string(
            [
                "10-Residential building: Residential (default)",
                "12-Residential building: Other",
                "20-Non-res building: Office/Administration",
                "21-Non-res building: School half-days (< 7 h)",
                "22-Non-res building: School full-time (≥ 7 h)",
                "23-Non-res.: Other",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    4: ComponentInput(
        _name="_ihg_type",
        _description=_build_options_string(
            [
                "1-User-defined",
                "3-PHPP-calculation ('IHG' worksheet)",
                "4-PHPP-calculation ('IHG non-res' worksheet)",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    6: ComponentInput(_name="- " * 20, _description="", _type_hint=Component.NewStrHint()),
    7: ComponentInput(
        _name="_certification_type",
        _description=_build_options_string(
            [
                "10-Passive house",
                "21-EnerPHit (Component method)",
                "22-EnerPHit (Energy demand method)",
                "30-PHI Low Energy Building",
                "40-Other",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    8: ComponentInput(
        _name="_certification_class",
        _description=_build_options_string(
            [
                "10-Classic | PER (renewable)",
                "11-Classic | PE (non-renewable)",
                "20-Plus | PER (renewable)",
                "30-Premium | PER (renewable)",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    9: ComponentInput(
        _name="_primary_energy_type",
        _description=_build_options_string(
            [
                "1-Standard",
                "2-Project-specific",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
    11: ComponentInput(
        _name="_retrofit",
        _description=_build_options_string(
            [
                "1-New building",
                "2-Retrofit",
                "3-Staged retrofit",
            ]
        ),
        _type_hint=Component.NewStrHint(),
    ),
}


def get_component_inputs(_phpp_version_number):
    # type: (str) -> dict
    """Select the component input-node group to show based on the 'type' specified."""

    if "9" in str(_phpp_version_number):
        return inputs_phpp_9
    elif "10" in str(_phpp_version_number):
        return inputs_phpp_10
    else:
        return inputs_phpp_9


# -----------------------------------------------------------------------------
# -- Component Interface


class _CertSettingsPHPP_9(object):
    """Settings for PHPP-9 inputs."""

    def __init__(self, _IGH, _phpp_version, _input_dict):
        # type: (gh_io.IGH, int, Dict[str, Any]) -> None
        self.IGH = gh_io.input_to_int(_IGH)
        self.phpp_version = _phpp_version
        self.building_category_type = gh_io.input_to_int(_input_dict["_building_category_type"])
        self.building_use_type = gh_io.input_to_int(_input_dict["_building_use_type"])
        self.ihg_type = gh_io.input_to_int(_input_dict["_ihg_type"])
        self.occupancy_type = gh_io.input_to_int(_input_dict["_occupancy_type"])
        self.certification_type = gh_io.input_to_int(_input_dict["_certification_type"])
        self.certification_class = gh_io.input_to_int(_input_dict["_certification_class"])
        self.primary_energy_type = gh_io.input_to_int(_input_dict["_primary_energy_type"])
        self.enerphit_type = gh_io.input_to_int(_input_dict["_enerphit_type"])
        self.retrofit = gh_io.input_to_int(_input_dict["_retrofit"])

    def run(self):
        # type: () -> phi.PhiCertification
        phi_certification_ = phi.PhiCertification(self.phpp_version)
        attrs = phi_certification_.attributes  # type: phi.PHPPSettings9
        attrs.building_category_type = self.building_category_type
        attrs.building_use_type = self.building_use_type
        attrs.ihg_type = self.ihg_type
        attrs.occupancy_type = self.occupancy_type
        attrs.certification_type = self.certification_type
        attrs.certification_class = self.certification_class
        attrs.primary_energy_type = self.primary_energy_type
        attrs.enerphit_type = self.enerphit_type
        attrs.retrofit_type = self.retrofit
        return phi_certification_


class _CertSettingsPHPP_10(object):
    """Settings for PHPP-10 inputs."""

    def __init__(self, _IGH, _phpp_version, _input_dict):
        # type: (gh_io.IGH, int, Dict[str, str]) -> None
        self.IGH = _IGH
        self.phpp_version = _phpp_version
        self.building_use_type = gh_io.input_to_int(_input_dict["_building_use_type"])
        self.ihg_type = gh_io.input_to_int(_input_dict["_ihg_type"])
        self.certification_type = gh_io.input_to_int(_input_dict["_certification_type"])
        self.certification_class = gh_io.input_to_int(_input_dict["_certification_class"])
        self.primary_energy_type = gh_io.input_to_int(_input_dict["_primary_energy_type"])
        self.retrofit = gh_io.input_to_int(_input_dict["_retrofit"])

    def run(self):
        # type: () -> phi.PhiCertification
        phi_certification_ = phi.PhiCertification(self.phpp_version)
        attrs = phi_certification_.attributes  # type: phi.PHPPSettings10
        attrs.building_use_type = self.building_use_type
        attrs.ihg_type = self.ihg_type
        attrs.certification_type = self.certification_type
        attrs.certification_class = self.certification_class
        attrs.primary_energy_type = self.primary_energy_type
        attrs.retrofit_type = self.retrofit
        return phi_certification_


class GHCompo_PhiCertification(object):
    def __init__(self, _IGH, _phpp_version, _input_dict):
        # type: (gh_io.IGH, int, Dict[str, Any]) -> None
        self.IGH = _IGH
        self.phpp_version = _phpp_version or 9

        if "9" in str(self.phpp_version):
            self.builder = _CertSettingsPHPP_9(_IGH, self.phpp_version, _input_dict)
        elif "10" in str(self.phpp_version):
            self.builder = _CertSettingsPHPP_10(_IGH, self.phpp_version, _input_dict)
        else:
            msg = "Error: Unsupported PHPP version. Got: '{}'".format(self.phpp_version)
            self.IGH.error(msg)

    def run(self):
        return self.builder.run()
