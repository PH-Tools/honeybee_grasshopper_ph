# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Airtable Create Material Layers."""

try:
    from typing import List, Any, Dict, Optional
except ImportError:
    pass  # IronPython 2.7

from honeybee.typing import clean_ep_string

try:
    from honeybee_energy.material.opaque import EnergyMaterial
except ImportError:
    raise Exception("Error importing honeybee_energy modules?")

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io.airtable_download_data import TableRecord
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

AT_COLUMN_NAMES = {
    "name": "DISPLAY_NAME",
    "material": "LAYER_MATERIAL",
    "thickness_mm": "LAYER_THICKNESS [MM]",
    "conductivity_w_mk": "CONDUCTIVITY_W_MK",
    "data": "DATA_SHEET",
    "notes": "NOTES",
    "link" : "LINK"
}

class EpMaterialCollection(object):
    def __init__(self):
        self._storage = {}

    def keys(self):
        return self._storage.keys()

    def values(self):
        return self._storage.values()

    def __getitem__(self, key):
        return self._storage[key]

    def __setitem__(self, key, value):
        self._storage[key] = value

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)

    def __contains__(self, key):
        return key in self._storage

    def __repr__(self):
        return "EpMaterialCollection({})".format(self._storage)

    def __str__(self):
        return "{}({} items)".format(self.__class__.__name__, len(self))

    def ToString(self):
        return str(self)


class GHCompo_AirTableCreateMaterialLayers(object):
    DENSITY = 999.9999  # type: float
    SPEC_HEAT = 999.999  # type: float
    ROUGHNESS = "Rough"  # type: str
    THERM_ABS = 0.9  # type: float
    SOL_ABS = 0.7  # type: float
    VIS_ABS = 0.7  # type: float

    def __init__(self, IGH, _material_records, _layer_records, *args, **kwargs):
        # type: (gh_io.IGH, List[TableRecord], List[TableRecord], *Any, **Any) -> None
        self.IGH = IGH
        self.materials = self.create_material_dict(_material_records)
        self.layer_records = _layer_records
        self.material_layers_collection = EpMaterialCollection()

    def clean_name(self, _in):
        # type: (str) -> str
        """Clean the name of the material. Strip whitespace, remove commas."""
        return str(_in).strip().replace(",", "")

    def create_material_dict(self, _material_records):
        # type: (List[TableRecord]) -> Dict
        """Create a dictionary of materials from the AirTable Data."""
        return {record.ID: record.FIELDS for record in _material_records}

    def create_ep_material(self, _record):
        # type: (TableRecord) -> Optional[EnergyMaterial]
        """Create the EnergyPlus Material Layers from the AirTable Data."""

        # -- Pull out the Layer Data
        layer_data = _record.FIELDS
        layer_mat_id_list = layer_data.get(AT_COLUMN_NAMES['material'], None)
        if not layer_mat_id_list:
            msg = "Layer Material not found for layer: {}".format(
                layer_data[AT_COLUMN_NAMES['name']]
            )
            self.IGH.warning(msg)
            return None
        layer_thickness_mm = float(layer_data.get(AT_COLUMN_NAMES['thickness_mm'], 1.0))
        layer_thickness_m = layer_thickness_mm / 1000.00
        layer_name = layer_data.get(AT_COLUMN_NAMES['name'], "__unnamed__")

        # -- Get the Layer Material Data
        layer_mat_id = layer_mat_id_list[0]
        layer_mat = self.materials[layer_mat_id]

        # -- Build the HB-Material
        hb_mat = EnergyMaterial(
            clean_ep_string(self.clean_name(layer_name)),
            layer_thickness_m,
            float(layer_mat[AT_COLUMN_NAMES["conductivity_w_mk"]]),
            self.DENSITY,
            self.SPEC_HEAT,
            self.ROUGHNESS,
            self.THERM_ABS,
            self.SOL_ABS,
            self.VIS_ABS,
        )
        return hb_mat

    @property
    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        if not self.layer_records:
            return False
        if not self.materials:
            return False
        return True

    def run(self):
        # type: () -> EpMaterialCollection
        """Run the component."""
        if not self.ready:
            return self.material_layers_collection

        for record in self.layer_records:
            mat = self.create_ep_material(record)
            if not mat:
                continue
            self.material_layers_collection[record.ID] = mat

        return self.material_layers_collection
