# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Material Color."""

try:
    from typing import Union
except ImportError:
    pass  # IronPython 2.7

try:
    import System.Drawing.Color  # type: ignore
except ImportError:
    raise Exception("Error importing System.Drawing.Color.")

try:
    from honeybee_energy.material import opaque

    try:
        HBMaterial = Union[
            opaque.EnergyMaterial,
            opaque.EnergyMaterialNoMass,
            opaque.EnergyMaterialVegetation,
        ]
    except NameError:
        pass  # Union is not defined, IronPython 2.7
except ImportError:
    raise Exception("Error importing honeybee_energy modules.")

try:
    from honeybee_ph_utils.color import PhColor
except ImportError:
    raise Exception("Error importing honeybee_ph_utils modules.")


class GHCompo_SetMaterialColor(object):
    def __init__(self, _IHG, _material, _color, *args, **kwargs):
        # type : gh_io.IGH, Optional[HBMaterial], Optional[System.Drawing.Color] -> None
        self.IGH = _IHG
        self.material = _material
        self.color = _color

    @property
    def ready(self):
        # type: () -> bool
        return self.material and self.color

    def run(self):
        # type: () -> HBMaterial
        if not self.ready:
            return self.material

        material_ = self.material.duplicate()
        material_.properties.ph.ph_color = PhColor.from_system_color(self.color)

        return material_
