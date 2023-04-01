# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Get From Custom Collection."""

try:
    from typing import Dict, List
except ImportError:
    pass #IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

from honeybee_ph_rhino.gh_compo_io.util_create_collection import CustomCollection

class GHCompo_GetFromCustomCollection(object):

    def __init__(self, _IGH, _collection, _keys, *args, **kwargs):
        # type: (gh_io.IGH, CustomCollection, List[str], List, Dict) -> None
        self.IGH = _IGH
        self.collection = _collection
        self.keys = _keys

    def run(self):
        # type: () -> List
        if not self.collection or not self.keys:
            return []

        return [self.collection.get(key, None) for key in self.keys]