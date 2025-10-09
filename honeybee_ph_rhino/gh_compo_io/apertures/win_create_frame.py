# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create PH Window Frame."""

try:
    from honeybee.typing import clean_and_id_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction import window
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import validators
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))


class GHCompo_CreatePhWinFrame(object):
    """Interface to collect and clean PhWindowFrame user-inputs."""

    display_name = validators.HBName("display_name")

    def __init__(self, _display_name, _top, _right, _bottom, _left):
        # type: (str, window.PhWindowFrameElement | None, window.PhWindowFrameElement | None,  window.PhWindowFrameElement | None,  window.PhWindowFrameElement | None) -> None
        self.display_name = _display_name or clean_and_id_ep_string("PhWindowFrame")
        self._top = _top
        self._right = _right
        self._bottom = _bottom
        self._left = _left

        self._default_frame = window.PhWindowFrameElement(clean_and_id_ep_string("PhWindowFrameElement"))

    @property
    def top(self):
        # type: () -> window.PhWindowFrameElement
        return self._top or self._default_frame

    @top.setter
    def top(self, _in):
        if _in is not None:
            self._top = _in

    @property
    def right(self):
        # type: () -> window.PhWindowFrameElement
        return self._right or self.top

    @right.setter
    def right(self, _in):
        if _in is not None:
            self._right = _in

    @property
    def bottom(self):
        # type: () -> window.PhWindowFrameElement
        return self._bottom or self.top

    @bottom.setter
    def bottom(self, _in):
        if _in is not None:
            self._bottom = _in

    @property
    def left(self):
        # type: () -> window.PhWindowFrameElement
        return self._left or self.top

    @left.setter
    def left(self, _in):
        if _in is not None:
            self._left = _in

    def run(self):
        # type: () -> window.PhWindowFrame
        """Returns a new HBPH PhWindowFrame object."""

        obj = window.PhWindowFrame(self.display_name)
        obj.display_name = self.display_name
        obj.top = self.top
        obj.left = self.left
        obj.bottom = self.bottom
        obj.right = self.right

        return obj

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self.display_name)
