# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create PH Equipment."""

try:
    from typing import Type
except ImportError:
    pass  # IronPython 2.7

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

try:
    STRING_TYPES = (basestring,)  # noqa: F821
except NameError:
    STRING_TYPES = (str,)


def _normalize_input_value(_attr_name, _input_value, _current_value):
    # type: (str, object, object) -> tuple[bool, object]
    """Normalize a component input for assignment to an equipment attribute."""
    if _input_value is None:
        return False, None

    if isinstance(_input_value, STRING_TYPES):
        stripped_value = _input_value.strip()
        if not stripped_value or stripped_value.lower() == "none":
            return False, None

    if isinstance(_current_value, bool):
        # -- Apply the value itself: a truth test would drop an explicit False.
        if isinstance(_input_value, STRING_TYPES):
            text_value = _input_value.strip().lower()
            if text_value in ("true", "1"):
                return True, True
            if text_value in ("false", "0"):
                return True, False
        elif isinstance(_input_value, (bool, int, float)) and _input_value in (0, 1):
            return True, bool(_input_value)
        msg = "Error: Input '{}' with value '{}' cannot be converted to bool.".format(_attr_name, _input_value)
        raise Exception(msg)

    is_numeric_attr = isinstance(_current_value, (int, float))
    if is_numeric_attr:
        try:
            if isinstance(_current_value, float):
                return True, float(_input_value)

            float_value = float(_input_value)
            if not float_value.is_integer():
                raise ValueError
            return True, int(float_value)
        except (TypeError, ValueError, OverflowError):
            msg = "Error: Input '{}' with value '{}' cannot be converted to {}.".format(
                _attr_name, _input_value, type(_current_value).__name__
            )
            raise Exception(msg)

    return bool(_input_value), _input_value


# -----------------------------------------------------------------------------
# -- Setup the component input node groups

# -- Each input's '_name' is the equipment attribute it sets (the value-lookup key) and must not
# -- change. The '_nickname' is the canvas label. WUFI-Passive and METr read 'energy_demand' through
# -- 'reference_energy_norm'; PHPP ignores both and reads 'energy_demand_per_use' instead.

REF_QUANTITY_CODES = (
    "1-PH-case occupants, 2-Zone occupants, 3-Bedrooms, 4-PH-case units, 5-User defined, "
    "6-PH-case floor area, 7-Zone floor area, 8-n.a."
)


def _base_inputs(_ref_quantities, _norm, _energy_demand, _energy_per_use):
    # type: (str, str, str, str) -> dict[int, ComponentInput]
    """Return the common input nodes, with the type-specific text for the slots whose meaning varies."""
    return {
        2: ComponentInput(
            _name="comment",
            _nickname="comment",
            _description="(str) Note shown in WUFI-Passive and METr ('Comment'). Not used by PHPP.",
            _type_hint=Component.NewStrHint(),
        ),
        3: ComponentInput(
            _name="reference_quantity",
            _nickname="ref_quantity",
            _description="(int) WUFI/METr 'Reference quantity': what the energy demand is scaled by. "
            "Codes: {}.\nFor this type use: {}.\nNot used by PHPP.".format(REF_QUANTITY_CODES, _ref_quantities),
            _type_hint=Hints.GH_IntegerHint_CS(),
        ),
        4: ComponentInput(
            _name="quantity",
            _nickname="quantity",
            _description="(int) default=1. WUFI/METr 'Quantity': the number of units of this appliance. "
            "The 'energy_demand' is the value for a single unit, so the total is 'energy_demand' x 'quantity'. "
            "Not used by PHPP.",
            _type_hint=Component.NewStrHint(),
        ),
        5: ComponentInput(
            _name="in_conditioned_space",
            _nickname="in_conditioned_space",
            _description="(bool) default=True. WUFI/METr 'In conditioned space' and the PHPP 'inside' column. "
            "Set False if the appliance is outside and its waste heat does not count as an internal gain.",
            _type_hint=Hints.GH_BooleanHint_CS(),
        ),
        6: ComponentInput(
            _name="reference_energy_norm",
            _nickname="norm_reference",
            _description="(int) WUFI/METr 'Energy demand (norm) reference': the period the 'energy_demand' "
            "is given for. For this type: {}.\nNot used by PHPP.".format(_norm),
            _type_hint=Hints.GH_IntegerHint_CS(),
        ),
        7: ComponentInput(
            _name="energy_demand",
            _nickname="energy_demand",
            _description=_energy_demand,
            _type_hint=Component.NewFloatHint(),
        ),
        8: ComponentInput(
            _name="energy_demand_per_use",
            _nickname="energy_per_use_PHPP",
            _description=_energy_per_use,
            _type_hint=Component.NewFloatHint(),
        ),
        9: ComponentInput(
            _name="combined_energy_factor",
            _nickname="CEF",
            _description="(float) WUFI/METr 'CEF - Combined energy factor'. Used by the clothes dryer only.",
            _type_hint=Component.NewFloatHint(),
        ),
    }


