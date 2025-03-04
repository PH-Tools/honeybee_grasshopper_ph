# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create PH Equipment."""

from copy import copy  # Use copy so that specific equipments can overwrite base with their own hints


try:
    from typing import Type
except ImportError:
    pass # IronPython 2.7

from GhPython import Component  # type: ignore
from Grasshopper.Kernel.Parameters import Hints  # type: ignore

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_io import ComponentInput
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_energy_ph.load import ph_equipment
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_utils.input_tools import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))


# -----------------------------------------------------------------------------
# -- Setup the component input node groups

inputs_base = {
    2: ComponentInput(
        _name="comment",
        _description="(str) User defined comment / note.",
        _type_hint=Component.NewStrHint(),
    ),
    3: ComponentInput(_name="reference_quantity", _description="() some WUFI stuff."),
    4: ComponentInput(
        _name="quantity",
        _description="(int) The total number of appliances / pieces of equipment included.",
        _type_hint=Hints.GH_IntegerHint_CS(),
    ),
    5: ComponentInput(
        _name="in_conditioned_space",
        _description="(bool) default=True, Set False if the appliance is outside and the waste heat from the appliance does not count towards internal-gains in the space.",
        _type_hint=Hints.GH_BooleanHint_CS(),
    ),
    6: ComponentInput(
        _name="reference_energy_norm",
        _description="() some other WUFI stuff.",
        _type_hint=Component.NewStrHint(),
    ),
    7: ComponentInput(
        _name="energy_demand",
        _description="(float) usually kWh/yr",
        _type_hint=Component.NewFloatHint(),
    ),
    8: ComponentInput(
        _name="energy_demand_per_use",
        _description="(float) usually kWh/use",
        _type_hint=Component.NewFloatHint(),
    ),
    9: ComponentInput(
        _name="combined_energy_factor",
        _description="(float)",
        _type_hint=Component.NewFloatHint(),
    ),
}

inputs_dishwasher = copy(inputs_base)
inputs_dishwasher.update(
    {
        10: ComponentInput(
            _name="capacity_type",
            _description='Input "1-Standard" or ',
            _type_hint=Component.NewStrHint(),
        ),
        11: ComponentInput(_name="capacity", _description="(float)", _type_hint=Component.NewFloatHint()),
        12: ComponentInput(
            _name="water_connection",
            _description='Input either -\n "1-DHW Connection"\n "2-Cold Water Connection"',
            _type_hint=Component.NewStrHint(),
        ),
    }
)

inputs_clothes_washer = copy(inputs_base)
inputs_clothes_washer.update(
    {
        10: ComponentInput(_name="capacity", _description="", _type_hint=Component.NewFloatHint()),
        11: ComponentInput(
            _name="modified_energy_factor",
            _description="",
            _type_hint=Component.NewFloatHint(),
        ),
        12: ComponentInput(
            _name="water_connection",
            _description='Input either -\n "1-DHW Connection"\n "2-Cold Water Connection"',
            _type_hint=Component.NewStrHint(),
        ),
        13: ComponentInput(
            _name="utilization_factor",
            _description="",
            _type_hint=Component.NewFloatHint(),
        ),
    }
)

inputs_clothes_dryer = copy(inputs_base)
inputs_clothes_dryer.update(
    {
        10: ComponentInput(
            _name="dryer_type",
            _description='Input either -\n "1-CLOTHES LINE"\n "2-DRYING CLOSET (COLD!)"\n "3-DRYING CLOSET (COLD!) IN EXTRACT AIR"\n "4-CONDENSATION DRYER"\n "5-ELECTRIC EXHAUST AIR DRYER"\n "6-GAS EXHAUST AIR DRYER"\n ',
            _type_hint=Component.NewStrHint(),
        ),
        11: ComponentInput(_name="gas_consumption", _description="", _type_hint=Component.NewFloatHint()),
        12: ComponentInput(
            _name="gas_efficiency_factor",
            _description="",
            _type_hint=Component.NewFloatHint(),
        ),
        13: ComponentInput(
            _name="field_utilization_factor_type",
            _description="",
            _type_hint=Component.NewFloatHint(),
        ),
        14: ComponentInput(
            _name="field_utilization_factor",
            _description="",
            _type_hint=Component.NewFloatHint(),
        ),
    }
)

