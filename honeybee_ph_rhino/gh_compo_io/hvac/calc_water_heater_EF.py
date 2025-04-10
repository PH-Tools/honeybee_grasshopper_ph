# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Calculate Water Heater Energy Factor."""

try:
    from typing import Any, Callable
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_rhino.gh_io import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

# -- Use-Types
CONSUMER = 1
INSTANT = 2
COMMERCIAL = 3

# -- Heater-Types
GAS = 1
ELECTRIC_RESISTANCE = 2
HEAT_PUMP = 3


def get_conversion_function(_use_type, _heater_type):
    # type: (int | None, int | None) -> Callable[[float], float] | None
    """Returns a UEF -> EF conversion function based on use-type and heater-type.

    Conversion functions are based on the RESNET calculator:
    > 'RESNET Energy Factor Conversion Equations based on Water Heater Type'
    > https://www.resnet.us/wp-content/uploads/RESNET-EF-Calculator-2017.xlsx
    """
    conversion_functions = {
        None: {},
        # 1 - Use-Type: Consumer (Single family home)
        CONSUMER: {
            GAS: lambda uef: 0.9066 * uef + 0.0711,
            ELECTRIC_RESISTANCE: lambda uef: min(2.4029 * uef - 1.2844, 0.96),
            HEAT_PUMP: lambda uef: 1.2101 * uef - 0.6052,
        },
        # 2 - Use-Type: Instant
        INSTANT: {
            GAS: lambda uef: uef,
            ELECTRIC_RESISTANCE: lambda uef: min(uef, 1.0),
            HEAT_PUMP: lambda uef: uef,
        },
        # 3 - Use-Type: Commercial (including Multi-Family)
        COMMERCIAL: {
            GAS: lambda uef: 1.0005 * uef + 0.0019,
            ELECTRIC_RESISTANCE: lambda uef: min(1.0219 * uef - 0.0025, 1.0),
            HEAT_PUMP: lambda uef: uef,
        },
    }
    return conversion_functions.get(_use_type, {}).get(_heater_type, None)


class GHCompo_CalculateWaterHeaterEnergyFactor(object):

    def __init__(self, IGH, _heater_type, _use_type, _UEF, *args, **kwargs):
        # type: (gh_io.IGH, str, str, float, *Any, **Any) -> None
        self.IGH = IGH
        self.heater_type = input_to_int(_heater_type)
        self.use_type = input_to_int(_use_type)
        self.UEF = _UEF

    @property
    def heater_type(self):
        # type: () -> int | None
        return self._heater_type

    @heater_type.setter
    def heater_type(self, value):
        # type: (int | None) -> None

        # Map standard WUFI heater-types to RESNET types
        heater_type_map = {
            None: None,
            1: ELECTRIC_RESISTANCE,
            2: GAS,
            3: GAS,
            4: ELECTRIC_RESISTANCE,
            5: HEAT_PUMP,
            6: HEAT_PUMP,
            7: HEAT_PUMP,
        }
        self._heater_type = heater_type_map.get(value, None)

    @property
    def ready(self):
        # type: () -> bool
        # -- Check Inputs
        if self.heater_type is None:
            msg = "Please provide a valid _heater_type"
            print(msg)
            self.IGH.warning(msg)
            return False

        if self.use_type is None:
            msg = "Please provide a valid _use_type"
            print(msg)
            self.IGH.warning(msg)
            return False

        if self.UEF is None:
            return False

        return True

    def run(self):
        # type: () -> float | None
        if not self.ready:
            return None

        # -- Calculate the Right EF Value
        print(
            "Getting RESNET conversion function for use-type={} | heater-type={}".format(
                self.use_type, self.heater_type
            )
        )
        func = get_conversion_function(self.use_type, self.heater_type)
        if func is None:
            msg = "Failed to find a conversion function for use-type={} | heater-type={}.".format(
                self.use_type, self.heater_type
            )
            print(msg)
            self.IGH.error(msg)
            return None

        return func(self.UEF)
