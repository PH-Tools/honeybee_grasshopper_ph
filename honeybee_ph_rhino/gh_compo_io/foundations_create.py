# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Foundation."""

from copy import copy

try:
    from typing import Any, Dict, Optional, Type, Union, Iterable, List
except ImportError:
    pass  # IronPython 2.7

try:
    from GhPython import Component  # type: ignore
    from Grasshopper.Kernel.Parameters import Hints  # type: ignore
except ImportError:
    pass  # Outside Grasshopper

try:
    from honeybee_ph import foundations
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_io import ComponentInput
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_utils.input_tools import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from ph_units import converter, parser
except ImportError as e:
    raise ImportError("\nFailed to import ph-units:\n\t{}".format(e))


# -----------------------------------------------------------------------------
# -- Setup the component input node groups

inputs_base = {
    1: ComponentInput(
        _name="_display_name",
        _description="(str) Optional display-name for the Foundation.",
        _type_hint=Component.NewStrHint(),
        _target_unit="None",
    ),
}

inputs_heated_basement = copy(inputs_base)
inputs_heated_basement.update(
    {
        2: ComponentInput(
            _name="floor_slab_area_m2",
            _description="(float) M2 area of the floor slab.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M2",
        ),
        3: ComponentInput(
            _name="floor_slab_u_value",
            _description="(float) U-Value (W/m2k) of the floor slab.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/M2K",
        ),
        4: ComponentInput(
            _name="floor_slab_exposed_perimeter_m",
            _description="(float) Input the total length (m) of the exposed perimeter edges.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M",
        ),
        5: ComponentInput(
            _name="slab_depth_below_grade_m",
            _description="(float) The average depth (m) of the top of the floor slab below grade.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M",
        ),
        6: ComponentInput(
            _name="basement_wall_u_value",
            _description="(float) The U-Value (W/m2k) of the basement wall below grade.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/M2K",
        ),
    }
)

inputs_unheated_basement = copy(inputs_base)
inputs_unheated_basement.update(
    {
        2: ComponentInput(
            _name="floor_ceiling_area_m2",
            _description="(float) M2 area of the floor / ceiling.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M2",
        ),
        3: ComponentInput(
            _name="ceiling_u_value",
            _description="(float) U-Value (W/m2k) of the ceiling above the cellar.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/M2K",
        ),
        4: ComponentInput(
            _name="floor_slab_exposed_perimeter_m",
            _description="(float) Input the total length (m) of the exposed perimeter edges.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M",
        ),
        5: ComponentInput(
            _name="slab_depth_below_grade_m",
            _description="(float) The average depth (m) of the top of the floor slab below grade.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M",
        ),
        6: ComponentInput(
            _name="basement_wall_height_above_grade_m",
            _description="(float) The average height (m) of the basement wall above grade.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M",
        ),
        7: ComponentInput(
            _name="basement_wall_uValue_below_grade",
            _description="(float) The U-Value (W/m2k) of the basement wall below grade.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/M2K",
        ),
        8: ComponentInput(
            _name="basement_wall_uValue_above_grade",
            _description="(float) The U-Value (W/m2k) of the basement wall above grade.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/M2K",
        ),
        9: ComponentInput(
            _name="floor_slab_u_value",
            _description="(float) U-Value (W/m2k) of the floor slab.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/M2K",
        ),
        10: ComponentInput(
            _name="basement_volume_m3",
            _description="(float) The Volume (m3) of the basement space.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M3",
        ),
        11: ComponentInput(
            _name="basement_ventilation_ach",
            _description="(float) The ACH of the basement space. Typical=0.5 ACH",
            _type_hint=Component.NewFloatHint(),
        ),
    }
)

