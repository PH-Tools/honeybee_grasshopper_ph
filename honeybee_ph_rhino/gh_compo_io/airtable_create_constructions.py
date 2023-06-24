# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Airtable Create Constructions."""

try:
    from typing import List, Any, Dict
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.typing import clean_ep_string
except ImportError:
    raise ImportError("Failed to import honeybee.typing")

try:
    from honeybee_energy.material.opaque import EnergyMaterial
    from honeybee_energy.construction.opaque import OpaqueConstruction
except ImportError:
    raise Exception("Error importing honeybee_energy modules?")

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io.airtable_download_data import TableRecord
    from honeybee_ph_rhino.gh_compo_io.airtable_create_mat_layers import (
        EpMaterialCollection,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_AirTableCreateConstructions(object):
    """GHCompo Interface: HBPH - Airtable Create Constructions."""

    def __init__(self, IGH, _ep_mat_layers, _const_records, *args, **kwargs):
        # type: (gh_io.IGH, EpMaterialCollection, List[TableRecord], *Any, **Any) -> None
        self.IGH = IGH
        self.ep_mat_layers = _ep_mat_layers
        self.const_records = _const_records

    def get_layers(self, record):
        # type: (TableRecord) -> Dict[str, List[str]]
        """Get material layers from a record."""
        layers = {}
        for k, v in record.FIELDS.items():
            if "LAYER" in k.upper():
                layers[k] = v[0]
        return layers

    def create_hb_constructions(self, _name, _materials):
        # type: (str, List[EnergyMaterial]) -> OpaqueConstruction
        """Create a Honeybee construction from the input data."""
        hb_const = OpaqueConstruction(
            identifier=_name,
            materials=_materials,
        )
        hb_const.display_name = _name
        return hb_const

    @property
    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        if not self.ep_mat_layers:
            return False
        if not self.const_records:
            return False
        return True

    def run(self):
        # type: () -> List[OpaqueConstruction]
        """Run the component."""
        if not self.ready:
            return []

        constructions_ = []
        for record in self.const_records:
            const_name = clean_ep_string(record.FIELDS["DISPLAY_NAME"])
            layers = self.get_layers(record)

            mats = []
            for layer_name in sorted(layers):
                mats.append(self.ep_mat_layers[layers[layer_name]])

            const = self.create_hb_constructions(const_name, mats)
            constructions_.append(const)

        return constructions_
