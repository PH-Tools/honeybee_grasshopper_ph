# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH Climate Monthly Radiation."""

try:
    from typing import Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph import phi
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


class GHCompo_PhiCertification(object):

    def __init__(self, _IGH, _building_category_type, _building_use_type, _ihg_type, _occupancy_type, _certification_type, _certification_class, _primary_energy_type, _enerphit_type, _retrofit,):
        # type: (gh_io.IGH, Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], Optional[int], Optional[int]) -> None
        self.IGH = gh_io.input_to_int(_IGH)
        self.building_category_type = gh_io.input_to_int(_building_category_type)
        self.building_use_type = gh_io.input_to_int(_building_use_type)
        self.ihg_type = gh_io.input_to_int(_ihg_type)
        self.occupancy_type = gh_io.input_to_int(_occupancy_type)
        self.certification_type = gh_io.input_to_int(_certification_type)
        self.certification_class = gh_io.input_to_int(_certification_class)
        self.primary_energy_type = gh_io.input_to_int(_primary_energy_type)
        self.enerphit_type = gh_io.input_to_int(_enerphit_type)
        self.retrofit = gh_io.input_to_int(_retrofit)

    def run(self):
        # type: () -> phi.PhiCertification
        phi_certification_ =  phi.PhiCertification()

        phi_certification_.building_category_type = self.building_category_type
        phi_certification_.building_use_type = self.building_use_type
        phi_certification_.ihg_type = self.ihg_type
        phi_certification_.occupancy_type = self.occupancy_type

        phi_certification_.certification_type = self.certification_type
        phi_certification_.certification_class = self.certification_class
        phi_certification_.primary_energy_type = self.primary_energy_type
        phi_certification_.enerphit_type = self.enerphit_type
        phi_certification_.retrofit_type = self.retrofit

        return phi_certification_