# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Apply SHW System."""

try:
    from typing import List, Optional
except ImportError:
    pass # IronPython 2.7

try:
    from ladybug_rhino.config import conversion_to_meters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:
    from honeybee import room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy import shw
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

class GHCompo_ApplySHWSys(object):
    """Interface for the GH Component"""

    def __init__(self, _hb_shw, _hb_rooms):
        # type: (shw.SHWSystem, List[room.Room]) -> None
        self.hb_shw = _hb_shw
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> Optional[List[room.Room]]
        """Assign the new HB-Energy SHW System to each HB-Room.

        Returns:
        --------
            * (List[room.Room]): A list of the HB-Room with their HB-Energy
                SHW System modified.
        """
        
        if self.hb_shw is None:
            return self.hb_rooms

        hb_rooms_ = [] # type: List[room.Room]
        for room in self.hb_rooms:
            new_room = room.duplicate()

            hb_energy_props = new_room.properties.energy # type: ignore
            
            if hb_energy_props.service_hot_water is None:
                # -- Assign a Hot Water flow first
                # -- this will add a default service_hot_water load
                flow = 0.001 # L/hour
                hb_energy_props.abolute_service_hot_water(flow, conversion_to_meters())
            
            hb_energy_props.shw = self.hb_shw
            hb_rooms_.append(new_room)

        return hb_rooms_
