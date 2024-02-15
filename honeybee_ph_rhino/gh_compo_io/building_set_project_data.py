# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Set Model Project Data."""

try:
    from typing import Dict, List, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import model
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph.team import ProjectTeam, ProjectTeamMember
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_SetProjectData(object):
    def __init__(
        self, _IGH, _customer, _building, _owner, _designer, _model, *args, **kwargs
    ):
        # type: (gh_io.IGH, ProjectTeamMember, ProjectTeamMember, ProjectTeamMember, ProjectTeamMember, model.Model, List, Dict) -> None
        self.IGH = _IGH
        self.customer = _customer
        self.building = _building
        self.owner = _owner
        self.designer = _designer
        self.model = _model

    def run(self):
        # type: () -> Optional[model.Model]
        if not self.model:
            return None

        # -- Make a new team
        existing_team = self.model.properties.ph.team  # type: ProjectTeam # type: ignore
        new_team = ProjectTeam()
        new_team.customer = self.customer or existing_team.customer
        new_team.building = self.building or existing_team.building
        new_team.owner = self.owner or existing_team.owner
        new_team.designer = self.designer or existing_team.designer

        # -- Set the HB-model's Team
        model_ = self.model.duplicate()  # type: model.Model # type: ignore
        model_.properties.ph.team = new_team

        return model_
