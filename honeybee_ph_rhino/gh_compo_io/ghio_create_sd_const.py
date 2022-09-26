# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""HBPH Create SD Construction Interfaces"""

try:
    from itertools import izip_longest
except ImportError:
    # -- Python 3+
    from itertools import zip_longest as izip_longest

try:
    from honeybee_energy.material.opaque import EnergyMaterial, EnergyMaterialNoMass
    from honeybee_energy.construction.opaque import OpaqueConstruction
except ImportError:
    raise Exception("Error importing honeybee_energy modules?")

class ICreateSDConst(object):
    MASS_HB_MAT = EnergyMaterial('MAT_Mass', 0.01, 100, 2500, 460, 'Rough',0.9, 0.7, 0.7)

    def __init__(self, _names, _u_values):
        self.names = _names
        self.u_values = _u_values
        self._cleanup_input_lists()

    def _cleanup_input_lists(self):
        """Make sure the input list lengths align."""
        if not self.names or not self.u_values:
            return

        if len(self.names) < len(self.u_values):
            for _ in range(len(self.u_values)-len(self.names)):
                self.names.append(self.names[0])
        elif len(self.names) > len(self.u_values):
            for _ in range(len(self.names) - len(self.u_values)):
                self.u_values.append(self.u_values[0])

    def create_sd_constructions(self):
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