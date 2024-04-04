# -*- Python Version: 2.7 -*-
# -*- coding: utf-8 -*-

"""GHCompo Interface: HBPH - Apply SHW System."""

try:
    from typing import List, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from ladybug_rhino.config import conversion_to_meters
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy import shw
    from honeybee_energy.properties.room import RoomEnergyProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))


class GHCompo_ApplySHWSys(object):
    """Interface for the GH Component"""

    def __init__(self, _hb_shw, _hb_rooms):
        # type: (shw.SHWSystem, List[room.Room]) -> None
        self.hb_shw = _hb_shw
        self.hb_rooms = _hb_rooms

    def set_absolute_service_hot_water(self, _hb_e_prop, _flow_rate=0.001):
        # type: (RoomEnergyProperties, Optional[float]) -> RoomEnergyProperties
        """Set the Absolute Hot Water Flow Rate on an HB-Room's .properties.energy

        Implemented to support HBE <1.5 and 1.6 where they corrected the type on the
        attribute name (added the missing 's' in 'absolute')

        Arguments:
        ----------
            * hb_e_prop (): The Honeybee-Room .properties.energy to modify
            * _flow_rate (float): Liters / Hour flow rate. Default=0.001 L/hr

        Returns:
        --------
            *
        """
        if hasattr(_hb_e_prop, "abolute_service_hot_water"):
            _hb_e_prop.abolute_service_hot_water(_flow_rate, conversion_to_meters())  # type: ignore
        else:
            _hb_e_prop.absolute_service_hot_water(_flow_rate, conversion_to_meters())  # type: ignore

        return _hb_e_prop

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

        hb_rooms_ = []  # type: List[room.Room]
        for room in self.hb_rooms:
            new_room = room.duplicate()  # type: room.Room # type: ignore

            hb_energy_props = new_room.properties.energy  # type: RoomEnergyProperties # type: ignore
            if hb_energy_props.service_hot_water is None:
                # -- Assign a Hot Water flow first
                # -- this will add a default service_hot_water load
                # -- if it doesn't already exist
                hb_energy_props = self.set_absolute_service_hot_water(hb_energy_props)

            hb_energy_props.shw = self.hb_shw
            hb_rooms_.append(new_room)

        return hb_rooms_
