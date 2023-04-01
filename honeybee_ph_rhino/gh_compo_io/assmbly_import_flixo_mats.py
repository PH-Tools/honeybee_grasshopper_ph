# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Import Flixo Materials."""

try:
    from typing import Optional, List
except ImportError:
    pass # IronPython 2.7

from itertools import izip
import os
from io import open as io_open

from honeybee.typing import clean_ep_string
from honeybee_energy.material.opaque import EnergyMaterial
from honeybee_ph_rhino import gh_io

class FlixoDataItem(object):
    
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, str(k), str(v))
    
    @property
    def display_name(self):
        # type: () -> str
        return getattr(self, "Name", "")
        
    @property
    def conductivity(self):
        # type: () -> Optional[float]
        try:
            return float(getattr(self, "LambdaHor"))
        except:
            return None

    def __str__(self):
        # type: () -> str
        return "{}(display_name={})".format(self.__class__.__name__, self.display_name)

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)


class GHCompo_ImportFlixoMaterials(object):
    THICKNESS = 1.0 #m
    DENSITY = 999.9999
    SPEC_HEAT = 999.999
    ROUGHNESS = "Rough"
    THERM_ABS = 0.9
    SOL_ABS = 0.7
    VIS_ABS = 0.7

    def __init__(self, _IGH, _path):
        # type: (gh_io.IGH, str) -> None
        self.IGH = _IGH
        self._path = str(_path)

    @property
    def path(self):
        # type: () -> Optional[str]
        if not os.path.exists(self._path):
            return None
        
        file_extension = str(os.path.splitext(self._path)[1]).upper()
        if not file_extension == ".CSV":
            msg = "Error: please input only .CSV files."
            self.IGH.warning(msg)
            return None
        
        return self._path
    
    def build_headers(self, _headers):
        # type: (str) -> List[str]
        headers_list = _headers.split(";")

        headers_ = []
        for header_name in headers_list:
            
            counter = len([header_name for h in headers_ if "{}_".format(header_name) in h or header_name in h])
            if counter != 0:
                header_name = "{}_{}".format(header_name, counter)
            headers_.append(header_name)
            
        return headers_
    
    def build_flixo_data_from_inputs(self, _data):
        # type: (List[str]) -> List[FlixoDataItem]
        flixo_data_items = []
        headers = self.build_headers(_data[1])
        for item in _data[2:]:
            flixo_data_items.append(
                FlixoDataItem(
                        **{k:v for k, v in izip(headers, item.split(";")[1:])}
                    )
                )
        return flixo_data_items
    
    def build_hb_materials(self, _flixo_data_items):
        # type: (List[FlixoDataItem]) -> List[EnergyMaterial]
        materials_ = []
        for fl in sorted(_flixo_data_items, key=lambda f: f.display_name):
            if not fl.display_name:
                continue
            
            hb_mat = EnergyMaterial(
                clean_ep_string(fl.display_name), self.THICKNESS, fl.conductivity, self.DENSITY, 
                self.SPEC_HEAT, self.ROUGHNESS, self.THERM_ABS, self.SOL_ABS, self.VIS_ABS)
            materials_.append(hb_mat)
        return materials_

    def run(self):
        # type: () -> List[EnergyMaterial]
        if not self.path:
            return []

        # -- Get the file data
        with io_open(self.path) as f:
            data = f.readlines()
        
        flixo_data_items = self.build_flixo_data_from_inputs(data)
        return self.build_hb_materials(flixo_data_items)
