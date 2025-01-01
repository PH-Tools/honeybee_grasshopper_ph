# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Material Column/Row."""

try:
    from typing import Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_energy.material import opaque
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties.materials.opaque import EnergyMaterialPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_SetMaterialColumnAndRow(object):
    def __init__(self, IGH, _column_position, _row_position, _hbe_material):
        # type: (gh_io.IGH, Optional[int], Optional[int], opaque.EnergyMaterial) -> None
        self.IGH = IGH
        self.column_position = _column_position
        self.row_position = _row_position
        self.hbe_material = _hbe_material

    def ready(self):
        # type: () -> bool
        if self.column_position is None:
            return False
        if self.row_position is None:
            return False
        if self.hbe_material is None:
            return False
        return True

    def run(self):
        # type: () -> Optional[opaque.EnergyMaterial]
        if not self.ready():
            return self.hbe_material

        col_position = gh_io.input_to_int(str(self.column_position))
        row_position = gh_io.input_to_int(str(self.row_position))

        hbe_material_ = self.hbe_material.duplicate()
        ph_prop = getattr(hbe_material_.properties, "ph")  # type: EnergyMaterialPhProperties

        if not hasattr(ph_prop, "user_data"):
            ph_prop.user_data = {}

        ph_prop.user_data["column_position"] = col_position
        ph_prop.user_data["row_position"] = row_position

        return hbe_material_
