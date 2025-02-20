# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Space PH Ventilation."""

try:
    from typing import Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper import DataTree  # type: ignore
except ImportError:
    pass  # outside Grasshopper

try:
    from itertools import izip_longest  # type: ignore
except:
    # Python 3+
    from itertools import zip_longest as izip_longest

try:
    from honeybee_ph_utils import input_tools
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_utils: {}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino: {}".format(e))


class SpacePhVentFlowRates(object):
    """Temporary dataclass to store flow-rate info"""

    v_sup = ghio_validators.UnitM3_S("v_sup")
    v_eta = ghio_validators.UnitM3_S("v_eta")
    v_tran = ghio_validators.UnitM3_S("v_tran")

    def __init__(self, _v_sup, _v_eta, _v_tran):
        # type: (Optional[float], Optional[float], Optional[float]) -> None
        self.v_sup = _v_sup or 0.0
        self.v_eta = _v_eta or 0.0
        self.v_tran = _v_tran or 0.0

    def __add__(self, other):
        # type: (SpacePhVentFlowRates, SpacePhVentFlowRates) -> SpacePhVentFlowRates
        obj = SpacePhVentFlowRates(0.0, 0.0, 0.0)
        obj.v_sup = self.v_sup + other.v_sup
        obj.v_eta = self.v_eta + other.v_eta
        obj.v_tran = self.v_tran + other.v_tran
        return obj

    def __radd__(self, other):
        # type: (SpacePhVentFlowRates, SpacePhVentFlowRates) -> SpacePhVentFlowRates
        if isinstance(other, int):
            return self
        else:
            return self + other

    def __str__(self):
        try:
            return "{}(v_sup={:.4f} m3/s, v_eta={:.4f} m3/s, v_tran={:.4f} m3/s)".format(
                self.__class__.__name__, self.v_sup, self.v_eta, self.v_tran
            )
        except Exception as e:
            return "{}(v_sup={} m3/s, v_eta={} m3/s, v_tran={} m3/s)".format(
                self.__class__.__name__, self.v_sup, self.v_eta, self.v_tran
            )

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)


class GHCompo_CreateSpaceVent(object):
    """Grasshopper Component Interface for"""

    def __init__(self, _IGH, _v_sups, _v_etas, _v_trans):
        # type: (gh_io.IGH, DataTree, DataTree, DataTree) -> None
        self.IGH = _IGH
        self.v_sup_tree = _v_sups
        self.v_eta_tree = _v_etas
        self.v_tran_tree = _v_trans

    def run(self):
        # type: () -> DataTree
        output = self.IGH.Grasshopper.DataTree[SpacePhVentFlowRates]()
        pth = self.IGH.Grasshopper.Kernel.Data.GH_Path

        for branch_num, branches in enumerate(
            izip_longest(
                self.v_sup_tree.Branches,
                self.v_eta_tree.Branches,
                self.v_tran_tree.Branches,
            )
        ):
            # -- Any branch might be None, give empty list if so
            s, e, t = branches
            s = s or []
            e = e or []
            t = t or []

            # -- Build the output Branch based on the longest list input
            branch_len = max(len(s), len(e), len(t))
            for i in range(branch_len):
                output.Add(
                    SpacePhVentFlowRates(
                        input_tools.clean_get(s, i, 0.0),
                        input_tools.clean_get(e, i, 0.0),
                        input_tools.clean_get(t, i, 0.0),
                    ),
                    pth(branch_num),
                )

        return output

    def __str__(self):
        return "{}()".format(self.__class__.__name__)

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)
