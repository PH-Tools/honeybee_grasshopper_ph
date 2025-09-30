# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Write WUFI XML Settings."""

try:
    from typing import Any, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class WufiWriteSettings(object):
    """WUFI-XML Write Settings."""

    def __init__(
        self,
        _group_components=True,
        _merge_faces=False,
        _merge_spaces_by_erv=False,
        _merge_exhaust_vent_devices=False,
        _generate_log_files=0,
        *args,
        **kwargs
    ):
        # type: (bool, Union[bool, float],bool, bool, int, *Any, **Any) -> None
        self.group_components = _group_components
        self.merge_faces = _merge_faces
        self.merge_spaces_by_erv = _merge_spaces_by_erv
        self.merge_exhaust_vent_devices = _merge_exhaust_vent_devices   
        self.generate_log_files = _generate_log_files

    def __str__(self):
        return "WufiWriteSettings(group_components={}, merge_faces={}, merge_spaces_by_erv={}, merge_exhaust_vent_devices={}, generate_log_files={})".format(
            self.group_components, self.merge_faces, self.merge_spaces_by_erv, self.merge_exhaust_vent_devices, self.generate_log_files
        )

    def __repr__(self):
        return self.__str__()

    def ToString(self):
        return self.__str__()


class GHCompo_WriteWufiXmlSettings(object):
    """GHCompo Interface: HBPH - Write WUFI XML Settings."""

    def __init__(
        self, _IGH, _group_components, _merge_faces, _merge_spaces_by_erv, _merge_exhaust_vent_devices, _generate_log_files, *args, **kwargs
    ):
        # type: (gh_io.IGH, bool, Union[bool, float], bool, bool, int, *Any, **Any) -> None
        self.IGH = _IGH
        self.generate_log_files = _generate_log_files or 0

        # -- Group the model components during export to XML?
        if _group_components is None or _group_components == True:
            self.group_components = True  # default == True
        else:
            self.group_components = False

        # -- Merge the model faces during export to XML?
        if _merge_faces is None or _merge_faces is False:
            self.merge_faces = False  # Default = will not merge faces
        elif _merge_faces == True:
            self.merge_faces = True  # Will use default model tolerance
        else:
            self.merge_faces = float(_merge_faces)  # Tolerance

        # -- Merge spaces by ERV?
        if _merge_spaces_by_erv is None or _merge_spaces_by_erv == False:
            self.merge_spaces_by_erv = False  # default == False
        else:
            self.merge_spaces_by_erv = True

        # -- Merge exhaust vent devices?
        if _merge_exhaust_vent_devices is None or _merge_exhaust_vent_devices == False:
            self.merge_exhaust_vent_devices = False  # default == False
        else:
            self.merge_exhaust_vent_devices = True

    def run(self):
        # type: () -> WufiWriteSettings
        return WufiWriteSettings(
            self.group_components,
            self.merge_faces,
            self.merge_spaces_by_erv,
            self.merge_exhaust_vent_devices,
            self.generate_log_files,
        )
