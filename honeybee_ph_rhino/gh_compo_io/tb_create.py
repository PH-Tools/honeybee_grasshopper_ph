# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Add Thermal Bridges to Rooms."""

from uuid import uuid4

try:
    from typing import List, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from ladybug_rhino.togeometry import to_polyline3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from ladybug_geometry.geometry3d.polyline import LineSegment3D, Polyline3D
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_geometry:\n\t{}".format(e))

from honeybee_energy_ph.construction import thermal_bridge
from honeybee_ph_utils import input_tools

from honeybee_ph_rhino import gh_io
from honeybee_ph_rhino.gh_compo_io import ghio_validators


class _TBBuilder(object):
    """Interface for collect and clean PhThermalBridge user-inputs"""

    display_name = ghio_validators.HBName("display_name", default="_unnamed_bldg_segment_")
    psi_value = ghio_validators.UnitW_MK("psi_value", default=0.1)
    fRsi_value = ghio_validators.FloatPercentage("fRsi_value", default=0.75)
    quantity = ghio_validators.Float("quantity", default=1.0)

    def __init__(
        self,
        _IGH,
        _geometry,
        _display_name="_unnamed_bldg_segment_",
        _psi=0.1,
        _fRsi=0.75,
        _quantity=1.0,
        _grp_type=15,
    ):
        # type: (gh_io.IGH, Union[Polyline3D, LineSegment3D], str, float, float, float, int) -> None
        self.IGH = _IGH
        self.geometry = _geometry
        self.display_name = _display_name
        self.psi_value = _psi
        self.fRsi_value = _fRsi
        self.quantity = _quantity
        self.group_type = _grp_type

    def _convert_to_polyline(self, _input):
        """Try to convert to a Rhino Polyline object"""
        cps = self.IGH.ghpythonlib_components.ControlPoints(_input).points
        return self.IGH.ghpythonlib_components.PolyLine(cps, False)

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, _input):
        try:
            self._geometry = to_polyline3d(_input)
        except:
            try:
                self._geometry = to_polyline3d(self._convert_to_polyline(_input))
            except Exception as e:
                raise Exception("{}\nError: Input {} cannot be converted to an LBT Polyline3D?".format(e, _input))

    @property
    def group_type(self):
        return self._group_type

    @group_type.setter
    def group_type(self, _in):
        # type: (int) -> None
        input_int = input_tools.input_to_int(_in)
        if input_int:
            self._group_type = thermal_bridge.PhThermalBridgeType(input_int)
        else:
            self._group_type = thermal_bridge.PhThermalBridgeType(15)

    def create_hbph_thermal_bridge(self):
        # type () -> thermal_bridge.PhThermalBridge
        if not self.geometry:
            raise Exception("Error: Invalid or None Geometry input? Cannot build Thermal Bridge.")

        new_obj = thermal_bridge.PhThermalBridge(uuid4(), self.geometry)
        new_obj.display_name = self.display_name
        new_obj.psi_value = self.psi_value
        new_obj.fRsi_value = self.fRsi_value
        new_obj.quantity = self.quantity
        new_obj.group_type = self.group_type.number

        return new_obj


class GHCompo_CreateTB(object):
    def __init__(self, _IGH, _geometry, _names, _psi_values, _fRsi_values, _types, _quantities):
        self.IGH = _IGH
        self.geometry = _geometry
        self.names = _names
        self.psi_values = _psi_values
        self.fRsi_values = _fRsi_values
        self.types = _types
        self.quantities = _quantities

    def run(self):
        # type: () -> List[thermal_bridge.PhThermalBridge]
        thermal_bridges_ = []
        for i in range(len(self.geometry)):
            tb_builder = _TBBuilder(
                self.IGH,
                input_tools.clean_get(self.geometry, i),
                input_tools.clean_get(self.names, i),
                input_tools.clean_get(self.psi_values, i),
                input_tools.clean_get(self.fRsi_values, i, 0.75),
                input_tools.clean_get(self.quantities, i, 1),
                input_tools.clean_get(self.types, i, 15),
            )
            thermal_bridges_.append(tb_builder.create_hbph_thermal_bridge())

        return thermal_bridges_
