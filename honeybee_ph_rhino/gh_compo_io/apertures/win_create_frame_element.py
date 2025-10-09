# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create PH Window Frame Element."""

try:
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction import window
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io, validators
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

try:
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


class GHCompo_CreatePhWinFrameElement(object):
    """Interface to collect and clean PhWindowFrameElement user-inputs."""

    display_name = validators.HBName("display_name")
    width = validators.UnitM("width", default=0.1)
    u_factor = validators.UnitW_M2K("u_factor", default=1.0)
    psi_glazing = validators.UnitW_MK("psi_glazing", default=0.04)
    psi_install = validators.UnitW_MK("psi_install", default=0.04)
    chi_value = validators.UnitW_K("chi_value", default=0.0)

    def __init__(self, _IGH, _display_name, _width, _u_factor, _psi_glazing, _psi_install, _chi_value):
        # type: (gh_io.IGH, str, float, float, float, float, float) -> None
        self.IGH = _IGH
        self.display_name = _display_name or clean_and_id_ep_string("PhWindowFrameElement")
        self.width = self.value_with_unit(_width)
        self.u_factor = _u_factor
        self.psi_glazing = _psi_glazing
        self.psi_install = _psi_install
        self.chi_value = _chi_value

    def value_with_unit(self, _value):
        # type: (str | float | None) -> str | None
        """Return a string of a value and a unit. If none is supplied, with use the Rhino-doc's unit type."""

        if _value is None:
            return None

        # -- If the user supplied an input unit, just use that
        input_value, input_unit = parse_input(_value)

        # -- otherwise use the Rhino document unit system as the input unit
        if not input_unit:
            input_unit = self.IGH.get_rhino_unit_system_name()

        if input_value is None:
            raise ValueError("Failed to parse reveal-distance input {}?".format(_value))

        return "{} {}".format(input_value, input_unit)

    def run(self):
        # type: () -> window.PhWindowFrameElement
        """Returns a new HBPH PhWindowFrameElement object."""

        obj = window.PhWindowFrameElement(self.display_name)
        obj.display_name = self.display_name
        obj.width = self.width
        obj.u_factor = self.u_factor
        obj.psi_glazing = self.psi_glazing
        obj.psi_install = self.psi_install
        obj.chi_value = self.chi_value

        return obj

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self.display_name)
