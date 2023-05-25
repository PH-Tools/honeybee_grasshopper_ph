# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Rhino Geometry."""

try:
    from itertools import izip  # type: ignore
except ImportError:
    # Python 3
    izip = zip

try:
    from typing import List, Tuple, Dict
except ImportError:
    pass  # Python 3

try:
    from Rhino.Geometry import LineCurve, Brep  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io.win_create_types import WindowUnitType
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreateWindowRhinoGeometry(object):
    def __init__(self, _IGH, _win_baselines, _win_names, _win_collection):
        # type: (gh_io.IGH, List[LineCurve], List[str], Dict[str, WindowUnitType]) -> None
        self.IGH = _IGH
        self.win_collection = _win_collection
        self.win_baselines = _win_baselines
        self.win_names = _win_names

    def check_input(self):
        if not self.win_baselines or not self.win_names:
            return

        if len(self.win_baselines) != len(self.win_names):
            msg = "The number of window-baselines and window-names must be the same."
            raise Exception(msg)

    def check_result(self, _win_type, _srfcs, _names):
        if len(_srfcs) != len(_names):
            msg = "Failed to create window geometry for window type: {}".format(_win_type)
            raise Exception(msg)

    def run(self):
        # type: () -> Tuple[List[Brep], List[str]]
        """Return a list of window surfaces and their names."""
        self.check_input()

        win_surfaces_, srfc_names_ = [], []
        for baseline, name in izip(self.win_baselines, self.win_names):
            win_type = self.win_collection[name]
            srfcs, names = win_type.build(baseline)
            self.check_result(win_type, srfcs, names)

            win_surfaces_ += srfcs
            srfc_names_ += names

        return win_surfaces_, srfc_names_
