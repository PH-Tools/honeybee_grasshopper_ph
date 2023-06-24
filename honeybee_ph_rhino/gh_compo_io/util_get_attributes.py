# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Get Object Attributes."""

try:
    from typing import List
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


class GHCompo_GetObjectAttributes(object):
    def __init__(self, _IGH, _objects, _keys):
        # type: (gh_io.IGH, List[object], List[str]) -> None
        self.IGH = _IGH
        self.objects = _objects
        self.keys = [self.clean_key(k) for k in _keys]

    def clean_key(self, _key):
        # type: (str) -> str
        """Returns the input key, cleaned and upper-cased."""
        return str(_key).strip().upper()

    def run(self):
        # type: () -> DataTree
        """Return a DataTree with the values gotten from the objects."""

        values_ = DataTree[Object]()

        for object in self.objects:
            for i, key in enumerate(self.keys):
                _ = getattr(object, key)
                if isinstance(_, list):
                    values_.AddRange(_, GH_Path(i))
                else:
                    values_.Add(_, GH_Path(i))

        return values_
