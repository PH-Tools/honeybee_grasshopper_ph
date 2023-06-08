# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Import Flixo Materials."""

try:
    from typing import Optional, List, Any
except ImportError:
    pass # IronPython 2.7

try:
    from itertools import izip
except ImportError:
    izip = zip
from io import open
import os

from honeybee.typing import clean_ep_string
from honeybee_energy.material.opaque import EnergyMaterial
from honeybee_ph_rhino import gh_io

class FlixoDataItem(object):
    """
    Represents a data item in Flixo, a software for thermal analysis of building components.
    """

    def __init__(self, *args, **kwargs):
        # type: (*Any, **Any) -> None
        """
        Initializes the object with any number of keyword arguments.

        :param kwargs: The keyword arguments to set as attributes of the object.
        """
        for k, v in kwargs.items():
            setattr(self, str(k), str(v))

    @property
    def display_name(self):
        # type: () -> str
        """
        Gets the display name of the data item.

        :return: The display name of the data item as a string.
        """
        return getattr(self, "Name", "")

    @property
    def conductivity(self):
        # type: () -> Optional[float]
        """
        Gets the thermal conductivity of the data item.

        :return: The thermal conductivity of the data item as a float, or None if it cannot be converted to a float.
        """
        try:
            return float(getattr(self, "LambdaHor"))
        except:
            return None

    def __str__(self):
        # type: () -> str
        """
        Returns a string representation of the object.

        :return: A string representation of the object.
        """
        return "{}(display_name={})".format(self.__class__.__name__, self.display_name)

    def __repr__(self):
        # type: () -> str
        """
        Returns a string representation of the object.

        :return: A string representation of the object.
        """
        return str(self)

    def ToString(self):
        # type: () -> str
        """
        Returns a string representation of the object.

        :return: A string representation of the object.
        """
        return str(self)

class GHCompo_ImportFlixoMaterials(object):
    """
    A class for importing materials from Flixo, a software for thermal analysis of building components, into Honeybee.
    """

    THICKNESS = 1.0  # type: float
    DENSITY = 999.9999  # type: float
    SPEC_HEAT = 999.999  # type: float
    ROUGHNESS = "Rough"  # type: str
    THERM_ABS = 0.9  # type: float
    SOL_ABS = 0.7  # type: float
    VIS_ABS = 0.7  # type: float

    def __init__(self, _IGH, _path):
        # type: (gh_io.IGH, str) -> None
        """
        Initializes the object with an instance of the Grasshopper IGH interface and a path to the Flixo material file.

        :param _IGH: An instance of the Grasshopper IGH interface.
        :param _path: A path to the Flixo material file as a string.
        """
        self.IGH = _IGH
        self._path = str(_path)

    @property
    def path(self):
        # type: () -> Optional[str]
        """
        Gets the path to the Flixo material file.

        :return: The path to the Flixo material file as a string, or None if the file does not exist or is not a CSV file.
        """
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
        """
        Builds a list of headers from a semicolon-separated string of headers.

        :param _headers: A semicolon-separated string of headers as a string.
        :return: A list of headers as a list of strings.
        """
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
        """
        Builds a list of Flixo data items from a list of semicolon-separated strings of data.

        :param _data: A list of semicolon-separated strings of data as a list of strings.
        :return: A list of Flixo data items as a list of FlixoDataItem objects.
        """
        flixo_data_items = []
        headers = self.build_headers(_data[1])
        for item in _data[2:]:
            flixo_data_items.append(
                FlixoDataItem(
                    **{k: v for k, v in izip(headers, item.split(";")[1:])}
                )
            )
        return flixo_data_items

    def build_hb_materials(self, _flixo_data_items):
        # type: (List[FlixoDataItem]) -> List[EnergyMaterial]
        """
        Builds a list of Honeybee energy materials from a list of Flixo data items.

        :param _flixo_data_items: A list of Flixo data items as a list of FlixoDataItem objects.
        :return: A list of Honeybee energy materials as a list of EnergyMaterial objects.
        """
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
        """
        Runs the import process and returns a list of Honeybee energy materials.

        :return: A list of Honeybee energy materials as a list of EnergyMaterial objects.
        """
        if not self.path:
            return []

        # -- Get the file data
        with open(self.path) as f:
            data = f.readlines()

        flixo_data_items = self.build_flixo_data_from_inputs(data)
        return self.build_hb_materials(flixo_data_items)