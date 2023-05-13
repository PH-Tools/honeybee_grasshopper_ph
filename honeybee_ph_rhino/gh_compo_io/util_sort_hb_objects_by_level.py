# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Sort HB Objects by Level."""

import re
from collections import defaultdict

try:
    from typing import List, Tuple, Union, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from Grasshopper import DataTree  # type: ignore
    from System import Object  # type: ignore
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


class StepDomain(object):
    """A simple data class representing a domain (range) with a start and ending value."""

    def __init__(self, _start, _end):
        # type: (float, float) -> None
        self.start = _start
        self.end = _end

    @staticmethod
    def _parse_input(_input):
        # type: (str) -> Tuple[float, float]
        match = re.search(
            r"(\d+\.\d+)?\s*To\s*(\d+\.\d+)?", _input.upper(), re.IGNORECASE
        )
        if match:
            _min = float(match.group(1).strip())
            _max = float(match.group(2).strip())
            return (_min, _max)
        else:
            msg = "Failed to step domain input parse: {}".format(_input)
            raise ValueError(msg)

    @classmethod
    def from_string(cls, _input):
        # type: (str) -> StepDomain
        if not _input:
            return cls(0, 0)
        _min, _max = cls._parse_input(_input)
        obj = cls(_min, _max)
        return obj

    def to_string(self):
        # type: () -> str
        return "{:.4f} To {:.4f}".format(self.start, self.end)


class GHCompo_SortHbObjectsByLevel(object):
    """Utility for sorting HB-hb_objects objects by their Z-location (height)."""

    def __init__(self, _IGH, _hb_objects, _tolerance, _groups, _steps):
        # type: (gh_io.IGH, List[Aperture], float, Optional[int], DataTree[str]) -> None
        self.IGH = _IGH
        self.hb_objects = _hb_objects
        self.tolerance = _tolerance or 0.001
        self.groups = _groups

        # -------------------------------------------------------------------------------
        # -- Optional starting configuration for the hb_objects_by_level ----------------
        self.hb_objects_by_level = defaultdict(list)
        if self.groups:
            # -- hb_objects_by_level dict with the number of groups
            # -- If the user supplies a number of specified groups, prime the
            self.z_range = self.max_z - self.min_z
            height_steps = self.z_range / self.groups
            for i in range(self.groups):
                z = self.min_z + i * height_steps
                key = "{0:.{precision}f}".format(z, precision=4)
                self.hb_objects_by_level[key] = []
        elif _steps.BranchCount > 0:
            # -- OR, If the user supplies a list of steps, prime the hb_objects_by_level dict
            for step_domain in (StepDomain.from_string(_[0]) for _ in _steps.Branches):
                self.hb_objects_by_level[str(step_domain.start)] = []
            self.groups = len(self.hb_objects_by_level.keys())

    @property
    def max_z(self):
        # type: () -> float
        """Return the maximum Z-height of all the geometry objects in the group."""
        if not hasattr(self, "_max_z") or not self._max_z:
            self._max_z = self.find_group_max_z()
        return self._max_z

    @max_z.setter
    def max_z(self, _input):
        # type: (float | str) -> None
        self._max_z = float(str(_input).strip())

    @property
    def min_z(self):
        # type: () -> float
        """Return the minimum Z-height of all the geometry objects in the group."""
        if not hasattr(self, "_min_z") or not self._min_z:
            self._min_z = self.find_group_min_z()
        return self._min_z

    @min_z.setter
    def min_z(self, _input):
        # type: (float | str) -> None
        self._min_z = float(str(_input).strip())

    def steps(self, _hb_objects):
        # type: (DataTree[Union[Room, Aperture]]) -> DataTree[str]
        """Return the step domains corresponding to the geometry objects in the group."""
        step_domains_ = DataTree[Object]()

        for t, object_branch in enumerate(_hb_objects.Branches):
            if not object_branch:
                step_domains_.Add("", GH_Path(t))
                continue

            step_domains_.Add(
                StepDomain(
                    min(obj.min.z for obj in object_branch),
                    max(obj.max.z for obj in object_branch),
                ).to_string(),
                GH_Path(t),
            )

        return step_domains_

    def find_group_max_z(self):
        # type: () -> float
        """Find the maximum Z-height of all the geometry objects in the group."""
        if self.hb_objects:
            return max({obj.max.z for obj in self.hb_objects})
        else:
            return 0

    def find_group_min_z(self):
        # type: () -> float
        """Find the minimum Z-height of all the geometry objects in the group."""
        if self.hb_objects:
            return min({obj.min.z for obj in self.hb_objects})
        else:
            return 0

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

    def get_dict_key(self, _z_height):
        # type: (float) -> str
        """Return the dict key for sorting the HB-Object by Z-height. Will try and group
        together the geometry objects taking into account the tolerance value.
        """

        if self.groups:
            # -- If the user has specified a number of groups, return
            # -- the key for the first group that is larger than it's Z-height
            sorted_keys = sorted(
                self.hb_objects_by_level.keys(), key=lambda k: float(k), reverse=True
            )
            for k in sorted_keys:
                if float(_z_height) >= float(k):
                    return k
            else:
                return sorted_keys[-1]
        else:
            # -- Try to add to an existing key
            for k in self.hb_objects_by_level.keys():
                if abs(float(k) - _z_height) < self.tolerance:
                    return k
            else:
                # -- if not, add a new key
                return "{0:.{precision}f}".format(_z_height, precision=4)

    def run(self):
        # type: () -> Tuple[DataTree[Object], DataTree[str]]
        """Returns a DataTree with the HB-Objects organized into branches by their 'level'"""

        # -- Get all the Geom object info from the RH Scene
        for hb_object in self.hb_objects:
            object_z_height = self.get_obj_min_z(hb_object)
            dict_key = self.get_dict_key(object_z_height)
            self.hb_objects_by_level[dict_key].append(hb_object.duplicate())  # type: ignore

        # -- Package up for output
        hb_objects_ = DataTree[Object]()
        for i, k in enumerate(
            sorted(self.hb_objects_by_level.keys(), key=lambda n: float(n))
        ):
            hb_objects_.AddRange([_ for _ in self.hb_objects_by_level[k]], GH_Path(i))
        return hb_objects_, self.steps(hb_objects_)