WATER_CONNECTION = ComponentInput(
    _name="water_connection",
    _nickname="water_connection",
    _description="WUFI/METr 'Water connection' and the PHPP connection selector. Input either -\n"
    ' "1-DHW Connection"\n "2-Cold Water Connection"',
    _type_hint=Component.NewStrHint(),
)

inputs_dishwasher = _base_inputs(
    "1, 2 or 5",
    "2-Year",
    "(float) kWh/yr per unit. WUFI/METr 'Annual energy use rating'. Phius default: 269.",
    "(float) kWh/use. PHPP only; WUFI/METr ignore it. PHI default: 1.1.",
)
inputs_dishwasher.update(
    {
        10: ComponentInput(
            _name="capacity_type",
            _nickname="capacity_type",
            _description="WUFI/METr 'Dishwasher capacity, preselection'. Input \"1-Standard\".",
            _type_hint=Component.NewStrHint(),
        ),
        11: ComponentInput(
            _name="capacity",
            _nickname="capacity",
            _description="(float) WUFI/METr 'Dishwasher capacity, in place settings'. Default: 12.",
            _type_hint=Component.NewFloatHint(),
        ),
        12: WATER_CONNECTION,
    }
)

inputs_clothes_washer = _base_inputs(
    "1, 2 or 5",
    "2-Year",
    "(float) kWh/yr per unit. WUFI/METr 'Annual energy use'. Phius default: 120.",
    "(float) kWh/use. PHPP only; WUFI/METr ignore it. PHI default: 1.1.",
)
inputs_clothes_washer.update(
    {
        10: ComponentInput(
            _name="capacity",
            _nickname="capacity",
            _description="(float) m3. WUFI/METr 'Capacity of clothes washer' (shown in ft3 in IP). "
            "Default: 0.1274 m3 (4.5 ft3).",
            _type_hint=Component.NewFloatHint(),
        ),
        11: ComponentInput(
            _name="modified_energy_factor",
            _nickname="MEF",
            _description="(float) WUFI/METr 'MEF - Modified energy factor'. Default: 2.7.",
            _type_hint=Component.NewFloatHint(),
        ),
        12: WATER_CONNECTION,
        13: ComponentInput(
            _name="utilization_factor",
            _nickname="utilization_factor",
            _description="(float) WUFI/METr 'Utilization factor'. Default: 1.0.",
            _type_hint=Component.NewFloatHint(),
        ),
    }
)

inputs_clothes_dryer = _base_inputs(
    "1, 2 or 5",
    "2-CEF (enter the value in 'CEF')",
    "Not used by the clothes dryer: WUFI/METr read 'CEF', PHPP reads 'energy_per_use_PHPP'.",
    "(float) kWh/use. PHPP only; WUFI/METr ignore it. PHI default: 3.5.",
)
inputs_clothes_dryer[9] = ComponentInput(
    _name="combined_energy_factor",
    _nickname="CEF",
    _description="(float) lb/kWh. WUFI/METr 'CEF - Combined energy factor'. Phius default: 3.93.",
    _type_hint=Component.NewFloatHint(),
)
inputs_clothes_dryer.update(
    {
        10: ComponentInput(
            _name="dryer_type",
            _nickname="dryer_type",
            _description="WUFI/METr 'Type of laundry-dryer' and the PHPP dryer selector. Input either -\n"
            ' "1-CLOTHES LINE"\n "2-DRYING CLOSET (COLD!)"\n "3-DRYING CLOSET (COLD!) IN EXTRACT AIR"\n'
            ' "4-CONDENSATION DRYER"\n "5-ELECTRIC EXHAUST AIR DRYER"\n "6-GAS EXHAUST AIR DRYER"',
            _type_hint=Component.NewStrHint(),
        ),
        11: ComponentInput(
            _name="gas_consumption",
            _nickname="gas_consumption",
            _description="(float) WUFI/METr 'Gas consumption'. Gas dryers (type 6) only.",
            _type_hint=Component.NewFloatHint(),
        ),
        12: ComponentInput(
            _name="gas_efficiency_factor",
            _nickname="gas_CEF",
            _description="(float) WUFI/METr 'CEF - Gas'. Gas dryers (type 6) only. " "Default: 2.67.",
            _type_hint=Component.NewFloatHint(),
        ),
        13: ComponentInput(
            _name="field_utilization_factor_type",
            _nickname="field_utilization_factor_type",
            _description="(int) WUFI/METr 'Field utilization factor, preselection'. 1-Timer controls (default).",
            _type_hint=Component.NewFloatHint(),
        ),
        14: ComponentInput(
            _name="field_utilization_factor",
            _nickname="field_utilization_factor",
            _description="(float) WUFI/METr 'Field utilization factor'. Default: 1.18.",
            _type_hint=Component.NewFloatHint(),
        ),
    }
)