inputs_slab_on_grade = copy(inputs_base)
inputs_slab_on_grade.update(
    {
        2: ComponentInput(
            _name="floor_slab_area_m2",
            _description="(float) M2 area of the floor slab.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M2",
        ),
        3: ComponentInput(
            _name="floor_slab_u_value",
            _description="(float) U-Value (W/m2k) of the floor slab.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/M2K",
        ),
        4: ComponentInput(
            _name="floor_slab_exposed_perimeter_m",
            _description="(float) Input the total length (m) of the exposed perimeter edges.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M",
        ),
        5: ComponentInput(
            _name="perim_insulation_position",
            _description='(str) Input either - "1-Undefined"\n"2-Horizontal"\n"3-Vertical"',
            _type_hint=Hints.GH_IntegerHint_CS(),
        ),
        6: ComponentInput(
            _name="perim_insulation_width_or_depth_m",
            _description="(float) The width (m) (if horizontal) or depth (if vertical) of the perimeter insulation.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M",
        ),
        7: ComponentInput(
            _name="perim_insulation_thickness_m",
            _description="(float) The thickness (m) of the perimeter insulation.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M",
        ),
        8: ComponentInput(
            _name="perim_insulation_conductivity",
            _description="(float) The thermal conductivity (W/mk) of the perimeter insulation.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/MK",
        ),
    }
)

inputs_vented_crawlspace = copy(inputs_base)
inputs_vented_crawlspace.update(
    {
        2: ComponentInput(
            _name="crawlspace_floor_slab_area_m2",
            _description="(float) M2 area of the crawlspace floor.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M2",
        ),
        3: ComponentInput(
            _name="ceiling_above_crawlspace_u_value",
            _description="(float) U-Value (W/m2k) of the ceiling above the crawlspace.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/M2K",
        ),
        4: ComponentInput(
            _name="crawlspace_floor_exposed_perimeter_m",
            _description="(float) Input the total length (m) of the exposed perimeter edges of the crawlspace floor.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M",
        ),
        5: ComponentInput(
            _name="crawlspace_wall_height_above_grade_m",
            _description="(float) The average height (m) of the crawlspace wall above grade.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M",
        ),
        6: ComponentInput(
            _name="crawlspace_floor_u_value",
            _description="(float) The U-Value (W/m2k) of the crawlspace floor.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/M2K",
        ),
        7: ComponentInput(
            _name="crawlspace_vent_opening_are_m2",
            _description="(float) The total area (m2) of the crawlspace ventilation openings.",
            _type_hint=Component.NewStrHint(),
            _target_unit="M2",
        ),
        8: ComponentInput(
            _name="crawlspace_wall_u_value",
            _description="(float) The U-Value (W/m2k) of the crawlspace wall.",
            _type_hint=Component.NewStrHint(),
            _target_unit="W/M2K",
        ),
    }
)

inputs_none = copy(inputs_base)
inputs_none.update({})

# -----------------------------------------------------------------------------

input_groups = {
    1: inputs_heated_basement,
    2: inputs_unheated_basement,
    3: inputs_slab_on_grade,
    4: inputs_vented_crawlspace,
    5: inputs_none,
}

# -----------------------------------------------------------------------------


def get_component_inputs(_foundation_type):
    # type: (str) -> Dict[int, ComponentInput]
    """Select the component input-node group based on the 'type' specified"""

    if not _foundation_type:
        return {}

    input_type_id = input_to_int(_foundation_type)

    if not input_type_id:
        raise Exception('Error: Foundation type: "{}" is not a valid type.'.format(input_type_id))

    try:
        return input_groups[input_type_id]
    except KeyError:
        raise Exception('Error: Foundation type: "{}" is not a valid type.'.format(input_type_id))


def get_component_input_by_name(_input_group, _name):
    # type: (Dict[int, ComponentInput], str) -> Optional[ComponentInput]
    """Get the component input from the input group by name."""
    for value in _input_group.values():
        if value.name == _name:
            return value


