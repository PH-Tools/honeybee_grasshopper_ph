# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Window Types."""

from collections import defaultdict, OrderedDict

try:
    from itertools import izip  # type: ignore
except ImportError:
    # Python 3
    izip = zip

try:
    from typing import List, Tuple, Dict, Any
except ImportError:
    pass  # IronPython 2.7

try:
    from Rhino.Geometry import LineCurve, Plane, Vector3d, Brep  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class WindowElement(object):
    """A Dataclass for a single Window 'Element' (sash) which can be added to a WindowType."""

    width = ghio_validators.UnitM("width")
    height = ghio_validators.UnitM("height")

    def __init__(self, _width, _height, _col, _row):
        # type: (float, float, int, int) -> None
        self.width = _width
        self.height = _height
        self.col = _col
        self.row = _row

    def get_display_name(self):
        # type: () -> str
        return "{}{}".format(self.col, self.row)

    def __str__(self):
        return "{}()".format(self.__class__.__name__)

    def __repr__(self):
        return "{}( width={}, height={}, col={}, row={} )".format(
            self.__class__.__name__, self.width, self.height, self.col, self.row
        )

    def ToString(self):
        return repr(self)


class WindowUnitType(object):
    """A Class to organize a single Window 'Type' with all its WindowElements."""

    def __init__(self, _IGH, _type_name, _spacer=0.0):
        # type: (gh_io.IGH, str, float) -> None
        self.IGH = _IGH
        self.type_name = _type_name
        self.spacer = _spacer
        self.elements = []

    def elements_by_column(self, _elements):
        # type: (List[WindowElement]) -> List[List[WindowElement]]
        """Return a list with lists of WindowElements sorted by their column"""
        # -- Sort the WindowElements by their column name
        d = defaultdict(list)
        for element in _elements:
            d[element.col].append(element)

        # -- Convert the dict to a list of lists
        output = []
        for k in sorted(d.keys()):
            output.append(d[k])
        return output

    def elements_by_row(self, _elements):
        # type: (List[WindowElement]) -> List[WindowElement]
        """Return a lists of WindowElements sorted by their row."""
        return sorted(_elements, key=lambda e: e.row)

    @property
    def x_vector(self):
        # type: () -> Vector3d
        if not self.base_curve:
            raise ValueError(
                "Error: window {} is missing a base_curve?".format(self.type_name)
            )
        start_pt, end_pt = self.IGH.ghc.EndPoints(self.base_curve)
        return self.IGH.ghc.Vector2Pt(start_pt, end_pt, True).vector

    @property
    def y_vector(self):
        # type: () -> Vector3d
        return self.IGH.ghc.UnitZ(1)

    def build_origin_plane(self, _base_curve):
        # type: (LineCurve) -> Plane
        start_pt, end_pt = self.IGH.ghc.EndPoints(_base_curve)
        pl = self.IGH.ghc.ConstructPlane(start_pt, self.x_vector, self.y_vector)
        return pl

    def build_srfc_base_crv(self, _width, _origin_plane):
        # type: (float, Plane) -> LineCurve
        pt_1 = _origin_plane.Origin
        move_width = _width - self.spacer
        move_vector = self.IGH.ghc.Amplitude(self.x_vector, move_width)
        pt_2 = self.IGH.ghc.Move(pt_1, move_vector).geometry
        return self.IGH.ghc.Line(pt_1, pt_2)

    def build(self, _base_curve):
        # type: (LineCurve) -> Tuple[List[Brep], OrderedDict[int, Dict[str, Any]]]
        """Create the window's Rhino geometry based on the Elements."""
        surfaces_ = []
        id_data_ = OrderedDict()

        # 1)  Get the Base Plane and create a starting origin plane from it
        self.base_curve = _base_curve
        origin_plane = self.build_origin_plane(_base_curve)
        if not origin_plane:
            msg = (
                "Error: Something went wrong building the Origin-Planes for "
                "the window with base-curve: {}. Note this window builder ONLY works for vertical "
                "planar windows. Skylights or windows on sloped surfaces are not supported".format(_base_curve)
            )
            raise Exception(msg)

        # -- Walk through each column, and each row in each column
        for col_element_lists in self.elements_by_column(self.elements):

            # 2) Build the base-curve for the Column's elements
            width = col_element_lists[0].width
            base_curve = self.build_srfc_base_crv(width, origin_plane)

            for row_element in self.elements_by_row(col_element_lists):
                el_id_data = {}
                # -- Extrude the surface
                height = row_element.height
                surfaces_.append(
                    self.IGH.ghc.Extrude(
                        base_curve, self.IGH.ghc.Amplitude(self.y_vector, height)
                    )
                )

                # 2.b)-- Keep track of the id-data for the surface
                el_name = row_element.get_display_name()
                el_id_data["type_name"] = self.type_name
                el_id_data["row"] = row_element.row
                el_id_data["col"] = row_element.col
                id_data_[el_name] = el_id_data

                # 3) Move the base curve up
                base_curve = self.IGH.ghc.Move(
                    base_curve, self.IGH.ghc.Amplitude(self.y_vector, height)
                ).geometry

            # 4) Move the origin plane over to the next column
            origin_plane = self.IGH.ghc.Move(
                origin_plane, self.IGH.ghc.Amplitude(self.x_vector, width)
            ).geometry

        return surfaces_, id_data_

    def __str__(self):
        return "{}()".format(self.__class__.__name__)

    def __repr__(self):
        return "{}(type_name={}, elements={})".format(
            self.__class__.__name__, self.type_name, self.elements
        )

    def ToString(self):
        return repr(self)


class GHCompo_CreateWindowUnitTypes(object):
    def __init__(self, _IGH, _type_names, _widths, _heights, _pos_cols, _pos_rows):
        # type: (gh_io.IGH, List[str], List[float], List[float], List[int], List[int]) -> None
        self.IGH = _IGH
        self.type_names = _type_names
        self.widths = _widths
        self.heights = _heights
        self.pos_cols = _pos_cols
        self.pos_rows = _pos_rows

    def run(self):
        # type: () -> List[WindowUnitType]

        # ------------------------------------------------------------------------------
        # -- Sort all the input data and group by 'Type Name'

        # -- Build up all the types
        window_types = {}
        for type_name in self.type_names:
            window_types[type_name] = WindowUnitType(self.IGH, type_name)

        # -- Add the window elements (sashes) to the types
        input_lists = izip(
            self.type_names, self.widths, self.heights, self.pos_cols, self.pos_rows
        )
        for input_data in input_lists:
            type_name, width, height, pos_col, pos_row = input_data
            window_types[type_name].elements.append(
                WindowElement(width, height, pos_col, pos_row)
            )

        return list(window_types.values())