_fridge_args = (
    "4 or 5",
    "1-Day or 2-Year",
    "(float) kWh per day (norm 1) or per year (norm 2), per unit. WUFI/METr 'Energy demand (rated)'.",
    "(float) kWh/day. PHPP only; WUFI/METr ignore it.",
)
inputs_refrigerator = _base_inputs(*_fridge_args)
inputs_freezer = _base_inputs(*_fridge_args)
inputs_fridge_freezer = _base_inputs(*_fridge_args)

inputs_cooktop = _base_inputs(
    "1, 2 or 5",
    "1-Use",
    "(float) kWh/use. WUFI/METr 'Energy demand (rated)'. Phius default: 0.2.",
    "(float) kWh/use. PHPP only; WUFI/METr ignore it. PHI default: 0.25.",
)
inputs_cooktop.update(
    {
        10: ComponentInput(
            _name="cooktop_type",
            _nickname="cooktop_type",
            _description="WUFI/METr 'Cooking with' and the PHPP cooking selector. Input either -\n"
            ' "1-ELECTRICITY"\n "2-NATURAL GAS"\n "3-LPG"',
            _type_hint=Component.NewStrHint(),
        ),
    }
)

_phius_calculated = "(float) default=0. WUFI/METr derive this Phius load from the 'ref_quantity'."
input_Phius_MEL = _base_inputs("3 or 5", "not used", _phius_calculated, "Not used.")

FRAC_HIGH_EFFICIENCY = ComponentInput(
    _name="frac_high_efficiency",
    _nickname="frac_high_efficiency",
    _description="(float) 0.0-1.0, default=1.0. The fraction of the lighting that is high efficiency "
    "(WUFI/METr 'Fraction of high efficiency').",
    _type_hint=Component.NewFloatHint(),
)

inputs_Phius_Lighting_Int = _base_inputs("6, 7 or 5", "not used", _phius_calculated, "Not used.")
inputs_Phius_Lighting_Int.update({10: FRAC_HIGH_EFFICIENCY})

inputs_Phius_Lighting_Ext = _base_inputs("6, 7 or 5", "not used", _phius_calculated, "Not used.")
inputs_Phius_Lighting_Ext.update({10: FRAC_HIGH_EFFICIENCY})

inputs_Phius_Lighting_Garage = _base_inputs("8", "not used", _phius_calculated, "Not used.")
inputs_Phius_Lighting_Garage.update({10: FRAC_HIGH_EFFICIENCY})

_custom_args = (
    "5",
    "not used",
    "(float) kWh/yr per unit. WUFI/METr get 'energy_demand' x 'quantity' on a single line; "
    "PHPP gets the same total on its annual row.",
    "Not used.",
)
inputs_Custom_Elec = _base_inputs(*_custom_args)
inputs_Custom_Lighting = _base_inputs(*_custom_args)
inputs_Custom_MEL = _base_inputs(*_custom_args)

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
        except KeyError:
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
            should_set, normalized_val = _normalize_input_value(
                attr_name, input_val, getattr(_equipment_obj, attr_name)
            )
            if should_set:
                print("Setting attribute '{}' to '{}' [{}]".format(attr_name, normalized_val, type(normalized_val)))
                setattr(_equipment_obj, attr_name, normalized_val)

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
