# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Sort HB Objects by Level."""

try:
    from typing import Dict, List, Tuple, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from itertools import izip  # type: ignore
except ImportError:
    izip = zip  # Python 3

from collections import defaultdict

try:
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from Grasshopper import DataTree  # type: ignore
    from System import Object  # type: ignore
    import Rhino  # type: ignore
    from Rhino.Geometry import GeometryBase  # type: ignore
except:
    pass  # Outside Rhino

try:
    from honeybee.aperture import Aperture
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_SortHbObjectsByLevel(object):
    """Utility for sorting HB-hb_objects objects by their Z-location (height)."""

    def __init__(self, _IGH, _hb_objects, _tolerance):
        # type: (gh_io.IGH, List[Aperture], float) -> None
        self.IGH = _IGH
        self.hb_objects = _hb_objects
        self.hb_objects_by_level = defaultdict(
            list
        )  # type: defaultdict[str, List[Aperture]]
        self.tolerance = _tolerance or 0.001

    def get_obj_min_z(self, _hb_object):
        # type: (Union[Room, Aperture]) -> float
        try:
            return _hb_object.min.z
        except:
            raise ValueError(
                "Unsupported Honeybee Object type. Got: {}?".format(
                    type(_hb_object).__name__
                )
            )

    def get_dict_key(self, _hb_object):
        # type: (Union[Room, Aperture]) -> str
        """Return the dict key for sorting the HB-Aperture by height. Will try and group
        together the geometry objects taking into account the tolerance value.
        """
        z_height = self.get_obj_min_z(_hb_object)

        # -- Try to add to an existing key
        for k in self.hb_objects_by_level.keys():
            if abs(float(k) - z_height) < self.tolerance:
                return k
        else:
            # -- if not, add a new key
            return "{0:.{precision}f}".format(z_height, precision=4)

    def run(self):
        # type: () -> Tuple[List[float], List[GeometryBase], List[Dict]]
        """Returns a DataTree with the HB-Objects organized into branches by their 'level'"""

        # -- Get all the Geom object info from the RH Scene
        for hb_object in self.hb_objects:
            dict_key = self.get_dict_key(hb_object)
            self.hb_objects_by_level[dict_key].append(hb_object.duplicate())

        # -- Package up for output
        hb_hb_objects_ = DataTree[Object]()
        for i, k in enumerate(
            sorted(self.hb_objects_by_level.keys(), key=lambda n: float(n))
        ):
            hb_hb_objects_.AddRange([_ for _ in self.hb_objects_by_level[k]], GH_Path(i))

        return hb_hb_objects_
