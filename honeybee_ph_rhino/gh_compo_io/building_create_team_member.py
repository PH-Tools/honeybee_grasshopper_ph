# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Model Project Data."""

try:
    from typing import Optional, List, Dict
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph.team import ProjectTeamMember
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreateProjectTeamMember(object):
    def __init__(
        self, _IGH, _name, _street, _city, _post_code, _telephone, _email, *args, **kwargs
    ):
        # type: (gh_io.IGH, Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], List, Dict) -> None
        self.IGH = _IGH
        self.name = _name
        self.street = _street
        self.city = _city
        self.post_code = _post_code
        self.telephone = _telephone
        self.email = _email

    def __bool__(self):
        # type: () -> bool
        return any(
            {
                self.name,
                self.street,
                self.city,
                self.post_code,
                self.telephone,
                self.email,
            }
        )

    def __nonzero__(self):
        # type: () -> bool
        return self.__bool__()

    def run(self):
        # type: () -> Optional[ProjectTeamMember]
        new_team_member = ProjectTeamMember()

        new_team_member.name = self.name
        new_team_member.street = self.street
        new_team_member.city = self.city
        new_team_member.post_code = self.post_code
        new_team_member.telephone = self.telephone
        new_team_member.email = self.email

        return new_team_member
