# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Res Occupancy."""

try:
    from typing import List
except ImportError:
    pass # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from honeybee_energy.load import people
    from honeybee_energy.lib import schedules
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

class GHCompo_SetResOccupancy(object):

    def __init__(self, _IGH, _num_bedrooms, _hb_rooms):
        # type: (gh_io.IGH, List[int], List[room.Room]) -> None
        self.IGH = _IGH
        self.number_bedrooms = _num_bedrooms
        self.hb_rooms = _hb_rooms

    def dup_load(self, hb_obj, object_name, object_class):
        """Duplicate a load object assigned to a Room or ProgramType."""
        # get the always on schedule
        always_on = schedules.schedule_by_identifier('Always On')

        # try to get the load object assigned to the Room or ProgramType
        try:  # assume it's a Room
            load_obj = hb_obj.properties
            for attribute in ('energy', object_name):
                load_obj = getattr(load_obj, attribute)
        except AttributeError:  # it's a ProgramType
            load_obj = getattr(hb_obj, object_name)

        load_id = '{}_{}'.format(hb_obj.identifier, object_name)
        try:  # duplicate the load object
            dup_load = load_obj.duplicate()
            dup_load.identifier = load_id
            return dup_load
        except AttributeError:  # create a new object
            try:  # assume it's People, Lighting, Equipment or Infiltration
                return object_class(load_id, 0, always_on)
            except:  # it's a Ventilation object
                return object_class(load_id)
   
    def run(self):
        hb_rooms_ = []
        
        for i, room in enumerate(self.hb_rooms):
            try:
                room_num_bedrooms = self.number_bedrooms[i]
            except IndexError:
                try:
                    room_num_bedrooms = self.number_bedrooms[0]
                except IndexError:
                    hb_rooms_.append(room)
                    continue
            
            new_room = room.duplicate()
            new_hb_ppl_obj = self.dup_load(new_room, 'people', people.People)
            
            # -- Set the properties
            new_hb_ppl_obj.properties.ph.number_bedrooms = room_num_bedrooms
            new_hb_ppl_obj.properties.ph.number_people = room_num_bedrooms + 1
            ppl_per_m2 = new_hb_ppl_obj.properties.ph.number_people / room.floor_area
            new_hb_ppl_obj.people_per_area = ppl_per_m2
            new_hb_ppl_obj.properties.ph.is_dwelling_unit = True
            
            new_room.properties.energy.people = new_hb_ppl_obj # type: ignore
            hb_rooms_.append(new_room)
        
        return hb_rooms_