# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Sort Geom by Level."""

try:
    from typing import Dict, List, Tuple, Any
except ImportError:
    pass # IronPython 2.7

from collections import defaultdict

try:
    from Grasshopper.Kernel.Data import GH_Path # type: ignore
    from Grasshopper import DataTree # type: ignore
    from System import Object # type: ignore
    import Rhino # type: ignore
    from Rhino.Geometry import GeometryBase # type: ignore
except:
    pass # Outside Rhino

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))
        
class GHCompo_SortGeomObjectsByLevel(object):
    """Utility for sorting any Rhino Geometry objects by their Z-location (height)."""

    def __init__(self, _IGH, _geom, _tolerance):
        # type: (gh_io.IGH, List[Rhino.Geometry.GeometryBase], float) -> None
        self.IGH = _IGH
        self.geom = _geom
        self.items_by_level = defaultdict(list) # type: defaultdict[str, List[GeometryBase]]
        self.tolerance = _tolerance or 0.001

    def get_z_height(self, _geom):
        # type: (Rhino.Geometry.GeometryBase) -> float
        """Return the Z-dimension value for the bottom / lowest element of the geometry."""
        return min((_.Z for _ in self.IGH.ghc.BoxCorners(_geom)))

    def get_dict_key(self, _geom):
        # type: (GeometryBase) -> str
        """Return the dict key for sorting the geometry by height. Will try and group
        together the geometry objects taking into account the tolerance value.
        """
        z_height = self.get_z_height(_geom)

        for k in self.items_by_level.keys():
            # -- try to add to an existing key first, if it can.
            if abs(float(k) - z_height) < self.tolerance:
                return k
        else:
            # -- if not, add a new key
            return'{0:.{precision}f}'.format(z_height, precision=4)

    def run(self):
        # type: () -> Tuple[List[float], List[GeometryBase], List[Dict]]
        """Returns a DataTree with the geometry organized into branches by their 'level'"""

        # -- Get all the Geom object info from the RH Scene
        with self.IGH.context_rh_doc():
            for geom in self.geom:
                dict_key = self.get_dict_key(geom)
                self.items_by_level[dict_key].append(geom)
        
        # -- Package up for output
        output = DataTree[Object]()
        for i, k in enumerate(sorted(self.items_by_level.keys(), key=lambda n: float(n))):
            output.AddRange([_ for _ in self.items_by_level[k]], GH_Path(i))

        return output
