# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create SD Constructions."""

try:
    from typing import List, Union, Tuple
except ImportError:
    pass # IronPython 2.7

try:
    from itertools import izip_longest # type: ignore
except ImportError:
    # -- Python 3+
    from itertools import zip_longest as izip_longest

try:
    from honeybee_ph_utils import units
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))

try:
    from honeybee_energy.material.opaque import EnergyMaterial, EnergyMaterialNoMass
    from honeybee_energy.construction.opaque import OpaqueConstruction
except ImportError:
    raise Exception("Error importing honeybee_energy modules?")

class GHCompo_CreateSDConstructions(object):
    MASS_HB_MAT = EnergyMaterial('MAT_Mass', 0.01, 100, 2500, 460, 'Rough',0.9, 0.7, 0.7)

    def __init__(self, _names, _u_values):
        # type: (List[str], List[str]) -> None
        _u_value_inputs, self.names = self._cleanup_input_lists(_names, _u_values)
        self.u_values = self._convert_u_value_units(_u_value_inputs)

    def _cleanup_input_lists(self, _names, _u_value_inputs):
        # type: (List[str], List[str]) -> Tuple[List[str], List[str]]
        """Make sure the input list lengths align."""
        u_value_inputs_ = [] # type: List[str]
        names_ = [] # type: List[str]
        
        if len(_names) < len(_u_value_inputs):
            for u_value_input, name in izip_longest(_u_value_inputs, _names, fillvalue=_u_value_inputs[0]):
                u_value_inputs_.append(u_value_input)
                names_.append(name)
        elif len(_names) > len(_u_value_inputs):
            for u_value_input, name in izip_longest(_u_value_inputs, _names, fillvalue=_names[0]):
                u_value_inputs_.append(u_value_input)
                names_.append(name)
        else:
            for u_value_input, name in izip_longest(_u_value_inputs, _names):
                u_value_inputs_.append(u_value_input)
                names_.append(name)

        return u_value_inputs_, names_

    def _convert_u_value_units(self, _u_value_inputs):
        # type: (List[str]) -> List[Union[int, float]]
        """Ensure all U-Values are converted to SI units."""
        _ = [] # type: List[Union[float, int]]
        
        for u_value in _u_value_inputs:
            val, unit = units.parse_input(u_value)
            
            val = units.convert(val, unit, "W/M2K")
            if val:
                _.append(val)
        return _

    def run(self):
        # type: () -> List[OpaqueConstruction]
        hb_constructions_ = []
        if self.names and self.u_values:
            # Create and add a new HB Construction to the output list
            for name, u_value in izip_longest(self.names, self.u_values):
                hb_constructions_.append(
                    OpaqueConstruction(
                        name,
                        [
                            self.MASS_HB_MAT,
                            EnergyMaterialNoMass("MAT_{}".format(name), 1/u_value, 'Rough', 0.9, 0.7, 0.7),
                            self.MASS_HB_MAT
                        ]
                    )
                )

        return hb_constructions_