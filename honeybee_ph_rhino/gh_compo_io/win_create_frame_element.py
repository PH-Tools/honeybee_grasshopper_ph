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
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreatePhWinFrameElement(object):
    """Interface to collect and clean PhWindowFrameElement user-inputs."""

    display_name = ghio_validators.HBName("display_name")
    width = ghio_validators.UnitM("width", default=0.1)
    u_factor = ghio_validators.UnitW_M2K("u_factor", default=1.0)
    psi_glazing = ghio_validators.UnitW_MK("psi_glazing", default=0.04)
    psi_install = ghio_validators.UnitW_MK("psi_install", default=0.04)
    chi_value = ghio_validators.UnitW_K("chi_value", default=0.0)

    def __init__(
        self, _display_name, _width, _u_factor, _psi_glazing, _psi_install, _chi_value
    ):
        # type: (str, float, float, float, float, float) -> None
        self.display_name = _display_name or clean_and_id_ep_string(
            "PhWindowFrameElement"
        )
        self.width = _width
        self.u_factor = _u_factor
        self.psi_glazing = _psi_glazing
        self.psi_install = _psi_install
        self.chi_value = _chi_value

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
