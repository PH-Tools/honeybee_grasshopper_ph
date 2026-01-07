# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH Additional Zone.

This component follows the protocol as implementing in the Phius 'TRF' Calculator. For details, see:
https://www.phius.org/phius-temperature-reduction-factor-auxiliary-space-heating-estimator
"""

try:
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.boundarycondition import PhAdditionalZone
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


REDUCTION_FACTOR_OUTSIDE = 1.0
REDUCTION_FACTOR_INSIDE = 0.0
AVERAGE_TEMP_C_INSIDE = 20.0


class GHCompo_AdditionalZone(object):
    attached_zone_temp_C = ghio_validators.UnitDegreeC("attached_zone_temp_C", default=4.444)

    def __init__(self, _IGH, _attached_zone_name, _attached_zone_temp_C, _monthly_outdoor_air_drybulb_temps_C):
        # type: (gh_io.IGH, str, float, list[float]) -> None
        self.IGH = _IGH
        self.attached_zone_name = _attached_zone_name
        self.attached_zone_temp_C = _attached_zone_temp_C
        self.monthly_outdoor_air_drybulb_temps_C = _monthly_outdoor_air_drybulb_temps_C
        self.zone_type = "Unheated space"

    @property
    def monthly_outdoor_air_drybulb_temps_C(self):
        # type: () -> list[float]
        """The monthly outdoor air drybulb temps in deg-C."""

        return self._monthly_outdoor_air_drybulb_temps_C

    @monthly_outdoor_air_drybulb_temps_C.setter
    def monthly_outdoor_air_drybulb_temps_C(self, _input_list):
        # type: (list[float]) -> None
        """Validate that the input data is the right shape."""

        if not _input_list:
            self._monthly_outdoor_air_drybulb_temps_C = []
            return

        if len(_input_list) != 12:
            msg = "Error: Monthly data should be a collection of 12 numeric items.\n" "Got a {} of length: {}?".format(
                type(_input_list), len(_input_list)
            )
            raise Exception(msg)

        temps_C = []
        for t in _input_list:
            input_value, input_units = parse_input(str(t))
            result = convert(input_value, input_units or "C", "C")
            temps_C.append(result)

        self._monthly_outdoor_air_drybulb_temps_C = temps_C

    @property
    def average_monthly_outdoor_air_drybulb_temps_C(self):
        # type: () -> float
        """The average of the monthly outdoor air drybulb temps that are less than or equal to the attached zone temp."""

        t = [_ for _ in self.monthly_outdoor_air_drybulb_temps_C if _ <= self.attached_zone_temp_C]
        try:
            avg_temp = sum(t) / len(t)
        except ZeroDivisionError:
            avg_temp = self.attached_zone_temp_C
        return avg_temp

    @property
    def slope(self):
        # type: () -> float
        """The slope used to determine the temperature reduction factor."""
        
        slope = (AVERAGE_TEMP_C_INSIDE - self.average_monthly_outdoor_air_drybulb_temps_C) / (
            REDUCTION_FACTOR_INSIDE - REDUCTION_FACTOR_OUTSIDE
        )
        return slope

    @property
    def temp_reduction_factor(self):
        # type: () -> float
        """The temperature reduction factor for the additional zone."""

        return max((self.attached_zone_temp_C - AVERAGE_TEMP_C_INSIDE) / self.slope, 0)

    @property
    def ready(self):
        # type: () -> bool
        """Check if the component has all required inputs to run."""
        
        if not self.attached_zone_name:
            return False
        if not self.attached_zone_temp_C:
            return False
        if not self.monthly_outdoor_air_drybulb_temps_C:
            return False
        return True

    def print_inputs(self):
        # type: () -> None
        """Print log messages for the user."""

        print("Attached Zone Temp: {:.2f} deg-C".format(self.attached_zone_temp_C))
        print("Average Monthly Outdoor Air Drybulb Temps: {:.2f} deg-C".format(self.average_monthly_outdoor_air_drybulb_temps_C))
        print(
            "slope = ({:.2f} - {:.2f}) / ({:.2f} - {:.2f}) = {:.2f}".format(
                AVERAGE_TEMP_C_INSIDE,
                self.average_monthly_outdoor_air_drybulb_temps_C,
                REDUCTION_FACTOR_INSIDE,
                REDUCTION_FACTOR_OUTSIDE,
                self.slope,
            )
        )
        print(
            "temp_reduction_factor = ({:.2f} - {:.2f}) / {:.2f} = {:.3f}".format(
                self.attached_zone_temp_C, AVERAGE_TEMP_C_INSIDE, self.slope, self.temp_reduction_factor
            )
        )

    def run(self):
        # type: () -> PhAdditionalZone | None
        if not self.ready:
            return None
        
        self.print_inputs()

        return PhAdditionalZone(
            identifier=clean_and_id_string("PhAdditionalZone"),
            temperature=self.average_monthly_outdoor_air_drybulb_temps_C,
            zone_name=self.attached_zone_name,
            zone_type=self.zone_type,
            temperature_reduction_factor=self.temp_reduction_factor,
        )
