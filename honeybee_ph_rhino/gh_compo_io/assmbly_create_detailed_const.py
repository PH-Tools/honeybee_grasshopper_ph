# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Detailed Constructions."""

try:
    from typing import List, Optional, Dict, Any
except ImportError:
    pass  # IronPython 2.7

import os
import json

from honeybee_energy.material.opaque import EnergyMaterial
from honeybee_energy.construction.opaque import OpaqueConstruction
from honeybee.typing import clean_ep_string

from ph_units.parser import parse_input
from ph_units.converter import convert

from honeybee_ph_rhino import gh_io


class GHCompo_CreateDetailedConstructions(object):
    def __init__(self, _IGH, _path, _materials):
        # type: (gh_io.IGH, str, List[EnergyMaterial]) -> None
        self.IGH = _IGH
        self._path = str(_path)

        # -- Turn the materials into a dict
        self.materials = {
            m.display_name: m for m in _materials
        }  # type: Dict[str, EnergyMaterial]

    @property
    def path(self):
        # type: () -> Optional[str]
        if not os.path.exists(self._path):
            return None

        file_extension = str(os.path.splitext(self._path)[1]).upper()
        if not file_extension == ".JSON":
            msg = "Error: please input only .JSON files."
            self.IGH.warning(msg)
            return None

        return self._path

    def _clean_name(self, _in):
        # type: (str) -> str
        """Clean the name of the material. Strip whitespace, remove commas."""
        return str(_in).strip().replace(",", "")

    def create_materials(self, _const_data):
        # type: (Dict[str, Any]) -> List[EnergyMaterial]
        """Create materials from the input data by adding the thickness to each material."""

        materials_w_thickness_added_ = []
        for i, mat_name in enumerate(_const_data["materials"]):
            base_mat = self.materials[self._clean_name(mat_name)]

            # -- If thicknesses are provided, try and get the thickness
            try:
                value, unit = parse_input(_const_data["thicknesses"][i])
                thickness = convert(value, unit, "M")
            except:
                thickness = base_mat.thickness

            # -- Build the new material with the new thickness
            new_mat = base_mat.duplicate()  # type: EnergyMaterial # type: ignore
            new_mat.identifier = "{}_{:.3f}m".format(base_mat.display_name, thickness)
            new_mat.thickness = thickness
            new_mat.lock()  # type: ignore

            materials_w_thickness_added_.append(new_mat)

        return materials_w_thickness_added_

    def run(self):
        # type: () -> List[OpaqueConstruction]
        """Return a list of constructions with the materials with thicknesses set."""

        if not self.path or not self.materials:
            return []

        # -- Load the input file
        try:
            with open(self.path) as json_file:
                input_data = json.load(json_file)
        except:
            msg = "Failed to load the JSON file at {}.".format(self.path)
            self.IGH.warning(msg)
            return []

        # -- Build the constructions with the materials (with thickness added)
        constructions_ = [
            OpaqueConstruction(
                identifier=clean_ep_string(const_data["identifier"]),
                materials=self.create_materials(const_data),
            )
            for const_data in input_data.values()
        ]

        return constructions_
