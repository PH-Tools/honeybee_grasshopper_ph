# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Objects From CSV."""

try:
    from itertools import izip_longest # type: ignore
except ImportError:
    pass # Python 3.x

import os

try:
    from typing import Dict, List, Optional
except ImportError:
    pass #IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


class CustomObject(object):
    """A simple wrapper Object for input CSV data"""
    # Optional types for casting input values
    datatypes = {}

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            key = self.clean_key(k)

            try:
                # -- Try and cast the value based on the user's type info
                data_type = self.datatypes[key]
            except KeyError:
                data_type = "str"
            
            value = eval("{}({!r})".format(data_type, str(v).strip()))
            setattr(self, key, value)

    def clean_key(self, _key):
        # type: (str) -> str
        return self.strip_characters(str(_key).upper().strip())

    def strip_characters(self, _key):
        """Remove non-unicode characters."""
        return _key.replace("\xcf", "").replace("\xbb", "").replace("\xbf", "")

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, vars(self))
    
    def __repr__(self):
        return str(self)
    
    def ToString(self):
        return str(self)

class GHCompo_CreateObjectsFromCSV(object):

    def __init__(self, _IGH, _path, _class_name, _datatypes, *args, **kwargs):
        # type: (gh_io.IGH, str, str, List[str], List, Dict) -> None
        self.IGH = _IGH
        self.path = _path
        self.class_name = _class_name
        self.datatypes = self.create_datatype_dict(_datatypes)

    @property
    def class_name(self):
        # type: () -> Optional[str]
        return self._class_name

    @class_name.setter
    def class_name(self, _input):
        # type: (Optional[str]) -> None
        if _input:
            self._class_name = str(_input).strip().replace(" ", "_")
        else:
            self._class_name = None

    def create_datatype_dict(self, _datatypes):
        # type: (List[str]) -> Dict
        d = {}

        for _ in _datatypes:
            if ":" not in _:
                continue
            line = str(_).split(":")
            d[line[0].upper().strip()] = line[1].strip()

        return d

    def create_custom_object_type(self, _datatypes):
        # type: (Dict) -> type
        # Create a new class dynamically with the user supplied name
        class_name = self.class_name or "CustomObject"
        new_type =  type(class_name, (CustomObject, ), {
                # data members
                "datatypes": _datatypes,
            })
        return new_type

    def get_file_data(self):
        # type: () -> List[str]
        with open(self.path, "r") as csv_file:
            return list(csv_file.readlines())

    def build_objects_from_data(self, _data):
        # type: (List[str]) -> List[CustomObject]
        
        NewObjectType = self.create_custom_object_type(self.datatypes)

        headers = [_ for _ in _data[0].split(",")]
        new_objects_ = [
            NewObjectType(
                **{h:d for h, d in izip_longest(headers, line.split(","))}
            ) for line in _data[1:]
        ]

        return new_objects_

    def run(self):
        # type: () -> List[CustomObject]

        if not self.path:
            return []

        if not os.path.exists(self.path):
            msg = "I cannot find the file '{}'? Please supply the full path.".format(self.path)
            self.IGH.warning(msg)
            return []

        data = self.get_file_data()
        new_objects_ = self.build_objects_from_data(data)    
    
        return new_objects_