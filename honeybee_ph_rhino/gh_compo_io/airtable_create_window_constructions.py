# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Airtable Create Window Constructions."""

try:
    from typing import List, Any, Dict
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_energy.material.glazing import EnergyWindowMaterialSimpleGlazSys
    from honeybee_energy.construction.window import WindowConstruction
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction.window import (
        PhWindowGlazing,
        PhWindowFrameElement,
        PhWindowFrame,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_utils import iso_10077_1
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io.airtable_download_data import (
        TableRecord,
        TableFields,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_AirTableCreateWindowConstructions(object):
    """GHCompo Interface: HBPH - Airtable Create Constructions."""

    def __init__(
        self,
        IGH,
        _glazing_records,
        _frame_element_records,
        _window_unit_records,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, List[TableRecord], List[TableRecord], List[TableRecord], *Any, **Any) -> None
        self.IGH = IGH
        self.glazing_records = _glazing_records
        self.frame_element_records = _frame_element_records
        self.window_unit_records = _window_unit_records

        self.hbph_glazings = {}  # type: Dict[str, PhWindowGlazing]
        self.hbph_frame_elements = {}  # type: Dict[str, PhWindowFrameElement]
        self.hbph_window_frames = {}  # type: Dict[str, PhWindowFrame]

    @property
    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        if not self.glazing_records:
            return False
        if not self.frame_element_records:
            return False
        if not self.window_unit_records:
            return False
        return True

    def create_new_hbph_glazing(self, record):
        # type: (TableRecord) -> PhWindowGlazing
        """Create a new Honeybee Window Glazing from a TableRecord."""
        glazing_data = record.FIELDS

        hbph_glazing = PhWindowGlazing(glazing_data.display_name)
        hbph_glazing.display_name = glazing_data.display_name
        hbph_glazing.u_factor = float(glazing_data["U-VALUE [W/M2K]"])
        hbph_glazing.g_value = float(glazing_data["G-VALUE [%]"])

        return hbph_glazing

    def create_new_hbph_frame_elememt(self, record):
        # type: (TableRecord) -> PhWindowFrameElement
        """Create a new Honeybee Window Frame Element from a TableRecord."""
        frame_data = record.FIELDS

        hbph_frame_element = PhWindowFrameElement(frame_data.display_name)
        hbph_frame_element.display_name = frame_data.display_name
        hbph_frame_element.width = float(frame_data["WIDTH [MM]"]) / 1000
        hbph_frame_element.u_factor = float(frame_data["U-VALUE [W/M2K]"])
        hbph_frame_element.psi_glazing = float(frame_data["PSI-GLAZING [W/MK]"])
        hbph_frame_element.psi_install = 0.0
        hbph_frame_element.chi_value = 0.0

        return hbph_frame_element

    def create_new_hbph_window_frame(self, record):
        # type: (TableRecord) -> PhWindowFrame
        """Create a new Honeybee Window Frame from a TableRecord."""
        frame_data = record.FIELDS

        hbph_frame_type = PhWindowFrame(frame_data.display_name)
        hbph_frame_type.display_name = frame_data.display_name
        hbph_frame_type.top = self.hbph_frame_elements[
            frame_data["FRAME ELEMENT NAME: TOP"][0]
        ]
        hbph_frame_type.right = self.hbph_frame_elements[
            frame_data["FRAME ELEMENT NAME: RIGHT"][0]
        ]
        hbph_frame_type.bottom = self.hbph_frame_elements[
            frame_data["FRAME ELEMENT NAME: BOTTOM"][0]
        ]
        hbph_frame_type.left = self.hbph_frame_elements[
            frame_data["FRAME ELEMENT NAME: LEFT"][0]
        ]
        return hbph_frame_type

    def create_new_hbph_window_material(self, _display_name, _hbph_frame, _hbph_glazing):
        # type: (str, PhWindowFrame, PhWindowGlazing) -> EnergyWindowMaterialSimpleGlazSys
        """Create a new HB Simple Window Material and set the NFRC/HBmaterial properties"""
        nfrc_u_factor = iso_10077_1.calculate_window_uw(_hbph_frame, _hbph_glazing)
        nfrc_shgc = _hbph_glazing.g_value
        t_vis = 0.6
        window_mat = EnergyWindowMaterialSimpleGlazSys(
            _display_name, nfrc_u_factor, nfrc_shgc, t_vis
        )
        window_mat.display_name = _display_name
        return window_mat

    def _get_frame_type(self, _key, _window_data):
        # type: (str, TableFields) -> PhWindowFrame
        """Return a HB Window Frame from the collection"""
        return self.hbph_window_frames[_key]

    def _get_glazing_type(self, _window_data):
        # type: (TableFields) -> PhWindowGlazing
        """Return a HB Window Glazing from the collection"""
        glazing_names = _window_data.glazing_name  # type: List[str]
        glazing_name = glazing_names[0]
        return self.hbph_glazings[glazing_name]

    def create_new_hbph_window_construction(self, record):
        # type: (TableRecord) -> WindowConstruction
        """Return the new HB Window Construction"""
        window_data = record.FIELDS
        hbph_display_name = str(window_data.display_name)
        hbph_frame = self._get_frame_type(hbph_display_name, window_data)
        hbph_glazing = self._get_glazing_type(window_data)

        # # -------------------------------------------------------------------------------------
        # -- Build the HB Window Materal and Construction
        hbph_mat = self.create_new_hbph_window_material(
            hbph_display_name, hbph_frame, hbph_glazing
        )
        hb_win_construction = WindowConstruction(hbph_display_name, [hbph_mat])

        # # -- Set the PH Properties on the WindowConstructionProperties
        prop_ph = hb_win_construction.properties.ph  # type: ignore
        prop_ph.ph_frame = hbph_frame
        prop_ph.ph_glazing = hbph_glazing

        return hb_win_construction

    def run(self):
        # type: () -> List[WindowConstruction]
        window_constructions_ = []  # type: List[WindowConstruction]
        if not self.ready:
            return window_constructions_

        # -- Build the Ph-Window Glazing Collection
        for record in self.glazing_records:
            hb_ph_glazing = self.create_new_hbph_glazing(record)
            self.hbph_glazings[hb_ph_glazing.display_name] = hb_ph_glazing

        # -- Build the Ph-Window Frame Element Collection
        for record in self.frame_element_records:
            hbph_frame_element = self.create_new_hbph_frame_elememt(record)
            self.hbph_frame_elements[hbph_frame_element.display_name] = hbph_frame_element

        # -- Build the Ph-Window Frames Collection
        for record in self.window_unit_records:
            hbph_window_frame = self.create_new_hbph_window_frame(record)
            self.hbph_window_frames[hbph_window_frame.display_name] = hbph_window_frame

        # -- Build all the HBPH Window Constructions
        for record in self.window_unit_records:
            window_constructions_.append(self.create_new_hbph_window_construction(record))

        return window_constructions_
