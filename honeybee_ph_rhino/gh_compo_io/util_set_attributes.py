# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Object Attributes."""

from copy import copy

try:
    from itertools import izip  # type: ignore
except ImportError:
    izip = zip  # Python3

try:
    from typing import List, Any
except ImportError:
    pass  # IronPython 2.7

try:
    from System import Object  # type: ignore
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
except:
    pass  # Outside Rhino

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


def copy_and_set(obj, _key, _value):
    # type: (Any, str, Any) -> Any
    """Return a copy of the input object, with the attribute set."""
    new_obj = copy(obj)
    setattr(new_obj, _key, _value)
    return new_obj


class GHCompo_SetObjectAttributes(object):
    def __init__(self, _IGH, _objects, _keys, _values):
        # type: (gh_io.IGH, List[object], List[str], List[Any]) -> None
        self.IGH = _IGH
        self.objects = _objects
        self._keys = [self.clean_key(k) for k in _keys]
        self.values = _values

    def clean_key(self, _key):
        # type: (str) -> str
        """Returns the input key, cleaned and upper-cased."""
        return str(_key).strip().upper()

    @property
    def keys(self):
        # type: () -> List[str]
        """Returns a list of keys with a length that matches the input values."""
        keys_ = []
        for i in range(len(self.values)):
            try:
                keys_.append(self._keys[i])
            except IndexError:
                try:
                    keys_.append(self._keys[0])
                except IndexError:
                    return []
        return keys_

    def run(self):
        # type: () -> List[Any]
        """Set the Object attributes with the keys and values supplied."""

        return [
            copy_and_set(obj, k, v)
            for obj, k, v in izip(self.objects, self.keys, self.values)
        ]
