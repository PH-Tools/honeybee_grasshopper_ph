# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Rebuild Window Surfaces."""

try:
    from typing import Dict, List, Tuple, Union
except ImportError:
    pass #IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


from ph_units.parser import parse_input
from ph_units.converter import convert

class GHCompo_RebuildWindowSurfaces(object):


    def __init__(self, _IGH, _window_surfaces, _widths, _heights, *args, **kwargs):
        # type: (gh_io.IGH, List, List[float], List[float], List, Dict) -> None
        self.IGH = _IGH
        self.window_surfaces = _window_surfaces
        self.widths = _widths
        self.heights = _heights
    
    def get_height(self, i):
        # type: (int) -> Union[int, float]
        """Get the user-supplied height of the i-th window surface, handle unit conversions."""
        val, unit = parse_input(self.widths[i])
        if not unit:
            return float(val)
        
        rh_unit = self.IGH.get_rhino_unit_system_name()
        result = convert(val, unit, rh_unit)
        if not result:
            msg = "Failed to convert the input width from {} to {}?".format(unit, rh_unit)
            raise Exception(msg)
        print("Converted height {} {} to {} {}".format(val, unit, result, rh_unit))
        return result

    def get_width(self, i):
        # type: (int) -> Union[int, float]
        """Get the user-supplied width of the i-th window surface, handle unit conversions."""
        val, unit = parse_input(self.heights[i])
        if not unit:
            return float(val)
        
        rh_unit = self.IGH.get_rhino_unit_system_name()
        result = convert(val, unit, rh_unit)
        if not result:
            msg = "Failed to convert the input width from {} to {}?".format(unit, rh_unit)
            raise Exception(msg)
        print("Converted width {} {} to {} {}".format(val, unit, result, rh_unit))
        return result

    @property
    def names(self):
        # type: () -> List[Guid]
        with self.IGH.context_rh_doc():
            return [str(self.IGH.ghc.ObjectDetails(s).name) for s in self.window_surfaces]
    
    def rebuild_surface(self, _surface_guid, _i):
        # type: (Guid, int) -> Rhino.Geometry
        
        RADIUS = 0
        
        # -- Get info of the original geometry
        plane = self.IGH.ghc.IsPlanar(_surface_guid, True).plane
        old_centroid = self.IGH.ghc.Area(_surface_guid).centroid
        
        # -- Build the new Geometry
        new_perim = self.IGH.ghc.Rectangle(plane, self.get_width(_i), self.get_height(_i), RADIUS).rectangle
        new_surface = self.IGH.ghc.BoundarySurfaces(new_perim)
        
        # -- Align new geom to old geom
        new_centroid = self.IGH.ghc.Area(new_surface).centroid
        move_vector = self.IGH.ghc.Vector2Pt(new_centroid, old_centroid, False).vector
        
        return self.IGH.ghc.Move(new_surface, move_vector).geometry
    
    def run(self):
        # type: () -> Tuple[List[Rhino.Geometry], List[str]]

        if not self.window_surfaces:
            return [], []

        if not self.widths or not self.heights:
            return self.window_surfaces, self.names
    
        if not len(self.window_surfaces) == len(self.widths) == len(self.heights):
            msg = "Error: The lengths of the inputs do not match?"
            self.IGH.error(msg)
            return [], []
    
        new_surfaces_ = []
        for i, surface in enumerate(self.window_surfaces):
            new_surfaces_.append(self.rebuild_surface(surface, i))
    
        return new_surfaces_, self.names