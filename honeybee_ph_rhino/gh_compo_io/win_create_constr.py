# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create PH Window Construction."""

try:
    from typing import Optional, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_energy.construction.window import WindowConstruction
    from honeybee_energy.construction.windowshade import WindowConstructionShade
    from honeybee_energy.material.glazing import EnergyWindowMaterialSimpleGlazSys
    from honeybee_energy.material.shade import EnergyWindowMaterialShade
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_utils import iso_10077_1
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction import window
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))


class GHCompo_CreatePhConstruction(object):
    display_name = ghio_validators.HBName("display_name")
    nfrc_u_factor = ghio_validators.UnitW_M2K("nfrc_u_factor", default=None)
    nfrc_shgc = ghio_validators.FloatPercentage("nfrc_shgc", default=None)
    t_vis = ghio_validators.Float("t_vis", default=0.6)

    def __init__(
        self,
        _IGH,
        _display_name,
        _frame,
        _glazing,
        _nfrc_u_factor,
        _nfrc_shgc,
        _t_vis,
        _shading=None,
    ):
        # type: (gh_io.IGH, str, window.PhWindowFrame, window.PhWindowGlazing, float, float, float, Optional[EnergyWindowMaterialShade] ) -> None
        self.IGH = _IGH
        self.display_name = _display_name or clean_and_id_ep_string("PhWindowConstruction")
        self.frame = _frame
        self.glazing = _glazing
        self.hb_shade_material = _shading
        self.nfrc_u_factor = _nfrc_u_factor
        self.nfrc_shgc = _nfrc_shgc
        self.t_vis = _t_vis

    def make_hb_window_construction(self, _window_mat, _hbph_frame, _hbph_glazing):
        # type: (EnergyWindowMaterialSimpleGlazSys, window.PhWindowFrame, window.PhWindowGlazing) -> Union[WindowConstruction, WindowConstructionShade]
        """Return the new HB Window Construction"""

        hb_win_construction = WindowConstruction(self.display_name, [_window_mat])

        # -------------------------------------------------------------------------------------
        # -- Set the PH Properties on the WindowConstructionProperties
        hb_win_construction.properties.ph.ph_frame = _hbph_frame  # type: ignore
        hb_win_construction.properties.ph.ph_glazing = _hbph_glazing  # type: ignore

        # -------------------------------------------------------------------------------------
        # -- If it is a 'shade', return a WindowConstructionShade which has the normal window
        # -- construction as one of its attributes,Otherwise, just return the normal WindowConstruction
        if self.hb_shade_material:
            return WindowConstructionShade(self.display_name, hb_win_construction, self.hb_shade_material)
        else:
            return hb_win_construction

    def run(self):
        # type: () -> Optional[Union[WindowConstruction, WindowConstructionShade]]
        """Return a new HB-Window-Construction with values set by the PH Elements."""

        # ---------------------------------------------------------------------
        if not self.frame or not self.glazing:
            msg = "Supply a PH-Style Frame and Glazing to build a new Construction."
            self.IGH.warning(msg)
            return None

        # ---------------------------------------------------------------------
        # -- Create a new HB Simple Window Material and set the NFRC/HBmaterial properties
        nfrc_u_factor = self.nfrc_u_factor or iso_10077_1.calculate_window_uw(self.frame, self.glazing)
        nfrc_shgc = self.nfrc_shgc or self.glazing.g_value
        t_vis = self.t_vis
        window_mat = EnergyWindowMaterialSimpleGlazSys(self.display_name, nfrc_u_factor, nfrc_shgc, t_vis)
        window_mat.display_name = self.display_name

        # -------------------------------------------------------------------------------------
        # -- Create and return a new HB Window Construction
        # -- NOTE: do *NOT* set properties on the construction here. They will be set
        # -- by the function at the right level since Shade and Window have different
        # -- properties locations. Grrrrrr.....
        return self.make_hb_window_construction(window_mat, self.frame, self.glazing)

    def __str__(self):
        return "{}(display_name={})".format(self.__class__.__name__, self.display_name)

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)
