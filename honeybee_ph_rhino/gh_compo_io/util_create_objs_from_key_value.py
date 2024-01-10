# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Objects from Key-Values."""

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


class GHCompo_CreateObjectsFromKeyValues(object):
    def __init__(self, _IGH, _type_name, _keys, _values):
        # type: (gh_io.IGH, str, List[str], DataTree[List[Any]],) -> None
        self.IGH = _IGH
        self.type_name = _type_name
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
        if self.values.BranchCount != len(self._keys):
            msg = "The Number of Keys does not match the number of Values?"
            self.IGH.warning(msg)
        
        keys_ = []
        for i in range(self.values.BranchCount):
            try:
                keys_.append(self._keys[i])
            except IndexError:
                try:
                    keys_.append(self._keys[0])
                except IndexError:
                    return []
        return keys_

    @property
    def _new_type_(self):
        # type: () -> Object
        """Returns a new type with the 'self.keys' as attributes."""
        class NewType(object):
            def __init__(self, _type_name, _keys):
                if _type_name:
                    self.__class__.__name__ = _type_name
                
                for k in _keys:
                    setattr(self, k, None)

            def repr(self):
                return "{}({})".format(self.__class__.__name__, self.__dict__)
                
            def ToString(self):
                return self.repr()
            
        return NewType

    @property
    def ready(self):
        # type: () -> bool
        """Returns True if the input keys and values are ready to be processed."""
        if len(self.keys) > 0 and self.values.BranchCount > 0:
            return True
        return False

    def run(self):
        # type: () -> List[Object]
        """Create the new Objects with the keys and values supplied."""
        # self.keys: List = ['NUMBER', 'NAME', 'V_SUP']
        # self.values: List[List[Any]] = [ [1, 2, 3, ...], ['Test', ...], [100, 200, 300, ...], ... ]


        new_objects = []
        if not self.ready:
            return new_objects

        for i in range(len(self.values.Branch(0))):
            new_obj = self._new_type_(self.type_name, self.keys)
            
            for k, branch in zip(self.keys, self.values.Branches):
                setattr(new_obj, k, branch[i])

            new_objects.append(new_obj)
        return new_objects