inputs_refrigerator = copy(inputs_base)
inputs_refrigerator.update({})

inputs_freezer = copy(inputs_base)
inputs_freezer.update({})

inputs_fridge_freezer = copy(inputs_base)
inputs_fridge_freezer.update({})

inputs_cooktop = copy(inputs_base)
inputs_cooktop.update(
    {
        10: ComponentInput(
            _name="cooktop_type",
            _description='Input either -\n "1-ELECTRICITY"\n "2-NATURAL GAS"\n "3-LPG",',
            _type_hint=Component.NewStrHint(),
        ),
    }
)

input_Phius_MEL = copy(inputs_base)
input_Phius_MEL.update({})

inputs_Phius_Lighting_Int = copy(inputs_base)
inputs_Phius_Lighting_Int.update(
    {
        10: ComponentInput(
            _name="frac_high_efficiency",
            _description='The percentage of lighting which is "high efficiency."',
            _type_hint=Component.NewFloatHint(),
        ),
    }
)


inputs_Phius_Lighting_Ext = copy(inputs_base)
inputs_Phius_Lighting_Ext.update(
    {
        10: ComponentInput(
            _name="frac_high_efficiency",
            _description='The percentage of lighting which is "high efficiency."',
            _type_hint=Component.NewFloatHint(),
        ),
    }
)


inputs_Phius_Lighting_Garage = copy(inputs_base)
inputs_Phius_Lighting_Garage.update(
    {
        10: ComponentInput(
            _name="frac_high_efficiency",
            _description='The percentage of lighting which is "high efficiency."',
            _type_hint=Component.NewFloatHint(),
        ),
    }
)

inputs_Custom_Elec = copy(inputs_base)
inputs_Custom_Lighting = copy(inputs_base)
inputs_Custom_MEL = copy(inputs_base)

inputs_phius_defaults = {}
inputs_phi_defaults = {}

# -----------------------------------------------------------------------------

input_groups = {
    1: inputs_dishwasher,
    2: inputs_clothes_washer,
    3: inputs_clothes_dryer,
    4: inputs_refrigerator,
    5: inputs_freezer,
    6: inputs_fridge_freezer,
    7: inputs_cooktop,
    13: input_Phius_MEL,
    14: inputs_Phius_Lighting_Int,
    15: inputs_Phius_Lighting_Ext,
    16: inputs_Phius_Lighting_Garage,
    11: inputs_Custom_Elec,
    17: inputs_Custom_Lighting,
    18: inputs_Custom_MEL,
    100: inputs_phius_defaults,
    200: inputs_phi_defaults,
}

# -----------------------------------------------------------------------------


def get_component_inputs(_equipment_type):
    # type: (str) -> dict
    """Select the component input-node group based on the 'type' specified"""

    if not _equipment_type:
        return {}

    input_type_id = input_to_int(_equipment_type)

    if not input_type_id:
        raise Exception('Error: Equip. type ID: "{}" is not a valid equip type.'.format(input_type_id))

    try:
        return input_groups[input_type_id]
    except KeyError:
        raise Exception('Error: Equip. type ID: "{}" is not a valid equip type.'.format(input_type_id))


# -----------------------------------------------------------------------------
# Component Interface


