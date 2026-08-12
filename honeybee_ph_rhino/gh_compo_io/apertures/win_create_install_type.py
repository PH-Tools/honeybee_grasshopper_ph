# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Aperture Install Type."""

try:
    from honeybee.typing import clean_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction.window import PhApertureInstallType
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

# -- NOTE: gh_io is used in type-comments only. The import is optional so this module's
# -- pure helpers stay importable (and testable) outside of Rhino (see issue #59 lesson).
try:
    from ph_gh_component_io import gh_io
except ImportError:
    pass

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


def parse_psi_install_w_mk(_raw_input):
    # type: (str) -> float
    """Parse a user-provided psi-install input and return the value in W/mK.

    Accepts a bare number (assumed W/mK) or a value with a unit (ie: '0.15 BTU/HR-FT-F').
    An explicit 0 is a real value (the 'no install thermal bridge' state).
    """
    input_value, input_unit = parse_input(str(_raw_input))
    if input_value is None or input_value == "":
        raise ValueError("Failed to parse Psi-Install input: '{}'".format(_raw_input))

    input_unit = input_unit or "W/MK"
    result = convert(input_value, input_unit, "W/mK")
    if result is None:
        raise ValueError("Failed to convert Psi-Install input {} {} to W/mK".format(input_value, input_unit))

    return result


def content_keyed_identifier(_psi_install_w_mk):
    # type: (float) -> str
    """Return a stable, content-keyed identifier for an un-named Install Type.

    The identifier is derived from the value (never a uuid), so repeated runs of the
    same definition produce identical identifiers and downstream consumers can dedupe.
    """
    return clean_ep_string("PhApertureInstallType_{:.4f}".format(_psi_install_w_mk))


def build_install_type(_display_name, _psi_install_w_mk, _source=""):
    # type: (str | None, float, str) -> PhApertureInstallType
    """Build a PhApertureInstallType. Un-named types get a content-keyed identifier."""
    if _display_name:
        identifier = clean_ep_string(_display_name)
    else:
        identifier = content_keyed_identifier(_psi_install_w_mk)

    install_type = PhApertureInstallType(identifier)
    install_type.display_name = _display_name or identifier
    install_type.psi_install = _psi_install_w_mk
    install_type.source = _source or ""
    return install_type


class GHCompo_CreateApertureInstallType(object):
    """Interface to collect and clean PhApertureInstallType user-inputs."""

    def __init__(self, _IGH, _display_name, _psi_install, _source, *args, **kwargs):
        # type: (gh_io.IGH, str | None, str | None, str | None, list, dict) -> None
        self.IGH = _IGH
        self.display_name = _display_name
        self.psi_install = _psi_install
        self.source = _source

    @property
    def ready(self):
        # type: () -> bool
        return self.psi_install is not None

    def run(self):
        # type: () -> PhApertureInstallType | None
        """Return a new HBPH PhApertureInstallType object."""
        if not self.ready:
            return None

        psi_install_w_mk = parse_psi_install_w_mk(self.psi_install)
        print("Psi-Install: {:.4f} W/mK".format(psi_install_w_mk))
        return build_install_type(self.display_name, psi_install_w_mk, self.source)

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self.display_name)
