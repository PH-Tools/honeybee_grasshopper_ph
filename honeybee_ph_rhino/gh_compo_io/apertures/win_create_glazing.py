# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create PH Glazing."""

try:
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction import window
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import validators
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))


class GHCompo_CreatePhGlazing(object):
    """Interface to collect and clean PhWindowGlazing user-inputs."""

    display_name = validators.HBName("display_name", default="PhWindowGlazing")
    u_factor = validators.UnitW_M2K("u_factor", default=0.8)
    g_value = validators.FloatPercentage("g_value", default=0.4)

    def __init__(self, _name, _u_factor, _g_value):
        # type: (str, float, float) -> None
        self.display_name = _name or clean_and_id_ep_string("PhWindowGlazing")
        self.u_factor = _u_factor
        self.g_value = _g_value

    def run(self):
        # type: () -> window.PhWindowGlazing
        """Returns a new HBPH PhWindowGlazing object."""

        obj = window.PhWindowGlazing(self.display_name)
        obj.display_name = self.display_name
        obj.u_factor = self.u_factor
        obj.g_value = self.g_value

        return obj

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self.display_name)
