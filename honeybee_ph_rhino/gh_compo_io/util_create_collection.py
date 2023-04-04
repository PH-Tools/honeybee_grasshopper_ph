# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Custom Collection."""

try:
    from typing import Collection, TypeVar, ValuesView, KeysView, ItemsView, Dict, List, Optional
    T = TypeVar("T")
except ImportError:
    pass #IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


class CustomCollection(object):

    """A custom 'Collection' class which works like a Python Dictionary."""

    def __init__(self, _display_name="", *args, **kwargs):
        # type: (str, List, Dict) -> None
        self.display_name = _display_name or ""
        self._storage = {}

    def keys(self):
        # type: () -> KeysView[str]
        return self._storage.keys()
    
    def items(self):
        # type: () -> ItemsView[str, T]
        return self._storage.items()
    
    def values(self):
        # type: () -> ValuesView[T]
        return self._storage.values()
    
    def __setitem__(self, k, v):
        # type: (str, T) -> None
        self._storage[k] = v

    def __getitem__(self, k):
        # type: (str) -> T
        return self._storage[k]
    
    def get(self, k, default):
        # type: (str, T) -> Optional[T]
        return self._storage.get(k, default)

    def __str__(self):
        # type: () -> str
        return '{} {} ({} items)\n{}'.format(
            self.__class__.__name__,
            self.display_name,
            len(self._storage),
            "\n".join([
                    "\t - Key: {} = {}...".format(k, str(v)[:25].replace("\n", "")) 
                    for k, v in self.items()
                    ]
                )
            )
    
    def __repr__(self):
        return str(self)
    
    def ToString(self):
        return str(self)

class GHCompo_CreateCustomCollection(object):

    def __init__(self, _IGH, _name, _key_name, _items, *args, **kwargs):
        # type: (gh_io.IGH, str, str, Collection, List, Dict) -> None
        self.IGH = _IGH
        self.name = _name
        self.key_name = _key_name
        self.items = _items

    def key(self, _item):
        # type: (T) -> str
        """Return the Key to use when storing the value. Returns id(item) by default."""
        if self.key_name and "," in self.key_name:
            values = [str(getattr(_item, str(_).strip())) for _ in self.key_name.split(",")]
            return "_".join(values)
        elif self.key_name:
            return str(getattr(_item, self.key_name))
        else:
            return str(id(_item))

    def run(self):
        # type: () -> CustomCollection
        collection_ = CustomCollection(self.name)
        
        for item in self.items:
            collection_[self.key(item)] = item

        return collection_