# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Phius Program Finder."""

try:
    from typing import List, Optional
except ImportError:
    pass #IronPython 2.7

try:
    from honeybee_energy.programtype import ProgramType
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from honeybee_energy_ph.library import programtypes
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


class GHCompo_FindPhiusProgram(object):

    def __init__(self, _IGH, _name, _description, _protocol, _base_program):
        # type: (gh_io.IGH, str, str, str, str) -> None
        self.IGH = _IGH
        self.name = _name
        self.description = _description
        self.protocol = _protocol
        self.base_program = _base_program

    def run(self):
        # type: () -> Optional[List[ProgramType]]

        # -- Get the data from in the Phius data set
        if not self.name and not self.description:
            msg = "Input a name or a description of the space to find a Program."
            self.IGH.warning(msg)
            return None
        
        if self.name:
            prog_data = programtypes.load_data_from_Phius_standards(self.name, 'name', self.protocol)
            if not prog_data:
                msg = "No Phius data found for name: '{}'".format(self.name)
                self.IGH.warning(msg)
        elif self.description:
            prog_data = programtypes.load_data_from_Phius_standards(self.description, 'description', self.protocol)
            if not prog_data:
                msg = "No Phius data found for description: '{}'".format(self.description)
                self.IGH.warning(msg)
        else:
            prog_data = []
            msg = "No Phius data found for name: '{}' or description: '{}'".format(self.name, self.description)
            self.IGH.warning(msg)

        # ------------------------------------------------------------------------------
        # -- Turn the datasets found into a HB Programs
        programs_ = []
        for data in prog_data:
            prog = programtypes.build_hb_program_from_Phius_data(data)
            programs_.append(prog)

        return programs_