def convert_input(_input, _target_unit):
    # type: (str, str) -> Optional[Union[float, int]]
    """Convert a single input to the target unit."""
    user_input_value, user_input_unit = parser.parse_input(_input)
    converted_input = converter.convert(user_input_value, user_input_unit, _target_unit)
    print(
        "Converting: {:.3f}-{} --> {:.3f}-{}".format(
            float(user_input_value), user_input_unit, converted_input, _target_unit
        )
    )
    return converted_input


def convert_list_of_inputs(_input_list, _target_unit):
    # type: (Iterable[Any], str) -> List[Optional[Union[float, int]]]
    """Convert a list of inputs to the target unit."""
    user_input = []
    for val in _input_list:
        val, input_unit = parser.parse_input(val)
        val = converter.convert(val, input_unit, _target_unit)
        user_input.append(val)
    return user_input


# -----------------------------------------------------------------------------
# Component Interface


class GHCompo_CreateFoundations(object):
    foundation_classes = {
        1: foundations.PhHeatedBasement,
        2: foundations.PhUnheatedBasement,
        3: foundations.PhSlabOnGrade,
        4: foundations.PhVentedCrawlspace,
        5: foundations.PhFoundation,
    }  # type: Dict[int, Type[foundations.PhFoundation]]

    def __init__(self, _IGH, _type, _input_dict):
        # type: (gh_io.IGH, int, Dict[str, Any]) -> None
        self.IGH = _IGH
        self._foundation_type = _type
        self.input_dict = _input_dict

    @property
    def foundation_type_number(self):
        # type: () -> int
        """Get the foundation type number."""
        if not self._foundation_type:
            msg = "Set the '_type' to configure the user-inputs."
            self.IGH.warning(msg)
            return 5

        return int(self._foundation_type)

    @foundation_type_number.setter
    def foundation_type_number(self, _in):
        # type: (Union[str, int]) -> None
        """Set the foundation type number."""
        self._foundation_type = input_to_int(_in)

    @property
    def valid_foundation_type_names(self):
        # type: () -> List[str]
        """Get the list of valid foundation types."""
        return sorted(foundations.PhFoundationType.allowed)

    def create_new_foundation(self):
        # type: () -> foundations.PhFoundation
        """Create a new PhFoundation object based on the user-inputs."""
        try:
            foundation_class = self.foundation_classes[self.foundation_type_number]
            return foundation_class()
        except KeyError as e:
            raise Exception(
                "Error: Input foundation type: '{}' not supported. Please only input: "
                "{}".format(self.foundation_type_number, self.valid_foundation_type_names)
            )

    @property
    def gh_component_input_group(self):
        # type: () -> Dict[int, ComponentInput]
        """Get the GH-Component input group dict for this system type."""
        if self.foundation_type_number:
            return get_component_inputs(str(self.foundation_type_number))
        else:
            return {}

    def run(self):
        # type: () -> foundations.PhFoundation
        """Return a new PhFoundation object with attributes based on the user-inputs."""

        # -- Create the new PhFoundation Object
        hbph_foundation_obj_ = self.create_new_foundation()
        hbph_foundation_obj_.display_name = self.input_dict["_display_name"]

        # -- Set all the new PhFoundation Object's attributes from user-inputs
        for attr_name in dir(hbph_foundation_obj_):
            if attr_name.startswith("_"):
                continue

            # -- Pull out the user-input-value for this attribute
            user_input = self.input_dict.get(attr_name, None)

            # -- Find the GH-Component's Input Node for the attribute so we can check the unit-conversion (if any)
            target_unit = None
            gh_compo_input = get_component_input_by_name(self.gh_component_input_group, attr_name)
            if gh_compo_input:
                target_unit = gh_compo_input.target_unit

            # -- Convert the attribute's user-input-value, if necessary
            if user_input and target_unit:
                if isinstance(user_input, (list, tuple, set)):
                    user_input = convert_list_of_inputs(user_input, target_unit)
                else:
                    user_input = convert_input(user_input, target_unit)

            # -- Set the attribute value
            if user_input:
                setattr(hbph_foundation_obj_, attr_name, user_input)

        return hbph_foundation_obj_
