# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Detailed Constructions."""

try:
    from typing import List, Optional, Dict, Any
except ImportError:
    pass # IronPython 2.7

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
        self.materials = _materials
    
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
    
    def create_materials(self, _const_data):
        # type: (Dict[str, Any]) -> List[EnergyMaterial]
        
        # -- Turn the materials into a dict
        materials = {m.display_name:m for m in self.materials}
        
        materials_ = []
        for i, mat_name in enumerate(_const_data["materials"]):
            
            base_mat = materials[mat_name]
            
            # -- If thicknesses are provided, try and set the thickness
            try:
                value, unit = parse_input(_const_data["thicknesses"][i])
                thickness = convert(value, unit, "M")
            except:
                thickness = base_mat.thickness
            
            # -- build the new material
            new_mat = base_mat.duplicate()
            new_mat.identifier = "{}_{:.3f}m".format(base_mat.display_name, thickness)
            new_mat.thickness = thickness
            new_mat.lock()
            
            materials_.append(new_mat)
            
        return  materials_

    def run(self):
        # type: () -> List[OpaqueConstruction]
        if not self.path or not self.materials:
            return []

        # Load the file
        with open(self.path) as json_file:
            input_data = json.load(json_file)

        constructions_ = []
        for const_data in input_data.values():
            new_const = OpaqueConstruction(
                identifier=clean_ep_string(const_data["identifier"]),
                materials = self.create_materials(const_data)
            )
            constructions_.append(new_const)
        
        return constructions_