class GHCompo_CreateElecEquip(object):
    phius_defaults = [
        ph_equipment.PhDishwasher.phius_default,
        ph_equipment.PhClothesWasher.phius_default,
        ph_equipment.PhClothesDryer.phius_default,
        ph_equipment.PhFridgeFreezer.phius_default,
        ph_equipment.PhCooktop.phius_default,
        ph_equipment.PhPhiusMEL.phius_default,
        ph_equipment.PhPhiusLightingInterior.phius_default,
        ph_equipment.PhPhiusLightingExterior.phius_default,
    ]
    phi_defaults = [
        ph_equipment.PhDishwasher.phi_default,
        ph_equipment.PhClothesWasher.phi_default,
        ph_equipment.PhClothesDryer.phi_default,
        ph_equipment.PhFridgeFreezer.phi_default,
        ph_equipment.PhCooktop.phi_default,
    ]
    equipment_classes = {
        None: [],
        1: [ph_equipment.PhDishwasher],
        2: [ph_equipment.PhClothesWasher],
        3: [ph_equipment.PhClothesDryer],
        4: [ph_equipment.PhRefrigerator],
        5: [ph_equipment.PhFreezer],
        6: [ph_equipment.PhFridgeFreezer],
        7: [ph_equipment.PhCooktop],
        13: [ph_equipment.PhPhiusMEL],
        14: [ph_equipment.PhPhiusLightingInterior],
        15: [ph_equipment.PhPhiusLightingExterior],
        16: [ph_equipment.PhPhiusLightingGarage],
        11: [ph_equipment.PhCustomAnnualElectric],
        17: [ph_equipment.PhCustomAnnualLighting],
        18: [ph_equipment.PhCustomAnnualMEL],
        100: phius_defaults,
        200: phi_defaults,
    }
    valid_equipment_types = [
        "1-dishwasher",
        "2-clothes_washer",
        "3-clothes_dryer",
        "4-fridge",
        "5-freezer",
        "6-fridge_freezer",
        "7-cooking",
        "13-PHIUS_MEL",
        "14-PHIUS_Lighting_Int",
        "15-PHIUS_Lighting_Ext",
        "16-PHIUS_Lighting_Garage",
        "11-Custom_Electric_per_Year",
        "17-Custom_Electric_Lighting_per_Year",
        "18-Custom_Electric_MEL_per_Use",
        "100-PhiUS_Defaults",
        "200-Phi_Defaults",
    ]
    # "21-Commercial_Dishwasher", "22-Commercial_Refrigerator", "23-Commercial_Cooking", "24-Commercial_Custom"]

    def __init__(self, _IGH, _equip_type, _input_dict):
        # type: (gh_io.IGH, int, dict) -> None
        self.IGH = _IGH
        self.equip_type = _equip_type
        self.input_dict = _input_dict

    @property
    def equip_type(self):
        # type: () -> int | None
        return self._equip_type

    @equip_type.setter
    def equip_type(self, _in):
        # type: (int) -> None
        self._equip_type = input_to_int(_in)

    @property
    def ready(self):
        # type: () -> bool
        if self.equip_type is None:
            msg = "Set the '_type' to configure the user-inputs."
            self.IGH.warning(msg)
            return False
        return True

    def get_equipment_classes(self):
        # type: () -> list[Type[ph_equipment.PhEquipment]]
        """Get a list of the equipment classes to build, based on the equipment-type input."""
        try:
            return self.equipment_classes[self.equip_type]
        except KeyError as e:
            raise Exception(
                "Error: Input Equipment type: '{}' is not supported. Please only input: "
                "{}".format(self.equip_type, self.valid_equipment_types)
            )
    
    def set_object_attributes(self, _equipment_obj):
        # type: (ph_equipment.PhEquipment) -> ph_equipment.PhEquipment
        """Set the object's attributes based on the component inputs"""
        for attr_name in dir(_equipment_obj):
            if attr_name.startswith("_"):
                continue

            input_val = self.input_dict.get(attr_name)
            if input_val:
                setattr(_equipment_obj, attr_name, input_val)
        
        return _equipment_obj

    def run(self):
        # type: () -> list[ph_equipment.PhEquipment]
        equipment_ = []
        if not self.ready:
            return equipment_

        for equip_class in self.get_equipment_classes():
            equipment_obj = equip_class()
            equipment_obj = self.set_object_attributes(equipment_obj)
            equipment_.append(equipment_obj)

        return equipment_
