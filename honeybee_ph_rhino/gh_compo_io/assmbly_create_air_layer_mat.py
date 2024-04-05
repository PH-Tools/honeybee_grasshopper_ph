# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Calc Air Layer HB Material."""

try:
    from typing import Optional
except ImportError:
    pass  # IronPython 2.7

from honeybee.typing import clean_ep_string
from honeybee_energy.material.opaque import EnergyMaterial

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_utils.input_tools import input_to_int
except:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))


class GHCompo_AirLayerMaterial(object):
    """Equivalent Thermal Conductivity of Still Air Layers according to PHPP method.

    Applicable to assembly air-layers which are up to 300m thick (12in) AND where
    the width and length of the layer are BOTH >10x the thickness of the layer.
    This method is similar to the ISO-6946-2017, Appendix D method but not identical.
    """

    display_name = ghio_validators.HBName("display_name")
    thickness = ghio_validators.UnitM("thickness")
    e_1 = ghio_validators.FloatPercentage("e_1")
    e_2 = ghio_validators.FloatPercentage("e_2")

    def __init__(self, _IGH, _name, _hf_direction, _thickness, _e1, _e2):
        # type: (gh_io.IGH, str, str, float, float, float) -> None
        self.IGH = _IGH
        self.hf_direction = input_to_int(_hf_direction, 2)
        self.thickness = _thickness or 0.000
        self.e_1 = _e1 or 0.9
        self.e_2 = _e2 or 0.9
        self.display_name = _name or "PH_AirLayer_({:.3f}m_{})".format(self.thickness, self.orientation)

    @property
    def h_r(self):
        # type: () -> float
        """Radiative Coefficient (W/m2-K)"""
        return 5.1 / (1 / self.e_1 + 1 / self.e_2 - 1)

    @property
    def alpha(self):
        # type: () -> int
        """Surface normal direction in degrees. 0=up, 180=down"""
        if self.hf_direction == 1:
            return 0  # Upwards
        elif self.hf_direction == 2:
            return 90  # Horizontal
        elif self.hf_direction == 3:
            return 180
        else:
            raise Exception("Error: Surface orientation not allowed.")

    @property
    def orientation(self):
        # type: () -> str
        """Surface normal direction description"""
        if self.hf_direction == 1:
            return "Upwards Heat Flow"
        elif self.hf_direction == 2:
            return "Horizontal Heat Flow"
        elif self.hf_direction == 3:
            return "Downwards Heat Flow"
        else:
            raise Exception("Error: Surface orientation not allowed.")

    @property
    def h_a(self):
        # type: () -> float
        """Conduction / Convection Coefficient (W/m2-K)

        h a is determined by conduction in still air for narrow airspaces and
        by convection in wide cavities. For calculations in accordance with
        ISO-6946-2017, it is the larger of 0.025/d and the value of h_a obtained from
        Table D.1 or Table D.2. In Tables D.1 and D.2, d is the thickness of the
        airspace in the direction of heat flow, in metres, and ΔT is the temperature
        difference across the airspace, in kelvins. Table D.1 should be used when
        the temperature difference across the airspace is less than or equal to 5K.
        """

        if self.alpha == 0:
            # Upwards
            return max(1.95, 0.025 / self.thickness)
        elif self.alpha == 90:
            # Horizontal
            return max(1.25, 0.025 / self.thickness)
        elif self.alpha == 180:
            # Downwards
            return max(0.12 * (self.thickness**-0.44), 0.025 / self.thickness)
        else:
            raise Exception("Error: Surface orientation not")

    @property
    def thermal_conductivity(self):
        # type: () -> float
        """W/mK"""
        return self.thickness * (self.h_a + self.h_r)

    def create_new_HB_Material(self):
        # type: () -> EnergyMaterial
        return EnergyMaterial(
            identifier=self.display_name,
            thickness=self.thickness,
            conductivity=self.thermal_conductivity,
            density=999.999,
            specific_heat=999.999,
            roughness="MediumRough",
            thermal_absorptance=0.9,
            solar_absorptance=0.7,
            visible_absorptance=None,
        )

    def run(self):
        # type: () -> Optional[EnergyMaterial]
        if not self.thickness or not self.hf_direction:
            return None

        return self.create_new_HB_Material()
